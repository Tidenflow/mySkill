#!/usr/bin/env python3
"""Generate images through an OpenAI-compatible upstream HTTP endpoint."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - only possible on Python < 3.11
    tomllib = None  # type: ignore[assignment]


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-image-2"
DATA_URL_RE = re.compile(
    r"data:(image/[a-zA-Z0-9.+-]+);base64,([A-Za-z0-9+/=\r\n]+)"
)
URL_RE = re.compile(r"https?://[^\s\"'<>]+")
EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


class GenerationError(RuntimeError):
    """Raised for safe, user-facing generation failures."""


@dataclass
class Upstream:
    api_base: str
    generation_endpoint: str
    models_endpoint: str
    api_key: str | None
    provider_headers: dict[str, str]
    environment_headers: dict[str, str]
    provider_source: str
    auth_source: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call an upstream OpenAI-compatible image generation endpoint."
    )
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument("--prompt", help="Text-to-image prompt")
    prompt_group.add_argument("--prompt-file", type=Path, help="UTF-8 prompt file")
    parser.add_argument("--out", type=Path, help="Output image path")
    parser.add_argument("--model", help="Image model override")
    parser.add_argument("--api-base", help="API base URL override")
    parser.add_argument("--endpoint", help="Complete generation endpoint override")
    parser.add_argument("--models-endpoint", help="Complete models endpoint override")
    parser.add_argument(
        "--codex-config",
        type=Path,
        help="Codex config.toml path; defaults to $CODEX_HOME/config.toml",
    )
    parser.add_argument(
        "--no-codex-config",
        action="store_true",
        help="Do not reuse the active Codex/CC Switch provider",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List model IDs visible to the resolved provider, then exit",
    )
    parser.add_argument("--size", default="1536x1024", help="Requested image size")
    parser.add_argument(
        "--quality", default="high", choices=("auto", "low", "medium", "high")
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        default="png",
        choices=("png", "jpeg", "webp"),
    )
    parser.add_argument(
        "--background", choices=("auto", "opaque", "transparent")
    )
    parser.add_argument("--compression", type=int, help="JPEG/WebP compression 0-100")
    parser.add_argument("--n", type=int, default=1, help="Number of images")
    parser.add_argument("--timeout", type=float, default=300, help="HTTP timeout seconds")
    parser.add_argument(
        "--extra-json", default="{}", help="Provider-specific JSON request fields"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing output files",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print resolved request details, then exit"
    )
    return parser.parse_args()


def env_first(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def parse_json_object(raw: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GenerationError(f"{label} is not valid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise GenerationError(f"{label} must be a JSON object")
    return value


def string_headers(value: Any, label: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str)
        for key, item in value.items()
    ):
        raise GenerationError(f"{label} must contain only string keys and values")
    return dict(value)


def default_codex_config_path() -> Path:
    explicit = env_first("CODEX_CONFIG_PATH", "CODEX_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "config.toml"
    return Path.home() / ".codex" / "config.toml"


def load_auth_json_key(config_path: Path) -> str | None:
    auth_path = config_path.parent / "auth.json"
    if not auth_path.is_file():
        return None
    try:
        value = json.loads(auth_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    api_key = value.get("OPENAI_API_KEY")
    return api_key if isinstance(api_key, str) and api_key else None


def load_codex_provider(path: Path) -> dict[str, Any]:
    """Load reusable upstream fields from the active Codex provider."""
    if not path.is_file():
        return {}
    if tomllib is None:
        raise GenerationError(
            "Codex config discovery requires Python 3.11+; use environment variables "
            "or --no-codex-config with an older Python"
        )
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise GenerationError(f"could not read Codex configuration {path}: {exc}") from exc

    provider_name = config.get("model_provider")
    providers = config.get("model_providers", {})
    if not isinstance(provider_name, str) or not isinstance(providers, dict):
        return {}
    provider = providers.get(provider_name)
    if not isinstance(provider, dict):
        return {}

    resolved: dict[str, Any] = {
        "provider_name": provider_name,
        "headers": string_headers(
            provider.get("http_headers"),
            f"model_providers.{provider_name}.http_headers",
        ),
    }

    base_url = provider.get("base_url")
    if isinstance(base_url, str) and base_url:
        resolved["base_url"] = base_url

    env_headers = provider.get("env_http_headers")
    if env_headers is not None:
        mapping = string_headers(
            env_headers, f"model_providers.{provider_name}.env_http_headers"
        )
        for header_name, variable_name in mapping.items():
            value = os.environ.get(variable_name)
            if value:
                resolved["headers"][header_name] = value

    env_key_name = provider.get("env_key") or provider.get("env_key_name")
    if isinstance(env_key_name, str) and env_key_name:
        env_key = os.environ.get(env_key_name)
        if env_key:
            resolved["api_key"] = env_key
            resolved["auth_source"] = f"codex-provider-env:{env_key_name}"

    bearer_token = provider.get("experimental_bearer_token")
    if "api_key" not in resolved and isinstance(bearer_token, str) and bearer_token:
        resolved["api_key"] = bearer_token
        resolved["auth_source"] = "codex-provider-token"

    if "api_key" not in resolved and provider.get("requires_openai_auth") is True:
        auth_key = load_auth_json_key(path)
        if auth_key:
            resolved["api_key"] = auth_key
            resolved["auth_source"] = "codex-auth-json"

    return resolved


def normalize_endpoint(api_base: str, suffix: str, override: str | None) -> str:
    if override:
        return override
    return api_base.rstrip("/") + suffix


def environment_headers() -> dict[str, str]:
    raw = os.environ.get("UPSTREAM_IMAGE_HEADERS")
    if not raw:
        return {}
    return string_headers(
        parse_json_object(raw, "UPSTREAM_IMAGE_HEADERS"),
        "UPSTREAM_IMAGE_HEADERS",
    )


def resolve_upstream(args: argparse.Namespace) -> Upstream:
    provider: dict[str, Any] = {}
    config_path = (args.codex_config or default_codex_config_path()).expanduser()
    if not args.no_codex_config:
        provider = load_codex_provider(config_path)

    explicit_base = args.api_base or env_first(
        "UPSTREAM_IMAGE_API_BASE", "OPENAI_BASE_URL"
    )
    api_base = explicit_base or provider.get("base_url") or DEFAULT_BASE_URL
    generation_endpoint = normalize_endpoint(
        api_base,
        "/images/generations",
        args.endpoint or os.environ.get("UPSTREAM_IMAGE_ENDPOINT"),
    )
    models_endpoint = normalize_endpoint(
        api_base,
        "/models",
        args.models_endpoint or os.environ.get("UPSTREAM_IMAGE_MODELS_ENDPOINT"),
    )

    environment_key = env_first("UPSTREAM_IMAGE_API_KEY", "OPENAI_API_KEY")
    api_key = environment_key or provider.get("api_key")
    if explicit_base:
        provider_source = "command/environment"
    elif provider.get("base_url"):
        provider_source = f"codex-config:{provider.get('provider_name', 'active')}"
    else:
        provider_source = "default"

    if environment_key:
        auth_source = "environment"
    else:
        auth_source = str(provider.get("auth_source", "none"))

    return Upstream(
        api_base=api_base,
        generation_endpoint=generation_endpoint,
        models_endpoint=models_endpoint,
        api_key=api_key if isinstance(api_key, str) else None,
        provider_headers=string_headers(provider.get("headers"), "provider headers"),
        environment_headers=environment_headers(),
        provider_source=provider_source,
        auth_source=auth_source,
    )


def authorization_value(api_key: str) -> str:
    if api_key.lower().startswith(("bearer ", "basic ")):
        return api_key
    return f"Bearer {api_key}"


def request_headers(
    upstream: Upstream,
    *,
    accept: str = "application/json, image/*",
    include_content_type: bool = True,
) -> dict[str, str]:
    headers = {"Accept": accept}
    if include_content_type:
        headers["Content-Type"] = "application/json"
    headers.update(upstream.provider_headers)
    if upstream.api_key and not any(
        key.lower() == "authorization" for key in headers
    ):
        headers["Authorization"] = authorization_value(upstream.api_key)
    headers.update(upstream.environment_headers)
    return headers


def has_authentication(upstream: Upstream) -> bool:
    return any(
        key.lower() in {"authorization", "x-api-key", "api-key"}
        for key in request_headers(upstream)
    )


def build_payload(args: argparse.Namespace, prompt: str) -> dict[str, Any]:
    if args.n < 1:
        raise GenerationError("--n must be at least 1")
    if args.compression is not None and not 0 <= args.compression <= 100:
        raise GenerationError("--compression must be between 0 and 100")

    payload = parse_json_object(args.extra_json, "--extra-json")
    payload.update(
        {
            "model": args.model
            or env_first("UPSTREAM_IMAGE_MODEL", "IMAGE_MODEL")
            or DEFAULT_MODEL,
            "prompt": prompt,
            "n": args.n,
            "size": args.size,
            "quality": args.quality,
            "output_format": args.output_format,
        }
    )
    if args.background:
        payload["background"] = args.background
    if args.compression is not None:
        payload["output_compression"] = args.compression
    return payload


def safe_http_error(exc: urllib.error.HTTPError) -> GenerationError:
    body = exc.read().decode("utf-8", errors="replace")[:2000]
    return GenerationError(f"upstream returned HTTP {exc.code}: {body}")


def list_models(upstream: Upstream, timeout: float) -> list[str]:
    request = urllib.request.Request(
        upstream.models_endpoint,
        headers=request_headers(
            upstream, accept="application/json", include_content_type=False
        ),
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        raise safe_http_error(exc) from exc
    except urllib.error.URLError as exc:
        raise GenerationError(f"could not reach upstream: {exc.reason}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise GenerationError("models endpoint returned invalid JSON") from exc

    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        raise GenerationError("models endpoint response does not contain data[]")
    model_ids = {
        item.get("id")
        for item in data["data"]
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    return sorted(model_ids, key=str.lower)


def decode_base64(value: str) -> bytes | None:
    compact = "".join(value.split())
    if len(compact) < 16:
        return None
    try:
        return base64.b64decode(compact, validate=True)
    except (binascii.Error, ValueError):
        return None


def candidates_from_json(value: Any) -> list[tuple[str, bytes | str, str | None]]:
    found: list[tuple[str, bytes | str, str | None]] = []

    def add_text_candidate(text: str) -> None:
        for mime, encoded in DATA_URL_RE.findall(text):
            decoded = decode_base64(encoded)
            if decoded:
                found.append(("bytes", decoded, mime.lower()))
        if text.startswith(("http://", "https://")):
            found.append(("url", text, None))
        else:
            for url in URL_RE.findall(text):
                found.append(("url", url.rstrip(".,);]"), None))

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key in ("b64_json", "image_base64"):
                encoded = node.get(key)
                if isinstance(encoded, str):
                    decoded = decode_base64(encoded)
                    if decoded:
                        found.append(("bytes", decoded, None))

            result = node.get("result")
            node_type = str(node.get("type", ""))
            if isinstance(result, str) and "image" in node_type:
                decoded = decode_base64(result)
                if decoded:
                    found.append(("bytes", decoded, None))

            for key in ("url", "image_url"):
                url_value = node.get(key)
                if isinstance(url_value, dict):
                    url_value = url_value.get("url")
                if isinstance(url_value, str):
                    add_text_candidate(url_value)

            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)
        elif isinstance(node, str):
            add_text_candidate(node)

    visit(value)
    deduped: list[tuple[str, bytes | str, str | None]] = []
    seen: set[tuple[str, str]] = set()
    for kind, data, mime in found:
        marker = (
            kind,
            data
            if isinstance(data, str)
            else hashlib.sha256(data).hexdigest(),
        )
        if marker not in seen:
            seen.add(marker)
            deduped.append((kind, data, mime))
    return deduped


def http_call(
    upstream: Upstream, payload: dict[str, Any], timeout: float
) -> tuple[bytes, str]:
    request = urllib.request.Request(
        upstream.generation_endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=request_headers(upstream),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), response.headers.get_content_type()
    except urllib.error.HTTPError as exc:
        raise safe_http_error(exc) from exc
    except urllib.error.URLError as exc:
        raise GenerationError(f"could not reach upstream: {exc.reason}") from exc


def download(
    url: str, timeout: float, upstream: Upstream
) -> tuple[bytes, str | None]:
    image_origin = urllib.parse.urlsplit(url)[:2]
    api_origin = urllib.parse.urlsplit(upstream.generation_endpoint)[:2]
    if image_origin == api_origin:
        headers = request_headers(
            upstream, accept="image/*", include_content_type=False
        )
    else:
        headers = {"Accept": "image/*"}
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), response.headers.get_content_type()
    except urllib.error.HTTPError as exc:
        raise safe_http_error(exc) from exc
    except urllib.error.URLError as exc:
        raise GenerationError(f"could not download generated image: {exc.reason}") from exc


def image_suffix(mime: str | None, fallback: str) -> str:
    if mime in EXTENSIONS:
        return EXTENSIONS[mime]
    guessed = mimetypes.guess_extension(mime or "")
    return guessed or fallback


def output_paths(base: Path, count: int, fallback_suffix: str) -> list[Path]:
    suffix = base.suffix or fallback_suffix
    stem = base.stem if base.suffix else base.name
    if count == 1:
        return [base if base.suffix else base.with_suffix(suffix)]
    return [base.with_name(f"{stem}-{index}{suffix}") for index in range(1, count + 1)]


def save_candidates(
    candidates: list[tuple[str, bytes | str, str | None]],
    out: Path,
    timeout: float,
    requested_format: str,
    upstream: Upstream,
    overwrite: bool,
) -> list[Path]:
    if not candidates:
        raise GenerationError("upstream response did not contain an image")

    resolved: list[tuple[bytes, str | None]] = []
    for kind, value, mime in candidates:
        if kind == "url":
            data, downloaded_mime = download(str(value), timeout, upstream)
            resolved.append((data, downloaded_mime))
        else:
            resolved.append((bytes(value), mime))

    fallback = ".jpg" if requested_format == "jpeg" else f".{requested_format}"
    paths = output_paths(out, len(resolved), fallback)
    saved: list[Path] = []
    for (data, mime), path in zip(resolved, paths):
        if not path.suffix:
            path = path.with_suffix(image_suffix(mime, fallback))
        if path.exists() and not overwrite:
            raise GenerationError(f"refusing to overwrite existing file: {path}")
        if not data:
            raise GenerationError("upstream returned an empty image")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        saved.append(path.resolve())
    return saved


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return args.prompt_file.expanduser().read_text(encoding="utf-8-sig")
    return args.prompt or ""


def main() -> int:
    args = parse_args()
    try:
        upstream = resolve_upstream(args)

        if args.list_models:
            models = list_models(upstream, args.timeout)
            if not models:
                raise GenerationError("models endpoint returned no model IDs")
            for model in models:
                print(model)
            return 0

        prompt = read_prompt(args).strip()
        if not prompt:
            raise GenerationError("provide --prompt, --prompt-file, or --list-models")
        payload = build_payload(args, prompt)

        if args.dry_run:
            print(
                json.dumps(
                    {
                        "endpoint": upstream.generation_endpoint,
                        "models_endpoint": upstream.models_endpoint,
                        "payload": payload,
                        "provider_source": upstream.provider_source,
                        "auth_source": upstream.auth_source,
                        "authenticated": has_authentication(upstream),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

        if args.out is None:
            raise GenerationError("--out is required for image generation")
        output_path = args.out.expanduser()
        if output_path.exists() and not args.overwrite:
            raise GenerationError(f"refusing to overwrite existing file: {output_path}")

        body, content_type = http_call(upstream, payload, args.timeout)
        if content_type.startswith("image/"):
            candidates = [("bytes", body, content_type)]
        else:
            try:
                response_json = json.loads(body)
            except json.JSONDecodeError as exc:
                raise GenerationError(
                    f"upstream returned neither JSON nor an image ({content_type})"
                ) from exc
            candidates = candidates_from_json(response_json)

        saved = save_candidates(
            candidates,
            output_path,
            args.timeout,
            args.output_format,
            upstream,
            args.overwrite,
        )
        for path in saved:
            print(path)
        return 0
    except (GenerationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
