# Templates — Coin68 Writer

Article structure templates and terminology guide.

---

## Review Article Template

Use for "[Project] là gì?" encyclopedia-style articles (800-1500 words).

### Frontmatter

```yaml
---
type: article
category: review
project: [Project Name]
main_tag: crypto
sub_tags: [tag1, tag2]
status: draft
created: YYYY-MM-DD
---
```

### Structure

```markdown
# [Project] là gì? Tìm hiểu về [short description]

## [Project] là gì?

[2-3 sentences defining the project]
- Sentence 1: What it is (category + blockchain)
- Sentence 2: Core value proposition
- Sentence 3: Key differentiator (optional)

## Điểm nổi bật của [Project]

### [Feature 1 name]

[1-2 paragraphs explaining feature]
[Technical details if relevant]
[User benefit]

### [Feature 2 name]

[1-2 paragraphs explaining feature]

### [Feature 3 name]

[1-2 paragraphs explaining feature]

[... 3-6 features total depending on project complexity]

## [Sản phẩm chính / Cơ chế hoạt động] (optional)

Use this section when project has multiple products or complex mechanisms.

### [Component 1]

[Explanation]

### [Component 2]

[Explanation]

## Đội ngũ phát triển

[Project] được phát triển bởi [Company/Team Name], do [Founder Name] sáng lập.

[Optional: 1-2 sentences about founder background]

[Optional: Notable team members]

**If team info not available:**
Thông tin đội ngũ phát triển chưa được công bố, Coin68 sẽ cập nhật khi có thêm thông tin.

## Nhà đầu tư [và đối tác]

[Project] đã huy động được [amount] trong vòng [round name] do [lead investor] dẫn đầu, với sự tham gia của [other investors].

[Optional: Notable partnerships]

**If funding info not available:**
Thông tin về nhà đầu tư của [Project] chưa được công bố công khai. Coin68 sẽ cập nhật khi có thêm thông tin.

## Tokenomics (optional)

Only include if project has a token.

**Token:** [Symbol]
**Tổng cung:** [Total supply]
**Phân bổ:**
- [Category 1]: [percentage]
- [Category 2]: [percentage]
- [Category 3]: [percentage]

[Optional: Vesting schedule, utility, governance details]

**If no token:**
Omit this section entirely.

## Tổng kết

[2-3 sentences wrapping up]
- Sentence 1: Restate core value proposition
- Sentence 2: Current status or next milestone
- Sentence 3: Neutral closing (no investment advice)
```

---

## Filled Example (Phoenix)

