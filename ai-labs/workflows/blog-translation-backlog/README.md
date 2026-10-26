# Blog translation backlog

## What it does
Dịch các bài edgenotes.net chưa có bản tiếng Anh (148 bài ngày 23/10/2026) qua router chạy trên máy (`127.0.0.1:20128`, model `ag/gemini-3.8-flash`), thay cho Google AI Studio. Mỗi đợt 50 bài, các đợt cách nhau 5 giờ. Đợt nào qua test và build thì tự commit và push lên `main` của repo blog. Hết bài thì timer tự tắt.

## Setup
1. Thêm khóa của router vào `ai-labs/projects/personal-blog/.env.local`:
   ```
   TRANSLATION_OPENAI_API_KEY=<khóa router>
   ```
   URL router, tiền tố model và tên model được script đặt trực tiếp, nên không cần ghi vào `.env.local`. Vì các giá trị này được đặt khi chạy, script không bao giờ quay về gọi Gemini API trả phí.
2. Cài timer (systemd user):
   ```bash
   ln -sf "$PWD/systemd/blog-translation-backlog."{service,timer} ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable --now blog-translation-backlog.timer
   ```

## Usage
- Xem trước đợt kế tiếp, không dịch gì: `./run-batch.sh --dry-run`
- Chạy một đợt ngay: `systemctl --user start blog-translation-backlog.service`
- Chạy thử 1 bài: `BATCH_SIZE=1 ./run-batch.sh`
- Lịch chạy kế tiếp: `systemctl --user list-timers blog-translation-backlog.timer`
- Nhật ký: `logs/<ngày-giờ>.log`, và `journalctl --user -u blog-translation-backlog`
- Dừng hẳn: `systemctl --user disable --now blog-translation-backlog.timer`

Có thể đổi bằng biến môi trường: `BATCH_SIZE` (mặc định 50), `TIMEOUT_MS` (mặc định 300000, vì router bật suy luận nên mỗi bài mất 30–40 giây, đôi khi quá 90 giây), `ROUTER`, `MODEL_PREFIX`, `MODELS`, `WORKTREE`.

## Architecture
Mỗi đợt chạy các bước:
1. Kiểm tra router còn sống. Dùng `flock` để không có hai đợt chạy chồng nhau.
2. `git fetch`, rồi đưa worktree riêng ở `~/.cache/blog-translation-backlog/worktree` về `origin/main`. Worktree này tách khỏi thư mục repo mà người và Codex đang làm việc. Nếu worktree còn thay đổi dở từ đợt trước, script dừng lại thay vì ghi đè.
3. `pending-slugs.mjs` lấy tối đa 50 bài đã đăng, chưa bị disable, chưa có file trong `src/content/translations/en/`, mới nhất trước. Bản dịch cũ đã lệch nguồn không thuộc phạm vi này; CI tự dịch lại khi bài nguồn đổi.
4. Chạy `scripts/translate-content.mjs --slugs ...` của blog với `TRANSLATION_OPENAI_BASE_URL` trỏ tới router. Bài nào lỗi vẫn ở trạng thái chờ và được thử lại ở đợt sau.
5. Kiểm tra chỉ có file mới trong `src/content/translations/en/` thuộc đúng danh sách, rồi chạy `npx vitest run` và `npm run build`. Nếu không qua, các bản dịch được chuyển sang `logs/failed-<giờ>/` (không xóa) và đợt dừng lại.
6. Commit, rồi push lên `main`. Nếu bị từ chối, rebase lên `main` mới và thử lại tối đa 3 lần. Push file bản dịch không kích hoạt workflow dịch của GitHub, vì workflow đó chỉ theo dõi `src/content/writing/**`.

`translationModel` được ghi là `gemini-3.8-flash`, không có tiền tố `ag/`, nên CI coi các bản dịch này là còn hiệu lực.

## Status
Xong. Ngày 23/10/2026 bốn đợt đã dịch hết 148 bài tồn (commit `80ccc97`, `03ea06a`, `894b3ca`, `c6f4706` trên repo blog); `pending-slugs.mjs` trả về 0 bài. Timer đã link vào systemd nhưng không bật. Giữ lại script để dùng khi lại có bài tồn, ví dụ khi đổi `promptVersion` hoặc khi Google AI Studio hết tiền nạp trước.

Lỗi đã gặp khi chạy: bộ kiểm tra của blog hiểu thời lượng "6 tháng" là tháng 6, và khoảng trắng cuối dòng trong danh sách làm lệch cấu trúc Markdown. Cả hai đến từ bộ kiểm tra, không phải từ router.
