# CMS GitHub Draft Conflict — "Main đã thay đổi nhưng draft đang có trạng thái GitHub chờ xử lý"

Observed 2026-08-28 while publishing the Avici post. Root cause + fixes.

## What the message means

The CMS admin (`src/lib/cms/admin.ts`, `openPublished`) refuses to reload a
published article when BOTH hold:

1. `main` has changed since the local draft was captured (`local.source?.markdownSha !== article.markdownSha`), AND
2. the local draft still carries a GitHub `remote` (branch `cms/<slug>`) or a `pendingSaveId`.

Condition: `canReplace = stale && !local.remote && !local.pendingSaveId`. When
`!canReplace`, the CMS shows the message instead of letting you reload.

## How drafts get stuck

The CMS stores drafts in **browser localStorage** under key
`julius-blog-cms-drafts-v1` (see `src/lib/cms/repository.ts`). Every CMS save
creates a `cms/<slug>` branch + PR on GitHub (see `github.ts`). When the agent
pushes the same post directly to `main` via git (the normal flow here), the
PR branch is left dangling, and the local draft still references it. Result:
the CMS thinks a draft is pending while main has moved.

Also common: clicking "publish" in the CMS fails silently when main already
has the file (merge conflict) — the draft stays stuck.

## Chọn đúng lớp dữ liệu trước khi sửa

1. Fetch remote rồi đọc riêng hai bản, không suy từ tên commit:
   ```bash
   git fetch origin
   git show origin/main:src/content/writing/<slug>.md
   git show origin/cms/<slug>:src/content/writing/<slug>.md
   git log --all --oneline -- src/content/writing/<slug>.md
   ```
   Nhánh CMS có thể chứa phần anh sửa chưa có ở `main`. Nếu mục tiêu là bản đang biên tập, xác nhận nhánh đích khi chưa rõ; không ghi đè nó bằng bản `main`.
2. Với yêu cầu mất nội dung, phân biệt file trên Git, draft lưu trong trình duyệt và nội dung editor đang hiển thị. Nếu cả hai bản Git còn đầy đủ, báo đúng điều đã kiểm tra; bản local rỗng hoặc editor chưa tải là giả thuyết, chưa phải nguyên nhân đã xác định. Không tạo commit vô ích để “khôi phục” file vốn nguyên vẹn.
3. Chỉ sửa dữ liệu trình duyệt sau khi đọc được trạng thái thực tế và giữ được bản sao của đúng draft. Kiểm tra cơ chế lưu trong mã nguồn hiện hành trước khi truy cập; không mặc định khóa localStorage cũ vẫn là nguồn dữ liệu. Không xóa local draft, nhánh CMS hoặc bài trên `main` như bước đầu xử lý xung đột: thao tác đó có thể mất phần chưa đồng bộ.
4. Nếu chỉ lấy lại được bản Markdown từ Git, gọi đó là bản trích xuất phục hồi và giữ nguyên nội dung/metadata. Chỉ tuyên bố editor đã được khôi phục sau khi đọc lại chính editor hoặc kho draft đích; một file tải xuống không đủ chứng minh điều này.

## Sửa an toàn trên nhánh CMS đang có

Sau khi anh xác nhận bản CMS là đích, làm trong worktree riêng:

```bash
git worktree add --detach <scratch-worktree> origin/cms/<slug>
```

Đọc file ở worktree, patch phạm vi yêu cầu, chạy content validation và build. Stage đúng file đã sửa, kiểm tra diff, commit rồi đẩy tới đúng nhánh:

```bash
git push origin HEAD:cms/<slug>
git fetch origin
git show origin/cms/<slug>:src/content/writing/<slug>.md
```

Nếu push bị `fetch first`, fetch lại và so sánh phần remote mới với base của commit mình trước khi rebase. Khi phần sửa không xung đột:

```bash
git rebase origin/cms/<slug>
git push origin HEAD:cms/<slug>
```

Không force-push. Nếu có thay đổi giao nhau, giữ cả phần anh vừa sửa và phần được yêu cầu; hỏi khi ý định không rõ. Sau rebase, kiểm tra diff; chạy lại validation/build nếu nội dung hoặc mã ảnh hưởng build đã thay đổi. Cuối cùng fetch và đối chiếu nội dung remote với bản đã kiểm tra. Giữ nguyên embed và trạng thái đăng, không tự đưa bài sang `main`.

## Hợp nhất bản đầy đủ khi draft liên tục hiện nội dung cũ

