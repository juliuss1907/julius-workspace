# Recovering the full news brief (cron → blog flow)

## When

Julius replies to a Hermes News Brief cron delivery asking to write specific
stories ("viết news 2, 7, 8 vào blog"). The quoted cron response only shows part
of the first story — stories beyond it are NOT visible in the chat. The requested
numbers map to stories that only exist in the full brief.

## Proven recovery (2026-08-29 — disk first)

1. **Disk (fastest, try this first):** the brief output IS persisted. List or
   glob `~/.hermes/cron/output/<job_id>/*.md` (e.g. `90bed8de1f06/2026-08-29_09-09-58.md`)
   and read the run file. The full brief sits under the `## Response` marker —
   everything above it is the embedded news-brief-agent skill prompt and the
   job's run metadata, which you can skip. This avoids session_search entirely.
2. **Fallback — session_search:** search the cron session by a unique story
   phrase (e.g. "Schwab Solana Avalanche Chainlink", sort newest). The session id
   has the shape `cron_<jobid>_<yyyymmdd>_<hhmmss>`. Windowed reads
   (`session_search(session_id=..., around_message_id=<anchor>, window=10)`)
   return the full brief plus intermediate web_extract tool results.

## Notes

- Do NOT start writing from the quoted story #1 alone — the user's requested
  numbers (2,7,8) map to stories that only exist in the full brief.
- Do NOT ask Julius to re-paste the brief; the cron output dir / session DB is
  the source.
- Verify the requested numbers against the recovered story list BEFORE writing
  (see personal-blog-writer "Batch publish" pitfall).