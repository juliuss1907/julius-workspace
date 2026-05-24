---
name: deep-research
skill_id: deep-research
category: research
description: >
  Architecture and integration patterns for multi-stage research pipelines that combine
  X/Twitter data, web sources, and LLM synthesis into analytical reports.
  Supports both self-driven (agent-based) synthesis and external-API synthesis modes.
---

# Deep Research Pipeline

## When to Use

Building a research skill that:
- Fetches data from multiple sources (X/Twitter + web)
- Performs multi-pass LLM synthesis
- Generates structured reports with citations
- Runs either standalone or via Hermes agent

## Architecture Pattern

```
Stage 1: X Research      → twitter search / xurl search → tweets.json
Stage 2: Web Research    → Firecrawl / web_search → web_sources.json
Stage 3: Deep Synthesis  → 2-pass: summarize → analyze → synthesis.json
Stage 4: Report Gen      → Jinja2 template → Markdown + Telegram brief
```

## Agent-Driven Synthesis (Only Mode)

The synthesis stage **must trigger the Hermes agent directly**. External LLM APIs are not used — Julius explicitly rejected standalone mode.

**Why:**
- No API key dependencies or credential management
- Agent provides consistent voice and iterative refinement
- No "prompt user for API key" flow needed

**How (2-step delegation):**
1. Pipeline runs Stages 1-2 (data collection)
2. Script saves formatted prompt to `HERMES_SYNTHESIS_PROMPT.md` in temp dir
3. Script exits with code 42 and prints resume instructions
4. **Agent** reads prompt → writes `synthesis.json` to same temp dir
5. Re-run with `--skip-to-stage 4` → pipeline loads synthesis.json → generates report

**Implementation:**
```python
# main.py — agent-only flow (no --hermes-mode flag needed)
temp_dir = Path(tempfile.mkdtemp(prefix="x-research-"))
os.environ["XRESEARCH_TEMP_DIR"] = str(temp_dir)

# After Stages 1-2:
if not synthesis_path.exists():
    prompt = build_hermes_prompt(topic, tweets_data, web_data)
    with open(temp_dir / "HERMES_SYNTHESIS_PROMPT.md", 'w') as f:
        f.write(prompt)
    return 42  # signal: synthesis required

# Resume (agent wrote synthesis.json):
XRESEARCH_TEMP_DIR=/tmp/x-research-xxx \
python main.py --topic "..." --skip-to-stage 4
```

