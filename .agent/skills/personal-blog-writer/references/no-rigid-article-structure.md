# Không có khuôn bài bắt buộc — cấu trúc bài do tình huống quyết định

Observed 01/10/2026. Bổ sung cho `references/blog-style-guide.md`.

## Quyết định của Julius

*"Loại bỏ quy định về bài viết model mới đi nhé. Tôi thấy nó không ổn lắm."*

SKILL.md từng bắt buộc một cấu trúc 6 phần cho mọi tin ra mắt model: Giới thiệu /
Điểm nổi bật / Giá API / Hiệu suất / Khả dụng / Kết bài. Mục này đã bị xoá khỏi
SKILL.md.

## Vì sao khuôn cứng có vấn đề

Ba lý do quan sát được từ bài viết lại:

1. **Trùng dạng.** Mọi tin ra mắt model sẽ ra cùng một bố cục, nên người đọc không
   còn cảm giác đang đọc một tin mới.
2. **Mất mạch kể chuyện.** Phần "Điểm nổi bật" và "Khả dụng" là hai danh sách kỹ
   thuật ghép cạnh nhau, không phải một lập luận.
3. **Phần bắt buộc kéo bài lệch.** Bảng giá 6-8 dòng so sánh nhiều hãng bắt buộc
   phải có, kể cả khi bài không cần so sánh giá. Đó là triệu chứng rõ nhất của bài
   liệt kê thay vì bài luận.

## Mặc định khi viết bài

**Dẫn chuyện + 2 đến 3 heading phân tích.** Heading mô tả ý nghĩa, không chỉ đặt
tên chủ đề (rule 2 của style guide). Tin đa tầng dùng được 4 heading.

Chỉ dùng bảng Markdown khi thực sự có dữ liệu so sánh có cấu trúc và người đọc
cần quét nhanh. Ví dụ bài Gemini 4 Argon giữ lại một bảng 3 dòng với chỉ số đo
độc lập từ Artificial Analysis (điểm, hạng, chi phí mỗi tác vụ), vì đó là dữ liệu
ba số so sánh được và là phần mới của bài.

## Khi anh yêu cầu viết lại bài đang theo khuôn cứng

1. Đổi sang dạng dẫn chuyện, bỏ các mục "phần bắt buộc".
2. Đưa chi tiết bắt buộc vào đúng chỗ chúng đáng nằm trong mạch kể chuyện, không
   xoá hẳn. Ở bài Gemini, giá chỉ còn một câu trong mô tả thay vì một bảng 8 dòng.
3. **Tận dụng nguồn mới mà lần trước bài chưa có.** Bài viết lại dài hơn bản cũ
   (1.626 từ so với 1.352) chính vì có dữ liệu đo độc lập của bên thứ ba.
4. Báo cáo rõ đã bỏ gì và thêm gì, không im lặng thay đổi.

Cấu trúc cũ chỉ dùng lại khi Julius chủ động yêu cầu.