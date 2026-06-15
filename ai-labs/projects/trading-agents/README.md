# Trading Agents — Hệ thống phân tích crypto với shared brain, 2 consumer paths

`trading-agents` là hệ thống trading agent dùng AI để phân tích thị trường crypto, kết hợp technical analysis, news, sentiment, fundamentals, và derivatives data để tạo ra **một shared analysis core** phục vụ **hai output paths**:

- **Demo auto-trade**: paper/demo execution để kiểm chứng signal và vận hành feedback loop an toàn.
- **Manual trade report**: báo cáo markdown execution-free để anh review và vào lệnh real-money thủ công.

## Tổng quan

- **North star architecture:** 5 layers, shared analysis/synthesis core, separate policy + output paths
- **Current runtime shape:**
  - `orchestration.analyze_symbol()` / `orchestration.analysis_runner.analyze_symbol()` → normalized `FinalAnalysis`
  - `scripts/analyze_symbol_readonly.py` → thin read-only CLI over shared orchestration
  - `policies.demo_execution` → `scripts/run_paper_trading.py`
  - `policies.manual_report` → `scripts/generate_manual_trade_report.py`
- **LLM Providers:** OpenCode Go + Ollama Cloud Pro
- **Execution model:** manual real-money decisions stay execution-free; paper trading remains demo-only
- **Adaptive:** Parameter tuning, calibration, and backtesting support the core but are not the product center

## Current architecture status

Orchestration refactor đã hoàn thành các mốc chính từ shared core đến readonly cleanup:

- Shared contracts + analysis runner: `orchestration/contracts.py`, `orchestration/analysis_runner.py`
- Policy consumers: `policies/demo_execution.py`, `policies/manual_report.py`, `policies/reverse_planner.py`
- Runtime consumers: `scripts/run_paper_trading.py`, `scripts/generate_manual_trade_report.py`, `scripts/analyze_symbol_readonly.py`
- Boundary guardrails: `scripts/test_boundary_guardrails.py`

Repo hiện đang ở **repo hygiene + safe runtime dry-run smoke**: README/docs đã được căn lại với shared-core model; runtime dry-run smoke (`--single-cycle --dry-run`) đã được implement và validate. Bước tiếp theo là inventory các file chưa track trước khi stage rộng hơn.

### Core rule

`run_paper_trading.py` **không còn là system brain**. Nó là downstream consumer của shared orchestration layer.

Nếu một logic có thể dùng cho cả demo path và manual-report path, nó nên nằm ở:

- `orchestration/` nếu là shared analysis/synthesis
- `policies/` nếu là translation layer theo use case

Không nên nhét ngược về runtime script.

## Tính năng chính

✅ **Multi-mode Analysis**
- **Full Mode:** Phân tích sâu với tất cả agents (7h hàng ngày)
- **Quick Mode:** Phân tích nhanh technical + news (11h, 15h, 19h, 23h)
- **Lite Mode:** Giám sát giá real-time (mỗi giờ)
- **Flash Quick:** Phản ứng tức thì với biến động >10%

✅ **Data Sources Toàn diện**
- Spot & Futures prices (Binance, CCXT, GeckoTerminal, DEX Screener)
- Derivatives data (Hyperliquid, Binance Futures, Lighter)
- News & Sentiment (CryptoPanic, The Block, X/Twitter, Polymarket)
- On-chain metrics (DefiLlama, Token Terminal, Messari)

✅ **Risk Management Chặt chẽ**
- Risk-based position sizing (3% risk per trade)
- ATR-based stop loss (fallback: fixed 15%)
- Min risk/reward 1:2
- Max leverage x10 (isolated margin)

✅ **Two Output Paths**
- Virtual portfolio $10,000 USDT
- Spot + Futures trading
- Slippage & fees simulation
- So sánh performance với live trades của Julius
- Manual report path tạo một markdown artifact phẳng, không đòi runtime execution phải chạy

✅ **Adaptive Learning**
- Confidence weights tự điều chỉnh hàng tháng
- Per-coin parameter tuning (RSI, MACD, SL/TP...)
- Fine-tuning agents hàng tháng với DeepSeek V4 Flash

✅ **Telegram Integration**
- Notifications real-time
- Daily/weekly summaries
- On-demand queries (status, P&L, positions...)
- Natural language logging

## Cấu trúc Documentation

