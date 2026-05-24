# Twitter CLI Integration Notes

## Command
```bash
twitter search "QUERY" -n 20 --json
```

## Output Schema
```json
{
  "ok": true,
  "schema_version": "1",
  "data": [
    {
      "id": "2057034984331137483",
      "text": "tweet text...",
      "author": {
        "id": "1391775967581020169",
        "name": "Display Name",
        "screenName": "handle",
        "profileImageUrl": "...",
        "verified": true
      },
      "metrics": {
        "likes": 10,
        "retweets": 1,
        "replies": 3,
        "quotes": 0,
        "views": 2912,
        "bookmarks": 0
      },
      "createdAt": "Wed May 20 09:45:32 +0000 2026",
      "createdAtLocal": "2026-05-20 16:45",
      "createdAtISO": "2026-05-20T09:45:32+00:00",
      "isRetweet": false,
      "quotedTweet": { ... }
    }
  ]
}
```

## Field Mapping (vs xurl)

| Field | twitter CLI | xurl |
|-------|-------------|------|
| Handle | `author.screenName` | `author.username` |
| Likes | `metrics.likes` | `public_metrics.like_count` |
| RTs | `metrics.retweets` | `public_metrics.retweet_count` |
| Views | `metrics.views` | `public_metrics.impression_count` |
| Timestamp | `createdAtISO` | `created_at` |

## URL Construction
```python
url = f"https://x.com/{author['screenName']}/status/{tweet['id']}"
```

## Auth Requirements
- Must run `twitter auth` first to authenticate
- Uses OAuth2 app credentials
- Read-only operations don't consume API credits
