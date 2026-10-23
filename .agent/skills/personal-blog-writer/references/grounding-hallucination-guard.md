# Grounding guard: memory không phải nguồn

Session 2026-09-30. Đọc cùng `references/source-discovery-and-verification.md`.

## Failure mode

Bạn nhớ một chi tiết từ session trước, memory note, hoặc OpenViking context,
viết nó vào bài một cách tự nhiên. Bài vẫn PASS validator, build, push. **Không
công cụ nào bắt được** — validator chỉ check style, không check grounding.

Đây là loại lỗi nguy hiểm nhất của dạng task này vì nó im lặng.

## Observed

Bài "OpenAI gom 30 tỷ USD ở định giá 1,4 nghìn tỷ USD" (30/09/2026):

| Chi tiết viết vào | Nguồn đã đọc (TechCrunch, WuBlockchain) |
|---|---|
| Goldman Sachs dẫn dắt vòng mới | KHÔNG có |
| Vụ kiện bản quyền với New York Times | KHÔNG có |

Cả hai đến từ context trong phiên chat (nhắc tới các bài blog cũ về OpenAI), không
phải từ nguồn. Phát hiện khi grep lại nội dung, đã xoá trước khi validate.

## Quy tắc

**Mỗi khẳng định trong bài phải truy được về một URL trong `sources:`.**

Trước khi validate, đọc lại bài một lượt và hỏi đúng một câu cho từng chi tiết:
"câu này nằm ở trang nào?" Không trả lời được = cắt hoặc bỏ.

Đặc biệt nguy hiểm với các loại sau, vì chúng nghe hợp lý nên rất dễ lọt:

- số tiền, số %, số vụ kiện
- tên người dẫn dắt, tên nhà đầu tư
- ngày tháng cụ thể
- số liệu lấy từ bài cũ đã đăng cùng chủ đề

Nếu cần một chi tiết mà nguồn không có: `web_search` để lấy nguồn thật, hoặc
không viết. Đừng bịa để lấp chỗ trống.

## Đối chiếu số liệu

Khi hai nguồn cho hai con số khác nhau: giữ số của từng nguồn và nói rõ trong
bài, đừng chọn một rồi bỏ nguồn còn lại. Và đừng lấy con số thứ ba từ trí nhớ
để "hòa giải" — đó là cùng lỗi grounding ở dạng khó phát hiện hơn.

## Nguồn do user paste vào chat

Ở session 30/09, Julius paste nguyên văn bài Reuters (kèm frontmatter `source:`
và `published:`) trực tiếp trong chat, lưu thành file markdown trong `~/Downloads/`.
Đây là nguồn tốt nhất có thể có khi reuters.com bị chặn antibot: đọc file đó, đưa
URL syndication (Yahoo Finance) vào `sources:` cho người đọc tự tra, và nói rõ
bản đọc là bản Reuters user cung cấp. Đừng cố mở lại reuters.com.

## Báo cáo khi đã sửa

Khi phát hiện và gỡ một chi tiết không có nguồn, nói thẳng trong reply:
"bài #N tôi đã sửa, ban đầu tôi viết kèm X và Y vì có trong context, kiểm tra
lại thì không nguồn nào có, đã xoá." Không im lặng sửa rồi báo cáo bình thường —
Julius cần biết để tin bài còn lại.
