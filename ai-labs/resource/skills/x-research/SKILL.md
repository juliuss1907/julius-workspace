# X-Research Skill

## Metadata
- **Skill ID:** `x-research`
- **Version:** 1.0.0
- **Author:** Julius
- **Category:** Research & Analysis
- **Tags:** `research`, `x-twitter`, `web-scraping`, `synthesis`, `crypto`

---

## Description

Deep research skill kết hợp X/Twitter insights và web sources để tạo báo cáo phân tích chuyên sâu bằng **tiếng Việt**, hoàn toàn do **Hermes Agent** (Markus) thực hiện synthesis.

**Capabilities:**
- Search và thu thập tweets theo keyword (không giới hạn KOL list)
- Crawl web sources qua Firecrawl localhost
- **Agent Synthesis**: Markus đọc data, viết analysis insight-rich
- **Flat Output**: Chỉ 1 file `.md` duy nhất — không thư mục con, không raw data

**Use cases:**
- Crypto market research
- Technology trend analysis
- Competitive intelligence
- Event/narrative tracking

---

## Input Schema

```yaml
topic: string              # Required. Research topic/keyword
lookback_hours: int        # Optional. Default: 48
tweet_limit: int           # Optional. Default: 50
web_sources: int           # Optional. Default: 10
```

**Example:**
```bash
@Markus Run x-research on "Ethereum L2 2026"
```

---

## Output

### Primary Output
- **Markdown Report:** `/home/julius/julius-workspace/working/X/report/research/<topic-slug>-<date>.md`
  - Tóm tắt (4-5 câu)
  - Chỉ số chính (volume, thị phần, funding, user)
  - Bức tranh thị trường (dẫn đầu / thử thách / TAM)
  - Phân tích sâu (2500-3500 từ, 6 sub-sections)
  - Xu hướng nổi bật
  - Quan điểm trái chiều
  - Khoảng trống thông tin
  - Tín hiệu alpha

### Design Principles
- **Không raw data trong report**: tweets và web excerpts chỉ dùng làm context cho agent
- **Không section sources**: citations inline dạng [@handle] hoặc [domain.com]
- **Ngôn ngữ**: Tiếng Việt chuyên ngành crypto

---

## Dependencies

### External Tools
- `twitter` CLI (X/Twitter search)
- Firecrawl localhost:3002 (web scraping)
- Telegram bot (notification, optional)

### Python Packages
```
requests>=2.31.0
jinja2>=3.1.2
pyyaml>=6.0
click>=8.0
```

---

## Configuration

See `config.yaml` for full parameters.

**Key settings:**
- `research.tweet_limit`: Max tweets to collect (default: 50)
- `research.web_sources`: Max web pages to crawl (default: 10)
- `output.report_dir`: Output directory (absolute path)
- `telegram.enabled`: Send brief notification

---

## Execution Flow

```
1. X Research (Stage 1)
   └─> twitter search → tweets.json (temp)

2. Web Research (Stage 2)
   └─> Firecrawl search → web_sources.json (temp)

3. Agent Synthesis (Stage 3)
   └─> Markus reads HERMES_SYNTHESIS_PROMPT.md
   └─> Writes synthesis.json (temp)

4. Report Generation (Stage 4)
   └─> Jinja2 template → single .md report
   └─> Cleanup temp files
```

**Estimated runtime:** 2-3 minutes (data collection) + agent synthesis time

---

## Error Handling

| Error | Fallback |
|-------|----------|
| X search returns 0 results | Try keyword variations, continue with web only |
| Firecrawl localhost down | Use `web_search` + `web_extract` tools |
| Agent synthesis missing | Prompt user to write synthesis.json, then `--skip-to-stage 4` |
| Context overflow | Use first 15 tweets + 5 web sources in prompt |

---

## Usage Examples

### Via Hermes
```
@Markus Run x-research on "Solana vs Ethereum 2026"
```

### Direct CLI (Step 1: Collect data)
```bash
cd ai-labs/projects/x-research
python scripts/main.py --topic "Bitcoin ETF impact" --tweet-limit 30
# → Exits with prompt path. Agent writes synthesis.json.
```

### Resume to generate report
```bash
XRESEARCH_TEMP_DIR=/tmp/x-research-xxx \
python scripts/main.py --topic "Bitcoin ETF impact" --skip-to-stage 4
```

---

## Quality Criteria

✅ **Good research output:**
- Every claim cites source (@handle hoặc domain inline)
- Balanced view (không chỉ bullish hoặc bearish)
- Evidence-based, không speculation
- Contrarian views được highlight
- Deep analysis 2500+ từ với structure rõ ràng

❌ **Poor research output:**
- Generic statements không có citation
- Chỉ echo lại tweets không có synthesis
- Bias rõ ràng (hype hoặc FUD)
- Thiếu contrarian perspective
- Report < 2000 từ

---

## Maintenance Notes

**Regular checks:**
- `twitter` CLI vẫn hoạt động (OAuth token còn hiệu lực)
- Firecrawl localhost running
- Output directory permissions

**Known limitations:**
- X search limited by API rate limits (Free tier)
- Firecrawl không hỗ trợ JavaScript-heavy sites
- Agent synthesis requires human agent (Markus) — không chạy fully autonomous
- Không real-time (lookback window only)

---

## Changelog

### v1.0.0 (2026-05-21)
- Initial release
- 4-stage architecture (X → Web → Agent → Report)
- Agent-driven synthesis (Markus/Hermes)
- Flat output: single .md file
- Vietnamese language output
- No standalone LLM API dependency
