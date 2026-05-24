# Web Toolchain Diagnosis

How to trace why `web_search` or `web_extract` is slow, rate-limited, or failing.

---

## The Backend Chain

Hermes web tools use a prioritized chain:

```
web_search / web_extract
    ↓
1. Primary backend (configured in config.yaml → web.backend)
    ↓ fails (not configured / auth missing)
2. Fallback: DuckDuckGo (DDGS) for search, direct HTTP fetch for extract
    ↓
3. Rate limiting on direct HTTP → ⏱️ "Rate limited. Waiting Xs (attempt Y/3)"
```

If Firecrawl is the configured backend but auth is missing, it silently falls through to DDGS/direct HTTP. **web_search will still work** (via DDGS), but **web_extract will hit rate limits** because direct HTTP has no proxy/anti-detection.

---

## Diagnosis Sequence

### Step 1: Check config.yaml

```bash
hermes config | grep -A5 "web:"
```

Key fields:
- `web.backend` — the primary backend (e.g., `firecrawl`)
- `web.use_gateway` — whether to prefer Nous Tool Gateway over direct credentials

### Step 2: Check .env for credentials

```bash
cat ~/.hermes/.env | grep -iE "firecrawl|tavily|exa|brave|tool_gateway|nous_access"
```

For Firecrawl specifically:
- `FIRECRAWL_API_KEY` — cloud API key (firecrawl.dev)
- `FIRECRAWL_API_URL` — self-hosted instance URL
- `FIRECRAWL_GATEWAY_URL` — Nous gateway override
- `TOOL_GATEWAY_USER_TOKEN` — Nous subscriber token for managed gateway
- `NOUS_ACCESS_TOKEN` — alternative Nous auth token

**Common trap**: a variable may be in `.env` but not loaded into the Python process. The `.env` file is read at Hermes gateway startup; `execute_code` sandboxes may not have it. Always verify with `os.environ.get("VAR")` in the process you're debugging.

### Step 3: Test provider readiness

```python
# For Firecrawl:
from plugins.web.firecrawl.provider import (
    check_firecrawl_api_key,
    _has_direct_firecrawl_config,
    _is_tool_gateway_ready,
    _get_direct_firecrawl_config,
)
print(f"check_firecrawl_api_key: {check_firecrawl_api_key()}")
print(f"_has_direct_firecrawl_config: {_has_direct_firecrawl_config()}")
print(f"_is_tool_gateway_ready: {_is_tool_gateway_ready()}")
```

- `check_firecrawl_api_key()` returns `True` if EITHER direct config OR gateway is available
- `_has_direct_firecrawl_config()` returns `True` only if `FIRECRAWL_API_KEY` or `FIRECRAWL_API_URL` is set
- `_is_tool_gateway_ready()` returns `True` if Nous gateway URL + token are available

If all three return `False`, Firecrawl is non-functional → DDGS fallback is active.

### Step 4: Trace the client construction

```python
from plugins.web.firecrawl.provider import _get_firecrawl_client

try:
    client = _get_firecrawl_client()
    print(f"Client created: {type(client).__name__}")
    print(f"api_url: {client.api_url}")
except ValueError as e:
    print(f"Client init failed: {e}")
```

The `_get_firecrawl_client()` function decides between:
1. **Direct mode** — if `FIRECRAWL_API_KEY` or `FIRECRAWL_API_URL` is set AND `web.use_gateway` is not `true`
2. **Gateway mode** — if Nous Tool Gateway is configured
3. **Raises ValueError** — if neither is available

### Step 5: Test the SDK directly

If the client constructs successfully but calls fail, test with the SDK directly:

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_url="https://firecrawl-gateway.nousresearch.com")
result = app.scrape("https://example.com", formats=['markdown'])
```

Common failure modes:
- `UnauthorizedError` → gateway requires auth token not present
- `TypeError: got unexpected keyword argument 'params'` → wrong SDK API (use `formats=['markdown']` as keyword, not `params={...}`)
- `AttributeError: 'Firecrawl' object has no attribute 'scrape_url'` → method is `scrape()`, not `scrape_url()`

---

## Firecrawl SDK Version Differences

Version 4.17.0 (installed via `firecrawl-py`):
- `app.scrape(url, formats=['markdown'])` — keyword args, not `params` dict
- Returns a `Document` object with `.markdown` and `.metadata` attributes
- Not a dict — use attribute access, not `.get()`

---

## Symptoms → Likely Cause

| Symptom | Likely cause |
|---------|-------------|
| `web_search` works, `web_extract` rate-limited | Firecrawl not configured, DDGS doing search but direct HTTP doing extract |
| `⏱️ Rate limited. Waiting Xs...` | Server returned 429, web_extract retry mechanism triggered |
| `ValueError: Web tools are not configured` | No backend credentials set at all |
| Gateway returns `Unauthorized` | `TOOL_GATEWAY_USER_TOKEN` or `NOUS_ACCESS_TOKEN` missing |
| Firecrawl SDK import slow (~200ms) | Normal — SDK is lazy-loaded via proxy in Hermes |

---

## Quick Fix: Enable Firecrawl

### Option A — Firecrawl Cloud (recommended)

```bash
# .env
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxx
```

Get a key at https://firecrawl.dev/

### Option B — Self-hosted

```bash
# .env
FIRECRAWL_API_URL=http://localhost:3002
```

Requires a running Firecrawl instance (e.g., Camoufox-based local browser).

### Option C — Nous Tool Gateway

```bash
# .env
TOOL_GATEWAY_USER_TOKEN=<nous_subscriber_token>
# or
NOUS_ACCESS_TOKEN=<nous_token>
```

Then set in config.yaml:
```yaml
web:
  use_gateway: true
```

### Option D — Accept DDGS fallback

No config needed. Search works, but extract will be direct HTTP (prone to rate limiting). For most non-intensive use this is fine.
