# Batch-publish CMS draft conflict — which slug is stuck? (observed 2026-09-01)

Companion to `cms-github-draft-conflict.md` for the MID-BATCH case.

## When this applies

Julius pushes SEVERAL posts to `main` in one session (scheduled news batch),
then reports the CMS error "Main đã thay đổi nhưng draft đang có trạng thái
GitHub chờ xử lý" (or a stale-draft reload refusal). The error is per-slug,
but with N posts in flight it is NOT obvious which one Julius has open.
Observed: I assumed the wrong slug (Sony), Julius corrected with "Ý tôi là
bitmine-eth-treasury-131m á" — a wasted round-trip.

## Rules that emerged

1. **Confirm the slug first.** Ask Julius which post the CMS is on, or have him
   paste the URL, before touching any draft or branch. Do not guess from which
   `cms/*` branches exist (all prior posts leave dangling branches).
2. **Inspect before deleting** — a CMS draft can carry user-added content:
   ```bash
   git fetch origin 'refs/heads/cms/*:refs/remotes/origin/cms/*'
   git diff origin/main...origin/cms/<slug> -- src/content/writing/<slug>.md
   git ls-tree -r --name-only origin/cms/<slug> | grep public/images
   ```
   Common additions: a thumbnail webp under `public/images/articles/<slug>/`,
   an internal link to a prior post. Preserve them if the user wants them.
3. **CMS branches can CLOBBER scheduling.** Observed: the CMS branch rewrote
   `scheduledAt` to a wrong earlier value (04:00Z instead of the intended
   12:00Z) while keeping `draft: true`. If you merge a CMS branch back into
   `main`, re-verify `scheduledAt`/`publishedAt` against the planned schedule
   (batch = +2h apart, first post ≈ now +30min).
4. **Fastest fix for a localStorage-only draft** (no `cms/<slug>` branch in
   `git ls-remote origin 'refs/heads/cms/*'`): browser-console one-liner
   (see cms-github-draft-conflict.md Fix 2). It does NOT remove a dangling
   `cms/<slug>` branch if one exists — that's harmless junk.
5. **Prefer git flow over CMS saves** for scheduled batches: CMS saves create
   orphan `cms/*` branches + localStorage drafts that fight agent pushes to
   `main`. Push straight to `main` with `draft:true`/`scheduledAt`.
