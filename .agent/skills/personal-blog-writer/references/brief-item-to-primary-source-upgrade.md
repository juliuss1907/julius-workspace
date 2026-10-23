# Nâng brief item thành bài sâu: đi tìm nguồn gốc

Quan sát 2026-10-03. Bổ sung cho `references/news-post-depth.md` (viết sâu) và
`references/source-discovery-and-verification.md` (săn nguồn).

Brief là **bản tóm tắt**, không phải nguồn. Một item có 2–3 bullet trong brief
thường đủ để dựng bài 400 từ, nhưng không đủ cho bài 700–900 từ mà Julius
muốn. Phần chênh lệch nằm ở chi tiết cơ chế, số liệu gốc và tên riêng.

## Bốn đích nguồn gốc, theo thứ tự ưu tiên

1. **Trang công bố chính thức của bên sự kiện.**
   Ví dụ tin đào tạo của Anthropic: bài của hãng có cơ chế 4 bước, tên huy hiệu,
   khối lượng chứng chỉ nền tảng, đối tượng và điều kiện tiêu chuẩn. Không có
   gì trong báo chí bản tin. Ưu tiên tên miền gốc trong `sources:`, tạm dừng làm
   bản tin trung gian.

2. **Bài đăng X của chính bên đó.**
   Khi dự án tự thông báo (Blast, Coinbase, một L2...), đọc nguyên văn qua
   `curl -sL https://api.fxtwitter.com/status/<id>` rồi lấy `tweet.text`.
   Nội dung thường dài hơn tiêu đề bài báo, và có mốc thời gian cụ thể
   (ngày giờ, hạn chót) mà bài báo thường bỏ sót. `curl | python3` bị security
   scan gắn cờ, nhưng vẫn được auto-approve, nên cứ gọi bình thường.

3. **Văn bản gốc của cơ quan nhà nước.**
   Tin chính sách thì đọc luôn văn bản gốc (`whitehouse.gov`, `sec.gov`,
   `imf.org`), không dừng ở bản tường thuật. Ở phiên 2026-10-03, đọc Executive
   Order 14434 cho thấy "SI" chỉ là **thuật ngữ hành pháp trong nhánh hành pháp**,
   định nghĩa liên bang chưa có và phải trình dự thảo trong 60 ngày. Chi tiết này
   đổi hẳn ý nghĩa của tin so với cách viết theo tiêu đề.

4. **Bài gốc của hãng an ninh/nghiên cứu.**
   Khi blog tổng hợp tóm tắt báo cáo của hãng khác, đi tìm bài gốc. Ở phiên này
   bản tóm tắt có đủ ý, nhưng bài gốc của Help Net Security có cả cơ chế kỹ
   thuật (công cụ browser-in-browser, chuyển tiếp credential tới máy chủ thật,
   tên miền giả danh từng tổ chức) mà bản tóm tắt bỏ hết.

## Khi trang bị chặn hoặc render bằng JavaScript

`web_extract` trả về vỏ trang rỗng với hai kiểu: SPA render client-side
(The Defiant) và antibot (`document_antibot`, ví dụ một số trang CoinDesk).
Cả hai đều gọi được qua proxy dịch:

```bash
curl -sL --max-time 70 "https://r.jina.ai/https://<url>" -o /tmp/out.md
```

RSS `<content:encoded>` của nhà xuất bản chỉ cho excerpt 200–300 ký tự, đủ để
định danh bài nhưng không đủ để viết. Kiểm tra bằng `content:encoded` trước khi
kết luận là hết cách.

## Khi KHÔNG tìm được nguồn gốc: viết ngắn và nói thẳng

Không phải tin nào cũng có nguồn gốc đọc được. Ví dụ tin "SEC duyệt ETP đòn bẩy
3x" chỉ đến từ tweet của một chuyên gia phân tích về tài liệu cơ quan quản lý.
Khi đó:

- **Viết ngắn hơn thay vì bịa chi tiết** (489 từ so với 750–870 từ của các bài
  cùng đợt). Nói rõ trong bài rằng đây là phát biểu của bên thứ ba, chưa có
  xác nhận từ cơ quan chứng năng.
- **Dựng hẳn một phần về mức độ chắc chắn** thay vì giấu nhẹm. Bài đó có section
  riêng giải thích vì sao "tài liệu được chia sẻ" khác "thông báo chính thức",
  và kết bằng câu nói rõ bài đang ở mức nào.
- **Nêu điều kiện để viết lại**: đọc được thông báo chính thức thì viết lại ở
  mức tương đương các bài khác. Đưa điều này vào reply, đừng tự hứa.

Câu hỏi tự kiểm trước khi viết: *con số này tôi đọc ở đâu, hay tôi đang suy ra
từ bối cảnh?* Con số suy ra thì không viết, hoặc viết kèm nhãn suy đoán.

## Hai hosting lưu lượng có số liệu mâu thuẫn: đưa cả hai vào

Bài .si có Hostinger nói tên miền .si là phần mở rộng phổ biến thứ hai của họ,
còn Wix nói không thấy tăng "có ý nghĩa". Không chọn bừa một bên. Đưa cả hai vào
bài và nói thẳng số liệu phụ thuộc nền tảng nào đo. Một chi tiết như vậy làm bài
đáng tin hơn hẳn so với chỉ dẫn con số dễ nghe nhất.