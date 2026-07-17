# Cross-platform setup

## Contents

- Install the skill
- Automatic CC Switch discovery
- Explicit environment configuration
- Windows invocation
- Linux and macOS invocation
- Provider compatibility and errors

## Install the skill

Copy the complete `upstream-imagegen` directory into the active agent's skill directory. Start a new agent session after installation so the skill catalog is refreshed.

### Windows PowerShell

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
New-Item -ItemType Directory -Force (Join-Path $codexHome "skills") | Out-Null
Copy-Item -Recurse -Force ".\dev-tools\upstream-imagegen" (Join-Path $codexHome "skills\upstream-imagegen")
```

### Linux and macOS

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R ./dev-tools/upstream-imagegen "${CODEX_HOME:-$HOME/.codex}/skills/upstream-imagegen"
```

## Automatic CC Switch discovery

The script reads the active Codex provider on every run. It does not hard-code a relay name, URL, group, or credential.

| Platform | Default Codex configuration |
|----------|-----------------------------|
| Windows | `%USERPROFILE%\.codex\config.toml` |
| Linux | `$HOME/.codex/config.toml` |
| macOS | `$HOME/.codex/config.toml` |
| Custom | `$CODEX_HOME/config.toml` |

Recognized active-provider fields include:

- `base_url`
- `experimental_bearer_token`
- `env_key` or `env_key_name`
- `http_headers`
- `env_http_headers`
- `requires_openai_auth`, with `auth.json` API-key fallback

CC Switch changes take effect on the next script execution because configuration is read at runtime.

## Explicit environment configuration

Use explicit variables when the provider is not stored in Codex configuration or when image generation uses a separate key, model, group, or endpoint.

### Windows PowerShell

```powershell
$env:UPSTREAM_IMAGE_API_BASE = "https://relay.example.com/v1"
$env:UPSTREAM_IMAGE_API_KEY = "your-key"
$env:UPSTREAM_IMAGE_MODEL = "gpt-image-2"
```

For a provider-specific group header:

```powershell
$env:UPSTREAM_IMAGE_HEADERS = '{"X-API-Group":"image"}'
```

### Windows Command Prompt

```bat
set UPSTREAM_IMAGE_API_BASE=https://relay.example.com/v1
set UPSTREAM_IMAGE_API_KEY=your-key
set UPSTREAM_IMAGE_MODEL=gpt-image-2
```

### Linux and macOS

```bash
export UPSTREAM_IMAGE_API_BASE="https://relay.example.com/v1"
export UPSTREAM_IMAGE_API_KEY="your-key"
export UPSTREAM_IMAGE_MODEL="gpt-image-2"
```

Set secrets in the environment that launches the agent. Do not paste credentials into chat, commit them to the skill, or pass them as command-line arguments.

## Windows invocation

Use `python` or the Python launcher `py -3.11`. Quote paths containing spaces.

```powershell
py -3.11 ".\scripts\generate_image.py" `
  --prompt-file ".\prompt.txt" `
  --out "C:\Users\me\Pictures\generated.png" `
  --size "1536x1024" `
  --quality high
```

Use a UTF-8 prompt file for long Chinese prompts to avoid PowerShell or CMD quoting differences.

## Linux and macOS invocation

```bash
python3 ./scripts/generate_image.py \
  --prompt-file ./prompt.txt \
  --out "$PWD/generated.png" \
  --size 1536x1024 \
  --quality high
```

## Provider compatibility and errors

| Result | Meaning | Action |
|--------|---------|--------|
| `401` | No usable credential reached the provider | Check the active provider, environment, and `auth_source` in dry-run output |
| `403` | Credential is valid but lacks permission | Check the key's group and image entitlement |
| `404` | Endpoint or model is unavailable | Confirm `/images/generations` support and run `--list-models` |
| `429` | Rate or quota limit | Wait or change an authorized channel |
| `503 model_not_found` | The group has no channel for the requested model | Run `--list-models` and set the returned image model explicitly |

The provider name and group label do not define capability. Successful generation requires a compatible endpoint, a visible model ID, valid authentication, and a group with a working channel.
