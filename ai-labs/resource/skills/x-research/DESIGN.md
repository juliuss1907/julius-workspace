# X-Research — Design Document

> Skill: Deep research combining X/Twitter + Web sources  
> Output: Analytical report (single .md, Vietnamese)  
> Synthesis: Hermes Agent (Markus)  
> Author: Julius  
> Date: 2026-05-21

---

## 1. Overview

`x-research` là skill thực hiện deep research kết hợp 2 nguồn:
- **X/Twitter**: Search tweets theo keyword qua `twitter` CLI
- **Web**: Crawl sources qua Firecrawl localhost

Output: Báo cáo phân tích chi tiết bằng **tiếng Việt** — chỉ **1 file .md duy nhất**, không thư mục con, không raw data.

Synthesis được thực hiện bởi **Hermes Agent** (Markus), không qua LLM API.

---

## 2. Architecture (4 Stages)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STAGE 1: X Research                          │
│  twitter search <topic> -n <limit> --json → 20-50 tweets            │
│  Extract: text, author, engagement metrics                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       STAGE 2: Web Research                        │
│  Firecrawl localhost:3002 /v1/search → tìm URLs liên quan            │
│  /v1/scrape → crawl full page markdown                               │
│  Target: 5-10 sources                                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STAGE 3: Agent Synthesis                         │
│  Markus đọc HERMES_SYNTHESIS_PROMPT.md (tweets + web context)        │
│  Viết synthesis.json với structure:                                  │
│    - executive_summary, market_landscape, deep_analysis              │
│    - key_metrics, emerging_trends, contrarian_views                  │
│    - information_gaps, alpha_signals                                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STAGE 4: Report Generation                       │
│  Jinja2 template (tiếng Việt) → Markdown report                      │
│  Single file: <topic-slug>-<date>.md                                 │
│  Cleanup temp files                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Directory Structure

```
ai-labs/projects/x-research/
├── DESIGN.md                 ← This file
├── SKILL.md                  ← Skill definition for Hermes
├── README.md                 ← Quick start guide
├── config.yaml               ← Research params + output settings
├── requirements.txt          ← Python deps
├── Makefile                  ← Build automation
├── .gitignore
├── scripts/
│   ├── main.py              ← Orchestrator: 4 stages, agent delegation
│   ├── x_research.py        ← Stage 1: twitter CLI search + parse
│   ├── web_research.py      ← Stage 2: Firecrawl search + scrape
│   ├── synthesis.py         ← Stage 3: placeholder (agent-driven)
│   └── report.py            ← Stage 4: Jinja2 render → single .md
├── templates/
│   └── report.j2            ← Vietnamese Markdown template
└── lib/
    ├── llm_client.py        ← Placeholder (no API calls)
    └── utils.py             ← Logging, slugify, Telegram brief
```

---

## 4. Stage Detail

### Stage 1 — X Research (`x_research.py`)

**Input:** Topic string

**Process:**
```bash
twitter search "<topic>" -n 50 --json
```

**Extract fields:**
```python
{
  "id": "...",
  "author": "@handle",
  "text": "...",
  "created_at": "...",
  "likes": 123,
  "retweets": 45,
  "views": 5000
}
```

**Output:** `tweets.json` (temp dir, auto-cleanup)

---

### Stage 2 — Web Research (`web_research.py`)

**Input:** Topic string

**Process:**
1. **Search** via Firecrawl:
   ```bash
   curl -X POST http://localhost:3002/v1/search \
     -d '{"query":"<topic>","limit":10}'
   ```

2. **Scrape** từng URL:
   ```bash
   curl -X POST http://localhost:3002/v1/scrape \
     -d '{"url":"<url>","formats":["markdown"]}'
   ```

**Target:** 5-10 unique sources (filter duplicate domains)

**Extract fields:**
```python
{
  "url": "...",
  "title": "...",
  "markdown": "..."
}
```

**Output:** `web_sources.json` (temp dir, auto-cleanup)

---

### Stage 3 — Agent Synthesis (`synthesis.py`)

**Không còn 2-pass LLM.** Thay vào đó:

1. `main.py` tạo `HERMES_SYNTHESIS_PROMPT.md` chứa:
   - JSON schema yêu cầu
   - 15 tweets đầu tiên (context)
   - 5 web sources đầu tiên (context)
   - Hướng dẫn viết tiếng Việt, 2500-3500 từ

