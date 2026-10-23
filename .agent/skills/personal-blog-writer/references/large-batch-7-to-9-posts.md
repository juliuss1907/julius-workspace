# Batch lớn (7-9 bài) — bổ sung cho batch-publish-and-backup-workflow.md

Session 2026-09-30: 9 bài trong một lượt. Bài tham chiếu gốc viết cho 4 bài, một
số bước cần mở rộng khi batch lớn hơn.

## Gộp tin trùng TRƯỚC khi viết

Khi Julius liệt kê số mục từ brief (ví dụ "viết news 1, 2, 4, 9, 10, 12") và
đồng thời đính kèm thêm vài tin riêng, **số mục trong brief và các tin đính kèm
có thể trùng nhau**. Observed 30/09: mục 4 của brief là GPT-6.1 Sol, và Julius
cũng gửi kèm một mục GPT-6.1 Sol riêng kèm 4 URL.

Cách xử lý: gộp thành **một bài**, nhưng dùng bộ nguồn đầy đủ hơn. Ở batch này,
bài GPT-6.1 Sol dài nhất batch (856 từ) vì có bộ nguồn gộp gồm trang chính
thức OpenAI, VentureBeat, Artificial Analysis, Implicator và trang recap
DevDay. Giá trị thật nằm ở **đối chiếu số liệu tự công bố với đo độc lập**:
tuyên bố "ngang Astra" chỉ đúng ở mức suy luận trung bình, lên mức cao nhất
thì Claude Opus 5.5 vượt lại. Chi tiết này không có ở bất kỳ nguồn đơn lẻ nào.

Báo cáo rõ trong reply rằng đã gộp mục nào và dùng nguồn nào, để anh kiểm tra.

## Nhiều URL bị chặn trong phần user đính kèm

Context warning thường báo `no content extracted` cho `openai.com/index/...` và
`x.com/...`. Không dừng lại: `web_extract` lại trực tiếp các URL đó thường ra
kết quả (openai.com đọc được; chỉ context-packer ban đầu không lấy được). Với
`x.com/...` mà vẫn không được, dùng `web_search` để tìm bản phát ngôn chính
thức hoặc nguồn tốt khác.

## Ghi `scheduledAt` bằng script, không gõ tay 9 lần

Sau khi validate + build đã pass, chèn `scheduledAt` vào cả batch bằng
`execute_code` thay vì `patch` từng file (9 lần patch dễ lỗi và tốn thời gian):

```python
import pathlib
base = pathlib.Path("<project>/src/content/writing")
schedule = {"slug1": "2026-09-30T03:09:52.000Z", ...}
for slug, ts in schedule.items():
    p = base / f"{slug}.md"
    t = p.read_text(encoding="utf-8")
    assert "scheduledAt:" not in t, slug        # tránh chèn hai lần
    p.write_text(t.replace("draft: true", f"draft: true\nscheduledAt: \"{ts}\"", 1), encoding="utf-8")
```

Tính lại mốc đầu tiên NGAY TRƯỚC lúc chèn (xem
`references/scheduled-post-timing.md`), rồi build lại lần nữa để chắc chắn
`scheduledAt` không làm vỡ frontmatter.

## Push bị từ chối: cách xử lý

`git push` bị reject với thông báo tiếng Việt "cập nhật bị từ chối bởi vì máy chủ
có chứa thay đổi". Đừng dùng `stash` cho trường hợp này — không có thay đổi cục
bộ nào cần giữ, vì mọi file đã được commit. Chỉ cần:

```
git pull --rebase origin main && git push origin main
```

Batch 30/09: remote đã tiến từ `be4aa29` lên `687ab3d` giữa lúc viết, rebase
sạch, không xung đột filename vì slug đều mới.

Lưu ý: nếu chạy `git push -q ... && echo OK || (...)` thì lệnh `echo` sẽ làm
exit code thành 0 dù push fail. Kiểm tra output push thật, đừng tin chuỗi `&&`.

## Verify remote bằng cách đọc frontmatter trực tiếp

Sau khi push, xác nhận từng file trên `origin/main` có cả `draft: true` và
`scheduledAt` đúng giá trị:

```python
r = subprocess.run(["git","show",f"origin/main:src/content/writing/{slug}.md"],
                   cwd=project, capture_output=True, text=True)
```

In ra cả hai dòng cho mỗi slug. Đây là verify có giá trị vì nó bắt được trường
hợp `scheduledAt` bị chèn sai format hoặc bị mất khi rebase.
