# AI Agent trong Giao dịch Tài chính: Nghiên cứu Tổng quan 2025–2026

> **Tác giả:** Feynman Research Agent  
> **Ngày:** 23-05-2026  
> **Mục tiêu:** Tổng hợp toàn diện về AI agent trong trading — từ kiến trúc học thuật, triển khai thực tế, đến bối cảnh tại Việt Nam.

---

## Mục lục

1. [Giới thiệu](#1-giới-thiệu)
2. [Kiến trúc AI Agent trong Trading](#2-kiến-trúc-ai-agent-trong-trading)
3. [Các Framework & Hệ thống Học thuật Nổi bật](#3-các-framework--hệ-thống-học-thuật-nổi-bật)
   - 3.1 [TradingAgents](#31-tradingagents)
   - 3.2 [QuantAgent](#32-quantagent)
   - 3.3 [TiMi (Trade in Minutes)](#33-timi-trade-in-minutes)
   - 3.4 [TrustTrade](#34-trusttrade)
   - 3.5 [SHARP](#35-sharp)
   - 3.6 [Các hệ thống khác](#36-các-hệ-thống-khác)
4. [Triển khai Thực tế & Sản phẩm Thương mại](#4-triển-khai-thực-tế--sản-phẩm-thương-mại)
   - 4.1 [Gemini Agentic Trading (sàn CEX)](#41-gemini-agentic-trading-sàn-cex)
   - 4.2 [Sygnum Bank – AI Agent Ngân hàng](#42-sygnum-bank--ai-agent-ngân-hàng)
   - 4.3 [NVIDIA Signal Discovery Agent](#43-nvidia-signal-discovery-agent)
   - 4.4 [NexusTrade / Public Portfolio Challenge](#44-nexustrade--public-portfolio-challenge)
   - 4.5 [Open-source Projects](#45-open-source-projects)
5. [Bối cảnh tại Việt Nam](#5-bối-cảnh-tại-việt-nam)
   - 5.1 [StockGuru (VPBankS)](#51-stockguru-vpbanks)
   - 5.2 [MASA AI (Mirae Asset)](#52-masa-ai-mirae-asset)
   - 5.3 [Dự án Open-source Việt Nam](#53-dự-án-open-source-việt-nam)
   - 5.4 [Fintech AI & Agent AI](#54-fintech-ai--agent-ai)
6. [Thách thức & Rủi ro](#6-thách-thức--rủi-ro)
7. [Tương lai & Xu hướng](#7-tương-lai--xu-hướng)
8. [Tổng kết](#8-tổng-kết)
9. [Nguồn tham khảo](#9-nguồn-tham-khảo)

---

## 1. Giới thiệu

**AI Agent trong trading** là các hệ thống tự trị sử dụng mô hình ngôn ngữ lớn (LLM) và/hoặc học tăng cường (RL) để thực hiện các hoạt động giao dịch tài chính: từ phân tích thị trường, sinh tín hiệu, quản lý rủi ro, đến đặt lệnh thực tế. Không giống bot giao dịch truyền thống (rule-based), AI agent có khả năng:

- **Lập kế hoạch (planning):** phân chia tác vụ phức tạp thành các bước nhỏ.
- **Sử dụng công cụ (tool use):** gọi API thị trường, chạy backtest, truy vấn dữ liệu.
- **Suy luận (reasoning):** phân tích ngữ nghĩa, đọc báo cáo tài chính, cảm xúc thị trường.
- **Tự cải thiện (self-improvement):** học từ kết quả giao dịch, tối ưu hóa chiến lược.

Sự khác biệt cốt lõi giữa AI Agent và bot truyền thống:

| Tiêu chí | Bot truyền thống | AI Agent (LLM-based) |
|---|---|---|
| Logic | Rule-based, cố định | Suy luận linh hoạt, thích nghi |
| Dữ liệu | Giá, khối lượng | Giá + tin tức + báo cáo + cảm xúc |
| Ra quyết định | Máy móc | Multi-agent debate, consensus |
| Khả năng học | Không/có giới hạn | Tự cải thiện qua reflection |
| Giải trình | Khó | Có thể giải thích bằng ngôn ngữ tự nhiên |

---

## 2. Kiến trúc AI Agent trong Trading

Đa số các hệ thống AI Agent tiên tiến đều chia giao dịch thành nhiều vai trò chuyên biệt, mô phỏng cấu trúc của một quỹ đầu tư thực tế:

```
┌──────────────┐
│  Orchestrator│ (Điều phối viên)──── phân công nhiệm vụ
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│            NHÓM PHÂN TÍCH                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Fundamental│ │Technical │ │Sentiment │      │
│  │  Analyst  │ │  Analyst │ │  Analyst │      │
│  └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐                    │
│  │   News   │ │   Bull/  │                    │
│  │  Analyst │ │ Bear Team│                    │
│  └──────────┘ └──────────┘                    │
└──────────────────────────────────────────────┘
       │
       ▼ debate & tổng hợp
┌──────────────────┐
│  Research Team   │─── tranh luận, phản biện luận điểm
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Trader Agent    │─── đề xuất chiến lược (entry/stop/target)
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│  Portfolio Manager   │─── phê duyệt cuối cùng
└──────────────────────┘
         │
         ▼
┌──────────────────────┐
│  Risk Manager        │─── kiểm soát drawdown, exposure
└──────────────────────┘
```

Kiến trúc này được TradingAgents (TauricResearch) tiên phong, sau đó được kế thừa và cải tiến bởi nhiều framework khác.

---

## 3. Các Framework & Hệ thống Học thuật Nổi bật

### 3.1 TradingAgents

- **Paper:** "TradingAgents: Multi-Agents LLM Financial Trading Framework" (arXiv:2412.20138, v7, 2025)
- **Hội nghị:** MARW tại AAAI 2025
- **GitHub:** [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) ⭐ ~47k stars

TradingAgents là framework đặt nền móng cho hướng tiếp cận multi-agent LLM trong trading. Hệ thống mô phỏng một công ty giao dịch với các vai trò:

- **Bull & Bear Researchers:** đánh giá điều kiện thị trường từ hai phía
- **Fundamental / Sentiment / Technical Analysts:** ba loại phân tích song song
- **Traders đa dạng rủi ro:** tổng hợp insights từ debate và dữ liệu lịch sử
- **Risk Management Team:** giám sát exposure
- **Portfolio Manager:** quyết định cuối cùng

Kết quả thực nghiệm cho thấy cải thiện vượt trội so với baseline ở cumulative returns, Sharpe ratio, và maximum drawdown.

### 3.2 QuantAgent

- **Paper:** "QuantAgent: Price-Driven Multi-Agent LLMs for High-Frequency Trading" (arXiv:2509.09995, 2025)
- **ICLR 2026 (under review)**

QuantAgent là framework multi-agent LLM đầu tiên được thiết kế riêng cho **high-frequency trading (HFT)**. Bốn agent chuyên biệt:

| Agent | Chức năng | Công cụ |
|---|---|---|
| **Indicator** | Tính toán chỉ báo kỹ thuật | SMA, RSI, MACD, Bollinger Bands |
| **Pattern** | Nhận diện mô hình giá | Chart pattern recognition |
| **Trend** | Phân tích xu hướng | Trend detection algorithms |
| **Risk** | Kiểm soát rủi ro | Position sizing, stop-loss |

Thử nghiệm trên 9 công cụ tài chính (Bitcoin, Nasdaq futures,...) cho thấy QuantAgent outperforms các baseline ở cả khung giờ 1h và 4h.

### 3.3 TiMi (Trade in Minutes)

- **Paper:** "TiMi: Trade in Minutes — A Rationality-Driven Multi-Agent System" (arXiv:2510.04787, 2025)

Điểm đột phá của TiMi là tách biệt kiến trúc giữa **strategy development** (phát triển chiến lược) và **minute-level deployment** (triển khai cấp phút). Hệ thống có:

- **Two-tier analytical paradigm:** từ macro patterns đến micro customization
- **Layered programming design:** thiết kế bot giao dịch theo lớp
- **Closed-loop optimization:** học qua mathematical reflection

Thử nghiệm trên 200+ cặp giao dịch (stock + crypto) chứng minh hiệu quả về stable profitability, action efficiency, và risk control.

### 3.4 TrustTrade

- **Paper:** "TrustTrade: Human-Inspired Selective Consensus Reduces Decision Uncertainty in LLM Trading Agents" (arXiv:2603.22567, 2026)

TrustTrade giải quyết một vấn đề hành vi nguy hiểm của LLM: **uniform trust** — tin tưởng mọi nguồn thông tin như nhau. Giải pháp:

- **Cross-agent selective consensus:** tổng hợp từ nhiều LLM agents, gán trọng số theo mức độ đồng thuận
- **Deterministic temporal signals:** neo thông tin bằng tín hiệu thời gian tái lập được
- **Reflective memory mechanism:** điều chỉnh risk preference tại test time mà không cần training

Kết quả: chuyển hành vi từ extreme risk-return về mid-risk mid-return profile, giống con người hơn.

### 3.5 SHARP

- **Paper:** "SHARP: A Self-Evolving Human-Auditable Rubric Policy for Financial Trading Agents" (arXiv:2605.06822, 2026)

SHARP là neuro-symbolic framework thay thế tối ưu hóa prompt không cấu trúc bằng **symbolic policy optimization** — một bộ luật condition-action rõ ràng, con người đọc được.

- Khi giao dịch thua lỗ, attribution agent phân tích cross-sample để cô lập lỗi logic
- Atomic policy edits + walk-forward validation
- Tăng 10–20 điểm phần trăm hiệu suất cho model nhỏ (GPT-4o-mini)

Điểm mạnh: **tính minh bạch và kiểm toán** — yêu cầu bắt buộc của tài chính tổ chức.

### 3.6 Các hệ thống khác

| Hệ thống | Đặc điểm chính | Nguồn |
|---|---|---|
| **FLAG-TRADER** | Fusion LLM-Agent + Gradient-based RL | ACL 2025 Findings |
| **FactorMiner** | Tự động khám phá alpha factors (self-evolving) | arXiv:2602.14670 |
| **Moira** | Hierarchical RL cho pair trading | arXiv:2605.01954 |
| **Agent Trading Arena** | Benchmark so sánh LLM agents real-time | arXiv:2502.17967 |
| **BlindTrade** | Anonymize ticker để kiểm tra understanding thực sự | ICLR 2026 FinAI Workshop |

---

## 4. Triển khai Thực tế & Sản phẩm Thương mại

### 4.1 Gemini Agentic Trading (sàn CEX)

- **Thời điểm:** Tháng 5/2026
- **Mô tả:** Gemini (sàn crypto Mỹ) tích hợp toàn bộ trading API vào Model Context Protocol (MCP) của Anthropic.

Cho phép AI agents (ChatGPT, Claude) kết nối trực tiếp vào tài khoản người dùng để:

- Kéo dữ liệu thị trường real-time
- Tra cứu order book
- Đặt lệnh và quản lý vị thế

Người dùng đặt ngân sách, chiến lược và giới hạn — agent tự động thực thi. "Trading Skills" dạng module bao gồm DCA, grid trading, multi-leg structures.

**Ý nghĩa:** Gemini là sàn CEX có quản lý đầu tiên mở giao diện agentic, biến AI thành một *client class* trên sàn, không chỉ là nguồn tín hiệu.

### 4.2 Sygnum Bank – AI Agent Ngân hàng

- **Thời điểm:** 18/05/2026
- **Mô tả:** Sygnum (ngân hàng tài sản số Thụy Sĩ có quản lý) hoàn thành giao dịch AI-agent đầu tiên.

Kiến trúc: MCP server (Claude) — model-agnostic, asset-agnostic. Client gửi lệnh bằng ngôn ngữ tự nhiên, agent tự động lên kế hoạch, kiểm tra smart contract, đánh giá rủi ro, trình client phê duyệt — **private keys không bao giờ rời khỏi thiết bị client**.

Phương châm: **"Human-in-the-Loop"** — AI augment, không thay thế con người.

### 4.3 NVIDIA Signal Discovery Agent

- **Thời điểm:** Tháng 4–5/2026
- **Bài blog:** NVIDIA Developer Blog

Hệ thống multi-agent phát hiện alpha signal tự động, dùng NeMo Agent Toolkit:

1. **Signal Agent** → sinh giả thuyết tín hiệu mới (dùng Nemotron-3-Nano)
2. **Code Agent** → chuyển thành Python code
3. **Evaluation Agent** → backtest, tính IC & Rank IC, gửi phản hồi

Sau 3 iteration: tìm ra tín hiệu momentum có ý nghĩa thống kê (p < 1e-7) trên 3,504 ngày giao dịch S&P 500.

### 4.4 NexusTrade / Public Portfolio Challenge

- **Tác giả:** Austin (cựu kỹ sư Coinbase)
- **Mô tả:** Sử dụng AI agent (multi-model bake-off) để thiết kế chiến lược options, sau đó triển khai $25,000 thật.

Luồng hoạt động:
1. **Bake-off:** 5 LLMs song song (GPT-5.4-mini, Gemini 3 Flash, DeepSeek V4-Pro, Kimi K2.6, Grok-4.3)
2. **Hội tụ:** 3/4 agent chọn bull call spread (50Δ/20Δ) — Kimi K2.6 & DeepSeek V4-Pro trùng delta structure
3. **Stress test:** 4 chế độ thị trường (2022 bear, 2023 bull, 2024 chop, 2025–nay)
4. **Watchdog agent** tuần tra hàng tuần, đề xuất phòng thủ
5. **Atomic spread submission** — cả hai chân lệnh được link, broker nhận cả hoặc từ chối cả

Chi phí bake-off: $42.17, 55M tokens, 1,355 API calls.

### 4.5 Open-source Projects

| Dự án | Mô tả | Link |
|---|---|---|
| **TradingAgents** | Framework gốc, ~47k stars | [GitHub](https://github.com/TauricResearch/TradingAgents) |
| **PyHedge** | Autonomous hedge agent, 122 strategies, 115+ exchanges | [GitHub](https://github.com/FidesFiscus/pyhedge) |
| **Autonomous Investment Swarm** | Darwinian evolution + HMAC-signed execution | [GitHub](https://github.com/kmshihab7878/Autonomous-Investment-Swarm) |
| **open-traitor** | Multi-asset (Coinbase + IBKR), local LLM inference | [GitHub](https://github.com/liljestk/open-traitor) |
| **OpenAlice** | File-driven AI trading agent engine | [GitHub](https://github.com/wenhacx/OpenAlice) |
| **ATLAS** | Self-improving agents (Karpathy autoresearch) | [GitHub](https://github.com/chrisworsey55/atlas-gic) |
| **AutoHedge** | Swarm intelligence hedge fund | [GitHub](https://github.com/the-swarm-corporation/autohedge) |

---

## 5. Bối cảnh tại Việt Nam

### 5.1 StockGuru (VPBankS)

- **Thời điểm:** Tháng 7/2025
- **Đối tác:** VPBankS + Fintech AI

StockGuru là trợ lý tư vấn đầu tư đầu tiên tại Việt Nam ứng dụng **Agentic AI** — khác biệt so với Generative AI thông thường. Hệ thống vận hành như một "công ty AI" với **17 AI Agent chuyên biệt**:

- CEO AI điều phối
- Các Agent đảm nhiệm: phân tích cơ bản, kỹ thuật, định giá, ngành, tâm lý thị trường
- Xử lý lên đến 193,000 token (~450 trang A4)
- Báo cáo phân tích trong 20–30 giây

StockGuru được "đo ni đóng giày" cho thị trường Việt Nam — không giống ChatGPT, Grok hay Gemini.

### 5.2 MASA AI (Mirae Asset)

**MASA AI** là chuyên gia phân tích AI Agent được Chứng khoán Mirae Asset (Việt Nam) ra mắt trên nền tảng M-Stock, hỗ trợ nhà đầu tư ra quyết định với dữ liệu đầu vào từ trung tâm phân tích nội bộ.

### 5.3 Dự án Open-source Việt Nam

| Dự án | Tác giả | Mô tả |
|---|---|---|
| **vn-stock-ai-hedgefund** | [anhquan075](https://github.com/anhquan075/vn-stock-ai-hedgefund) | Finance Agent cho chứng khoán Việt Nam, multi-agent pipeline (Agno), phân tích cơ bản + kỹ thuật + tin tức + sentiment, có backtest |
| **Agent-to-agent-ai-trading-vietnam** | [huudatscience](https://github.com/huudatscience/Agent-to-agent-ai-trading-vietnam) | Hệ thống 3 AI Agents (Senior Analyst, Risk Manager, Trader) sử dụng Google GenAI + A2A protocol |
| **VnStock RAG** | [meth04](https://github.com/meth04/vn_stock_rag) | Multi-Agent RAG với CrewAI + Gemini, tự động thu thập và phân tích dữ liệu chứng khoán |

### 5.4 Fintech AI & Agent AI

Công ty **Fintech AI** (fintechai.vn) nổi lên như một startup trung tâm trong hệ sinh thái Agent AI tài chính tại Việt Nam:

- Phát triển nền tảng AI Agent với Agentic AI
- Hợp tác với VPBankS ra mắt StockGuru
- Định vị: "AI không chỉ phân tích mà còn hiểu và hành động như một nhà đầu tư thực thụ"

Bên cạnh đó, **miquant** (vnquant.vn) phát triển Valuation Engine 1.0 ứng dụng AI Agent giúp nhà đầu tư tiếp cận phân tích định giá linh hoạt. **Finhay** chuẩn bị ra mắt giao dịch tự động với AI-Agent.

> **Lưu ý:** Thị trường AI Agent trading tại Việt Nam đang ở giai đoạn rất sớm. Các hệ thống hiện tại chủ yếu là **trợ lý tư vấn** (advisory), chưa có triển khai giao dịch tự động hoàn toàn với tiền thật như Gemini hay NexusTrade ở quốc tế.

---

## 6. Thách thức & Rủi ro

### 6.1 Uniform Trust & Hallucination

- LLMs có xu hướng **uniform trust** (TrustTrade, 2026): tin tưởng mọi nguồn thông tin như nhau, không phân biệt độ tin cậy.
- Dẫn đến **noise amplification**: nhiễu từ tin tức giả, cảm xúc thị trường bị khuếch đại.

### 6.2 Credit Assignment (SHARP, 2026)

Thị trường tài chính có tỷ lệ tín hiệu/nhiễu (SNR) thấp. Khi thua lỗ, khó phân biệt:
- Lỗi logic trong chiến lược?
- Hay biến động thị trường ngẫu nhiên?

Tối ưu hóa prompt không cấu trúc làm trầm trọng thêm vấn đề này → **policy drift**.

### 6.3 Rủi ro Hệ thống (Systemic Risk)

- **Coordinated patterns:** nếu nhiều người dùng cùng chạy AI agents giống nhau hoặc tinh chỉnh trên cùng dữ liệu, có thể tạo ra hành vi giống cartel hóa dòng lệnh (Gemini agentic trading warning).
- **Amplified feedback loops:** trong thời kỳ biến động mạnh, agent strategies gắn chặt có thể khuếch đại các vòng phản hồi.

### 6.4 Quản lý & Kiểm soát

- **FINRA (2026):** AI agents hành động vượt quá phạm vi người dùng mong muốn là rủi ro cốt lõi.
- **EU AI Act:** hiệu lực từ tháng 8/2026 — yêu cầu minh bạch, giám sát con người, trách nhiệm giải trình.
- **FINMA (Thụy Sĩ, 2024):** hướng dẫn giám sát cho tổ chức tài chính sử dụng AI.

### 6.5 Các vấn đề kỹ thuật khác

| Vấn đề | Mô tả |
|---|---|
| **Latency** | LLM inference slow → không phù hợp HFT nếu không tối ưu |
| **Token cost** | Multi-agent = nhiều token = chi phí API lớn |
| **Memory poisoning** | Dữ liệu quá khứ sai lệch có thể làm hỏng agent memory |
| **Schema mismatches** | Lỗi tương thích dữ liệu giữa agent và platform (NexusTrade case) |
| **Reproducibility** | LLM không tất định → khó tái tạo backtest |

---

## 7. Tương lai & Xu hướng

Dựa trên các phát hiện từ nghiên cứu và thực tế triển khai, các xu hướng chính đang định hình lĩnh vực AI Agent trading:

### 7.1 Từ Advisory → Autonomous

- **2024–2025:** Agent phân tích, đề xuất → con người quyết định
- **2025–2026:** Agent tự động đặt lệnh trong giới hạn (Gemini, NexusTrade)
- **2026+:** Agent tự quản lý danh mục hoàn toàn (Sygnum vision)

### 7.2 Multi-Agent → Swarm Intelligence

Kiến trúc đơn agent đã nhường chỗ cho multi-agent với debate, consensus, và phân công vai trò. Bước tiếp theo là **swarm intelligence**: bầy đàn agent phối hợp (AutoHedge, ATLAS).

### 7.3 Symbolic + Neural = Neuro-Symbolic

SHARP (2026) và FactorMiner cho thấy xu hướng kết hợp:

- **Neural:** LLM cho suy luận ngữ nghĩa linh hoạt
- **Symbolic:** rule-based policy rõ ràng, có thể kiểm toán
- → Tận dụng ưu điểm cả hai, triệt tiêu nhược điểm

### 7.4 MCP & A2A Protocols

- **Model Context Protocol (MCP)** của Anthropic đang trở thành tiêu chuẩn kết nối AI agents với hạ tầng tài chính (Gemini, Sygnum đều dùng MCP)
- **Agent-to-Agent (A2A)** protocol mở rộng khả năng giao tiếp giữa các agent từ nhiều hệ thống khác nhau

### 7.5 Self-Improving & Adaptive Agents

- **ATLAS:** tự cải thiện prompt qua market feedback
- **SHARP:** tự động xác định và sửa lỗi chiến lược
- **FactorMiner:** tích lũy knowledge và skills qua thời gian

### 7.6 Tại Việt Nam

Kỳ vọng trong 1–2 năm tới:

- Từ **trợ lý tư vấn** → **giao dịch bán tự động** (human-in-the-loop)
- Thêm các công ty chứng khoán ra mắt AI Agent riêng
- Cộng đồng open-source AI trading Việt Nam phát triển mạnh hơn
- Tích hợp dữ liệu tiếng Việt chất lượng cao cho LLM

---

## 8. Tổng kết

| Khía cạnh | Hiện trạng (2025–2026) |
|---|---|
| **Học thuật** | Framework multi-agent LLM đã matured — TradingAgents, QuantAgent, TiMi, TrustTrade, SHARP được ICLR/AAAI chấp nhận |
| **Triển khai thực tế** | Sàn Gemini cho phép AI agent làm client; Ngân hàng Sygnum chạy live transaction; NexusTrade deploy $25,000 thật |
| **Open-source** | Hệ sinh thái phong phú: TradingAgents (47k stars), PyHedge, ATLAS, AutoHedge, OpenAlice |
| **Việt Nam** | Giai đoạn đầu: StockGuru (VPBankS), MASA AI (Mirae Asset), và các dự án open-source cá nhân. Chủ yếu là advisory, chưa autonomous trading |
| **Rủi ro** | Uniform trust, credit assignment, systemic feedback loops, quản lý chưa theo kịp — nhưng các framework mới (TrustTrade, SHARP) đang giải quyết |
| **Hướng tới** | Neuro-symbolic, swarm intelligence, self-improving agents, tiêu chuẩn hóa kết nối (MCP, A2A) |

**Cảnh báo:** Mặc dù AI agent trading đang tiến bộ nhanh chóng, tất cả các hệ thống thực tế hiện tại đều có human-in-the-loop, giới hạn rủi ro, và cảnh báo rõ ràng. Giao dịch bằng AI agent không phải là "in vàng" — nó vận hành dựa trên xác suất, mô phỏng quá khứ, và giả định về thị trường có thể sai bất cứ lúc nào.

---

## 9. Nguồn tham khảo

### Papers & Academic

1. **TradingAgents** — Xiao et al., 2024. arXiv:2412.20138. https://arxiv.org/abs/2412.20138
2. **QuantAgent** — Zhang et al., 2025. arXiv:2509.09995. https://arxiv.org/abs/2509.09995
3. **TiMi (Trade in Minutes)** — Song et al., 2025. arXiv:2510.04787. https://arxiv.org/abs/2510.04787
4. **TrustTrade** — Li et al., 2026. arXiv:2603.22567. https://arxiv.org/abs/2603.22567
5. **SHARP** — Chen et al., 2026. arXiv:2605.06822. https://arxiv.org/abs/2605.06822
6. **FLAG-TRADER** — Xiong et al., 2025. ACL 2025 Findings. https://aclanthology.org/2025.findings-acl.716.pdf
7. **FactorMiner** — 2026. arXiv:2602.14670. https://arxiv.org/pdf/2602.14670
8. **Moira** — 2026. arXiv:2605.01954. https://arxiv.org/html/2605.01954v1
9. **Agent Trading Arena** — 2025. arXiv:2502.17967. https://arxiv.org/abs/2502.17967v2
10. **BlindTrade** — 2026. ICLR 2026 FinAI Workshop. http://arxiv.org/pdf/2603.17692
11. **Unified Agentic Framework for Portfolio Optimization** — 2026. Springer. https://link.springer.com/article/10.1007/s41060-026-01066-0
12. **Learning to Trade Like an Expert** — 2026. arXiv:2604.16862. https://arxiv.org/abs/2604.16862

### Industry / Products

13. **Gemini Agentic Trading** — crypto.news, 2026. https://crypto.news/geminis-agentic-trading-lets-ai-models-not-humans-drive-cex-order-flow/
14. **Sygnum AI Agent** — Sygnum Bank, 2026. https://www.sygnum.com/news/sygnum-completes-first-live-ai-agent-driven-digital-asset-transactions-by-a-regulated-swiss-bank/
15. **NVIDIA Signal Discovery Agent** — NVIDIA Developer Blog, 2026. https://developer.nvidia.com/blog/automating-and-optimizing-financial-signal-discovery-with-multi-agent-systems/
16. **NexusTrade Public Portfolio Challenge** — NexusTrade, 2026. https://nexustrade.io/blog/agent-deployed-options-strategy-tuesday-20260505
17. **Internal Market Representations in Financial Trading Agents** — Concordance, 2026. https://www.concordance.co/blog/internal-market-representation-financial-agents
18. **AlphaPortfolio** — NBER, 2026. https://www.nber.org/papers/w35195

### Việt Nam

19. **StockGuru (VPBankS)** — MarketTimes, 2025. https://markettimes.vn/vpbanks-dua-cong-nghe-agentic-ai-moi-nhat-vao-tro-ly-dau-tu-stockguru-86542.html
20. **MASA AI (Mirae Asset)** — https://masvn.com/article/ra-mat-masa-ai-doc-quyen-cua-chung-khoan-mirae-asset-620028
21. **Fintech AI Platform** — https://fintechai.vn/
22. **Agent-to-Agent AI Trading Vietnam** — Viblo. https://viblo.asia/p/xay-dung-ai-trading-team-vietnam-ung-dung-giao-thuc-agent-to-agent-a2a-trong-dau-tu-chung-khoan-y37LddnNLov
23. **vn-stock-ai-hedgefund** — GitHub. https://github.com/anhquan075/vn-stock-ai-hedgefund
24. **VnStock RAG** — GitHub. https://github.com/meth04/vn_stock_rag
25. **miquant Valuation Engine** — https://vnquant.vn/posts/2025/2025-03-18-agents-valuation/
26. **Finhay AI-Agent** — https://www.finhay.com.vn/giao-dich-tu-dong-voi-ai-agent-ready

### GitHub Repositories

27. https://github.com/TauricResearch/TradingAgents
28. https://github.com/FidesFiscus/pyhedge
29. https://github.com/kmshihab7878/Autonomous-Investment-Swarm
30. https://github.com/liljestk/open-traitor
31. https://github.com/chrisworsey55/atlas-gic
32. https://github.com/the-swarm-corporation/autohedge
33. https://github.com/wenhacx/OpenAlice
34. https://github.com/NVIDIA-AI-Blueprints/quantitative-signal-discovery-agent

---

> **Research conducted:** 23-05-2026  
> **Status:** Tổng quan dựa trên các nguồn công khai — paper, blog, GitHub, báo chí.  
> **Không phải lời khuyên tài chính.**
