# SKILL — Coin68 Contents

**Agent:** Hermes (local)
**Purpose:** Skill bundle for Coin68 content production pipeline
**Version:** 1.0
**Last updated:** 2026-05-26

---

## Overview

Parent skill bundle cho toàn bộ quy trình sản xuất nội dung Coin68.

## Sub-Skills

| Skill | Purpose | Status |
|---|---|---|
| `source-researcher/` | Gap-driven source collection & verification | Active |
| `seo-optimizer/` | Pre-writing SEO/GEO brief generation | Active |
| `content-writer/` | Write Vietnamese crypto articles | Active |
| `seo-audit/` | Post-writing SEO quality audit | Active |

## Skill Loading Order

Trong pipeline viết bài, các skills được load theo thứ tự:

1. **source-researcher/** — Collect & verify sources, produce Research Dossier
2. **seo-optimizer/** — Generate SEO brief (can read Dossier for keyword extraction)
3. **content-writer/** — Write article draft using Dossier + SEO brief
4. **seo-audit/** — Audit draft for SEO quality before presenting to Julius

## Future Sub-Skills (TBD)

Các skill sau đang được cân nhắc nhưng chưa quyết định:
- Publisher — Sheet update, notification, delivery

## Related

- Pipeline: `ai-labs/pipelines/coin68-pipeline/`
- Workspace: `working/Coin68/`
- Legacy skill (deprecated): `ai-labs/resource/skills/coin68-writer/`

---

**Maintainer:** Julius
**Last updated:** 2026-05-26