2. **Markus (Hermes Agent)** đọc prompt → viết `synthesis.json`

3. `main.py --skip-to-stage 4` đọc `synthesis.json` → generate report

**Output:** `synthesis.json` (temp dir, auto-cleanup)

---

### Stage 4 — Report Generation (`report.py`)

**Template:** Jinja2 (`templates/report.j2`) — tiếng Việt

**Report sections:**
```markdown
# [TOPIC] — Báo cáo Nghiên cứu

**Ngày:** DD MMMM YYYY  
**Nguồn:** N tweet, M bài viết  
**Mô hình:** Markus (Hermes Agent)

---

## Tóm tắt
## Chỉ số chính
## Bức tranh Thị trường
## Phân tích Sâu (6 sub-sections)
## Xu hướng Nổi bật
## Quan điểm Trái chiều
## Khoảng trống Thông tin
## Tín hiệu Alpha
```

**Output location:**
```
/home/julius/julius-workspace/working/X/report/research/
└── <topic-slug>-<DD-MM-YYYY>.md   ← Single file only
```

---

## 5. Config Schema (`config.yaml`)

```yaml
---
# X-Research Configuration

# Research parameters
research:
  topic: ""                    # Injected at runtime
  lookback_hours: 48           # Tweet time filter
  tweet_limit: 50              # Max tweets from X search
  web_sources: 10              # Max web sources to crawl
  min_relevance_score: 0.5

# X/Twitter
x_twitter:
  search_tool: "twitter"
  timeout: 30

# Firecrawl
firecrawl:
  base_url: "http://localhost:3002"
  timeout: 60
  retries: 3

# Model (agent-driven, no API)
models:
  synthesis:
    agent: "hermes"
    language: "vi"

# Output
output:
  report_dir: "/home/julius/julius-workspace/working/X/report/research"
  filename_pattern: "{topic_slug}-{date}.md"
  date_format: "%d-%m-%Y"

# Telegram (optional)
telegram:
  enabled: true
  bot_token_env: "TELEGRAM_BOT_TOKEN"
  chat_id_env: "TELEGRAM_CHAT_ID"
```

---

## 6. Key Decisions

| Decision | Rationale |
|----------|-----------|
| No KOL list, search by keyword | Research cần breadth, không giới hạn bởi danh sách |
| `twitter` CLI thay vì `xurl` | xurl free tier = read-only (401). `twitter` CLI hoạt động ổn định |
| Firecrawl localhost | Free, no rate limit, Julius đã setup sẵn |
| Agent synthesis (Markus) | Không cần API key, chất lượng cao, luôn available |
| Flat output (single .md) | Dễ quản lý, dễ share, không clutter |
| No raw data in report | Tweets/web chỉ làm context — report là insight tổng hợp |
| Vietnamese language | Phù hợp audience chính, crypto-native terminology |
| No standalone mode | Simplify codebase, eliminate API key management |

---

## 7. Pitfalls & Mitigations

| Pitfall | Mitigation |
|---------|------------|
| X search trả về ít/none | Fallback: thử keyword variations |
| Firecrawl localhost down | Fallback: `web_search` + `web_extract` |
| Agent chưa viết synthesis.json | Resume với `--skip-to-stage 4` sau khi agent hoàn thành |
| Report generic/bland | Prompt yêu cầu 2500+ từ, citation inline, specific names |
| Duplicate web sources | Filter by domain trước khi scrape |
| Temp dir bị xóa trước khi resume | Dùng `XRESEARCH_TEMP_DIR` env để preserve |

---

## 8. Usage

```bash
cd ai-labs/projects/x-research

# Step 1: Collect data (exits with prompt)
python scripts/main.py --topic "Ethereum L2 2026"

# Step 2: Agent (Markus) viết synthesis.json vào temp dir

# Step 3: Generate report
XRESEARCH_TEMP_DIR=/tmp/x-research-xxx \
python scripts/main.py --topic "Ethereum L2 2026" --skip-to-stage 4
```

Or via Hermes:
```
@Markus Run x-research on "Ethereum L2 2026"
```

---

**Status:** Implemented & tested. Ready for production use.
