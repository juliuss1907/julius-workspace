# SKILL — Coin68 Source Researcher

**Agent:** Hermes (local)
**Purpose:** Gap-driven source collection & verification for Coin68 articles
**Version:** 1.0
**Last updated:** 2026-05-26

---

## Role

Thu thập, xác minh, và cấu trúc hóa nguồn thông tin cho Coin68 articles. Skill này chạy **trước** seo-optimizer và content-writer.

**Core principle: Gap-driven research.**
Đọc nguồn gốc trước → phát hiện section nào thiếu info → chỉ tìm thêm targeted cho phần thiếu. Không search blind.

---

## When to Use

Load this skill when:
- Bắt đầu viết bất kỳ Coin68 article nào (Review, News, Deep-dive)
- Julius yêu cầu research project mới
- Pipeline scheduler trigger research phase từ Google Sheets queue

Do NOT use for:
- X content, Substack content
- Khi Julius đã cung cấp đầy đủ tất cả thông tin (skip to content-writer)

---

## Pipeline Position

```
source-researcher → seo-optimizer → content-writer → seo-audit
(Research Dossier)   (SEO Brief)     (Article Draft)   (Audit Report)
```

---

## Input

### Required
- Project name
- Source URLs (từ Julius / Google Sheets — docs, blog, website)

### Optional
- Category (nếu Julius đã xác định)
- Project description (1-2 sentences)

---

## Phase 0: Xác định category & đọc reference

Trước khi đọc bất kỳ nguồn nào, xác định context của bài viết.

### Step 0.1: Đọc published.md → match category

Đọc `working/Coin68/contents/published/published.md` và match project với category gần nhất.

Nếu không có category phù hợp:
- KHÔNG tự thêm tag mới vào published.md
- Ghi nhận trong dossier: "Category chưa xác định, cần Julius confirm"
- Có thể tiếp tục research nhưng flag trong Escalation Items

### Step 0.2: Đọc 2-3 bài published cùng category

Đọc 2-3 bài trong `working/Coin68/contents/published/` cùng category tag.

**Extract 3 thứ từ reference articles:**

| Extract | Dùng cho |
|---------|----------|
| Cấu trúc section (H2/H3 nào xuất hiện) | Xác định sections nào sẽ có trong bài mới |
| Cách mở đầu + kết thúc | Đồng nhất giọng văn với category |
| Cách dùng thuật ngữ (dịch hay giữ nguyên) | Nhất quán terminology |

### Step 0.3: Escalation nếu cần

Escalate khi:
- Không có category phù hợp trong published.md
- Có ít hơn 2 bài reference trong cùng category

---

## Phase 1: Đọc nguồn gốc (do Julius cung cấp)

Luôn đọc **TOÀN BỘ** nguồn gốc trước khi làm gì khác. Đây là tầng 1 — nguồn đáng tin cậy nhất.

### Step 1.1: Docs / Gitbook

- **Tool:** web_extract (thử trước) → browser_navigate (nếu web_extract fail do dynamic content)
- **Tìm:** Kiến trúc kỹ thuật, cơ chế hoạt động, tokenomics, roadmap
- **Note:** URL + date accessed

### Step 1.2: Blog chính thức

- **Tool:** web_extract
- **Tìm:** Funding announcement, team story, problem statement, key quotes
- **Note:** URL + date accessed

### Step 1.3: Website landing page

- **Tool:** web_extract (thử trước) → browser_navigate (nếu fail)
- **Tìm:** Positioning, key metrics (AUM, users, nodes), USP
- **Note:** URL + date accessed

### Step 1.4: Project type check

Sau khi đọc xong nguồn gốc, xác định project type. Điều này quyết định sections nào sẽ có trong bài:

| Check | Nếu có | Ảnh hưởng |
|-------|--------|-----------|
| Có token? | → Thêm section Tokenomics | Cần tìm token supply, allocation, utility |
| Được incubate? | → Check parent company | Founder background từ parent company page |
| Foundation hay company? | → Phân biệt entity | Ảnh hưởng cách viết section Đội ngũ |
| Pre-mainnet? | → Nhấn mạnh testnet | Dùng roadmap data thay vì production metrics |

---

## Phase 2: Map gaps

Sau khi đọc xong tất cả nguồn gốc, kiểm tra từng section của bài:

