# The Defiant: các đường đọc đã hỏng, và cách thay thế đã kiểm chứng

**Quan sát 2026-10-02. Ghi đè phần "đường đúng" trong
`defiant-js-body-workaround.md` và `the-defiant-full-text-recovery.md`,
vì hai file đó đang mô tả trạng thái cũ.**

Hai tài liệu cũ khuyên dùng `curl https://thedefiant.io/rss` (cho toàn văn) và
`curl r.jina.ai/<url>`. **Cả hai đều không còn chạy.**

| Đường đọc | Tài liệu cũ nói | Thực tế 2026-10-02 |
|---|---|---|
| `thedefiant.io/rss` | "ra toàn văn, 100 item" | **HTTP 403** (Cloudflare) |
| `thedefiant.io/news/rss` | chưa thử | **HTTP 403** |
| `r.jina.ai/<url>` | "trả Markdown sạch" | **Lỗi `document_antibot`** |
| `thedefiant.io/news/feed` | chưa thử | **HTTP 200, 147 KB, nhưng body rỗng** |

Mâu thuẫn nội bộ đáng chú ý: `news/feed` và `/feed` trả **cùng nội dung** (200),
còn `/rss` và `/news/rss` trả 403. Nhà xuất bản đã đổi đường dẫn, đường `/rss`
cũ không còn được phục vụ.

## `news/feed` trả 200 nhưng KHÔNG dùng được làm nguồn nội dung

Feed vẫn có 100 item với `<title>`, `<link>`, `<pubDate>` đầy đủ, nhưng:

- `<description>` **rỗng** (độ dài 0).
- `<content:encoded>` chỉ chứa 38 ký tự: `Read the full story at The Defiant`.

Kiểm tra trước khi bóc, để khỏi tốn lượt gọi:

```bash
curl -sL --max-time 40 "https://thedefiant.io/news/feed" \
  | grep -o "Read the full story at The Defiant" | head -1
```

Chỉ dùng `news/feed` để **xác nhận tiêu đề và ngày đăng**, không dùng làm nguồn
nội dung.

## Đường thay thế đã kiểm chứng (dùng ngay)

Khi `web_extract` trả `Loading this article…`, `web_search` bằng **tiêu đề đầy
đủ** rồi đọc nguồn xuất hiện trong kết quả. Bảng này đã dùng thật trong phiên
ghi:

| Nhu cầu | Nguồn dùng được | Ghi chú |
|---|---|---|
| Tin Blockchains (EIP-8363) | `cryptonews.net/news/ethereum/<id>` | Đăng lại **nguyên văn** The Defiant, giữ cả số liệu chi tiết |
| Nghiên cứu SF Fed (mục Converge) | PDF gốc `frbsf.org/wp-content/uploads/el2026-26.pdf` | Nguồn gốc, tốt hơn bản tóm tắt |
| Xác nhận chéo tình tiết | `techcrunch.com`, `qz.com`, `siliconangle.com` | Tất cả đều dẫn lại WSJ, đọc được toàn văn |

`cryptonews.net` đặc biệt đáng dùng cho mục Blockchains: bài đăng lại giữ nguyên
cấu trúc, số liệu và trích dẫn của bài gốc, bao gồm cả phần lịch sử tranh luận.

## Trong bài viết, luôn tách bạch "nguồn bị chặn"

Nguồn đọc được qua đường thay thế vẫn phải được nói rõ. Trong reply và trong
bài:

- Đưa **URL bài gốc** vào `sources:` (người đọc cần tới được trang bài), không
  đưa URL feed hay URL syndication.
- Nói thẳng nguồn nào đã đọc thật và vì sao phải dùng đường thay thế.

## Đường đã thử và hỏng (không lặp lại)

- `curl` UA trình duyệt + regex `<p>`: chỉ bắt khối CSS của Tailwind.
- `curl` tải file + parse Next.js payload: không có body dạng portable text.
- Sanity CDN `6oftkxoa.api.sanity.io` (project id lấy từ URL ảnh
  `cdn.sanity.io/images/6oftkxoa/production/...`): `*[_type=="article"]` trả
  `result: []`. Dataset không public cho query tự do.
- `browser_exec` + `new_tab` + `js()` trong phiên cron: CLI in khối usage ra
  stdout, exit 0. Đây là giới hạn môi trường cron, không phải kết luận về
  công cụ; trong phiên tương tác với người dùng nên thử lại.

## Bài học bền hơn danh sách kỹ thuật

Workaround của một nhà xuất bản **thay đổi theo thời gian**. Hai tài liệu này
từng đúng và nay đã hỏng chỉ vì vài tuần trôi qua.

Quy trình bền vững, theo thứ tự:

1. Nhận diện triệu chứng (`Loading this article…`).
2. **Đọc reference trước khi thử kỹ thuật mới** — nhưng kiểm tra ngay xem mô tả
   trong reference còn khớp với ngày tháng không.
3. Tìm **nguồn gốc hoặc nguồn đăng lại toàn văn** qua `web_search`.
4. Chỉ dùng đường kỹ thuật (RSS, reader proxy) làm phương án dự phòng.

Đừng lặp lại một danh sách kỹ thuật cũ một cách máy móc rồi kết luận nguồn đó
"không đọc được". Cách đúng là chuyển sang nguồn khác và nói rõ đã làm vậy.