# Coin68 Article Structure Reference

> Extracted from reading N1 Chain, Fermah, and Converge published articles (May 2026).
> Use this as the canonical structure template for Coin68 Review dự án articles.

---

## Full Article Structure

### 1. Frontmatter (YAML)

```yaml
---
title: "[Project] là gì? Tìm hiểu về [mô tả ngắn]"
source: "https://coin68.com/[slug]/"
published: YYYY-MM-DD
created: YYYY-MM-DD
description: "[1-2 câu mô tả dự án]"
tags:
  - "[category-1]"
  - "[category-2]"
---
```

### 2. Opening Paragraph (Bold)

- **Bold toàn bộ đoạn mở đầu**
- Cấu trúc: Bối cảnh ngành → dự án xuất hiện giải quyết vấn đề gì → "Hãy cùng Coin68 tìm hiểu về dự án này trong bài viết dưới đây."
- Độ dài: 3-5 câu

### 3. ## [Project] là gì?

- Heading H2: `## [Project] là gì?`
- **Bold** tên dự án ở lần đầu mention
- Định nghĩa + mô tả kiến trúc/cách hoạt động cơ bản
- Có thể kèm bullet points cho các thành phần chính
- Link đến các khái niệm liên quan (nếu có trên coin68.com)

### 4. **Có thể bạn quan tâm:** (Cross-links)

- Section ngắn với 2-3 link đến bài viết liên quan trên Coin68
- Format:
  ```
  **Có thể bạn quan tâm:**
  
  - [Bài viết liên quan 1](https://coin68.com/...)
  - [Bài viết liên quan 2](https://coin68.com/...)
  ```

### 5. Body Sections (linh hoạt theo dự án)

Các section phổ biến (chọn 2-4 section phù hợp nhất với dự án):

- `## Sản phẩm và tính năng chính của [Project]` — nếu dự án có nhiều sản phẩm
- `## Điểm nổi bật của [Project]` — key differentiators
- `## Cơ chế hoạt động` — technical flow
- `## Kiến trúc và bảo mật` — nếu có yếu tố kỹ thuật đặc biệt
- `## [Token] Tokenomics` — nếu có token
- `## Lộ trình phát triển` — nếu có roadmap

Cấu trúc subsection: H3 cho từng sản phẩm/tính năng, H4 nếu cần phân cấp sâu hơn.

### 6. Đội ngũ phát triển

- `## Đội ngũ phát triển`
- Liệt kê founder + key members kèm background
- Nếu không có thông tin: "Thông tin về danh tính cụ thể của đội ngũ sáng lập [Project] hiện vẫn chưa công bố. Coin68 sẽ cập nhật thêm khi có thông báo mới nhất từ phía dự án."

### 7. Nhà đầu tư

- `## Nhà đầu tư`
- Liệt kê các vòng gọi vốn, quỹ tham gia, số tiền
- Nếu không có: "Hiện tại, [Project] chưa công bố thông tin chính thức về các vòng gọi vốn. Coin68 sẽ cập nhật thêm khi có thông báo mới nhất từ phía dự án."

### 8. Tổng kết

- `## Tổng kết`
- Tóm tắt 2-3 câu về dự án
- Công thức: "Trên đây là toàn bộ thông tin về dự án [Project], Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!"

### 9. Disclaimer

```
> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.
```

### 10. 🔍 Kiểm chứng thông tin (NỘI BỘ)

Block nội bộ cuối bài, track trạng thái xác minh:

```markdown
## 🔍 Kiểm chứng thông tin (NỘI BỘ)

| Mục | Trạng thái | Ghi chú |
|-----|-----------|--------|
| [Claim cần verify] | ✅/⚠️/❌ | [Nguồn hoặc lý do] |
```

Trạng thái:
- ✅ Đã xác minh — có nguồn cụ thể
- ⚠️ Cần cập nhật / xác minh lại — có nguồn nhưng có thể đã cũ
- ❌ Chưa có — cần Julius bổ sung

---

## Style Patterns Observed

### Language
- Vietnamese, formal but accessible
- Crypto terms giữ nguyên tiếng Anh: `staking`, `liquidity pool`, `smart contract`, `oracle`, `bridge`, `layer-1`, `validator`
- Không dịch ép: không dùng "chuỗi khối" cho blockchain, "hợp đồng thông minh" cho smart contract

### Formatting
- **Bold**: Tên dự án (first mention), số liệu quan trọng ($100M, 100.000 TPS), key terms
- `code`: không dùng trong bài (chỉ trong frontmatter)
- Lists: bullet points cho danh sách, numbered list cho steps
- No emoji trong body chính

### Image references
- Giữ nguyên reference từ published article: `![](https://cdn.coin68.com/images/...)`
- KHÔNG tự generate hoặc insert image mới
- Julius xử lý toàn bộ image sau khi có draft
