# Bản archive ở working/ KHÔNG được validator kiểm tra

Session 2026-09-30.

## Vấn đề

`scripts/validate-content.py` chỉ chạy trên các file trong
`src/content/writing/`. Bản sao lưu mà `scripts/backup-to-working-content.py`
sinh ra ở `working/Blog/Content/news/` **không bao giờ được validate**, dù nó
copy body verbatim.

Hệ quả: một lỗi style lọt vào bản archive mà bản chính đã sạch.

## Observed

9 bài viết 30/09/2026, cả 9 PASS validation ở `src/content/writing/`. Sau khi
backup, đọc lại bản archive thì thấy em-dash (U+2014) vẫn còn trong prose, ví dụ
"Bến tận chuyện an toàn lại là **mở rộng trung tâm dữ liệu**."

Vấn đề là em-dash đó **có thật trong bản chính** — nghĩa là validator đã bỏ sót,
hoặc (xác minh lại trước khi kết luận) bản archive được sinh ra từ một bản
chưa sửa.

## Bài học đúng đắn

Đừng coi "PASS validator" là bằng chứng rằng bản archive cũng sạch. Khi chạy
backup xong, đọc lại **một** file archive bằng mắt để xác nhận định dạng, và
nếu bài nào dùng em-dash/en-dash trong prose thì sửa ở **bản chính** rồi
backup lại — không sửa tay trong archive, vì archive sẽ bị ghi đè lần sau.

## Em-dash: vẫn nên tránh trong prose tiếng Việt

Style guide cấm em-dash, và 9 bài này vẫn lọt em-dash. Khi viết bài tiếng Việt,
dùng dấu phẩy, hai dấu gạch ngang, hoặc viết lại câu. Em-dash trong tiếng Việt
không có quy ước dùng như tiếng Anh, và người đọc diễn đạt không mượt.

## Nếu anh muốn dùng bản archive làm nguồn publish

Bản ở `working/` là bản lưu trữ tĩnh, không phải bản publish. Nếu sau này lấy
 nó làm nguồn để đăng điều chỉnh, phải chạy lại validation trên chính file
đó, không mượn kết quả validation của bản chính.
