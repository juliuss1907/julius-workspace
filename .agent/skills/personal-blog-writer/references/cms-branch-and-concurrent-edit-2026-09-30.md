# CMS branch, bài trùng, và rebase xung đột (30/09/2026)

Bổ sung cho `references/cms-github-draft-conflict.md` và
`references/follow-up-story-on-existing-slug.md`. Cả ba cùng nói về một
tình huống: CMS của Julius và agent git đang cùng đụng vào
`src/content/writing/`.

## Worktree riêng khi repo đang có công việc CMS

1. Từ repo blog, chạy `git status --short`, `git branch --show-current`, `git worktree list` và `git fetch origin` trước khi chọn nơi viết. Không mặc định nhánh đang checkout là `main`.
2. Nếu nhánh hiện tại thuộc công việc khác, tạo worktree ở scratch được runtime chỉ định:
   `git worktree add --detach <scratch>/blog-news-batch origin/main`.
   Detached HEAD giúp viết bài mà không checkout hoặc di chuyển nhánh của người đang sửa CMS.
3. Đọc schema và manifest trong worktree. Nếu dùng lại dependencies có sẵn, chỉ liên kết `node_modules` khi phiên bản trong lockfile tương thích; không stage liên kết đó. Chạy validation và build từ chính worktree chứa bài mới.
4. Kiểm tra trùng slug trên `origin/main` và các bản CMS có liên quan trước khi viết. Khi chia batch cho nhiều agent, giao tập đường dẫn không giao nhau; parent đọc lại bài và chạy validation toàn bộ tập được yêu cầu trước build.
5. Với worktree sạch chưa có commit riêng, lấy cập nhật bằng `git fetch origin` rồi `git merge --ff-only origin/main`. Nếu đã có commit riêng, xử lý lệch lịch sử theo quy trình rebase và dừng khi có xung đột nội dung hoặc xóa/sửa.
6. Stage đúng các Markdown được yêu cầu, so sánh tập staged paths, commit rồi push theo quyền đã được duyệt bằng `git push origin HEAD:main`. Sau push, fetch và đọc lại từng file từ `origin/main`; kiểm tra YAML cùng nội dung khớp bản đã build. Không dùng trạng thái của nhánh CMS để chứng minh batch đã lên remote.

## 1. Branch `cms/<slug>` chứa bản sửa tay của Julius

CMS lưu mỗi lần bấm Save thành branch `cms/<slug>` trên remote, KHÔNG tự
merge vào `main`. Agent đọc branch đó trước khi viết bài:

```bash
cd ai-labs/projects/personal-blog
git fetch origin -q
git log --oneline -3 origin/cms/<slug>
git log --oneline origin/main..origin/cms/<slug>    # commit chưa vào main
git show origin/cms/<slug>:src/content/writing/<slug>.md
```

Quan sát 30/09/2026: yêu cầu "viết news GPT-6.1 Sol", nhưng bài đã tồn tại
(slug `gpt-6-1-sol-launch`) trên branch CMS với 5 commit lúc 10:48-10:52,
do Julius sửa qua CMS. Bản đó có thứ bản agent viết không có:

- Ảnh bảng giá upload lên `public/images/articles/<slug>/bfdadd3ff48a.webp`
- Chi tiết OpenAI hủy GPT-6.1 Astra vì vấn đề tuân thủ (giải thích vì sao
  có "6.1 Sol" mà không có "6.1 Astra")
- Tweet Artificial Analysis nhúng thêm
- Bullet thay bảng Markdown, `readingMinutes: 7`, `scheduledAt` do CMS set

Cách xử lý đúng: đọc bản CMS, báo lại điểm khác biệt, hỏi Julius merge hay
viết lại. Khi anh bảo merge: `git merge --ff-only origin/cms/<slug>` (fast-forward
sạch vì không có commit nào trên main bị lệch), rồi validate + build + push.

Kiểm tra ảnh có thật sau khi merge:
```bash
ls public/images/articles/<slug>/          # file phải tồn tại
git ls-tree -r --name-only origin/cms/<slug> | grep <slug>
```

## 2. Ba tình huống khi bài đã tồn tại

Chạy TRƯỚC khi soạn, không phải sau:

