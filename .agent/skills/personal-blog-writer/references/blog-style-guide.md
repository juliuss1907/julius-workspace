# Blog Style Guide — từ bài đã chỉnh sửa

Đây là những quy tắc style rút ra từ việc so sánh bản draft và bản đã chỉnh sửa
trên edgenotes.net. Áp dụng cho mọi bài blog cá nhân (news, essay, opinion).

## Nguyên tắc cốt lõi

Viết như người kể chuyện có chuyên môn, không như người lập báo cáo kỹ thuật.
Coin68 writer gọi đây là "narrative prose over data dumps".

## 1. Đoạn văn liền mạch, ít bullet

- Bullet chỉ dùng khi liệt kê 5+ mục có cấu trúc giống nhau (benchmark, danh sách sản phẩm)
- Mỗi bullet phải là câu hoàn chỉnh, có động từ, không chỉ "Term: số"
- Nếu < 5 mục, viết thành đoạn văn liền mạch với bold cho con số then chốt

**Sai:** `- Terminal-Bench 2.1: 90,6%, vượt Opus-5.0 (89,1%)`
**Đúng:** `**Terminal-Bench 2.1:** Đạt 90,6%, vươn lên vượt qua Opus-5.0 (89,1%).`

## 2. Tiêu đề section mô tả, không chỉ nêu chủ đề

Tiêu đề H2 nên giải thích ý nghĩa, không chỉ đặt tên chủ đề.

**Sai:** `## KV cache: chỉ bằng 1/4 thế hệ trước`
**Đúng:** `## Tối ưu hóa bộ nhớ KV cache là cải tiến trọng tâm`

**Sai:** `## Vượt model Pro, giá rẻ hơn`
**Đúng:** `## Kết quả benchmark: vượt flagship ở mảng agent`

Heading bắt đầu từ `##`; không dùng `#` trong thân bài vì layout đã in tiêu đề thành H1. Bài dài từ 400 từ nên có ít nhất 3 heading để trang hiện mục lục.

## 3. Bold cho số liệu then chốt trong đoạn văn

Số liệu quan trọng nhất trong mỗi đoạn phải được bold, ngay cả khi không có bullet.
Không bold quá 2 cụm trong một đoạn.

**Ví dụ:** "Model đạt mức tối ưu ấn tượng: **chỉ kích hoạt 8 tỷ tham số ở bước xử lý đầu vào** và **16 tỷ tham số khi khởi tạo đầu ra**."

## 4. Mở bài trực tiếp, thêm embed/ảnh ngay sau lead

- Câu đầu tiên nêu thẳng tin: ai làm gì, khi nào
- Câu thứ 2-3 giải thích tại sao tin này quan trọng
- Ngay sau đoạn mở: X embed hoặc ảnh từ nguồn (nếu có)
- Không mở bằng bối cảnh ngành rồi mới dẫn đến tin

## 5. Nhóm benchmark/category thành mục, không liệt kê từng dòng

Khi có nhiều benchmark, nhóm lại theo loại:
- Nhóm chính (liên quan trực tiếp đến tin): 2-3 benchmark chi tiết
- Nhóm khác (khẳng định thêm): gộp chung 1 câu hoặc 1 bullet

**Sai:** Liệt kê 7 bullet riêng lẻ, mỗi cái 1 dòng
**Đúng:** Chi tiết 2-3 benchmark chính, rồi "Các benchmark khác (Codeforces, CyberGym, AutomationBench) cũng ghi nhận vị trí dẫn đầu."

## 6. "So what" dệt vào cuối bài, không tách section riêng

Không tạo section "## Đánh giá" hay "## So what" riêng.
Thay vào đó, tích hợp nhận định vào đoạn cuối của section cuối cùng.

**Sai:**
```
## Đánh giá
V4.1-Flash cho thấy DeepSeek đang đi theo hướng khác...
```

**Đúng:** Cuối section "Triển khai":
> "Nhìn tổng quan, V4.1-Flash cho thấy hướng đi khác biệt của DeepSeek khi không cuốn vào cuộc đua gia tăng tham số..."

