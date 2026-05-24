# Coin68 Content Calendar Pipeline

> Future direction (May 2026) — transforming Coin68 writing from reactive to proactive.
> Full plan: `ai-labs/pipelines/coin68-pipeline/idea.md`

---

## Vision

Replace manual Julius-assigned tasks with an automated Google Sheets-based pipeline that:
1. Julius adds project rows to a shared sheet
2. Cron job scans daily, auto-prioritizes based on funding + social signals
3. Hermes writes drafts for highest-priority pending project
4. Status auto-updates, Julius notified via Telegram

## Skill Bundle Architecture

```
source-researcher → seo-optimizer → content-writer → publisher
```

Each phase is a micro-skill — modular, reusable, independently testable.

## Google Sheets Columns

Julius specified these columns (May 2026):
- **Project Name** (tên dự án)
- **Priority** (High/Medium/Low)
- **Status** (Pending/Drafted/Reviewing/Published) — dropdown
- **Category** (multi-select dropdown: perp-dex, stablecoin, infrastructure, defi, rwa, etc.)
- **Sources** (URLs)
- Word Count, Date Drafted, SEO Keywords, Social Sentiment, Funding Alert, Notes

## Smart Priority Signals

| Signal | Source | Effect |
|--------|--------|--------|
| New funding (<7 days) | crypto-fundraising.info | Priority → HIGH (override) |
| X mentions >100 (24h) | x-search | Priority → HIGH if sentiment positive |
| Category = infrastructure/blue-chips | published.md | Priority → MEDIUM (default) |

## Implementation Status

- [ ] Day 1: Google Sheets template + source-researcher skill
- [ ] Day 2: Core cron job + priority logic  
- [ ] Day 3: Integration + testing + deploy

## Memory Layer

MemPalace (v3.3.5) installed at `~/.hermes/mempalace/` — hoàn toàn local, free, no API key.
Used for persistent memory across sessions; replaces Hermes built-in 2,200-char memory limit.
