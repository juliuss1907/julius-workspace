# Coin68 Content Pipeline — Idea & Architecture

> **Status**: Planning / Pending Implementation  
> **Created**: 2026-05-22  
> **Author**: Markus (Hermes Agent) + Julius  
> **Goal**: Transform Coin68 writing from reactive (wait Julius assign) to proactive (auto-pick trending topics)

---

## 1. Overview

**Coin68 Pipeline** is a Google Sheets-based automated content calendar system that:

1. **Reads** a shared Google Sheet (Coin68-Content-Calendar) daily at 8:30 AM
2. **Prioritizes** projects based on funding alerts + social sentiment signals
3. **Auto-writes** draft articles for the highest priority pending project
4. **Updates** sheet status → "Drafted" + notifies Julius via Telegram
5. **Handles errors** gracefully (escalate to inbox, stop, notify)

---

## 2. Architecture — Skill Bundle

Tách Coin68 workflow thành micro-skills độc lập:

```
coin68-pipeline/
├── source-researcher/          # Phase: Data collection
│   ├── fetch-docs-urls         # web_extract from project docs
│   ├── fetch-funding-data      # crypto-fundraising.info + web search
│   ├── fetch-social-sentiment  # X/Twitter mentions via x-search
│   └── fetch-team-linkedin     # Social scraping (optional)
│
├── seo-optimizer/              # Phase: Pre-writing
│   ├── generate-keywords       # From project name + category
│   ├── analyze-competitors     # Compare same-category published articles
│   └── suggest-title-tags      # Optimize meta-description + tags
│
├── content-writer/             # Phase: Writing (current coin68-writer)
│   ├── draft-frontmatter       # YAML header
│   ├── draft-body              # Main content sections (H2/H3 structure)
│   └── draft-verification      # Kiểm chứng block
│
└── publisher/                  # Phase: Post-writing
    ├── update-sheet-status     # Auto-update Google Sheets row
    ├── generate-notion-summary # Optional: Notion integration
    └── notify-julius           # Telegram notification
```

**Benefits of modular design:**
- Each skill does ONE thing — easy to debug and update
- Reusable across other workflows (Substack, X, research)
- Can run source-researcher for multiple projects in parallel
- Julius can edit one skill without breaking others

---

## 3. Google Sheets Template

### Sheet Structure

**Sheet Name**: `Coin68-Content-Calendar`

| Column | Name | Type | Description |
|--------|------|------|-------------|
| A | **Project** | String | Tên dự án (e.g., "Variational", "Belo") |
| B | **Priority** | Dropdown | High → Medium → Low |
| C | **Status** | Dropdown | Pending → Drafted → Reviewing → Published |
| D | **Category** | Multi-select | perp-dex, stablecoin, infrastructure, defi, rwa, ai, layer-1, layer-2... |
| E | **Sources** | String (URLs) | Comma-separated list of doc/blog URLs |
| F | **Word Count** | Number | Auto-calculated from draft file |
| G | **Date Added** | Date | When Julius added the row |
| H | **Date Drafted** | Date | When Hermes wrote the draft |
| I | **SEO Keywords** | String | Comma-separated keywords (semi-auto) |
| J | **Social Sentiment** | String | Emoji + mention count (e.g., "🔥 234 mentions") |
| K | **Funding Alert** | String | Checkmark + amount (e.g., "✅ $50M Series A") |
| L | **Notes** | String | Draft file path, errors, other notes |

### Data Validation Rules
- **Priority**: Only `High`, `Medium`, `Low` allowed
- **Status**: Only `Pending`, `Drafted`, `Reviewing`, `Published` allowed
- **Category**: Free text but suggest from published.md index
- **Sources**: Must start with http:// or https://

---

## 4. Smart Priority Logic

### Decision Tree

```
START: Scan all rows with Status = "Pending"

├─> Has Funding Alert in last 7 days?
│   └─> YES → Priority = HIGH (override, regardless of current)
│
├─> Social Mentions > 100 (last 24h)?
│   ├─> Sentiment Positive (>60%) → Priority = HIGH
│   └─> Sentiment Neutral/Mixed → Priority = MEDIUM
│
├─> Category = "infrastructure" OR "blue-chips"?
│   └─> YES → Priority = MEDIUM (default baseline)
│
└─> Else → Priority = LOW

FINAL: If multiple HIGH priority rows:
    1. Pick most recent funding (newer first)
    2. Pick highest social mentions
    3. Alphabetical fallback
```

### Signal Sources