```bash
git show origin/main:src/content/writing/<slug>.md >/dev/null 2>&1 && echo REMOTE-EXISTS || echo free
grep -rlE 'Astra|BitMine|GPT-6|THORChain' src/content/writing/ | head
```

| Tình huống | Cách làm |
|---|---|
| Bài cũ cùng sự kiện, đã publish | Viết tiếp, slug MỚI, neo bằng mốc thời gian. Xem `follow-up-story-on-existing-slug.md` |
| Bài cũ là DRAFT của chính bài đó | HỎI Julius. Không tự quyết |
| Bài đã bị Julius xóa | Xác nhận lý do xóa, rồi viết lại từ đầu |

Quan sát 30/09/2026: bài `gpt-6-1-sol-near-astra-price` bị Julius xóa lúc 10:17
với message "viết dở quá", nhưng vẫn còn `scheduledAt`. Viết đè lên bài đang
có `scheduledAt` sẽ phá lịch của anh.

## 3. Rebase xung đột vì Julius commit giữa lúc agent đang làm

Agent đang `git pull --rebase` thì Julius xóa file trên remote → rebase fail với
`XUNG ĐỘT (sửa/xóa)`. Quy tắc:

1. `git rebase --abort` trước, KHÔNG để lại rebase dở.
2. `git fetch origin` rồi đọc log có timestamp để biết chuyện gì vừa xảy ra:
   `git log --format='%h %ad %s' --date=format:'%H:%M' origin/main -5`
3. `git show --stat <remote-commit>` xem commit của Julius đụng file nào.
4. **Báo Julius và DỪNG.** Xóa và khôi phục là hai hướng ngược nhau.
   Không tự `rebase --skip` (mất thay đổi) và không tự khôi phục.
5. Khi anh xác nhận: `git reset --mixed <commit-truc>` để gỡ commit của bạn
   mà giữ file trên đĩa.

Dấu hiệu nhận biết trước: `git status` báo `DU <path>` (deleted by us,
modified by them) hoặc `git stash pop` báo "không thể áp dụng bản vá".

## 4. Bảo vệ bản sửa tay của Julius khi commit

Trước khi `git add` một file không phải do bạn vừa viết:

```bash
git fetch origin -q && git status --short <path>
git log --oneline -3 -- <path>       # commit gần nhất là của ai
```

Nếu commit gần nhất không phải của bạn, đọc lại file trước khi đụng vào.

## 5. Số liệu bên thứ ba suy diễn: đừng lặp lại

30/09/2026, gói ChatGPT Pro 500. Business Insider, aistify và pasqualepillitteri
đều viết "25 lần usage so với Plus". Trang help chính thức của OpenAI chỉ ghi
"highest included usage" — KHÔNG có hệ số. 25 là 500 chia cho 20, tức phép chia
GIÁ, không phải usage.

Hai nguồn tự thừa nhận: aistify ("the usage multiplier alone therefore does not
imply a lower price per unit"), pasqualepillitteri ("no official source says the
included usage grows in the same proportion").

Cách xử lý: dành một đoạn riêng nói rõ cái nào công bố, cái nào suy diễn, và
vì sao khác biệt quan trọng. Dẫn lại sự thừa nhận của nguồn.

Chi tiết đáng đưa thêm từ nguồn: Ultrafast nhanh hơn 8 lần nhưng CŨNG ăn usage
nhanh hơn 8 lần, credit mua thêm giá gấp 6 lần. Nên "gói đắt hơn" không đồng
nghĩa "nhiều công việc hơn theo tỷ lệ". Đây là loại chi tiết nhiều bài nguồn
nhấn mạnh và dễ khiến người đọc hiểu sai nhất.

## 6. Khi nhiều bài trong ngày cùng chạm một chủ đề

Ví dụ 30/09/2026: Sonnet 5.5 + IPO Anthropic + bữa trưa Amodei-Trump đều nhắc
lời kêu gọi "pace the frontier". Bài sau chỉ nhắc bài trước ở mức MỘT dòng bối
cảnh, không lặp lại lập luận. Báo Julius trước khi ghép đoạn kết nếu hai bài có
khả năng trùng ý.