```markdown
---
type: article
category: review
project: Phoenix
main_tag: crypto
sub_tags: [perpdex, defi, solana]
status: draft
created: 2026-05-04
---

# Phoenix là gì? Tìm hiểu về fully on-chain perp DEX trên Solana

## Phoenix là gì?

Phoenix là perp DEX được xây dựng hoàn toàn trên blockchain Solana bởi Ellipsis Labs. Với kiến trúc fully on-chain và sử dụng matching engine kép kết hợp sổ lệnh FIFO truyền thống với Spline liquidity độc quyền, Phoenix mang đến trải nghiệm giao dịch perpetual futures với tốc độ và hiệu quả vốn cao.

## Điểm nổi bật của Phoenix

### Kiến trúc fully on-chain

Phoenix được xây dựng hoàn toàn trên blockchain Solana, không sử dụng bất kỳ thành phần off-chain nào trong quá trình xử lý giao dịch. Điều này đảm bảo tính minh bạch tuyệt đối và khả năng kiểm chứng mọi hoạt động giao dịch trực tiếp trên blockchain.

Khác với các perp DEX sử dụng off-chain order book hoặc centralized sequencer, Phoenix xử lý toàn bộ logic matching và settlement trên Solana, tận dụng tốc độ xử lý cao của blockchain này để đảm bảo trải nghiệm giao dịch mượt mà.

### Matching engine kép

Phoenix sử dụng hai matching engine song song: sổ lệnh FIFO truyền thống cho các lệnh limit order và Spline liquidity engine độc quyền cho market order. Cơ chế này giúp tối ưu hóa việc khớp lệnh, giảm slippage và tăng hiệu quả vốn cho cả maker và taker.

Spline liquidity engine là công nghệ độc quyền của Ellipsis Labs, cho phép tạo ra các liquidity pool động thay đổi theo điều kiện thị trường, giúp cải thiện depth và giảm chi phí giao dịch.

### Phí giao dịch cạnh tranh

Phoenix áp dụng cấu trúc phí maker-taker với mức phí thấp hơn đáng kể so với các perp DEX khác. Maker được hưởng rebate, trong khi taker trả phí tối thiểu, khuyến khích thanh khoản và tạo môi trường giao dịch hiệu quả.

### Hỗ trợ nhiều loại lệnh giao dịch

Ngoài các lệnh market và limit cơ bản, Phoenix hỗ trợ stop-loss, take-profit, và các lệnh điều kiện phức tạp khác, giúp trader có thể quản lý rủi ro và tối ưu chiến lược giao dịch một cách linh hoạt.

### Cơ chế Self-Trade Prevention (STP)

Phoenix tích hợp cơ chế STP ngăn chặn tình trạng tự giao dịch với chính mình, bảo vệ trader khỏi các lỗi không mong muốn và đảm bảo tính công bằng trong quá trình khớp lệnh.

### Giao dịch gasless cho retail trader

Phoenix hỗ trợ giao dịch gasless thông qua cơ chế meta-transaction, cho phép người dùng giao dịch mà không cần giữ SOL để trả phí gas. Điều này giúp giảm rào cản gia nhập cho trader mới và cải thiện trải nghiệm người dùng.

## Đội ngũ phát triển

Phoenix được phát triển bởi Ellipsis Labs, một công ty nghiên cứu và phát triển blockchain chuyên về hạ tầng DeFi trên Solana. Đội ngũ bao gồm các kỹ sư có kinh nghiệm từ các công ty công nghệ hàng đầu và các dự án DeFi lớn trong hệ sinh thái Solana.

## Nhà đầu tư và đối tác

Phoenix đã huy động được $21 triệu trong vòng Series A do Electric Capital và Haun Ventures dẫn đầu, với sự tham gia của Wintermute Ventures, GSR, và các nhà đầu tư thiên thần từ cộng đồng Solana.

Dự án cũng đã thiết lập quan hệ đối tác với các giao thức DeFi lớn trên Solana như Jupiter, Drift Protocol, và Kamino Finance để tích hợp thanh khoản và mở rộng hệ sinh thái.

## Tokenomics

**Token:** PHNX
**Tổng cung:** 1,000,000,000 PHNX
**Phân bổ:**
- Community & Ecosystem: 40%
- Team & Advisors: 20% (vesting 4 năm)
- Investors: 18% (vesting 3 năm)
- Treasury: 15%
- Liquidity Mining: 7%

Token PHNX được sử dụng cho governance, staking để nhận phí giao dịch, và các incentive program trong hệ sinh thái Phoenix.

## Tổng kết

Phoenix là một perp DEX fully on-chain trên Solana với kiến trúc matching engine độc đáo, hướng tới mục tiêu mang đến trải nghiệm giao dịch perpetual futures nhanh chóng và hiệu quả vốn cao. Dự án hiện đang trong giai đoạn testnet và dự kiến ra mắt mainnet trong Q2/2026.
```

---

## Terminology Guide

### Crypto-Native Terms (Keep in English)

These terms should NOT be translated to Vietnamese:

**Trading & DeFi:**
- perp DEX (not "sàn giao dịch vĩnh viễn phi tập trung")
- perpetual futures (not "hợp đồng tương lai vĩnh viễn")
- liquidity pool (not "hồ thanh khoản")
- staking (not "đặt cọc")
- yield farming (not "canh tác lợi suất")
- market maker / taker (not "người tạo thị trường / người nhận")
- slippage (not "trượt giá")
- impermanent loss (not "tổn thất tạm thời")
- matching engine (not "động cơ khớp lệnh")

**Blockchain & Infrastructure:**
- smart contract (not "hợp đồng thông minh")
- gas fee → "phí gas" is OK
- mainnet / testnet (not "mạng chính / mạng thử nghiệm")
- layer 1 / layer 2 (not "tầng 1 / tầng 2")
- rollup (not "cuộn")
- bridge → "cầu" is OK

**Tokenomics:**
- tokenomics (not "kinh tế token")
- vesting (not "phân bổ dần")
- airdrop (not "thả rơi")
- governance → "quản trị" is OK
- whitepaper (not "sách trắng")

**Technical:**
- API (not "giao diện lập trình ứng dụng")
- SDK (not "bộ công cụ phát triển phần mềm")
- open-source → "mã nguồn mở" is OK

### Vietnamese Terms (Use These)

**General:**
- dự án (project)
- nền tảng (platform)
- hệ sinh thái (ecosystem)
- cộng đồng (community)
- đội ngũ phát triển (development team)
- nhà đầu tư (investor)
- đối tác (partner)

