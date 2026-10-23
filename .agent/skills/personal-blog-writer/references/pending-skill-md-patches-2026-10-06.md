# Cần patch SKILL.md (06/10/2026) — chưa áp dụng được do read-before-write guard

Phiên 06/10/2026 viết 9 bài draft-only. Trong lúc đó phát hiện **mục
`## Content validation` trong `SKILL.md` còn hướng dẫn cũ**, trái với
`references/README-scripts-first.md` và `scripts/validate-content.py` đang có.

Không patch được trong phiên curator vì guard read-before-write chặn ghi vào
file có sẵn. Người hoặc phiên sau hãy áp dụng hai thay đổi dưới đây bằng
`skill_manage(action='patch')` sau khi `skill_view` trả nội dung SKILL.md.

## 1. Thay mục `## Content validation (mandatory, pre-build)` trong SKILL.md

Cũ (đang gây lệch workflow):

```
- Load reference: `skill_view(name='personal-blog-writer', file_path='references/content-validation.md')`
- Chạy auto-check script trong reference bằng `execute_code` trên file `.md` vừa viết
```

Mới:

```
**Dùng script có sẵn, KHÔNG tự viết lại bộ đếm bằng `execute_code`:**

```bash
cd ai-labs/projects/personal-blog/src/content/writing && /usr/bin/python3 \
  /home/julius/julius-workspace/.hermes/skills/personal-blog-writer/scripts/validate-content.py \
  <slug1>.md <slug2>.md ...        # nhận N file một lượt
```

Script kiểm 11 rule + ngưỡng 350 từ, in `PASS/FAIL` kèm **số từ** và **English
density** cho từng file, rồi in `OVERALL: PASS|FAIL` ở cuối. Cho cả batch một
lệnh duy nhất, đừng gọi 9 lần cho 9 bài.

- Nếu FAIL: sửa từng vấn đề, chại lại cho đến khi `OVERALL: PASS`.
- `warn:` về Oxford comma là cảnh báo, không phải lỗi — đọc từng dòng, chỉ sửa
  khi là danh sách liệt kê thật (xem `references/oxford-comma-vietnamese-false-positive.md`).
- Bộ đếm có false positive đã biết: dấu chấm trong tên miền (`Crypto.com`,
  `x.com`, `Bitcoin.com`) bị báo "missing space". Khi gặp, **viết lại câu cho
  gọn** để né (ví dụ `Nhiều sàn lớn như Coinbase, Bitnomial` thay vì liệt kê
  `Coinbase, Crypto.com, Bitnomial`) thay vì để cả batch ở trạng thái FAIL.
  Đừng sửa cả đoạn tiếng Việt vốn đúng chỉ để làm im bộ đếm
  (xem `references/validation-false-positives-and-overclaim-guard.md`).
```

## 2. Thêm con trỏ ở mục `## Pitfalls` trong SKILL.md

Một dòng trỏ tới reference mới của phiên này:

```
- **Batch lớn 6-9 bài draft-only: xem `references/draft-only-batch-9-posts-2026-10-06.md`**
  (9 slug, chuỗi xác nhận 7 bước, cách né false positive tên miền, cách gộp hai
  URL Decrypt thành một bài kho bạc theo format bài trước).
```

## Vì sao việc 1 đáng sửa

`references/README-scripts-first.md` đã cảnh báo đúng vấn đề này từ trước,
nhưng SKILL.md vẫn trỏ agent tới script nhúng trong
`references/content-validation.md`. Agent đọc tuần tự sẽ tự dựng lại bộ đếm
bằng `execute_code` — tốn vòng lượt và dễ lệch logic so với `scripts/` đã đóng
gói. Ưu tiên cho `scripts/`, `references/content-validation.md` giữ vai trò
giải thích từng rule.