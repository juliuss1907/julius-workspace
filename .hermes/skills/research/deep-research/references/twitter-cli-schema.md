# Twitter CLI JSON Schema

Tool: `twitter` (distinct from `xurl`)

## Search Command

```bash
twitter search "QUERY" -n 20 --json
```

**Flags:**
- `-n N` — number of results (not `--limit`)
- `--json` — output JSON (required for parsing)

## Response Format

```json
{
  "ok": true,
  "schema_version": "1",
  "data": [
    {
      "id": "2057034984331137483",
      "text": "Tweet text...",
      "author": {
        "screenName": "Eveningtraders",
        "name": "Evening Traders"
      },
      "metrics": {
        "likes": 10,
        "retweets": 5,
        "replies": 2,
        "views": 1000
      },
      "createdAtISO": "2026-05-21T14:30:00.000Z"
    }
  ]
}
```

## Field Mapping

| twitter CLI | xurl / v2 API Equivalent |
|-------------|---------------------------|
| `author.screenName` | `author.username` |
| `author.name` | `author.name` |
| `metrics.likes` | `public_metrics.like_count` |
| `metrics.retweets` | `public_metrics.retweet_count` |
| `metrics.replies` | `public_metrics.reply_count` |
| `metrics.views` | `public_metrics.impression_count` |
| `createdAtISO` | `created_at` |

## URL Construction

```python
f"https://x.com/{author['screenName']}/status/{tweet_id}"
```

## Comparison with xurl

| Feature | twitter CLI | xurl |
|---------|-------------|------|
| Search | ✅ Works | ❌ 401 on free tier |
| Post/Reply | ❌ Unknown | ❌ CreditsDepleted |
| Timeline | ✅ | ✅ |
| Whoami | ✅ | ✅ |
| Rate limit | Unknown | Free tier very limited |

**Recommendation:** Use `twitter` for search, `xurl` for read-only profile/timeline.
