# OpenCode — Open Claude API Configuration

> **Source**: https://open-claude.com/docs#opencode
> **Date**: 2026-05-22
> **OpenCode version**: v1.15.7 (schema: https://opencode.ai/config.json)

## Key Learning

OpenCode v1.15.7 config schema differs from older docs:
- `model` at top-level is a **string** (`provider/model`), NOT an object map
- Models are declared under each provider with a `models` key
- Two providers needed for GPT vs Claude: `@ai-sdk/openai-compatible` and `@ai-sdk/anthropic`

## Working Config Template

File: `~/.config/opencode/opencode.jsonc`

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openclaude/gpt-5.4",          // default model: provider/id
  "provider": {
    "openclaude": {
      "name": "Open Claude (GPT)",
      "npm": "@ai-sdk/openai-compatible",  // for GPT/Gemini models
      "options": {
        "apiKey": "YOUR_API_KEY",
        "baseURL": "https://open-claude.com/v1"
      },
      "models": {
        "gpt-5.5": { "name": "GPT-5.5" },
        "gpt-5.4": { "name": "GPT-5.4" }
      }
    },
    "openclaude-anthropic": {
      "name": "Open Claude (Claude)",
      "npm": "@ai-sdk/anthropic",          // for Claude models
      "options": {
        "apiKey": "YOUR_API_KEY",
        "baseURL": "https://open-claude.com/v1"
      },
      "models": {
        "claude-opus-4-7": { "name": "Claude Opus 4.7" },
        "claude-opus-4-6": { "name": "Claude Opus 4.6" },
        "claude-sonnet-4-6": { "name": "Claude Sonnet 4.6" }
      }
    }
  }
}
```

## Usage

```bash
# Use specific model
opencode run 'prompt' --model openclaude/gpt-5.5
opencode run 'prompt' --model openclaude-anthropic/claude-sonnet-4-6

# Or interactive
opencode
# Then press Ctrl+X M to switch models
```

## Pitfalls

- **Schema mismatch**: Older docs show `model` as an object map — OpenCode v1.15+ expects a string `provider/id`. Error: `"Expected string | undefined, got {...}"` means the model field format is wrong.
- **npm packages**: OpenCode auto-installs `@ai-sdk/openai-compatible` and `@ai-sdk/anthropic` into `~/.config/opencode/node_modules/` on first run. No manual install needed.
- **Same baseURL, different SDKs**: Both providers point to `https://open-claude.com/v1` but use different npm packages because GPT models need OpenAI-compatible SDK while Claude models need Anthropic SDK.

## Verification

```bash
cd $(mktemp -d) && git init && opencode run 'Reply exactly: CONFIG_OK' --model openclaude/gpt-5.4
# Expected: CONFIG_OK
```
