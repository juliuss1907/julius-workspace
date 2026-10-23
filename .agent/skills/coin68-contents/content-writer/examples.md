# Examples — Coin68 Content Writer

Good vs bad article patterns.

**Version:** 2.0
**Last updated:** 2026-05-26

---

## Example 1: Good Review Article

**Project:** Phoenix
**Category:** perpdex
**Word count:** 1,247

### Frontmatter
```yaml
---
title: "Phoenix là gì? Tìm hiểu về fully on-chain perp DEX trên Solana"
description: "Phoenix là perp DEX fully on-chain trên Solana với matching engine kép. Tìm hiểu kiến trúc, phí giao dịch, đội ngũ và tokenomics PHNX."
source: "https://coin68.com/phoenix-la-gi/"
created: 2026-05-04
tags:
  - "perp-dex"
  - "solana"
---
```

**Why good:**
- `title` under 60 chars, primary keyword ("Phoenix là gì") at the start
- `description` is 148 chars, includes keyword + value proposition
- `tags` match published.md categories
- `source` provides canonical URL

### Title
```markdown
# Phoenix là gì? Tìm hiểu về fully on-chain perp DEX trên Solana
```

**Why good:**
- Clear format: "[Project] là gì? Tìm hiểu về [description]"
- Includes key differentiator (fully on-chain)
- Mentions blockchain (Solana)
- Under 60 characters

### Opening section
```markdown
## Phoenix là gì?

Phoenix là perp DEX được xây dựng hoàn toàn trên blockchain Solana bởi Ellipsis Labs. Với kiến trúc fully on-chain và sử dụng matching engine kép kết hợp sổ lệnh FIFO truyền thống với Spline liquidity độc quyền, Phoenix mang đến trải nghiệm giao dịch perpetual futures với tốc độ và hiệu quả vốn cao.
```

**Why good:**
- 2 sentences, concise
- Defines what it is (perp DEX on Solana)
- States key innovation (matching engine kép)
- Uses crypto-native terms correctly (perp DEX, not translated)
- No hype language

### Feature section
```markdown
## Điểm nổi bật của Phoenix

### Kiến trúc fully on-chain

Phoenix được xây dựng hoàn toàn trên blockchain Solana, không sử dụng bất kỳ thành phần off-chain nào trong quá trình xử lý giao dịch. Điều này đảm bảo tính minh bạch tuyệt đối và khả năng kiểm chứng mọi hoạt động giao dịch trực tiếp trên blockchain.

### Matching engine kép

Phoenix sử dụng hai matching engine song song: sổ lệnh FIFO truyền thống cho các lệnh limit order và Spline liquidity engine độc quyền cho market order. Cơ chế này giúp tối ưu hóa việc khớp lệnh, giảm slippage và tăng hiệu quả vốn cho cả maker và taker.
```

**Why good:**
- Each feature has clear H3 heading
- 1-2 paragraphs per feature
- Explains technical concept in accessible Vietnamese
- States user benefit (giảm slippage, tăng hiệu quả vốn)
- No marketing fluff

### Team section
```markdown
## Đội ngũ phát triển

Phoenix được phát triển bởi Ellipsis Labs, một công ty nghiên cứu và phát triển blockchain chuyên về hạ tầng DeFi trên Solana. Đội ngũ bao gồm các kỹ sư có kinh nghiệm từ các công ty công nghệ hàng đầu và các dự án DeFi lớn trong hệ sinh thái Solana.
```

**Why good:**
- States company name
- Brief background
- Neutral tone (no "all-star team")

### Closing
```markdown
## Tổng kết

Phoenix là một perp DEX fully on-chain trên Solana với kiến trúc matching engine độc đáo, hướng tới mục tiêu mang đến trải nghiệm giao dịch perpetual futures nhanh chóng và hiệu quả vốn cao. Dự án hiện đang trong giai đoạn testnet và dự kiến ra mắt mainnet trong Q2/2026.

**Có thể bạn quan tâm:**

- [Hyperliquid là gì? Tìm hiểu chi tiết về sàn phái sinh trên blockchain](https://coin68.com/hyperliquid-la-gi/)
- [Perpetual Protocol (PERP) là gì? Tìm hiểu về giao thức phái sinh trên Ethereum](https://coin68.com/perpetual-protocol-la-gi/)
```

**Why good:**
- Restates core value prop
- Mentions current status
- No investment advice, no hype
- Internal linking to 2 related published articles in same category (perp-dex)
- Descriptive anchor text (full article titles)

---

## Example 2: Bad Review Article

**Same project (Phoenix), but poorly executed**

### Title
```markdown
# Phoenix: Sàn Giao Dịch Perpetual Tốt Nhất Trên Solana!
```