| Signal | Source | Tool | Update Frequency |
|--------|--------|------|------------------|
| **Funding rounds** | crypto-fundraising.info | web_extract | Daily (7 AM) |
| **Social mentions** | X/Twitter | x-search | Every 6 hours |
| **Price changes** | CoinGecko API | API | Real-time |
| **GitHub activity** | GitHub API | gh CLI | Daily |
| **TVL changes** | DeFiLlama API | API | Hourly |

---

## 5. Cron Job Logic (Pseudocode)

```python
# File: coin68-pipeline/scripts/daily-scheduler.py
# Schedule: 30 8 * * * (8:30 AM daily)

from hermes_tools import read_sheet, write_sheet, web_search, web_extract
from hindsight_client import Hindsight  # Memory layer

def daily_content_scheduler():
    # 1. READ sheet
    projects = read_sheet("Coin68-Content-Calendar")
    
    # 2. FETCH external signals
    funding_updates = check_crypto_fundraising()  # from crypto-fundraising.info
    social_trends = check_x_trending()             # from x-search
    
    # 3. UPDATE priority based on signals
    for project in projects:
        if project['Status'] == 'Pending':
            # Boost priority if new funding detected
            if project['Project'] in funding_updates:
                project['Priority'] = 'High'
                project['Funding Alert'] = f"✅ ${funding_updates[project['Project']]['amount']} {funding_updates[project['Project']]['round']}"
            
            # Boost priority if X mentions > 100 in last 24h
            mentions = x_search(
                query=f"{project['Project']} crypto",
                since="24h",
                limit=100
            )
            if len(mentions) > 100:
                project['Social Sentiment'] = f"🔥 {len(mentions)} mentions"
                if project['Priority'] != 'High':
                    project['Priority'] = 'Medium'
    
    # 4. WRITE updates back to sheet
    write_sheet("Coin68-Content-Calendar", projects)
    
    # 5. SELECT highest priority pending project
    high_priority = [
        p for p in projects 
        if p['Status'] == 'Pending' and p['Priority'] == 'High'
    ]
    
    if not high_priority:
        logger.info("No high-priority projects in queue. Stand by.")
        return
    
    # Pick by: latest funding > highest mentions > alphabetical
    project = sorted(high_priority, key=lambda p: (
        p.get('Funding Alert', '') != '',  # Has funding?
        len(p.get('Social Sentiment', '')),  # Mention count
        p['Project']  # Alphabetical
    ), reverse=True)[0]
    
    # 6. TRIGGER Hermes content writer
    try:
        result = delegate_task(
            goal=f"Write Coin68 review article about {project['Project']}",
            context=f"""
                Sources: {project['Sources']}
                Category: {project['Category']}
                SEO Keywords: {project.get('SEO Keywords', '')}
                Published index: working/Coin68/contents/published/published.md
            """,
            toolsets=['web', 'terminal', 'file']
        )
        
        if result.success:
            # 7. UPDATE sheet when done
            update_sheet_row(
                project['Row'],
                Status='Drafted',
                DateDrafted=datetime.now().strftime('%Y-%m-%d'),
                Notes=f"Draft: {result.file_path}"
            )
            
            # 8. NOTIFY Julius
            send_message(
                target='telegram',
                message=f"✅ Drafted: {project['Project']}\n📄 {result.file_path}\n📊 Words: {result.word_count}"
            )
    except Exception as e:
        # 9. ERROR HANDLING
        error_msg = f"❌ Coin68 Writer Failed\nProject: {project['Project']}\nError: {str(e)}"
        send_message(target='telegram', message=error_msg)
        
        # Write escalation to inbox
        write_file(
            path=f"tasks/inbox/coin68-error-{datetime.now().strftime('%Y%m%d-%H%M')}.md",
            content=f"""
---
type: escalation
category: coin68-writer
project: {project['Project']}
error: {str(e)}
suggested_action: Check sources validity and sheet format
created: {datetime.now().isoformat()}
---

## Debug Checklist
- [ ] Project has valid source URLs?
- [ ] Sources accessible via web_extract?
- [ ] Category exists in published.md index?
- [ ] SEO keywords are clear and specific?
- [ ] Sheet row formatting correct?

## Error Details
```
{str(e)}
```
"""
        )

# Run daily
if __name__ == '__main__':
    daily_content_scheduler()
```

---

## 6. Error Handling Strategy

### Three possible behaviors when cron job fails:

**Option A: Stop + Escalate (Recommended)**
- Stop execution immediately
- Send Telegram alert to Julius
- Write detailed escalation to `tasks/inbox/`
- Wait for Julius fix before retrying

**Option B: Skip + Continue**
- Log error to Notes column
- Move to next pending project
- Risk: multiple failures stack silently

