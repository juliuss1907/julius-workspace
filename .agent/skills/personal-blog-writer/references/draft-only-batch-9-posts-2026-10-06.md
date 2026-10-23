# Batch 9 bài draft-only (06/10/2026) — xác nhận lại chuỗi, thêm ba bài học

Phiên: brief 15 mục → chọn mục **1, 2, 6, 12, 14, 15** (6 bài) + 3 nguồn đính
kèm = **9 slug**. Yêu cầu chốt là *"Viết xong đăng tất cả draft lên blog"* →
draft-only, không `scheduledAt`.

Chuỗi xác nhận đầy đủ (giống `draft-only-batch-session-2026-10-05.md`, vẫn đúng):

1. `scripts/validate-content.py` trên **cả 9 slug một lượt**, đọc dòng
   `OVERALL: PASS`. Không gọi 9 lần.
2. `npm run build` → exit 0.
3. **Kiểm tra ngược**: cả 9 slug vắng mặt trong `dist/articles/`.
4. `grep -l scheduledAt` rỗng + `grep -H "^draft:"` ra `draft: true` × 9.
5. `git add` **9 tên file tường minh** → `git diff --cached --name-only` đúng 9 dòng.
6. `git push` bị reject (`máy chủ có chứa thay đổi`) → `git pull --rebase -q
   origin main && git push origin main` → `eca8c72..d7e85fd`.
7. Verify remote: `git show origin/main:.../<slug>.md | grep "^draft:"` × 9 → `draft: true`.

## Bài học 1: tên miền làm FAIL cả batch

Bộ đếm báo `missing space` cho `Crypto.com` trong câu "Cách sàn như Coinbase,
Crypto.com, Bitnomial". Đây là false positive đã biết, nhưng để nguyên thì
`OVERALL: FAIL` và cả batch không sạch.

Xử lý đúng ở đây: **viết lại câu cho gọn** chứ không sửa prose đúng về ngữ pháp.
`Nhiều sàn lớn như Coinbase, Bitnomial cùng hai thị trường dự đoán Kalshi và
Polymarket vốn đã đăng ký là DCM.` Vừa né regex, vừa đúng ý (điểm của câu là
*nhóm hẹp hơn DCM*, không phải liệt kê đủ sàn).

Bài học rộng hơn: khi một bài FAIL vì false positive đã biết, đừng bỏ qua và
cũng đừng sửa tới mức méo văn. Viết lại câu ngắn hơn là đường thoát thứ ba.

## Bài học 2: hai bài Decrypt gộp thành một, theo kho bạc có sẵn

Strategy + BitMine là hai URL nhưng một chủ đề (`bao-cao-kho-bac-05-10-2026`).
Trước khi viết, `ls src/content/writing/ | grep -iE "kho-bac|treasury"` cho thấy
đã có `bao-cao-kho-bac-28-09-2026.md` với cùng cấu trúc: **Strategy trước,
BitMine sau**, đóng bằng đoạn "điểm chung là cùng một cơ chế tài trợ".

Đọc bài 28/09 trước khi viết bài mới để giữ đúng format tiêu đề dạng
`Báo cáo kho bạc DD/MM/YYYY: <điều đáng nhớ nhất>` và tránh lặp lại cấu trúc cũ.
Slug theo ngày báo cáo (05-10-2026), không theo ngày đăng.

Chi tiết đáng giữ nhất của phiên này, không có trong bài 28/09: **Strategy
mua 334 BTC (28,7 triệu USD) nhưng mua lại 176,3 triệu USD cổ ưu đãi STRC**,
tức hơn sáu lần. Mới có chi tiết này thì câu kết "tiền đang chảy từ Bitcoin sang
chứng khoán của chính công ty" mới đứng được.

## Bài học 3: trang công bố của chính hãng là nguồn gốc, không phải bài báo

Hai bài trong batch đều thắng rõ khi đọc nguồn gốc thay vì dựa vào tóm tắt
trong brief:

| Bài | Nguồn gốc | Chi tiết chỉ có ở nguồn gốc |
|---|---|---|
| OpenAI watermark | `openai.com/index/eu-text-provenance/` | Bảng 8 dòng benchmark có/không watermark; **thay 25% từ rơi về 17%** (TechCrunch chỉ nêu mức 10% → 66%); mục "watermark không nói được gì" gồm 5 ý |
| ChatGPT cartoonists | `niemanlab.org/...` (AI Weekly chỉ là tóm tắt) | Pat Byrnes ký từ 1998 và **luôn kết dấu chấm**, hơn tá tranh ChatGPT ký tên ông đều có dấu chấm; góc pháp lý Grimmelmann; Baltimore Sun đang đăng tranh AI |

`aiweekly.co/alerts/...` là **tóm tắt có cắt**, không phải nguồn gốc. Đọc bản
gốc phía sau nó (`Originally reported by ...`) trước khi viết bài dựa trên nó.

## Lần này đã làm đủ, không cần hỏi lại

Ba mục bị bỏ có chủ đích theo `draft-only-mode-scope.md` và đã nêu thẳng trong
reply, không im lặng: không `scheduledAt`, không bản sao lưu
`working/Blog/Content/`, không thumbnail. Hai file untracked có sẵn
(`blog-index.md`, `gpt-6-1-sol-near-astra-price.md`) không bị đụng tới.