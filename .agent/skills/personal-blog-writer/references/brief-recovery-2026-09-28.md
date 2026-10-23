# Content-collection output dirs and brief recovery (2026-09-28)

## What happened

A cron-delivered news brief needed recovering because the user's chat copy only
showed story #1, while they asked for stories "2, 3". The
`personal-blog-writer` `references/brief-recovery.md` documented a "disk first,
fastest path": glob `~/.hermes/cron/output/<job_id>/*.md` and read the run file
under its `## Response` marker.

**The directory existed and was completely empty.** No run files at all. The
"fastest path" cost a wasted round-trip before falling through to
`session_search`.

## Rule

Do not treat the cron output directory as reliable. It is a cheap probe, not a
guaranteed cache. One `ls` is fine; if it comes back empty, move on immediately
rather than trying alternate glob shapes or job-id subdirectories.

## Working recovery

`session_search` with a phrase that appears in the brief itself. Verified
working query on 2026-09-28:

```
session_search(query='"Tại sao đáng chú ý" News Brief', sort='newest', limit=5)
```

Anchor selection matters. The generic phrase `"Tại sao đáng chú ý"` ALSO matches
the `news-brief-agent` skill prompt that is embedded as the user message of every
cron run, so all 5 hits contained it. Pick the hit whose `messages[]` include an
assistant message whose content starts with `# News Brief - DD/MM/YYYY` — that
is the real brief.

Session id shapes are not guaranteed. The working hit was a plain
`20260925_095754_a280cd` with `source: cron` and a `parent_session_id` of
`cron_90bed8de1f06_20260925_090016`; the brief for a later day may surface under
a child id. Both carry the full text, so do not filter on the `cron_` prefix.

## Checklist before mapping numbers to stories

- Confirm the recovered brief is today's (check the date in its H1 against
  `date +%Y-%m-%d`).
- List the numbered stories and their headlines before writing anything.
- Verify the user's requested numbers exist in that list. If a requested number
  is out of range, say so instead of silently renumbering.
