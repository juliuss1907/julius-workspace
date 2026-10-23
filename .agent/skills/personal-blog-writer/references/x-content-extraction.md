# X (Twitter) Content Extraction — Fallback Chain

Personal blog posts often need to cite X/Twitter posts. The 4 direct paths
have all been observed to fail in this environment:

| Method | Failure mode | Reason |
|--------|-------------|--------|
| `web_extract(url)` | blank content | X login wall, JS-rendered |
| `browser-use open url` | 403 / ERR_HTTP_RESPONSE_CODE_FAILURE | X blocks the browser agent |
| `xurl read <id>` | 401 Unauthorized | xurl requires OAuth; not configured |
| `x_search(query)` | "out of credits" | xAI API spending limit reached |
| Nitter instances | ceased (2026-08-24) | cease & desist from X Corp. |
| XCancel | ceased (2026-08-25) | cease & desist from X Corp. |

## Verified fallback: twitter-cli (works, zero API cost)

`twitter-cli` (Python, binary `~/.local/bin/twitter`) reads tweets WITHOUT the
X API. Try it FIRST when the direct paths above fail, before the Google News
RSS chain below. Verified 2026-09-02 reading @arena's Gemini 3.8 benchmark
post end-to-end (user suggested "thử twitter-cli đi").

```bash
agent-reach doctor          # confirm "Twitter/X 推文 — twitter-cli ✅"
twitter -c tweet 2095179977805517149   # compact JSON: main tweet + replies
twitter tweet 2095179977805517149      # YAML output (parse with yaml.safe_load)
```

- Install if missing: `pip3 install twitter-cli` (per `agent-reach doctor`).
- Compact mode `-c` emits JSON but stderr carries a benign
  `WARNING twitter_cli.client: ...` line — redirect `2>/dev/null` before
  piping to `json.load`.
- Non-compact `twitter tweet` returns YAML (`data:` list); main tweet text is
  `data[0].text` (may be truncated in `-c` view — use non-compact for full).
- Read-only (browser-cookie auth); write ops still need xurl.

## Working fallback: Google News RSS + secondary sources

When all direct X paths fail, use this chain:

1. **Google News RSS search** (curl, no auth needed):
   ```bash
   curl -sL --max-time 40 -A "Mozilla/5.0" \
     "https://news.google.com/rss/search?q=AVICI+hack+Solana+when:3d" \
     -o /tmp/gn.xml
   ```
   Then parse with Python to find articles that quote the tweet verbatim.

2. **web_search** for the same query — outlets like The Defiant, KuCoin,
   BingX, or CoinDesk often embed the tweet text in their reporting.

3. **web_extract the quoting article** — these outlets are not blocked
   (they render server-side HTML). The Defiant, KuCoin, BingX, and
   Ambcrypto all returned readable text in the observed session.

4. **The tweet URL stays the primary source** in `sources:`. The quoting
   article is a secondary source that proves the tweet content was real.

## When even that fails

- If the event is big enough, Bloomberg / Reuters / TechCrunch will have
  a story that summarizes the X discussion. Use those.
- If the tweet is from a project's official account (e.g. @avici, @raincards,
  @useTria), the project's own press release may carry the same text.
- If nothing can be read, say so to Julius: "cả 4 tweet không đọc được nội
  dung qua các kênh thông thường" and skip the post.

## Do NOT

- Pretend you read the tweet when you only read Google News snippets. Label
  clearly: "theo mô tả từ nhiều nguồn" or "theo báo cáo của The Defiant/BingX".
- Fabricate tweet content. The quoting source's text is the ceiling of what
  you can assert.