**Why bad:**
- Exclamation mark (too promotional)
- Superlative ("Tốt Nhất") without evidence
- Forced Vietnamese translation ("Sàn Giao Dịch Perpetual")
- Missing "là gì?" format

### Opening
```markdown
## Phoenix là gì?

Phoenix là một dự án cực kỳ đột phá trong lĩnh vực DeFi! Đây là sàn giao dịch perpetual futures đầu tiên được xây dựng hoàn toàn on-chain trên Solana, mang đến trải nghiệm giao dịch tuyệt vời với tốc độ nhanh như chớp và phí cực thấp. Đội ngũ phát triển là những chuyên gia hàng đầu từ các công ty lớn nhất thế giới.
```

**Why bad:**
- Hype language ("cực kỳ đột phá", "tuyệt vời", "nhanh như chớp")
- Unverified claim ("đầu tiên")
- Mixing team info into definition section
- Exclamation mark

### Feature section
```markdown
## Tính năng

Phoenix có rất nhiều tính năng tuyệt vời:
- Fully on-chain
- Matching engine tốt
- Phí thấp
- Nhanh
- An toàn
```

**Why bad:**
- Generic heading ("Tính năng" instead of "Điểm nổi bật của Phoenix")
- Bullet list without any explanation
- Vague descriptions ("tốt", "nhanh", "an toàn")
- No technical details, no user benefits

### Team section
```markdown
## Team

Team rất mạnh, có người từ Google, Facebook, và các dự án DeFi lớn. Họ đã làm việc nhiều năm trong ngành và có kinh nghiệm sâu rộng.
```

**Why bad:**
- English heading ("Team")
- Vague unverified claims ("rất mạnh", "kinh nghiệm sâu rộng")
- No company name, no specific names or roles
- Reads like marketing copy

### Closing
```markdown
## Kết luận

Phoenix là một dự án đầy tiềm năng và đáng để đầu tư. Với đội ngũ mạnh, công nghệ tiên tiến, và hệ sinh thái Solana đang phát triển, Phoenix chắc chắn sẽ trở thành sàn perp DEX hàng đầu. Đừng bỏ lỡ cơ hội này!
```

**Why bad:**
- Investment advice ("đáng để đầu tư", "Đừng bỏ lỡ")
- Speculation ("chắc chắn sẽ trở thành")
- Hype language ("đầy tiềm năng")
- Exclamation mark

---

## Example 3: Handling Missing Information (Good)

**Project:** NewProject (hypothetical)
**Situation:** Team info not available

### What agent does

```markdown
## Đội ngũ phát triển

Thông tin về đội ngũ phát triển NewProject chưa được công bố công khai. Dự án hiện hoạt động dưới dạng pseudonymous, tập trung vào việc xây dựng sản phẩm và cộng đồng.
```

**Why good:**
- States the fact (info not available)
- Doesn't speculate or make up info
- Provides context (pseudonymous is common in crypto)
- Neutral tone

### What agent does NOT do

```markdown
## Đội ngũ phát triển

Đội ngũ NewProject bao gồm các chuyên gia blockchain có kinh nghiệm nhiều năm trong ngành. Mặc dù họ chọn giữ ẩn danh, nhưng chất lượng sản phẩm cho thấy họ là những người rất giỏi.
```

**Why bad:**
- Makes up information ("chuyên gia", "nhiều năm kinh nghiệm")
- Speculates about quality ("rất giỏi")
- Presents assumptions as facts

---

## Example 4: Escalation (Good)

**Project:** ComplexProject
**Situation:** Contradictory tokenomics info

**Escalation file:** `tasks/inbox/escalation-2026-05-04-1530.md`

```markdown
---
type: inbox
inbox_type: escalation
related_task: coin68-complexproject-ddl-10-05-2026
created: 2026-05-04-1530
---

# Escalation: Contradictory Tokenomics Information

## Task
coin68-complexproject-ddl-10-05-2026.md

## Issue
Found contradictory information about ComplexProject tokenomics:

**Source 1 (Whitepaper, page 12):**
- Total supply: 1,000,000,000 tokens
- Team allocation: 20%

**Source 2 (Official blog post, 2026-04-15):**
- Total supply: 100,000,000 tokens
- Team allocation: 15%

**Source 3 (CoinGecko):**
- Total supply: 1,000,000,000 tokens
- Team allocation: 20%

## Analysis
Whitepaper and CoinGecko agree. Blog post may be outdated or contain an error.

## Proposed Solutions
Option A: Use whitepaper + CoinGecko numbers, note blog discrepancy in article
Option B: Omit specific numbers, state "tokenomics details available in whitepaper"
Option C: Wait for you to verify with project team

Which approach do you prefer?
```

**Why good:**
- Clearly states the problem
- Lists all sources with specific details
- Provides analysis (which sources agree)
- Offers 3 concrete options
- Asks for decision rather than guessing

---

**Last updated:** 2026-05-26
