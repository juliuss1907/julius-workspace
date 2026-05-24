# Vietnamese Flat Agent-Only Refactor Notes

**Session:** 2026-05-21 — Julius building x-research skill in `ai-labs/projects/x-research/`

## Key Decisions Made

### 1. Standalone Mode Rejected
Julius explicitly said: *"Tôi nghĩ lại rồi, không cần thiết phải chạy standalone, hãy xóa phần đó nhé"*

**Action taken:**
- Removed `--hermes-mode` flag (always agent mode)
- Removed `run_synthesis()` API call from `main.py`
- Simplified `synthesis.py` to placeholder
- Simplified `llm_client.py` to placeholder
- Deleted `.env.example` (no API keys needed)
- Updated `config.yaml`: removed `model`/`temperature`/`max_tokens`, removed sections `x_insights`, `sentiment`, `web_findings`, `sources`

### 2. Flat Output Confirmed
Julius: *"chỉ cần 1 report dạng file md là được rồi"*

**Action taken:**
- Output path: `/home/julius/julius-workspace/working/X/report/research/{topic-slug}-{date}.md`
- No nested directories, no `data/` subfolder
- No `HERMES_SYNTHESIS_PROMPT.md` in final output
- Temp data in `/tmp/x-research-*/` (auto-cleanup after report gen)

### 3. No Raw Data in Report
Julius: *"Mục Web findings và X/Twitter Insights khá vô nghĩa, thay vì trình bày vào report, hãy sử dụng chúng làm context để viết report cho thật insightful hơn"*

**Action taken:**
- Removed X/Twitter Insights section from template
- Removed Web Findings section from template
- Removed Full Sources section from template
- Template now only shows synthesized insight sections

### 4. Vietnamese Language
Julius: *"Hãy viết report bằng tiếng Việt"*

**Action taken:**
- Synthesis prompt: `"bằng tiếng Việt"`
- Report template uses Vietnamese headings
- Agent writes `synthesis.json` in Vietnamese

## Report Template Structure (Vietnamese)

```
# {topic} — Báo cáo Nghiên cứu
├── Tóm tắt
├── Chỉ số chính (Key Metrics)
├── Bức tranh Thị trường (Market Landscape)
│   ├── Dẫn đầu
│   ├── Thử thách
│   └── TAM
├── Phân tích Sâu (~2500-3500 từ)
│   ├── 1. Tổng quan thị trường
│   ├── 2. Các bên chính & Định vị
│   ├── 3. Diễn biến & Catalyst gần đây
│   ├── 4. Xu hướng công nghệ
│   ├── 5. Bối cảnh pháp lý
│   └── 6. Rủi ro & Thách thức
├── Xu hướng Nổi bật
├── Quan điểm Trái chiều
├── Khoảng trống Thông tin
├── Tín hiệu Alpha
└── Footer
```

## Synthesis JSON Structure

The agent writes a JSON file with these keys:
```json
{
  "executive_summary": "string (4-5 sentences)",
  "market_landscape": {
    "leaders": ["..."],
    "challengers": ["..."],
    "total_addressable_market": "..."
  },
  "deep_analysis": "string (2500-3500 words, markdown)",
  "key_metrics": {
    "volume": "...",
    "market_share": "...",
    "funding": "...",
    "user_growth": "..."
  },
  "emerging_trends": ["..."],
  "contrarian_views": ["..."],
  "information_gaps": ["..."],
  "alpha_signals": ["..."],
  "metadata": {
    "tweet_count": N,
    "web_source_count": N,
    "model": "Hermes Agent"
  }
}
```

## Temp Dir Resume Flow

```bash
# Step 1: Collect data
python scripts/main.py --topic "Perp DEX 2026"
# → Exits 42, creates /tmp/x-research-xxx/
# → Writes HERMES_SYNTHESIS_PROMPT.md

# Step 2: Agent writes synthesis.json

# Step 3: Generate report
XRESEARCH_TEMP_DIR=/tmp/x-research-xxx \
python scripts/main.py --topic "Perp DEX 2026" --skip-to-stage 4
# → Reads synthesis.json from temp dir
# → Generates single .md
# → Cleans up temp dir
```

## Pitfall: Config Minimalism

Julius prefers a **flat config** without deep nesting. When accessing config values, always use `.get()` with defaults:

```python
# Good
domain_limit = config.get('processing', {}).get('domain_limit', 2)

# Bad (raises KeyError if section missing)
domain_limit = config['processing']['domain_limit']
```