| Section | Đủ info? | Nếu thiếu → |
|---------|----------|-------------|
| "[Project] là gì?" | ✅/⚠️ | Thường đủ từ Phase 1 |
| "Điểm nổi bật" | ✅/⚠️ | Thường đủ từ docs |
| "Sản phẩm chính" | ✅/⚠️/N/A | Chỉ khi project có nhiều products |
| "Đội ngũ phát triển" | ✅/⚠️ | → Phase 3.1 (founder search) |
| "Nhà đầu tư" | ✅/⚠️ | → Phase 3.2 + 3.3 (báo + crypto-fundraising) |
| "Tokenomics" | ✅/⚠️/N/A | Chỉ nếu có token (từ Phase 1.4) |
| "Cross-links" | ⚠️ | → Phase 3.4 (site:coin68.com) |

**CHỈ chuyển sang Phase 3 cho sections còn thiếu.**
Nếu tất cả sections đủ info → skip Phase 3, đi thẳng Phase 4.

---

## Phase 3: Research chủ động (agent tự tìm thêm)

**CHỈ tìm thêm cho sections còn thiếu từ Phase 2. Không search blind.**

### 3.1 Founder background → cho section "Đội ngũ"

Docs / blog thường chỉ có tên founder, không có background chi tiết.

#### 3.1a Thử internal sources trước

- `<project-url>/team/`
- `<project-url>/about/`
- Nếu dự án được incubate: `<parent-company-url>/company` hoặc `/team`
- **Tool:** web_extract

Nếu tìm thấy đủ info → dừng, không search external.

#### 3.1b Nếu internal không có → search external

- **Search pattern:** `"[Founder name]" + "background"` / `"LinkedIn"` / `"speaker"`
- **Tool:** web_extract (speaker profiles, company pages)
- Nếu có LinkedIn MCP tool (agent-reach) → dùng để cross-check
- **Cross-check:** đọc lại docs/website để confirm background claims

### 3.2 Bài báo lớn → cross-check funding + narrative

Sau khi biết số tiền từ blog chính thức, tìm thêm bài từ nguồn uy tín.

- **Search pattern:** `"[Project name]" + "funding"` + `"CoinDesk"` / `"The Block"` / `"Fortune"`
- **Tool:** web_extract
- **Mục đích:**
  - Context thị trường, competitor landscape
  - Chi tiết mà blog chưa rõ (lead investor, co-leads, valuation)
  - Narrative rộng hơn (tại sao dự án này quan trọng)
- **GIỚI HẠN: Tối đa 1-2 bài.** Đọc quá nhiều bài dễ loãng, sao chép giọng văn nguồn khác.

### 3.3 crypto-fundraising.info → confirm round details

- **URL pattern:** `https://crypto-fundraising.info/projects/<slug>/`
- **Tool:** web_extract hoặc browser_navigate
- **Tìm:**
  - Tổng số vốn huy động (có thể có nhiều vòng mà blog chỉ nhắc vòng gần nhất)
  - Phân biệt lead investor vs participants (blog thường gom hết vào 1 câu)
  - Cross-check số tiền giữa các nguồn
- **Nếu project không có trên crypto-fundraising.info:**
  - Ghi nhận trong dossier: "Không có trên crypto-fundraising.info"
  - Dùng blog + bài báo làm nguồn chính cho funding info

### 3.4 Search bài Coin68 liên quan → cross-links

