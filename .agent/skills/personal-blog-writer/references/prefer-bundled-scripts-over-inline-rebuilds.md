# Dùng script có sẵn, đừng tự dựng lại

Bổ sung cho `references/content-validation.md` và
`references/validation-false-positives-and-overclaim-guard.md`.

Skill này đã đóng gói sẵn hai script. Việc đúng là gọi chúng, không phải viết
lại bằng heredoc python mỗi lần.

## Hai script

```bash
# 1. Validation — chạy trong ai-labs/projects/personal-blog
python3 ~/julius-workspace/.agent/skills/personal-blog-writer/scripts/validate-content.py \
  src/content/writing/<slug>.md [<slug2>.md ...]

# 2. Backup vào working/Blog/Content — chạy trong ~/julius-workspace
python3 ~/julius-workspace/.agent/skills/personal-blog-writer/scripts/backup-to-working-content.py \
  <slug> [<slug2>.md ...]
```

`validate-content.py`: check đủ 11 rule trong `references/content-validation.md`
cộng ngưỡng 350 từ body. In PASS/FAIL kèm số từ và English density. Nhận nhiều
file một lượt. Exit 1 nếu có lỗi. Oxford comma chỉ là `warn`, không fail.

`backup-to-working-content.py`: đọc frontmatter bài trong
`ai-labs/projects/personal-blog/src/content/writing/`, sinh bản archive đúng
format `working/Blog/Content/AGENTS.md` (khối metadata, `## title`, `Meta:`,
body verbatim), rồi chèn wikilink lên đầu index `news.md`. Cả hai đều xử lý
nhiều slug trong một lệnh.

## Vì sao ghi lại

Phiên 2026-09-29 viết 4 bài news. Ba lượt đầu tôi tự dựng lại bộ đếm bằng
heredoc python ~60 dòng cho mỗi lần thay vì chạy script có sẵn. Riêng lượt ba
tôi còn vá bằng `patch` cả 8 dòng Oxford comma trong 3 bài, rồi cả 3 bài vẫn
FAIL vì bộ đếm tự viết bắn nhầm mệnh đề ghép tiếng Việt. Đến bài thứ tư mới
phát hiện `scripts/validate-content.py` tồn tại, chạy ra PASS ngay lần đầu.

Cùng phiên đó, phần backup cũng tự viết python inline ba lần cho từng bài, rồi
cuối cùng mới dùng `backup-to-working-content.py` — cũng PASS ngay.

Cả hai script đều đã có và hoạt động tốt suốt thời gian qua. Vấn đề là workflow
mặc định trong SKILL.md vẫn bảo "chạy auto-check script trong reference bằng
`execute_code`", tức chỉ tới `references/content-validation.md` chứ không tới
thư mục `scripts/`. Đọc hướng dẫn theo thứ tự thì rơi vào bản script nhúng trong
reference, dù bản đó đã bị thay bằng script riêng.

## Quy tắc

1. Trước khi viết bộ đếm, kiểm tra script có sẵn không:
   `ls ~/julius-workspace/.agent/skills/personal-blog-writer/scripts/`
2. Nếu script tồn tại, dùng nó. Không viết lại.
3. Khi SKILL.md có vẻ mâu thuẫn với `references/` hoặc `scripts/`, tin
   `scripts/` vì đó là bản chạy thật đã được kiểm chứng.
4. Nếu không nhớ script ở đâu, `ls` trước khi tự viết bất cứ logic dài nào.
