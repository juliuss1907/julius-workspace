# Frontmatter & Backup Pitfalls (personal-blog-writer)

Two real failures from session 2026-08-31 — both cost a build round-trip or a user
correction. Read before publishing a batch.

## 1. Single-quoted YAML title breaks on apostrophes

- **Symptom**: `title: '...We're Back...'` — a `'` inside single-quoted YAML
  throws a js-yaml parse error and fails `npm run build`.
- **When it surfaces**: ONLY at build time, never at write time. The frontmatter
  validator in `src/content.config.ts` / Astro content layer chokes on the
  unterminated quote, so the bug is silent until you run `npm run build`.
- **Actual case**: Saylor title "Michael Saylor đăng "We're Back" — Strategy
  sắp quay lại mua Bitcoin..." was written single-quoted → build failed.
- **Fixes**, in order of preference:
  1. Reword the title to avoid the apostrophe entirely.
  2. Use double-quoted YAML for that one field, escaping inner `"` as `\"`:
     `title: "Michael Saylor đăng \"We're Back\" — ..."` — apostrophes are fine
     inside double quotes.
  3. Double the apostrophe `''` inside single quotes (YAML escape).
- **Rule of thumb**: the "use single quotes so inner double quotes need no
  escaping" guidance holds ONLY when the title contains no `'`. Scan titles for
  apostrophes (can't, don't, We're, "I'm") before choosing the quoting style.
- **Always** run `npm run build` after writing/editing a batch of posts — it is
  the only gate that catches YAML frontmatter errors.

## 2. Backup `Meta:` line is a content summary, never workflow status

- **Actual case**: a backup copy in `working/Blog/Content/` had its Meta line
  written as "Bài đang ở trạng thái draft trên blog, hẹn tự động publish lúc
  16:00 hôm nay." Julius rejected it ("Tại sao lại có dòng...").
- **Why it's wrong**: the Meta line (and the Astro `description:` it mirrors)
  is reader-facing — it summarizes what the post is ABOUT. Scheduling/draft
  state belongs in frontmatter (`draft:`, `scheduledAt`) and the publishing
  worker, never in the article text.
- **Correct**: `Meta:` = one-line summary of the post content, kept in sync with
  the Astro `description:`. Example: "Aave mở Early Access cho người dùng iOS
  với ứng dụng tiết kiệm stablecoin, trong khi Android và web vẫn chờ."
