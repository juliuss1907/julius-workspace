# OpenCode Custom Provider — Open Claude Pattern

> Example: configuring OpenCode to use Open Claude as a provider gateway for GPT and Claude models.

## Config Structure

File: `~/.config/opencode/opencode.jsonc`

Two providers are needed because GPT models use `@ai-sdk/openai-compatible` and Claude models use `@ai-sdk/anthropic`.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openclaude/gpt-5.4",  // default model
  "provider": {
    "openclaude": {
      "name": "Open Claude (GPT)",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "apiKey": "your-api-key",
        "baseURL": "https://open-claude.com/v1"
      },
      "models": {
        "gpt-5.5": { "name": "GPT-5.5" },
        "gpt-5.4": { "name": "GPT-5.4" }
      }
    },
    "openclaude-anthropic": {
      "name": "Open Claude (Claude)",
      "npm": "@ai-sdk/anthropic",
      "options": {
        "apiKey": "your-api-key",
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

## Key Rules

1. **Top-level `model`** is a string: `provider/model-id` — NOT an object map
2. **Models live under provider**: each provider has a `models` object mapping model IDs to `{ "name": "Display Name" }`
3. **GPT models** → `@ai-sdk/openai-compatible` npm package
4. **Claude models** → `@ai-sdk/anthropic` npm package
5. **Same baseURL** for both: `https://open-claude.com/v1`
6. OpenCode auto-installs npm packages declared in providers on first use

## Usage After Config

```bash
# Check models available
opencode auth list

# Use specific model
opencode run "Refactor auth" --model openclaude-anthropic/claude-sonnet-4-6
opencode run "Debug tests" --model openclaude/gpt-5.4

# Interactive with default model
opencode
```

## Schema Pitfall

OpenCode v1.15.7 changed the config schema from earlier versions:
- **Old/deprecated**: `"model": { "gpt-5.4": { "provider": "...", "name": "..." } }` (object map at top level)
- **Current**: `"model": "provider/id"` (string reference), models declared inside provider objects

Using the old format produces: `Error: Expected string | undefined, got {...}`