- [docs/README.md](docs/README.md) — Index tài liệu, entrypoint nên đọc đầu tiên
- [01. Architecture](docs/01-architecture.md) — Kiến trúc 5 tầng, modes, Systems Thinking
- [02. Data Sources](docs/02-data-sources.md) — Nguồn dữ liệu, parallel fetch model
- [03. Execution Layer](docs/03-execution-layer.md) — Live advisory + paper trading
- [04. Error Handling](docs/04-error-handling.md) — Fallback, retry logic, data validation
- [05. State Management](docs/05-state-management.md) — SQLite + JSON, snapshots
- [06. Data Storage](docs/06-data-storage.md) — OHLCV, logs, reports, backup
- [07. Backtesting](docs/07-backtesting.md) — Framework, slippage, fees, baselines
- [08. Confidence Scoring](docs/08-confidence-scoring.md) — Weighted scoring, self-adjusting
- [09. Position Sizing](docs/09-position-sizing.md) — Risk-based sizing, SL/TP strategies
- [10. Monitoring](docs/10-monitoring.md) — Telegram dashboard, alerts
- [11. Parameter Tuning](docs/11-parameter-tuning.md) — Per-coin adaptive tuning
- [12. Fine-tuning](docs/12-fine-tuning.md) — Agent self-learning
- [13. Implementation Roadmap](docs/13-implementation-roadmap.md) — Phases chi tiết
- [14. Rescue Architecture](docs/14-rescue-architecture.md) — North-star reset: shared brain, separate demo/manual tracks
- [15. Orchestration Implementation Plan](docs/15-orchestration-implementation-plan.md) — Refactor roadmap đã dùng cho shared-core / policy / readonly cleanup milestones

## Quick Start

### Requirements

- Python 3.10+
- API keys:
  - OpenCode Go ($10/tháng)
  - Ollama Cloud Pro
  - Binance API (read-only)
  - Telegram Bot Token

### Installation

```bash
# Clone repo
cd ai-labs/projects/trading-agents

# Install dependencies
pip install -r requirements.txt

# Setup config
cp config/default_params.yaml.example config/default_params.yaml
cp .env.example .env
# Edit .env với API keys

# Initialize database
python scripts/init_db.py

# Test data fetchers
python scripts/test_data_sources.py
```

### Chạy lần đầu

```bash
# Xem docs index trước
cat docs/README.md

# Shared manual path (help should stay lightweight)
python scripts/generate_manual_trade_report.py --help

# Safe demo execution smoke (no Telegram startup, no position mutations, no production state writes)
python scripts/run_paper_trading.py --single-cycle --dry-run

# Read-only shared analysis path
python scripts/analyze_symbol_readonly.py BTCUSDT

> **Safety note:** Use `run_paper_trading.py --single-cycle --dry-run` for smoke tests. A plain `--single-cycle` run is an operational run: it may start the Telegram bot, send notifications, write runtime health/state, save portfolio snapshots, run reconciliation, and mutate paper positions depending on config.

# Optional demo-policy inspection for the same symbol (loads runtime-side managers intentionally)
python scripts/analyze_symbol_readonly.py BTCUSDT --include-demo-decision

# Chạy Full mode legacy entrypoint cho 1 coin (nếu còn dùng)
python main.py --mode full --coin BTC

# Xem output
cat reports/daily/$(date +%Y-%m-%d)-full.md
```

### Manual report path

```bash
# Generate one flat markdown artifact for discretionary review
python scripts/generate_manual_trade_report.py \
  --symbols BTCUSDT ETHUSDT SOLUSDT
# Default output: reports/manual-trade-report-$(date +%Y-%m-%d).md
```

### Boundary checks

```bash
python scripts/test_final_analysis_contract.py
python scripts/test_analysis_runner.py
python scripts/test_demo_execution_policy.py
python scripts/test_manual_report_policy.py
python scripts/test_boundary_guardrails.py
python scripts/test_readonly_analyzer_cli.py
```

## Configuration

Xem `config/` cho examples:
- `default_params.yaml` — Global defaults
- `coin_params/BTC.yaml` — Per-coin overrides
- `thresholds.yaml` — Risk thresholds

## Development roadmap

**Phase 1 (MVP):** Technical Analyst + data fetchers + paper trading
**Phase 2:** News & Sentiment analysts
**Phase 3:** Derivatives + Bull/Bear researchers
**Phase 4:** Risk & Portfolio management
**Phase 5:** Backtesting framework
**Phase 6:** Adaptive parameter tuning
**Phase 7:** Fine-tuning pipeline
**Phase 8:** Screening agent

Xem chi tiết tại [Implementation Roadmap](docs/13-implementation-roadmap.md).

## Architecture entrypoints cho contributor mới

Nếu muốn hiểu repo nhanh mà không drift về execution-first mindset, đọc theo thứ tự này:

1. [`docs/14-rescue-architecture.md`](docs/14-rescue-architecture.md)
2. [`docs/15-orchestration-implementation-plan.md`](docs/15-orchestration-implementation-plan.md)
3. [`docs/README.md`](docs/README.md)
4. `orchestration/contracts.py`
5. `orchestration/analysis_runner.py`
6. `policies/demo_execution.py`
7. `policies/manual_report.py`
8. `policies/reverse_planner.py`

Mục tiêu là thấy rõ:

- cái gì là **shared core**
- cái gì là **demo consumer**
- cái gì là **manual-report consumer**
- cái gì chỉ là **support tooling**

## Contributing

Hệ thống đang trong giai đoạn phát triển. Julius là maintainer chính.

## License

Private project — không public.

## Contact

Julius — Telegram: [Your handle]

---

**Note:** File `trading-agent-idea.md` ở root là phiên bản gốc (legacy), giữ nguyên cho reference.
