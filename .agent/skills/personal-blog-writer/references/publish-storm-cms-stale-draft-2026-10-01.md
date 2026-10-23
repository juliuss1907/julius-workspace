# Publish storm: "Draft trên GitHub đã thay đổi" after repeated publishes

Observed 2026-10-01 on `gemini-4-argon-ra-mat`. Completes the CMS-conflict
family: `cms-github-draft-conflict.md` explains the message, this file covers
the *repeated publish* trigger and the non-destructive repair.

## Root cause is a publish storm, not corruption

The commit log showed the article had been published **three times in 8
minutes** (11:06, 11:10, 11:14) before Julius hit the error, then added to
`src/content/disabled-articles.json` at 11:24. His editor tab was still
holding the version from before the first publish.

Read this BEFORE assuming anything is broken:

```bash
git fetch --all --prune -q
git log --oneline --format="%h %ad %s" --date=format:"%d/%m %H:%M" \
  origin/main -- src/content/writing/<slug>.md | head -12
```

Repeated `content: publish <slug>` commits minutes apart = the tab was stale.
Report that finding; it explains the error without needing a fix on the file.

## Diff BOTH sides before touching anything

The `cms/<slug>` branch often holds **real edits Julius made in the CMS that
never reached main**. Deleting the branch, or rewriting the post from your own
version, throws those away silently. The existing fix #1 in
`cms-github-draft-conflict.md` ("delete branch + rewrite the post") is LOSSY
for exactly this reason — use it only after proving the branch holds nothing.

```bash
git show origin/main:src/content/writing/<slug>.md | grep -E "^(title|draft|publishedAt):"
git show origin/cms/<slug>:src/content/writing/<slug>.md | grep -E "^(title|draft|publishedAt):"
diff <(git show origin/cms/<slug>:src/content/writing/<slug>.md) \
     <(git show origin/main:src/content/writing/<slug>.md)
```

## Ask per-difference, not per-side

2026-10-01: both sides held something worth keeping. Julius wanted the CMS
branch's body edit (a removed duplicate benchmark bullet) but main's
`draft: false` and his own retitled version. "Keep main" or "keep branch"
would each have destroyed something. Use `clarify` with the concrete options,
naming the actual text.

Apply only the agreed body change, keeping main's frontmatter state:

```bash
git checkout origin/main -- src/content/writing/<slug>.md   # main as base
# patch ONLY the body difference; never touch draft:/scheduledAt: here
```

Do NOT `git checkout origin/cms/<slug> -- <path>` wholesale: the branch's
`draft: true` would silently un-publish a live article.

## `disabled-articles.json` is shared state — check it before deleting

The branch also carried `src/content/disabled-articles.json`, and the branch
copy was **older** than main (`[]` vs `["gemini-4-argon-ra-mat"]`). Only the
CMS writes this file, so a stale branch can revert it and resurrect articles
Julius hid. Check it in the same diff pass, and never restore it from a branch.

If the article is in that list, it is deliberately hidden from the blog. Say
so plainly and confirm before removing it — do not "helpfully" un-disable it.

## Delete the branch last, after main is correct

```bash
git push origin --delete refs/heads/cms/<slug>   # destructive, confirm first
git fetch --prune -q origin
git branch -r | grep -c "cms/<slug>"    # expect 0
```

Order matters: sync content to main, verify build, THEN delete. Deleting first
removes the only record of the CMS-only edits.

## The browser step is still required

Branch deletion does not clear Julius's localStorage draft. He must still run
the console filter from `cms-github-draft-conflict.md` fix 2, or F5 will keep
showing the stale-draft refusal. Hand him the snippet and say it plainly —
otherwise the error looks unfixed.

## Repo-wide backlog

`git branch -r | grep -c 'cms/'` returned 180+ stale branches. They are the
fuel for this whole error class. Offer to audit them and present only the
branches that provably hold nothing exclusive to main; deletion stays his call.