- **Search pattern:** `site:coin68.com [từ khóa liên quan]`
- **Tool:** web_search (`site:coin68.com [từ khóa liên quan]`)
- **Tìm:** 2-3 bài published liên quan cho "Có thể bạn quan tâm" section
- **Chọn bài:**
  - Cùng category (e.g., cùng #stablecoin, #perp-dex)
  - Cùng ecosystem/blockchain
  - Related concept (e.g., bài về protocol mà project integrate với)
- **Nếu không tìm thấy:**
  - Ghi nhận trong dossier: "Không tìm thấy bài Coin68 liên quan"
  - Content-writer sẽ để placeholder hoặc bỏ section cross-links

---

## Phase 4: Verification

Per data point trong dossier, assign status:

| Status | Ý nghĩa | Khi nào dùng |
|--------|---------|--------------|
| ✅ Đã xác minh | Có nguồn chính thức (docs / blog / site của dự án) | Claim có trong official source |
| ⚠️ Cần cập nhật | Có nguồn nhưng có thể đã cũ / cần update | Source cũ, số liệu có thể thay đổi |
| ❌ Chưa có nguồn | Không tìm thấy nguồn nào | Cần Julius bổ sung |

### Red flags → auto-escalate

- Team members không có online presence nào
- Investors không confirmed trên official sites của chính investor
- Tokenomics numbers mâu thuẫn giữa sources
- Project category không rõ ràng (không match published.md)

### Xử lý nguồn mâu thuẫn

Khi 2 nguồn không đồng nhất:

| Tình huống | Cách xử lý |
|------------|------------|
| Docs ≠ Bài báo | Ưu tiên docs (nguồn chính thức của dự án) |
| Blog ≠ Landing page | Ưu tiên blog (thường cập nhật hơn landing page) |
| Docs cũ ≠ Blog mới | Ưu tiên blog mới (ghi chú docs cần update) |
| Cả 2 không rõ ràng | Ghi ⚠️ trong dossier, escalate cho Julius |

**Thứ tự ưu tiên nguồn:** Official docs/blog > Bài báo uy tín (CoinDesk, The Block) > Secondary source (crypto-fundraising.info, CoinGecko)

---

## Phase 5: Output Research Dossier

### Primary output: In-memory

Pass trực tiếp cho content-writer và seo-optimizer trong cùng session.

### Optional output: File-based

Ghi ra file khi agents chạy độc lập (cron, subagent, batch processing):

**Location:** `working/Coin68/contents/research/<project-slug>-dossier.md`

### Dossier format

```markdown
## Research Dossier: [Project Name]

**Date:** YYYY-MM-DD
**Category:** [tag from published.md]
**Project type:** [company / foundation / incubated by X]
**Has token:** yes / no
**Stage:** [mainnet / testnet / pre-launch]
**Sources accessed:** [count]

### Project Overview
- **Name:** [name]
- **Category:** [category]
- **Blockchain:** [chain]
- **Type:** [incubated foundation / company / DAO]
- **Description:** [1-2 sentences from official sources]

### Key Metrics

| Metric | Value | Source | Status |
|--------|-------|--------|--------|
| Total Raised | $X | Blog + crypto-fundraising.info | ✅ |
| Users / TVL | X | Landing page | ✅ |
| Token Supply | N/A | — | N/A (no token) |

### Verification Table

| Claim | Status | Source | Notes |
|-------|--------|--------|-------|
| [claim 1] | ✅/⚠️/❌ | [URL] | [details] |
| [claim 2] | ✅/⚠️/❌ | [URL] | [details] |

### Sources Used

| # | Type | URL | Date Accessed |
|---|------|-----|---------------|
| 1 | Docs | [url] | YYYY-MM-DD |
| 2 | Blog | [url] | YYYY-MM-DD |
| 3 | Landing | [url] | YYYY-MM-DD |
| 4 | CoinDesk | [url] | YYYY-MM-DD |
| 5 | crypto-fundraising.info | [url] | YYYY-MM-DD |

### Cross-Links Found

- [Article title](https://coin68.com/...) — [relevance note]
- [Article title](https://coin68.com/...) — [relevance note]
- (hoặc: "Không tìm thấy bài Coin68 liên quan")

### Reference Articles Read (Phase 0)

- [article-slug.md] — cùng category [tag], extract: [structure/voice/terminology notes]
- [article-slug.md] — cùng category [tag]

### Gaps

- [Section / info still missing after all research]
- [Questions that need Julius's input]

### Escalation Items

- [Issues requiring Julius's attention — contradictions, missing sources, unclear category]
```

---

## Ranh giới — KHÔNG làm

| Hành vi | Lý do |
|---------|-------|
| Đọc quá nhiều bài báo (5+) | Dễ loãng, sao chép giọng văn nguồn khác |
| Search giá token / CMC | Coin68 không làm price prediction, dễ thành financial advice |
| Đọc Reddit / Discord | Không phải nguồn chính thức, risk thông tin sai |
| Generate ảnh | Julius tự làm |
| Tự thêm category tag mới | Escalate cho Julius quyết định |

---

## Escalation

Escalate to `tasks/inbox/escalation-*.md` when:

- Project category không match published.md (cần tag mới)
- Nguồn gốc (docs/blog/site) không accessible (URL lỗi, restricted)
- Team / investor claims không thể verify từ bất kỳ nguồn nào
- Tokenomics data mâu thuẫn giữa sources và không thể xác định đâu là đúng
- Project có ít hơn 2 reference articles cùng category trong published/
- Phát hiện project có vấn đề (hack, controversy, regulatory) cần Julius đánh giá

---

## Related Skills

This skill produces input for:
- **seo-optimizer/** — Reads Dossier for keyword extraction, competitor analysis
- **content-writer/** — Reads Dossier for article content, verification block

---

## References

- `working/Coin68/AGENTS.md` — Domain-specific rules, verification block requirement
- `working/Coin68/contents/published/published.md` — Category index
- `ai-labs/pipelines/coin68-pipeline/idea.md` — Pipeline architecture
- agent-reach skill — Tools: web_extract, LinkedIn (optional)

---

**Maintainer:** Julius
**Last updated:** 2026-05-26
