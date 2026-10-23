# SKILL.md Patch Needed (background curator cannot apply)

The following additions to the Pitfalls section of `personal-blog-writer/SKILL.md`
are blocked by the read-before-write dedup guard. Apply in the next foreground session:

**Insert before the `working/Blog/` pitfall (last item):**

```markdown
- **CJK character leak in Vietnamese prose**: When generating Vietnamese text, the model occasionally mixes in Chinese characters (CJK U+4E00-9FFF) that look visually similar or are semantically related to the intended Vietnamese word. Common leak patterns: 掾控 for "tố cáo", 准备 for "chuẩn bị", 预期 for "dự kiến", 激励 for "incentive", 训练 for "huấn luyện", 密集 for "nặng", 限制 for "hạn chế", 提案 for "đề xuất". This happened across ALL 6 drafts in one session (2026-09-12). The content-validation script's CJK check (item #7) catches these, but the agent should also proactively self-check after writing. Prevention: after generating Vietnamese text, run the validation script before reporting "done." Full leak-pattern table in `references/cjk-and-build-pitfalls.md`.
- **Obsidian index files break Astro build**: Files like `blog-index.md` without proper YAML frontmatter cause `InvalidContentEntryDataError` in `src/content/writing/`. **Fix**: move to `src/content/` root. Do NOT add frontmatter. Observed 2026-09-12.
- **`git pull --rebase` fails on dirty tree**: `git stash → pull --rebase → push → stash pop`. Recurs every batch-push session. Observed 2026-09-10 and 2026-09-12.
```

**Also bump version** from 1.0.1 to 1.0.2.
