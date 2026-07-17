---
name: upstream-imagegen
description: Generate new raster images through an OpenAI-compatible upstream image API and save them locally. Reuse the active Codex or CC Switch provider on Windows, Linux, and macOS, or accept explicit API environment variables and command-line overrides. Use when the user requests text-to-image generation through a proxy, relay, custom model, or alternative to a built-in image tool. Do not use for editing an existing image or for providers that only expose Responses image-tool generation.
---

# Upstream Image Generator

Generate a bitmap by running `scripts/generate_image.py`. Call the configured upstream `/images/generations` API directly; do not invoke a built-in image-generation tool from this workflow.

## Resolve the upstream

Resolve configuration in this order. Never print, copy, or persist secret values.

1. Use explicit command-line overrides.
2. Use image-specific environment variables.
3. Read the active provider from `${CODEX_HOME}/config.toml` when `CODEX_HOME` is set; otherwise read `~/.codex/config.toml`. On Windows, `~` resolves to `%USERPROFILE%`.
4. Reuse the active provider's `base_url`, bearer token or configured API-key environment variable, and static/environment-backed HTTP headers.
5. Use the public OpenAI defaults only when no configured provider exists.

Recognize these environment variables:

- `UPSTREAM_IMAGE_API_BASE`: API base URL; fall back to `OPENAI_BASE_URL`.
- `UPSTREAM_IMAGE_ENDPOINT`: complete generation endpoint; otherwise append `/images/generations`.
- `UPSTREAM_IMAGE_API_KEY`: bearer token; fall back to `OPENAI_API_KEY`.
- `UPSTREAM_IMAGE_MODEL`: image model; fall back to `IMAGE_MODEL`, then `gpt-image-2`.
- `UPSTREAM_IMAGE_HEADERS`: JSON object containing extra request headers.
- `CODEX_HOME`: alternate Codex configuration directory.

Do not reuse the active Codex text model as the image model. Use `--list-models` when a relay rejects the default model, then pass the available image model through `--model` or `UPSTREAM_IMAGE_MODEL`.

Read [references/platform-setup.md](references/platform-setup.md) when installing or configuring this skill on Windows, when configuration discovery fails, or when the provider needs environment variables or custom headers.

## Generate an image

1. Turn the request into one concise production prompt. Preserve exact requested text, composition requirements, and avoid constraints.
2. Choose an output path in the current workspace. Do not overwrite an existing file unless the user explicitly requests replacement.
3. Inspect the effective provider without sending a request:

```text
python <skill-dir>/scripts/generate_image.py --prompt "diagnostic" --dry-run
```

Confirm that `endpoint`, `provider_source`, `auth_source`, and `authenticated` are plausible. The output must never contain credentials.

4. If the model name is uncertain, list the models visible to the current key:

```text
python <skill-dir>/scripts/generate_image.py --list-models
```

5. Generate the image:

```text
python <skill-dir>/scripts/generate_image.py --prompt "<production prompt>" --out "<absolute-output-path>" --size 1536x1024 --quality high
```

Use `--prompt-file` for long prompts or when shell quoting is unreliable. Use `--model`, `--endpoint`, `--format`, `--background`, or `--extra-json` only when the user or provider requires an override. Use `--overwrite` only with explicit permission.

6. If sandboxed network access fails, request permission and rerun the same command with network access. Do not change providers silently.
7. Inspect the saved image. Verify the subject, composition, requested text, and forbidden elements. Retry once with one targeted correction when needed.
8. Return the saved path and summarize the provider, model, size, and format. Never report the API key or custom header values.

## Provider compatibility

Require Python 3.11 or newer when discovering Codex/CC Switch TOML configuration. The generator otherwise uses only the Python standard library and works with native Windows and POSIX paths.

Send an OpenAI-style JSON request to `/images/generations`. Accept standard `data[].b64_json`, data URLs, ordinary image URLs, Responses-style nested image results, compatible nested image fields, or a direct `image/*` response.

Use `--extra-json` for narrowly scoped provider-specific fields. Explicit command-line fields take precedence.

```text
python <skill-dir>/scripts/generate_image.py --prompt "A precise engineering visualization" --out "<output.png>" --extra-json '{"negative_prompt":"watermark, distorted geometry"}'
```

Do not assume that every relay exposing `/responses` also exposes `/images/generations`. If the provider only supports `responses + image_generation`, report that this direct-image skill is incompatible instead of silently changing API styles.
