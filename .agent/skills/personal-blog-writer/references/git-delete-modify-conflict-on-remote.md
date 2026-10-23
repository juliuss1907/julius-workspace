# Xung đột git: Julius xoá bài ở remote trong lúc bạn viết lại ở local

Observed 01/10/2026. Khác hoàn toàn với `references/cms-github-draft-conflict.md`
(cái đó là CMS localStorage + dangling `cms/*` branch; cái này là git rebase).

## Tình huống

Julius xoá một bài đang draft trên GitHub (qua CMS hoặc trực tiếp) trong khi
bạn đang viết lại chính bài đó ở local. Khi bạn `git pull --rebase origin main`,
git báo không áp dụng được commit của bạn vì file vừa bị sửa ở local vừa bị
xoá ở upstream.

```
Không thể áp dụng <sha>... # content: rewrite ... post
```

## Phân biệt modify/delete để chọn đúng phía

Trước khi chọn, **kiểm tra cả hai phía của conflict** để biết upstream xoá thật
hay chỉ sửa. Không đoán:

```bash
git diff --name-only --diff-filter=U              # file nào đang conflict
git cat-file -p :2:<path>   # stage 2 = "ours" = phía đang rebase vào (upstream)
git cat-file -p :3:<path>   # stage 3 = "theirs" = commit của bạn
```

Kết quả `git cat-file -p :2:<path>` báo *"nằm trong chỉ mục, nhưng không phải ở
giai đoạn 2"* là **dấu hiệu upstream đã xoá file** (delete/modify conflict), chứ
không phải sửa nội dung.

Nếu `:2` trả nội dung đầy đủ thì upstream chỉ sửa file, và việc hợp nhất nội
dung là việc thật, cần đọc cả hai bản.

## Chọn phía

Khi đã xác nhận upstream chỉ **xoá** (không sửa nội dung) và Julius muốn bài quay
lại, giữ bản của bạn:

```bash
git checkout --theirs <path>    # lấy nội dung từ commit của bạn
git add <path>
git -c core.editor=true rebase --continue    # tránh editor mở khi rebase
git push origin main
```

Lưu ý phân kỳ tên stage trong rebase: `:2` là phía **upstream** (commit đang
rebase vào), `:3` là phía **commit của bạn** — ngược với trực giác của `git
merge`. Đây là lý do phải đọc nội dung thật trước khi chọn, không đoán theo tên.

## Bắt buộc báo cáo

Sau khi giải quyết conflict kiểu này, nói rõ với Julius: anh đã xoá gì ở remote,
bạn đã giữ lại gì, và **xác nhận không có nội dung nào của anh bị mất**. Nếu `:2`
cho thấy upstream có sửa nội dung (không phải chỉ xoá), phải hỏi anh trước khi
ghi đè.

## Phòng ngừa

Trước khi viết lại một bài mà anh có thể đã xoá, `git fetch -q origin` rồi
kiểm tra lịch sử để hiểu tình trạng:

```bash
git fetch -q origin
git log --oneline origin/main -5                     # có commit "delete <slug>"?
git show origin/main:src/content/writing/<slug>.md >/dev/null 2>&1 \
  && echo "còn trên remote" || echo "đã bị xoá ở remote"
```

Bài còn nằm ở local (`git status` không hiện) trong khi remote đã xoá là tình
huống trên, không phải file rác cần dọn. Xác nhận ý định của anh trước khi
ghi đè.