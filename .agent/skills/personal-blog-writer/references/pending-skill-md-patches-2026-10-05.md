# SKILL.md cần patch — vòng 2 (05/10/2026)

File này là hàng đợi cho phiên **foreground**. Curator background không patch được
SKILL.md (`read_before_write_required` từ chối cả `patch` lẫn `write_file` lên file
đã tồn tại, kể cả khi vừa `skill_view` xong).

Đã tạo được trong phiên này, không cần làm gì thêm:
`draft-only-batch-session-2026-10-05.md`, `benchmark-own-page-as-fifth-source.md`,
`oxford-comma-warn-can-be-right.md`.

Còn 5 việc dưới đây cần áp dụt vào SKILL.md.

---

## 1. Sửa mục "Content validation (mandatory, pre-build)" — ĐANG SAI, ƯU TIÊN CAO

Nội dung hiện tại bảo chạy script inline bằng `execute_code`. `execute_code` **bị
chặn trong scheduled session**:

```
BLOCKED: execute_code runs arbitrary local Python ... Cron jobs run without a
user present to approve it.
```

Hướng dẫn cũ còn sót từ trước khi có `scripts/`. Thay cả mục bằng:

> Chạy script có sẵn qua `terminal` (KHÔNG dùng `execute_code` — bị chặn trong
> cron/scheduled session):
>
> ```bash
> cd ai-labs/projects/personal-blog
> python3 ~/julius-workspace/.hermes/skills/personal-blog-writer/scripts/validate-content.py \
>   src/content/writing/<slug1>.md src/content/writing/<slug2>.md ...
> ```
>
> Nhận nhiều file một lượt, kiểm đủ 11 rule trong `references/content-validation.md`
> cộng ngưỡng 350 từ body, exit 1 nếu FAIL.

`references/README-scripts-first.md` đã nói đúng nguyên tắc này, nhưng SKILL.md là
thứ agent đọc đầu tiên nên chỉ dẫn sai ở đó là chỉ dẫn sai.

## 2. Oxford comma: thêm vế còn lại vào Pitfalls

> - **Oxford comma warn có thể đúng**: `warn` là tín hiệu "đọc từng dòng", không
>   phải "bỏ qua". Phần lớn là mệnh đề ghép tiếng Việt và hợp lệ, nhưng danh sách
>   liệt kê thật nằm trong cùng nhóm cảnh báo. Xem
>   `references/oxford-comma-warn-can-be-right.md`.

## 3. Draft-only: trỏ tới chuỗi kiểm chứng đầy đủ

Thêm vào mục "Chế độ draft-only":

> - Kiểm chứng đầy đủ (build exit 0 KHÔNG đủ, vì `draft: false` sót cũng exit 0):
>   validate → build → **slug vắng mặt trong `dist/articles/`** → không có
>   `scheduledAt` → `draft: true` → staged đúng N dòng → `git show origin/main:<slug>`.
>   Batch 4 bài, mọi bước và mẫu lệnh:
>   `references/draft-only-batch-session-2026-10-05.md`.

## 4. Nguồn gốc: thêm đích thứ năm

Thêm vào `references/brief-item-to-primary-source-upgrade.md` (đang có 4 đích):

> 5. **Trang chủ của chính hệ thống đo.** Khi tin mang dạng "model X đạt kết quả Y
>    trong benchmark Z", bên công bố thật sự là trang của Z — có điều kiện chạy,
>    thang đo và điểm đứng cuối bảng. Bài báo chỉ kể cốt truyện. Chi tiết:
>    `references/benchmark-own-page-as-fifth-source.md`.

## 5. Pitfall: file `??` có sẵn trong `src/content/writing/`

> - **Untracked có sẵn không phải của bạn**: `git status` có vài file `??` từ phiên
>   trước (`blog-index.md`, `gpt-6-1-sol-near-astra-price.md` quan sát 05/10).
>   Stage bằng **tên file tường minh**, không `git add .` không `git add <thư mục>`.
>   Không sửa/xoá/commit chúng, và nêu lại trong reply.

---

## Ghi chú kỹ thuật cho curator

`references/PATCH-NEEDED.md` (vòng 1) vẫn còn nguyên, ghi về bump version 1.0.1 →
1.0.2 và một số pitfall CJK/Obsidian/rebase. Vòng 2 này nên gộp vào đó khi có
foreground.