## 6b. Dùng "USD" thay cho ký hiệu "$"

Khi nói đến số tiền trong bài tiếng Việt, viết "100 tỷ USD" thay vì "$100 tỷ". Ký hiệu `$` chỉ dùng trong code, bảng, hoặc khi trích dẫn nguyên văn nguồn tiếng Anh.

**Sai:** `$100 tỷ`, `$77.120`, `huy động tới $100 tỷ`
**Đúng:** `100 tỷ USD`, `77.120 USD`, `huy động tới 100 tỷ USD`

## 7. Ngữ pháp Việt trau chuốt

- "chi phí vận hành" thay vì "chi phí tính toán"
- "chứng minh" thay vì "phản ánh" (khi có bằng chứng mạnh)
- "tối ưu hóa và giảm đáng kể" thay vì "giảm mạnh"
- "lượng input lớn" thay vì "nhiều input"
- "vận hành dựa trên kiến trúc" thay vì "dùng kiến trúc"
- Tránh "là việc", "là sự", "điều mà" — đặt động từ ngay sau chủ ngữ

**Sai:** "Điểm mấu chốt là việc bộ nhớ KV cache không tự sinh ra"
**Đúng:** "Điểm mấu chốt: bộ nhớ KV cache không tự sinh ra"

## 8. Thêm context industry/geopolitical khi có liên quan

Bài news không chỉ tường thuật sự kiện mà cần giải thích bối cảnh:
- Tin AI model → thêm context về cuộc đua AI, chiến lược giá
- Tin regulation → thêm context về chính trị, quan hệ quốc tế
- Tin funding → thêm context về thị trường, xu hướng đầu tư

Không cần section riêng — tích hợp tự nhiên vào bài.

## 9. Thêm disclaimer nguồn đúng chỗ

Khi số liệu do hãng tự công bố:
- Ghi rõ "Đây là số liệu DeepSeek tự công bố, chưa có kiểm chứng từ bên thứ ba"
- Đặt ngay sau đoạn trình bày số liệu, không đợi đến cuối bài

Khi benchmark do hãng tự đánh giá:
- "Các benchmark này do DeepSeek tự đánh giá trên framework nội bộ"

## 10. Ngày tháng phải đủ 2 chữ số

Ngày và tháng luôn viết đủ 2 chữ số, kể cả số nhỏ hơn 10.

**Sai:** ngày 7/9, tháng 2/2026, 14/9
**Đúng:** ngày 07/09, tháng 02/2026, 14/09

Áp dụng cho cả ngày tháng trong bài viết (frontmatter `publishedAt` vẫn dùng ISO format YYYY-MM-DD, không受影响).

## 11. Kết bài mở, không đóng

Kết bài bằng câu hỏi hoặc triển vọng, không tóm tắt lại những gì đã nói.

**Sai:** "Tóm lại, V4.1-Flash là model mới với kiến trúc CED, KV cache 1/4..."
**Đúng:** "Điểm cần theo dõi: V4.1-Pro chưa ra mắt, và khi nó xuất hiện, liệu Pro mới có giữ được khoảng cách so với Flash mới hay không."

## 12. Link nội bộ dệt vào câu, không gom cuối bài

Mỗi bài 2 đến 3 link sang bài đã đăng trên blog, gắn vào cụm từ có sẵn trong câu nhắc tới sự kiện hoặc khái niệm đó. Không tạo mục "Đọc thêm" hay "Bài liên quan" ở cuối bài; khung bài liên quan đã có sẵn trên trang. Quy tắc đầy đủ: `references/seo-checklist.md`, mục 5.

**Sai:** `Xem thêm về thỏa thuận trước đó [tại đây](/articles/anthropic-45b-nscale-vera-rubin/).`
**Đúng:** `Đây là thỏa thuận thứ hai, sau [hợp đồng 45 tỷ USD thuê chip Vera Rubin](/articles/anthropic-45b-nscale-vera-rubin/) ký hồi tháng 08.`
