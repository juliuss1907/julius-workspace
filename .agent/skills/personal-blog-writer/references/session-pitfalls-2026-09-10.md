# Pitfalls from 2026-09-10 session

## Push workflow: dirty tree blocks rebase

**Symptom:** `git pull --rebase` fails with "Bạn có các thay đổi chưa được đưa vào vùng chờ" when Julius has UI WIP files in the working tree.

**Fix (tested 3+ times):**
```
git stash --include-untracked
git pull --rebase origin main
git push origin main
git stash pop
```

**Do NOT** use `git stash push -- <specific-paths>` — it misses some files. Use `--include-untracked` without path args.

**Verify push succeeded:** Check for `main -> main` or `To github.com:...` in output. A local commit hash alone does NOT prove push success. If rebase failed, push also failed.

## Push failure misread trap

Terminal prints both error messages AND a local commit hash in the same output. Example:
```
lỗi: không thể pull với rebase: Bạn có các thay đổi chưa được đưa vào vùng chờ.
lỗi: Xin hãy chuyển giao hoặc tạm cất chúng.
gợi ý: máy chủ, hãy chạy 'git pull' trước khi đẩy lên.
gợi ý: Xem 'Note about fast-forwards' trong 'git push --help' để biết thông tin chi tiết.
463575d content: deepseek-v4-1-flash news
```

The `463575d` line is `git log --oneline -1` output (local commit), NOT proof of push success. The hints above it are push FAILURE messages. Don't report success until you see `main -> main`.

## Content accuracy: verify user framing

User said "CoinEx phá sản" but the actual event was voluntary shutdown (reserve ratio >100%, orderly wind-down). Always verify the user's framing against primary sources before writing. Don't assume the user's characterization is accurate.

## Validation false positives: domain names

The content validation script's "missing space" regex triggers on domain names like `x.com` and `Bitcoin.com` (the period in the domain matches the punctuation-followed-by-letter pattern). These are false positives — the agent should judge them manually.

## Validation false positives: NFC normalization

Vietnamese text with combining diacritical marks (NFD normalization) causes the English density check to massively overcount. The script must normalize to NFC first: `content = unicodedata.normalize('NFC', content)`.

## Validation false positives: HTML embed lines

Lines starting with `<` (blockquote, iframe, etc.) should be skipped by all checks. The `is_html()` helper: `line.lstrip().startswith('<')`.

## Validation false positives: Oxford comma threshold

The Oxford comma check (`,\s*(và|and)\s`) triggers on many normal Vietnamese sentences. Only warn when count > 2, not on every occurrence.

## blog-index.md: reference before writing

A cron job (daily 09:15 ICT) generates `ai-labs/projects/personal-blog/src/content/writing/blog-index.md` with metadata + excerpts of all blog articles. Before writing a new article, read this index to see what's been published and maintain style consistency. The file is in `.gitignore` (not committed to GitHub).

## Learn from published articles workflow

When Julius provides edgenotes.net URLs of published articles, the workflow is:
1. Read the published version (edgenotes.net)
2. Compare with the draft version (if exists)
3. Identify style differences (prose flow, bold usage, section headers, "so what" integration)
4. Update the style guide reference (`references/blog-style-guide.md`) with new rules
5. Apply to future articles

## News.md index: always re-read before patching

The `working/Blog/Content/news/news.md` index gets updated by the news-brief-agent cron job. Always re-read the current state before patching — the top entry may have changed since the last read.
