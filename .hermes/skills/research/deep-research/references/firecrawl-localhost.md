# Firecrawl Localhost API

## Base URL
```
http://localhost:3002
```

## Search Endpoint
```bash
POST /v1/search
Content-Type: application/json

{"query": "topic", "limit": 8}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "url": "https://example.com/article",
      "title": "Article Title",
      "description": "Snippet..."
    }
  ],
  "id": "uuid"
}
```

**Key:** The results array is under `"data"`, NOT `"results"`.

## Scrape Endpoint
```bash
POST /v1/scrape
Content-Type: application/json

{"url": "https://example.com", "formats": ["markdown"]}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "...",
    "title": "...",
    "markdown": "# Content...",
    "scraped_at": "..."
  }
}
```

## Error Handling
- 500 errors on scrape: retry with exponential backoff
- Some sites block crawlers (Cloudflare, etc.) — skip and continue
- Timeout: default 60s, increase for heavy pages

## Fallback
If Firecrawl is down, use `web_search` + `web_extract` tools instead.