**Option C: Retry + Escalate**
- Retry up to 3 times with 5-min delay
- If still fail → escalate
- Good for transient errors (API timeout)

**Current choice: Option A** — Julius can adjust.

---

## 7. Key Design Decisions

### Why Google Sheets instead of Notion/Airtable?
- ✅ Free tier generous (15GB Drive storage)
- ✅ Real-time collaboration (Julius edits, Hermes reads)
- ✅ Well-documented API with Python library
- ✅ Dropdown validation built-in
- ✅ Version history for rollback

### Why Memvid for memory layer?
- ✅ Single .mv2 file — no server needed
- ✅ Sub-5ms local retrieval
- ✅ Python SDK works with Hermes
- ✅ Smart Frames for append-only history
- ✅ Portable — can move between machines
- ✅ 30x compression for long-term storage

### Why separate source-researcher from content-writer?
- ✅ Source research is reusable for X threads, Substack, etc.
- ✅ Can run research for 5 projects in parallel (delegate_task batch)
- ✅ Content writer focuses purely on structure + Vietnamese text
- ✅ Easier to test each component independently

---

## 8. Status Workflow

```
[Pending] ──→ [Drafted] ──→ [Reviewing] ──→ [Published]
   ↑              │                │              │
   │              └── Auto by      └── Julius     └── Julius
   │                  Hermes           edits       moves file
   │                  (cron)                        to published/
   │
   └── Julius adds row to sheet
```

**Workflow steps:**
1. Julius adds project row → Status = "Pending"
2. Cron job (8:30 AM) picks highest priority "Pending" → writes draft
3. Status updated → "Drafted" (Notes column gets file path)
4. Julius reviews draft, edits → Status = "Reviewing"
5. Julius moves to `published/` → Status = "Published"

**Status never goes backwards** (except "Reviewing" → "Drafted" if major rewrite needed).

---

## 9. Implementation Plan (3 Days)

### Day 1: Foundation
- [ ] Create Google Sheet template with data validation
- [ ] Setup Google API auth (`gws auth login`)
- [ ] Build `source-researcher` skill:
  - `fetch_funding_data()` from crypto-fundraising.info
  - `fetch_social_mentions()` from x-search
  - `fetch_docs()` from web_extract
- [ ] Test read/write to sheet

### Day 2: Core Logic
- [ ] Write `scripts/daily-scheduler.py`
- [ ] Implement priority logic (Section 4)
- [ ] Implement error handling (Section 6)
- [ ] Test with 2-3 sample projects
- [ ] Add `seo-optimizer` basics (keyword generation)

### Day 3: Integration
- [ ] Connect with `content-writer` (coin68-writer skill)
- [ ] End-to-end test: Sheet → Draft → Notification
- [ ] Deploy cron job (8:30 AM daily)
- [ ] Write README.md documentation
- [ ] Test error handling edge cases

---

## 10. Future Enhancements (Phase 2+)

- [ ] **Batch mode**: Write 2-3 articles/day if queue >5 pending
- [ ] **Auto-category detection**: NLP from project description → suggest tag
- [ ] **Smart priority**: Price change >20% in 24h → auto-boost to HIGH
- [ ] **Multi-platform**: Same pipeline for Substack, X threads
- [ ] **Analytics dashboard**: Track words/month, avg time to publish, category distribution
- [ ] **A/B testing**: Auto-generate 2 alternative titles → Julius picks winner
- [ ] **Auto cross-links**: Suggest related Coin68 articles from published.md
- [ ] **Voice consistency checker**: Ensure all articles match Coin68 tone

---

## 11. Dependencies & Setup

### Required Tools
- `gws` CLI (Google Workspace) — for sheet read/write
- `x-search` (Hermes built-in) — for social sentiment
- `memvid-sdk` — for memory layer
- `crypto-fundraising.info` — web_extract target

### Auth Setup
```bash
# One-time setup
gws auth login              # Google API OAuth
hermes config set ...       # Ensure x-search configured
pip install memvid-sdk      # Memory layer
```

---

## 12. References

- **Coin68 Writer Skill**: `ai-labs/resource/skills/coin68-writer/SKILL.md`
- **Published Index**: `working/Coin68/contents/published/published.md`
- **Article Structure**: `skill_view(coin68-writer, file_path='references/article-structure.md')`
- **AGENTS.md Domain Rules**: `working/Coin68/AGENTS.md`
- **Memvid Docs**: https://github.com/memvid/memvid
- **Crypto Fundraising**: https://crypto-fundraising.info/

---

> **This document is a living design — update as we learn from implementation.**
