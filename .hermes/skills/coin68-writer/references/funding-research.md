# Funding Research for Coin68 Articles

> How to gather detailed round-by-round funding data for Coin68 project review articles.

---

## Primary Source: crypto-fundraising.info

**URL format**: `https://crypto-fundraising.info/projects/<project-slug>/`

**What it provides**:
- Total raised amount
- Round-by-round breakdown: date, amount, round type, lead investors, participating investors
- Links to source articles (Fortune, The Block, X/Twitter announcements)

**How to extract**:
```python
# Use web_extract for reliable content extraction
web_extract(["https://crypto-fundraising.info/projects/variational/"])
```

**Output example**:
```
Total raised: $61.80M

Raised May 2026 — $50M — Series A
  Lead: Dragonfly Capital
  Investors: Bain Capital Crypto, Coinbase Ventures

Raised Jun 2025 — $1.50M — Strategic
  Investors: Mirana Ventures, Caladan, Zoku Ventures

Raised Oct 2024 — $10.30M — Seed
  Lead: Bain Capital Crypto, Peak XV Partners
  Investors: Coinbase Ventures, Dragonfly Capital, Hack VC, North Island Ventures
```

---

## Secondary Sources

### Web search for funding announcements
```python
web_search("Variational funding round 2025 2026 Dragonfly Coinbase amount")
```

### Fortune / The Block / CryptoBriefing
Major funding rounds are covered by:
- fortune.com (Series A and above)
- theblock.co (seed, Series A)
- cryptobriefing.com (all stages)

### X/Twitter project announcements
Check the project's official X account for funding thread announcements.

---

## Integration with Coin68 Article

### In the article body
Use H3 subsections for each round, sorted newest-first:
```markdown
### Vòng Series A (Tháng 5/2026) - $50 triệu USD
**Lead investor:** Dragonfly Capital
**Các nhà đầu tư tham gia:** Bain Capital Crypto, Coinbase Ventures, Peak XV Partners
**Mục đích:** Mở rộng infrastructure, phát triển thị trường RWA

Đây là vòng gọi vốn lớn nhất của dự án...
```

### Hyperlink to related Coin68 articles
When Coin68 has covered the funding round:
```markdown
Thông tin chi tiết về vòng gọi vốn này đã được Coin68 đưa tin tại [bài viết này](https://coin68.com/variational-huy-dong-50-trieu-usd-de-dua-thanh-khoan-pho-wall-len-blockchain/).
```

### In kiểm chứng block
```markdown
| Tổng vốn huy động $61.8M | ✅ | crypto-fundraising.info |
| Vòng Series A $50M | ✅ | crypto-fundraising.info + Fortune |
| Vòng Seed $10.3M | ✅ | crypto-fundraising.info |
```

---

## Pitfalls

- **Not all projects are listed**: New/pre-launch projects may not appear on crypto-fundraising.info. Fall back to web_search + X announcements.
- **Amounts may be approximate**: Cross-reference with official sources when available.
- **Round types vary**: "Strategic", "Private", "Pre-seed" — use the exact label from the source, don't invent round names.
- **Investor names differ across sources**: Use the name as it appears on the investor's official site.
