# CJK & Build Pitfalls (personal-blog-writer)

Session-observed failures from 2026-09-12. Add to SKILL.md Pitfalls section when next
foreground edit is possible.

## 1. CJK character leak in Vietnamese prose

When generating Vietnamese text, the model occasionally mixes in Chinese characters
(CJK U+4E00-9FFF) that look visually similar or are semantically related to the
intended Vietnamese word.

**Common leak patterns observed:**

| Chinese (leaked) | Vietnamese (intended) |
|---|---|
| 掾控 | tố cáo |
| 准备 | chuẩn bị |
| 预期 | dự kiến |
| 激励 | incentive |
| 训练 | huấn luyện |
| 密集 | nặng |
| 限制 | hạn chế |
| 提案 | đề xuất |
| 他们是 | họ là |
| 至今 | vẫn chưa |
| 批评 | phê bình |
| 这意味着 | điều này có nghĩa là |

**Incident**: ALL 6 drafts in a single session contained CJK characters. The
content-validation script's CJK check (item #7) caught them all, but only after
writing was complete.

**Prevention**: After generating Vietnamese text, ALWAYS run the validation script
before reporting "done." If writing without `execute_code`, mentally scan for
characters that look "too complex" compared to surrounding Vietnamese text.

## 2. Obsidian index files break Astro build

Files like `blog-index.md` or other Obsidian-generated indexes without proper YAML
frontmatter will cause `InvalidContentEntryDataError` if they land in
`src/content/writing/`.

**Symptom**: `npm run build` fails with:
```
[InvalidContentEntryDataError] writing → blog-index data does not match collection schema.
  title**: **title: Required
  description**: **description: Required
```

These files are usually gitignored but can exist locally (Obsidian auto-generates them).

**Fix**: Move the file out of `src/content/writing/` (e.g. to `src/content/` root).
Do NOT add frontmatter to it — it is not an article.

## 3. `git pull --rebase` fails on dirty tree

The personal-blog repo often has local untracked/modified files (Obsidian configs,
stale WIP, `.gitignore` changes). `git pull --rebase origin main` refuses to run
with unstaged changes:

```
lỗi: không thể pull với rebase: Bạn có các thay đổi chưa được đưa vào vùng chờ.
```

**Fix** (recurring pattern):
```bash
git stash
git pull --rebase origin main
git push origin main
git stash pop
```

Observed on 2026-09-10 and 2026-09-12. Happens every batch-push session because
the blog repo accumulates local-only changes (Obsidian, blog-index.md, etc.).
