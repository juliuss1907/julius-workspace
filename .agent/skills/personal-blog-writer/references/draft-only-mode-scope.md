# Draft-only mode: phạm vi, kích hoạt, và phần bị bỏ qua

Quan sát 2026-09-29. Bổ sung cho mục "Chế độ draft-only" trong SKILL.md.

## "đăng draft" = draft-only, KHÔNG lên lịch

Câu thực tế của Julius: *"Viết news 1, 3, 6, 9 và 10 sau đó đăng draft lên blog"*.

Cụm **"đăng draft"** là tín hiệu draft-only, KHÔNG phải yêu cầu lên lịch. Tương tự "đăng lên blog nhưng KHÔNG publish". Viết `draft: true`, **không** đặt `scheduledAt`.

| Phát biểu | scheduledAt? | Backup `working/Blog/Content/`? |
|---|---|---|
| "...đăng draft lên blog" | KHÔNG | hỏi Julius, không tự tạo |
| "...đăng nhưng KHÔNG publish" | KHÔNG | hỏi Julius, không tự tạo |
| "...đăng lên blog" (trần) | CÓ, +30 phút rồi cách 2 giờ | CÓ |
| "...cho lịch / hẹn giờ đăng" | CÓ | CÓ |
| "...đăng lên blog dạng draft" | KHÔNG | hỏi Julius |
| "Viết news ..." (không nhắc gì tới đăng) | CÓ, +30 phút rồi cách 2 giờ | CÓ |

Từ khoá quyết định là chữ **"draft"** và chữ phủ định ("KHÔNG publish"). Có mặt
→ draft-only. Không có → quy trình publish đầy đủ, kể cả khi câu lệnh im lặng
hoàn toàn về việc đăng. "Viết news ..." trần là dạng phổ biến nhất của yêu cầu
brief → blog, nên im lặng nghĩa là "đi luồng mặc định", không phải mơ hồ cần
dừng lại hỏi.

## Vì sao bỏ qua backup ở draft-only

Bước 6 (backup `working/Blog/Content/<slug>.md` + wikilink vào `news/news.md`)
thuộc quy trình publish vì nó giữ cho bản Coin68-voice khớp với bài đã lên
blog. Ở draft-only, bài chưa lên blog, nên bản sao lưu chỉ tạo thêm file rác
local và phải đồng bộ lại khi bài được publish sau đó (thêm một lượt sửa nữa).

Cách xử lý đúng ở draft-only: viết bài sạch, và **hỏi thẳng trong report**
("Việc chưa làm: chưa tạo bản sao lưu vào `working/Blog/Content/`, cần thì tôi
làm nốt"). Đừng tự tạo rồi im lặng, cũng đừng bỏ qua mà không nói.

## Verify draft-only đúng: bài KHÔNG có mặt trong dist

`npm run build` exit 0 không đủ để kết luận đúng. Với draft-only, phải xác nhận
ngược lại: slug **vắng mặt** trong `dist/`.

```bash
cd ai-labs/projects/personal-blog && npm run build
for s in <slug1> <slug2>; do
  [ -d "dist/articles/$s" ] && echo "PUBLISHED(!): $s" || echo "draft ok: $s"
done
```

Có slug nào hiện trong `dist/` nghĩa là `draft: false` bị sót, hoặc Worker đã
publish. Kiểm tra lại frontmatter trước khi báo cáo.

## Commit + push vẫn bắt buộc

Draft-only KHÔNG có nghĩa giữ file local. Vẫn commit + push `main` để bài nằm
trong repo, chỉ là không bao giờ tự lên trang. Verify remote thật sự có file:

```bash
git fetch -q origin
git show origin/main:src/content/writing/<slug>.md >/dev/null 2>&1 && echo ON_REMOTE
```

## Report phải nói rõ 3 việc

1. Bảng: số thứ tự brief → slug → category → số từ. Không chỉ liệt kê slug.
2. **Ghi chú nguồn**: nguồn nào bị chặn, đã dùng thay bằng gì, và con số nào
   đến từ bản tóm tắt chứ chưa kiểm chứng độc lập (xem
   `blocked-primary-sources-and-figure-selection.md`).
3. **Phần chưa làm** (backup, thumbnail) nêu thẳng và đề xuất bước tiếp theo,
   không im lặng bỏ qua.

## Đăng batch đã viết ở lượt trước: tìm draft TRƯỚC khi kết luận

Yêu cầu "đăng các bài draft của ngày <X> lên blog" thường nghĩa là bài đã viết
xong ở lượt trước và chỉ còn thiếu bước push. Repo chính có thể sạch (chỉ vài
file untracked không liên quan) trong khi draft của ngày đó nằm untracked trong
một bản clone tạm dùng để viết bài. Nhìn mỗi repo rồi kết luận "không có draft"
là bỏ sót việc.

Thứ tự tìm, độ phủ tăng dần:

```bash
# 1. trong repo: slug nào còn là draft?
grep -rl "^draft: true" src/content/writing --include='*.md'

# 2. toàn workspace: file .md sửa trong ngày, và mốc publishedAt của ngày đó
cd /home/julius/julius-workspace
find . -name '*.md' -newermt '<YYYY-MM-DD> 00:00' -not -path '*/node_modules/*' -not -path '*/.git/*'
grep -rl "publishedAt: <YYYY-MM-DD>" --include='*.md' . | grep -v node_modules
```

Bước 2 chỉ ra `.hermes/cache/scratch/blog-news-<ngày>/src/content/writing/`.
Thư mục đó là repo git riêng, HEAD có thể cũ hơn `origin/main` — chỉ dùng để
lấy nội dung, không push từ đó.

Sau khi có tập file: đối chiếu từng slug với `origin/main` (slug chưa có mới là
việc), copy sang repo thật, validate, build, stage đúng tập path, commit, push.
Ghi nhận trong report là bản này do lượt trước viết, lượt này chỉ kiểm tra và
đẩy — kèm giới hạn là chưa đọc lại từng nguồn.

## Publish một bài mà không mang theo nhánh/công việc khác

Khi repo đang ở nhánh CMS hoặc working tree còn công việc khác, tách worktree từ
`origin/main` thay vì chuyển nhánh hay stash:

```bash
git fetch -q origin
git worktree add --detach <scratch>/<tên> origin/main
cp src/content/writing/<slug>.md <scratch>/<tên>/src/content/writing/<slug>.md
ln -s "$PWD/node_modules" <scratch>/<tên>/node_modules   # thiếu symlink là build fail
cd <scratch>/<tên> && npm run build
git add src/content/writing/<slug>.md && git commit -m "content: ..."
git push origin HEAD:main            # chạy được cả ở detached HEAD
git worktree remove --force <scratch>/<tên>
```

Sau push: `git fetch` rồi đọc lại bằng `git show origin/main:<path>`. Dọn worktree
ngay sau khi push xong — worktree bỏ lại sẽ thành đống clone tạm phải đoán công dụng
ở các lượt sau.
