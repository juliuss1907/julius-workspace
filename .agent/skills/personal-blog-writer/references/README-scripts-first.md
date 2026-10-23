# Skill này có script, hãy dùng script

Mục **Content validation** trong SKILL.md từng bảo chạy "auto-check script trong
reference bằng `execute_code`". Hướng dẫn đó chỉ tới bản script nhúng trong
`references/content-validation.md`, **không** chỉ tới thư mục `scripts/`, nên
agent đọc tuần tự sẽ tự viết lại bộ đếm bằng heredoc python thay vì gọi script
đã đóng gói.

Script thật nằm ở `scripts/` và chạy tốt:

- `scripts/validate-content.py` — 11 rule + ngưỡng 350 từ, nhận nhiều file một
  lượt, in PASS/FAIL kèm số từ và English density
- `scripts/backup-to-working-content.py` — sinh bản archive
  `working/Blog/Content/` + chèn wikilink lên đầu index

Xem `references/prefer-bundled-scripts-over-inline-rebuilds.md` để biết lệnh
gọi cụ thể và lý do workflow sai này tốn thời gian.

**Nếu bạn là agent đang đọc dòng này:** trước khi tự viết bộ đếm, kiểm tra
`scripts/` trước.
