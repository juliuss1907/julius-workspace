# Hermes YAML Frontmatter: Real Fix Example

Session: 2026-05-23
Context: Julius created `news-brief-skill` in `ai-labs/resource/skills/news-brief-skill/SKILL.md`. The skill would not load via `skill_view()` and had a malformed frontmatter. The fix was derived by reading `sentinel-scanner/SKILL.md` (a working user-local skill) as a reference template.

## The Problem (Before)

```yaml
---
name: news-brief-skill
aliases: ["news-brief", "brief", "tin tức", "news-aggregator"]
agent: Hermes (local)
description: Multi-topic automated news aggregator with keyword-first prioritization. Scrapes Telegram channels, websites, and RSS feeds. Delivers briefs in Vietnamese to Telegram and Markdown files. Supports unlimited topics (Crypto, Tech, AI Safety, etc.) with per-topic sources, keywords, and selection criteria.
version: 2.0
last_updated: 2026-05-23
---
```

Issues:
1. `aliases`, `agent`, `version`, `last_updated` at root level — flat structure
2. `description` is at root (correct) but the overall shape is wrong for user-local skills
3. No `metadata:` block
4. `last_updated:` is not a recognized key (should be `created:` inside metadata)

## The Fix (After)

```yaml
---
name: news-brief-skill
description: >
  Multi-topic automated news aggregator with keyword-first prioritization.
  Scrapes Telegram channels, websites, and RSS feeds.
  Delivers briefs in Vietnamese to Telegram and Markdown files.
  Supports unlimited topics (Crypto, Tech, AI Safety, etc.) with per-topic
  sources, keywords, and selection criteria.
metadata:
  version: "2.0"
  author: "Julius"
  created: "2026-05-23"
  aliases: ["news-brief", "brief", "tin tức", "news-aggregator"]
  trigger: "Cron 3x daily (7:00, 13:00, 21:00 ICT)"
  output: "Telegram message + Markdown file"
---
```

What changed:
- `description:` stays at root (this is REQUIRED)
- Everything else moves into `metadata:` block
- `version`, `author`, `created`, `aliases`, `trigger`, `output` are all inside `metadata:`
- No `agent:` field (not used in user-local format)
- No `last_updated:` (replaced by `created:`)

## User-Local vs In-Repo Quick Reference

| Field | User-Local (`~/.hermes/skills/`) | In-Repo (`skills/<cat>/<name>/`) |
|-------|-----------------------------------|----------------------------------|
| `name` | root | root |
| `description` | root | root |
| `version` | inside `metadata:` | root |
| `author` | inside `metadata:` | root |
| `license` | not used | root |
| `aliases` | inside `metadata:` | not used |
| `trigger` | inside `metadata:` | not used |
| `output` | inside `metadata:` | not used |
| `created` | inside `metadata:` | not used |
| `metadata.hermes.tags` | not used | inside `metadata.hermes:` |
| `metadata.hermes.related_skills` | not used | inside `metadata.hermes:` |

## Key Rule

> **Never mix the two shapes.** If you are authoring a user-local skill (one that lives in `~/.hermes/skills/` or a custom path indexed by Hermes), use the user-local shape with `metadata:` block. If you are committing a skill to the hermes-agent repo, use the in-repo peer-matched shape.
