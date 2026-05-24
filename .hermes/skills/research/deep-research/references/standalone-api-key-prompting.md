# Standalone Mode: API Key Prompting

When running a research pipeline standalone (not via Hermes agent), the pipeline needs an LLM API key for synthesis. Do not fail silently or use mock data without asking.

## Implementation Pattern

```python
def get_api_key() -> Optional[str]:
    """Get API key from env, config, or interactive prompt."""
    # 1. Environment variable (highest priority)
    for env_var in ["OPENROUTER_API_KEY", "OPENAI_API_KEY", "XAI_API_KEY"]:
        if os.getenv(env_var):
            return os.getenv(env_var)

    # 2. Hermes config (if running inside agent context)
    config_key = load_from_hermes_config()
    if config_key:
        return config_key

    # 3. Interactive prompt (standalone CLI)
    print("LLM API key required for synthesis.")
    print("Options:")
    print("  1. Enter OpenRouter API key")
    print("  2. Enter OpenAI API key")
    print("  3. Use mock mode (testing only)")
    choice = input("Choice [1/2/3]: ").strip()

    if choice == "1":
        key = input("OpenRouter API key: ").strip()
        return key
    elif choice == "2":
        key = input("OpenAI API key: ").strip()
        return key
    elif choice == "3":
        return None  # triggers mock mode

    return None
```

## Mock Mode for Testing

When no API key is available, use mock mode to verify the pipeline end-to-end:

```python
def call_llm(prompt: str, model: str, api_key: Optional[str]) -> str:
    if not api_key:
        logger.warning("No API key — using mock synthesis")
        return generate_mock_response(prompt)

    # Normal API call...
```

**Important:** Always log when falling back to mock mode. Never silently serve mock data as if it were real.
