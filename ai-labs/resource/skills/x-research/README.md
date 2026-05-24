# X-Research

Deep research skill combining X/Twitter insights and web sources to generate comprehensive analysis reports via Hermes Agent synthesis.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Step 1: Collect data (exits with prompt for agent)
python scripts/main.py --topic "Perp DEX 2026"

# Step 2: Agent writes synthesis.json to temp dir

# Step 3: Generate report
python scripts/main.py --topic "Perp DEX 2026" --skip-to-stage 4
```

## Features

- **X/Twitter Research**: Search tweets via `twitter` CLI
- **Web Research**: Scrape sources via Firecrawl localhost
- **Agent Synthesis**: Hermes agent reads data, writes structured synthesis
- **Flat Output**: Single `.md` file per topic — no nested directories

## Architecture

```
Stage 1: X Research
  └─> twitter search -> tweets.json

Stage 2: Web Research
  └─> Firecrawl -> web_sources.json

Stage 3: Agent Synthesis
  └─> Hermes agent reads prompt -> writes synthesis.json

Stage 4: Report Generation
  └─> Jinja2 template -> single .md report
```

## Configuration

Edit `config.yaml` to customize:

- `research.tweet_limit`: Max tweets (default: 50)
- `research.web_sources`: Max web pages (default: 10)
- `output.report_dir`: Output directory
- `telegram.enabled`: Send brief notification

## Usage

### Basic flow
```bash
# Run data collection
python scripts/main.py --topic "Ethereum L2 2026"
# -> Exits with prompt path. Agent writes synthesis.json.

# Resume to generate report
XRESEARCH_TEMP_DIR=/tmp/x-research-xxx \
python scripts/main.py --topic "Ethereum L2 2026" --skip-to-stage 4
```

### Custom parameters
```bash
python scripts/main.py \
  --topic "AI agents crypto" \
  --tweet-limit 30 \
  --web-sources 10
```

## Output

```
/home/julius/julius-workspace/working/X/report/research/
└── perp-dex-2026-21-05-2026.md   # Single file, Vietnamese, insight-rich
```

## Dependencies

### External Tools
- `twitter` CLI for X/Twitter search
- Firecrawl localhost:3002 for web scraping

### Python Packages
See `requirements.txt`

## Documentation

- [SKILL.md](SKILL.md) - Full skill specification
- [DESIGN.md](DESIGN.md) - Architecture and design decisions
- [config.yaml](config.yaml) - Configuration reference

## License

MIT

## Author

Julius - 2026
