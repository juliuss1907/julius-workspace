# Batch publish + backup workflow (learned 2026-09-28, refreshed 2026-09-29)

Applies when Julius asks for several news drafts in one turn ("viết cho tôi các
news sau và đăng draft lên blog") rather than one article at a time.

## Order of operations

1. Read every linked source FIRST, in one batch, before writing. Four stories
   means ~10 sources; a half-read batch produces a rewrite pass later.
2. List the requested slugs and check them against `origin/main` before writing
   anything. `git show origin/main:src/content/writing/<slug>.md` — if it errors,
   the slug is free.
3. Write ONE file per `write_file` call. Batch writes time out mid-stream.
4. Run `scripts/validate-content.py` on the whole set at once, fix, re-run.
5. One `npm run build` for the batch. Confirm all four are absent from
   `dist/articles/` when they are drafts.
6. `git add` the exact file list, then `git diff --cached --name-only` before
   committing. One commit for the batch is fine; do not `git add .`.
7. `git stash push --include-untracked` then `git pull --rebase origin main`,
   `git push origin main`, `git stash pop`. Remote advanced mid-batch
   (0ec910c..d44a9a4) during the observed run.
8. Backup with `scripts/backup-to-working-content.py` (see below), then verify
   each file landed on `origin/main` with `git show origin/main:<path> | grep`.
9. Report a table: title, slug, category, word count, plus anything the user
   should know about sourcing.

## Scripts (run by absolute path)

```bash
SKILL=~/julius-workspace/.agent/skills/personal-blog-writer
python3 $SKILL/scripts/validate-content.py --min-words 600 \
  src/content/writing/a.md src/content/writing/b.md
python3 $SKILL/scripts/backup-to-working-content.py a b c d
```

`--min-words` should match the depth the user asked for: 350 default, 600+ for
detailed news, 900 for a dense market piece. The validator exits 1 on any real
error so it can gate the commit.

## Conflicting numbers between outlets

A batch of market news will hand you two sources with different figures. Do not
silently pick one. Name the discrepancy, keep each outlet's own number, and say
in the report which one you followed. Observed 2026-09-29 on the Meta story:
Yahoo/gadgetreview reported a ~4% drop and USD 8.9bn lost on Friday 25/09;
Livemint reported a further USD 10.9bn on Monday 28/09. The article used the
two-session framing (over USD 19bn) because that reconciles both.

## Reuters is frequently antibot-blocked

`web_extract` on reuters.com returned `document_antibot` for both articles in
the 2026-09-29 batch. Reuters content is syndicated verbatim, so search the
headline and read a syndication partner instead:

- Yahoo Finance carries the full Reuters text under a Reuters byline:
  `finance.yahoo.com/technology/ai/articles/exclusive-...`
- Livemint and devdiscourse republish Reuters exclusives in full.

Put the syndication URL in `sources:`, not the reuters.com URL, and tell the
user which outlet you actually read. Do not cite a URL you could not open.