**Important:** The synthesis prompt should instruct the agent to write in **Vietnamese** (Julius's preference). See Language section below.

## Language: Vietnamese Output

Julius prefers **all report content in Vietnamese**. The synthesis prompt should instruct the agent to write in Vietnamese, using crypto-industry terminology where appropriate (English borrow terms like "perp DEX", "TVL", "funding" are acceptable inline).

**Template sections should use Vietnamese headings:**
```
Tóm tắt (not Executive Summary)
Chỉ số chính (not Key Metrics)
Bức tranh Thị trường (not Market Landscape)
Phân tích Sâu (not Deep Analysis)
Xu hướng Nổi bật (not Emerging Trends)
Quan điểm Trái chiều (not Contrarian Views)
Khoảng trống Thông tin (not Information Gaps)
Tín hiệu Alpha (not Alpha Signals)
```

**Synthesis prompt should include:**
```
- NGÔN NGỮ: Tiếng Việt chuyên ngành crypto, có thể dùng từ borrow từ tiếng Anh khi cần
```

## Key Integrations

### twitter CLI (Search-capable)

```bash
twitter search "QUERY" -n 20 --json
```

**Output format:**
```json
{
  "ok": true,
  "data": [
    {
      "id": "...",
      "text": "...",
      "author": {"screenName": "@user", "name": "Display Name"},
      "metrics": {"likes": 10, "retweets": 5, "replies": 2, "views": 1000},
      "createdAtISO": "2026-05-21T..."
    }
  ]
}
```

**Parse fields:**
- `author.screenName` (not `username`)
- `metrics.likes` / `retweets` / `replies` / `views` (not `public_metrics`)
- `createdAtISO` (not `created_at`)

### xurl CLI (Read-only on Free tier)

```bash
xurl search "QUERY" --max-results 20
```

**Quirks:**
- Free tier = read-only (search returns 401 Unauthorized, post returns "CreditsDepleted")
- Flag is `--max-results` not `--limit`
- Need Basic tier ($100/mo) for write/search credits
- Use `twitter` CLI as primary search tool instead

### Firecrawl Localhost

```bash
# Search
curl -X POST http://localhost:3002/v1/search \
  -d '{"query": "...", "limit": 8}'

# Scrape
curl -X POST http://localhost:3002/v1/scrape \
  -d '{"url": "...", "formats": ["markdown"]}'
```

**Response format:**
```json
{
  "success": true,
  "data": [
    {"url": "...", "title": "...", "description": "..."}
  ]
}
```

**Key:** response uses `"data"` array, NOT `"results"`.

## Output Format: Single Flat File (Vietnamese, No Raw Data)

**User preference (Julius):** 
1. **One self-contained `.md` file only**. No nested directories, no `data/` subfolder, no separate `brief.txt` or `sources.md`.
2. **No raw data in the report**. Do NOT list tweets, tweet excerpts, or web article excerpts in the final report. Use tweets and web sources as **context only** for synthesis. The report should contain only synthesized insights, analysis, and narrative.
3. **All content in Vietnamese**. See Language section above.

**Output path:**
```
/home/julius/julius-workspace/working/X/report/research/{topic-slug}-{date}.md
```

**Before (wrong):**
```
perp-dex-2026-21-05-2026/
├── HERMES_SYNTHESIS_PROMPT.md
├── data/
│   ├── tweets.json
│   ├── web_sources.json
│   └── synthesis.json
├── perp-dex-2026-21-05-2026-research.md
├── perp-dex-2026-21-05-2026-brief.txt
└── perp-dex-2026-21-05-2026-sources.md
```

**After (correct):**
```
/home/julius/julius-workspace/working/X/report/research/
└── perp-dex-2026-21-05-2026.md   ← one file, Vietnamese, insight-only
```

**Implementation:**
- Intermediate JSON goes to `/tmp/x-research-XXXX/` (auto-deleted after report generation)
- Template renders all sections inline: Tóm tắt, Chỉ số chính, Bức tranh Thị trường, Phân tích Sâu, Xu hướng Nổi bật, Quan điểm Trái chiều, Khoảng trống Thông tin, Tín hiệu Alpha
- Telegram brief is extracted by parsing the Tóm tắt section from the single .md file
- No "Full Sources" or "Nguồn" section at the end

## Pitfalls

| Issue | Fix |
|-------|-----|
| X search 401 | Use `twitter` CLI instead of `xurl`; xurl free tier is read-only |
| Firecrawl search empty | Response uses `"data"` array, NOT `"results"` |
| Firecrawl scrape 500 | Retry with backoff; some sites block crawlers |
| LLM context overflow | Chunk web content; summarize tweets before synthesis |
| Report sections empty | Check Jinja2 template conditions match data keys |
| Telegram not sent | Export `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| Config KeyError | Use `.get()` with defaults; user prefers minimal config without `processing` nesting |
| User wants 1 file only | Flat output mode: single `.md`, intermediate files in `/tmp` |
| `skip_to_stage` loses data | Cache intermediate JSON in `/tmp/x-research-*/` and auto-detect latest temp dir when resuming. |
| Web content truncated | Firecrawl returns full markdown; don't truncate in template. Use `[:800]` only for preview, full for synthesis. |
| Jinja2 `KeyError` in template | Use `.get()` everywhere in report context; deep_analysis may be string or dict depending on synthesis source. |
| Raw tweets appear in report | Ensure synthesis prompt explicitly says "KHÔNG liệt kê raw tweet trong output" and template has no X/Twitter Insights section |
| Report in English | Ensure synthesis prompt says "bằng tiếng Việt" and template uses Vietnamese headings |

## Quality Checklist

- [ ] Every claim cites source (@handle or URL)
- [ ] Balanced bullish/bearish perspective
- [ ] Contrarian views included
- [ ] Sources deduplicated (max 2 per domain)
- [ ] Relevance filter applied to tweets
- [ ] Report renders correctly in Markdown
