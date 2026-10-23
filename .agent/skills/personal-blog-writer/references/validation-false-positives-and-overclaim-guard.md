# Bộ đếm validation báo sai, và chống suy diễn quá nguồn

Bổ sung cho `references/content-validation.md`. Ghi lại từ phiên 2026-09-29.

## 1. Bộ đếm báo sai trên cách viết tiếng Việt đúng

Ba mẫu đã gặp. Cả ba là false positive, KHÔNG phải lỗi bài.

| Mẫu | Nguyên nhân | Cách xử lý |
|---|---|---|
| `oxford_count > 2` | Dấu phẩy nối hai mệnh đề (`A, và B`) bị đếm như Oxford comma trong danh sách | In tất cả dòng khớp trong một lần, đọc một mạch. Chỉ sửa khi có đúng một danh sách A, B, và C nối tiếp |
| `missing-space` | Dấu phẩy ngay sau URL trong markdown link | Strip link trước khi check: `re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', body)` |
| `english density` | Từ tiếng Anh trong tên riêng viết thường (slug trong URL) | Bỏ qua qua |

**Nguyên tắc:** đọc context rồi bỏ qua. Đừng sửa prose vốn đúng chỉ để làm im bộ đếm. Sửa vô tội vạ tốn vòng patch và dễ sinh lỗi chính tả mới. Phát hiện 2026-09-29: sau khi sửa 8 dòng Oxford comma trong 3 bài, cả 3 bài vẫn là cách viết đúng và vẫn FAIL.

Script dùng nhanh để soi mọi check có nhiều dòng:

```bash
python3 - <<'PY'
import re
p = "<file.md>"
for i,l in enumerate(open(p).read().splitlines(),1):
    for m in re.finditer(r'.{0,60},\s*(và|and)\s.{0,40}',l,re.I):
        print(f'L{i}: ...{m.group(0)}...')
PY
```

## 2. Chống suy diễn quá mức từ nguồn (quan trọng hơn lỗi bộ đếm)

Sourced từ một lần viết bài ở session 2026-09-29. Bản nháp đầu khẳng định
Pichai và Huang "đồng tình lời kêu gọi giảm tốc" chỉ vì câu của CNBC là
"lãnh đạo ngành như Altman và Musk đồng tình". Câu đó **không** nói về Pichai
hay Huang. Suy diễn đó phải bị bỏ khỏi bản viết lại.

Checklist trước khi commit, mỗi khẳng định về một cá nhân:

1. Câu nguồn có **chủ ngữ đúng người đó** không? "Các lãnh đạo ngành đã đồng
   tình" không phải bằng chứng về một cá nhân cụ thể.
2. Đây là số liệu do công ty tự công bố hay đã kiểm chứng độc lập? Nếu tự công
   bố, ghi rõ ngay sau đoạn đó.
3. Chi tiết có suy ra từ *bối cảnh* không (từ tên người tham dự, từ tiền lệ
   chính trị)? Nếu suy ra, đổi sang câu mô tả quan sát được thay vì gán ý kiến.

Khi phát hiện đã viết sai, viết lại file bằng slug mới, đừng sửa chồng lên bản
cũ rồi xóa. Bản chết phải đi qua delete request (AGENTS.md mục 8, cấm xóa file
kể cả file agent tự tạo), tốn thêm một vòng chờ duyệt từ Julius.

## 3. Viết đoạn kết theo yêu cầu mà chưa sửa file

Khi Julius yêu cầu "tôi cần 1 đoạn kết… không cần sửa trong bài, chỉ cần ghi ra
đây thôi", hoặc muốn đổi giọng đoạn kết ("chất vấn hơn"), thì:

- Viết trong chat, **không patch file**.
- Cho hai bản (đầy đủ và rút gọn) để anh chọn nhanh.
- Đề nghị patch + validation + push ở cuối reply, nhưng chờ anh nói "làm đi".

Giọng "chất vấn" anh thích: đặt câu hỏi ngay sau khi dẫn hai sự kiện đối lập
(lời kêu gọi giảm tốc ↔ nhịp phát hành dày), rồi tự dặt ranh giới bằng câu
"đây vẫn là cách tôi hiểu từ tài liệu công bố, chưa phải kết luận về động cơ".
Không kết bằng "So what" section riêng.