1. Fetch và so sánh `main`, nhánh CMS và lịch sử của đúng file. Nếu bản CMS vẫn nguyên, không restore thêm lần nữa: lỗi hiển thị chưa chứng minh có commit ghi đè mới.
2. Khi lịch sử chứng minh body bị ghi đè nhưng tiêu đề hoặc metadata mới cần giữ, lấy body từ commit tốt và ghép với metadata hiện tại; giữ nguồn, ảnh, embed và trạng thái đăng. Đừng rollback toàn file làm mất phần anh vừa chỉnh.
3. Nếu anh duyệt hợp nhất và xóa nhánh CMS, đưa bản đầy đủ đã chọn lên `main`, validate/build và push theo trạng thái đăng đã duyệt. Lưu ý quan trọng về ảnh tải lên từ CMS: CMS commit ảnh WebP vào `public/images/articles/<slug>/<hash>.webp` trên nhánh CMS. Trước khi hợp nhất sang `main`, luôn kiểm tra `git ls-tree -r --name-only origin/cms/<slug> public/images/articles/<slug>` và bắt buộc restore + commit cả thư mục ảnh này (`git restore --source=origin/cms/<slug> -- public/images/articles/<slug>/`) cùng file `.md`. Nếu chỉ copy file markdown, các link ảnh nội bộ trên `main` sẽ bị 404/broken link. Fetch rồi đối chiếu file trên `origin/main` với bản đầy đủ trước khi chạy `git push origin --delete cms/<slug>`. Xác minh nhánh không còn bằng `git ls-remote origin refs/heads/cms/<slug>`; giữ bài và lịch sử Git.
4. Báo riêng kết quả Git và kết quả trình duyệt. Xóa nhánh remote không xóa draft cục bộ hoặc nội dung editor đang mở; đừng tuyên bố đã xử lý cả ba lớp khi mới xác minh Git. Trước lần Save tiếp theo, editor cần tải lại bản đúng. Chỉ dọn riêng draft cục bộ theo cơ chế hiện hành sau khi có quyền và bảo toàn phần chưa đồng bộ; không xóa toàn bộ storage của CMS.

## Đừng đoán ai publish: đọc `committer` (sửa sai 2026-10-02)

Agent đã kết luận sai hai lần rằng "worker tự publish" khi thấy `draft: true → false`:

```bash
git log -1 --format="author: %an <%ae>%ncommitter: %cn <%ce>%ndate: %ad" <sha>
```

| Tác nhân | author | committer |
|---|---|---|
| Julius bấm Publish trong CMS | Julius | **Julius** |
| Cloudflare Worker flip `draft` qua API | Julius | **GitHub `<noreply@github.com>`** |

Commit của Julius đi qua đúng một người. Worker thật sự đóng dấu bằng
`committer: GitHub`. Kiểm tra `committer` TRƯỚC khi nói ai publish.

Bằng chứng đối chiếu được: commit `c8a1c64` (2026-09-09) là Worker thật
(`committer: GitHub`). Commit `9a68e72` (2026-10-02, bài
`openai-sa-tam-nghien-cuu-an-toan`) là Julius bấm Publish
(`committer: Julius`) 11 phút sau khi agent báo cáo xong.

## Kiểm tra Worker còn sống hay không

Đừng tin trạng thái ghi trong skill (từng có ghi chú Worker đã chết) — kiểm tra
bằng lịch sử commit, vì đó là bằng chứng trực tiếp và không cần mạng/đăng nhập:

```bash
git log --format="%h|%cn|%cd|%s" --date=short -25 -- src/content/writing
```

- Có commit `content: publish <slug>` với `committer: GitHub` trong vài ngày gần
  nhất → Worker đang chạy, các bài có `scheduledAt` sẽ tự publish.
- Không có commit nào như vậy trong nhiều ngày → nghi Worker đã chết; kiểm tra
  thêm bằng `npx wrangler deployments list --config wrangler.scheduler.jsonc` và
  báo Julius rằng lịch đăng cần publish tay.

Bài kẹt (Worker không flip dù đã qua giờ hẹn):

```bash
for f in $(grep -rl "^draft: true" src/content/writing/); do
  s=$(grep -m1 "^scheduledAt:" "$f" | sed 's/scheduledAt: //;s/"//g')
  [ -n "$s" ] && echo "$s $f"
done
```

Dòng nào hiện ra là bài chưa được publish → flip `draft: false` rồi build + push.

Đừng khẳng định "bài draft chưa lên blog" chỉ vì frontmatter ghi `draft: true`:
đã có slug viết mà KHÔNG kèm `scheduledAt` vẫn xuất hiện commit
`content: publish <slug>`. Muốn biết một bài đã lên trang hay chưa, đọc
`git log --oneline -- src/content/writing/<slug>.md`, đừng suy từ frontmatter.

## Đừng ngụ ý có bug khi chưa có bằng chứng

Vụ lỗi "Raw HTML không được phép" (2026-10-02): agent nói "nguyên nhân gốc
chưa xác định được" và ngụ ý có thể là bug CMS. Kết luận cuối: nguyên nhân
nằm ở chỗ anh gõ `<br />` trong editor Milkdown — CMS đúng, validator đúng,
`<br />` mới là thứ bị chặn. Không phải bug.

Bài học: `<br />` và các tag HTML rác **không phải lỗi CMS** — validator chặn
raw HTML là chủ ý (`github.ts:215`, cho phép duy nhất
`<blockquote class="twitter-tweet">`). Khi gặp lỗi này, tìm `<` trong bản
anh gửi trước, đừng đi tìm bug.

## General hygiene

- Với bài mới, đẩy tới `main` theo chế độ đăng đã duyệt. Với bài đang được sửa trên nhánh CMS, cập nhật đúng nhánh đó; không dùng `main` để né xung đột rồi làm mất phần biên tập chưa merge.
- After any CMS publish that seems to hang, check
  `git ls-remote origin 'refs/heads/cms/*'` and the localStorage draft list
  before telling Julius the publish failed.