**Business:**
- huy động vốn (raise capital)
- vòng gọi vốn (funding round)
- định giá (valuation)
- thị trường (market)
- người dùng (user)

**Technical (when appropriate):**
- phi tập trung (decentralized)
- minh bạch (transparent)
- bảo mật (security)
- hiệu quả (efficiency)
- tốc độ (speed)

---

## Formatting Guide

### Bold Usage

Use bold for:
- **Project name** on first mention in each major section
- **Key numbers** (funding amount, token supply, user count)
- **Important terms** on first definition

Example:
```markdown
**Phoenix** là perp DEX được xây dựng hoàn toàn trên blockchain Solana.

Dự án đã huy động được **$21 triệu** trong vòng Series A.

**Token:** PHNX
**Tổng cung:** 1,000,000,000 PHNX
```

### Italic Usage

Use sparingly:
- Technical terms on first use (with brief explanation)

Example:
```markdown
Phoenix sử dụng *Spline liquidity engine* — công nghệ độc quyền cho phép tạo liquidity pool động.
```

### Bullet Points

Use for: lists of features, team members, investors, token allocation, partnerships.

```markdown
**Phân bổ:**
- Community & Ecosystem: 40%
- Team & Advisors: 20%
- Investors: 18%
```

### Numbers

- Large numbers: "$21 triệu" (not "$21 million"), "1 tỷ token" (not "1 billion tokens")
- Percentages: "20%" (not "20 phần trăm")
- Dates: Q2/2026, tháng 4/2026, 15/05/2026
- Use comma for thousands: 1,000,000 (not 1.000.000)

---

## Section Length Guidelines

| Section | Typical Length | Notes |
|---|---|---|
| Title (H1) | 1 line | Under 70 characters |
| "là gì?" | 2-3 sentences | 50-80 words |
| "Điểm nổi bật" | 3-6 subsections | 400-800 words total |
| Each feature (H3) | 1-2 paragraphs | 80-150 words |
| "Sản phẩm chính" | 2-4 subsections | 200-400 words (optional) |
| "Đội ngũ" | 1-2 paragraphs | 50-100 words |
| "Nhà đầu tư" | 1-2 paragraphs | 50-100 words |
| "Tokenomics" | 1 paragraph + list | 100-150 words (optional) |
| "Tổng kết" | 2-3 sentences | 50-80 words |

**Total article length:** 1000-2000 words for Review type

---

## Common Mistakes to Avoid

### Don't Do This

**Hype language:**
```markdown
Phoenix là dự án CÁCH MẠNG sẽ thay đổi hoàn toàn ngành DeFi!
```

**Investment advice:**
```markdown
Đây là cơ hội tuyệt vời để đầu tư vào Phoenix trước khi giá tăng.
```

**Unverified superlatives:**
```markdown
Phoenix là perp DEX nhanh nhất và an toàn nhất trên Solana.
```

**Forced translations:**
```markdown
Phoenix là sàn giao dịch hợp đồng tương lai vĩnh viễn phi tập trung.
```

**Speculation as fact:**
```markdown
Phoenix chắc chắn sẽ trở thành perp DEX hàng đầu trong năm 2026.
```

### Do This Instead

**Neutral description:**
```markdown
Phoenix là perp DEX được xây dựng hoàn toàn trên blockchain Solana.
```

**Factual statement:**
```markdown
Dự án hiện đang trong giai đoạn testnet và dự kiến ra mắt mainnet trong Q2/2026.
```

**Verified claim:**
```markdown
Theo whitepaper, Phoenix sử dụng matching engine kép để tối ưu hiệu quả khớp lệnh.
```

**Neutral closing:**
```markdown
Phoenix hướng tới mục tiêu mang đến trải nghiệm giao dịch perpetual futures hiệu quả trên Solana.
```

---

## Verification Checklist

Before submitting article, verify:

**Content:**
- [ ] Every claim has a source
- [ ] No hype language or superlatives
- [ ] No investment advice
- [ ] Crypto-native terms used correctly
- [ ] Vietnamese grammar correct

**Structure:**
- [ ] Frontmatter complete
- [ ] All required sections present
- [ ] Heading hierarchy correct (H1 → H2 → H3)
- [ ] Length appropriate (1000-2000 words)

**Format:**
- [ ] Bold used correctly
- [ ] Bullet points formatted consistently
- [ ] No markdown images
- [ ] No emoji
- [ ] Numbers formatted correctly

---

**Last updated:** 2026-05-04
