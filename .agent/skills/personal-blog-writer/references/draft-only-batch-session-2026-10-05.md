# Draft-only batch: verification chain and reference grounding (05/10/2026)

Bổ sung cho `references/draft-only-mode-scope.md` (phạm vi draft-only) và
`references/README-scripts-first.md` (dùng script có sẵn). Ghi lại một phiên
4 bài draft-only chạy trơn tru, để lần sau có mẫu kiểm chứng cụ thể.

## Yêu cầu: "viết news 1, 3, 5 và 13 và đăng draft lên blog"

Đây là draft-only (chữ "draft" có mặt). 4 slug, `draft: true`, **không**
`scheduledAt`, commit + push vẫn bắt buộc.

## Chuỗi kiểm chứng đầy đủ cho draft-only

1. `validate-content.py` trên cả N slug một lượt (nhiều file, một lệnh).
2. `npm run build` → exit 0.
3. **Kiểm tra ngược**: slug phải VẮNG mặt trong `dist/articles/`.
4. **Kiểm tra không lên lịch**: `grep -l scheduledAt <files>` phải rỗng, và
   `grep -H "^draft:" <files>` phải ra `draft: true` cho tất cả.
5. `git diff --cached --name-only` phải đúng N dòng, đúng slug đã yêu cầu.
6. Sau push: `git show origin/main:src/content/writing/<slug>.md` cho từng slug.

Bước 3 và 4 là phần hay bị bỏ. Chỉ `build exit 0` KHÔNG chứng minh được draft-only
đúng, vì `draft: false` sót cũng build exit 0.

## File `??` có sẵn trong `src/content/writing/`

Phiên này có 2 file untracked từ trước (`blog-index.md`,
`gpt-6-1-sol-near-astra-price.md`) không phải do mình tạo. Công việc đúng:

- Stage bằng **tên file tường minh**, không `git add .` không `git add src/content/writing/`.
- Không sửa, không xoá, không commit chúng.
- Nêu lại trong reply để Julius biết chúng vẫn nằm đó và không bị đụng tới.

## Push bị từ chối: rebase là chuẩn, không phải sự cố

`git push` bị từ chối vì remote tiến trước giữa phiên. `git pull --rebase origin main
&& git push origin main` xử lý xong ngay. Không cần dừng lại hỏi Julius: rebase an toàn
vì mỗi bài dùng slug duy nhất, không có va chạm tên file.

## Triage cảnh báo Oxford comma

Script báo kiểu `warn: N line(s) with a comma before 'và'/'and'` cho cả 4 bài
(2-5 dòng mỗi bài). Đọc từng dòng thì phần lớn là mệnh đề ghép tiếng Việt và **giữ
nguyên**. Nhưng đừng bỏ cả nhóm: ở bài này có đúng một dòng là serial list thật
("môi trường có luật, model tự tìm cách vượt luật, và việc phát hiện...") và đã sửa.

Quy tắc: warn ≠ im lặng. Đọc từng dòng, sửa dòng là danh sách liệt kê thật, giữ mệnh
đề ghép. Xem `references/oxford-comma-vietnamese-false-positive.md`.

## Nâng brief item lên nguồn gốc: bốn hình dạng đã dùng

Bốn bài, bốn nguồn gốc khác nhau, tất cả đều đọc được:

| Tin | Nguồn gốc lấy thêm | Bài học |
|---|---|---|
| Super Intelligence Force | TechCrunch (đầy đủ) | Nguồn thứ cấp trong brief chỉ có tên người; outlet đầy đủ có **điều lệ lực lượng** và mốc 120 ngày, đó mới là phần đáng viết |
| GPT-6 Astra gian lận | Trang benchmark `starskirmish.com/bench` | **Trang của chính benchmark là nguồn gốc số liệu**, không phải bài báo. Lấy thang điểm, số ván đấu, tỉ lệ thắng, và điểm mấu chốt (Stardust thắng Astra mọi lần) |
| Altman vs Anthropic | Politico trực tiếp | Phần quan trọng nhất nằm ở **chi tiết bản tóm tắt bỏ**: hai bên đã gần nhau, OpenAI đã đồng ý giảm tốc và ủng hộ luật tiểu bang. Câu hỏi về mức can thiệp chưa được trả lời bằng ngưỡng cụ thể |
| AMD chia tải agent | Bài gốc Newsbytes.PH | Excerpt trong brief cắt mất phần định lượng: mức tải 5,7 triệu token vào/574.000 token ra, và so sánh 6.533 USD vs 81.108 USD |

Bổ sung vào `references/brief-item-to-primary-source-upgrade.md`:

**Đích thứ năm: trang chủ của chính hệ thống đo.** Khi tin là "model X làm Y trong
benchmark Z", trang của Z có bảng điểm gốc, điều kiện chạy và thang đo. Bài báo
chỉ kể cốt truyện, trang benchmark cho con số.

**Antibot không phải kết thúc chuỗi.** Kotaku chặn (`document_antibot`). Đừng bỏ
tin: (a) outlet đã trích nguyên văn — The Verge tóm tắt chi tiết hành vi gian lận,
(b) nguồn gốc bài báo dẫn tới — các bài đăng X của người tạo benchmark, (c) trang
gốc của hệ thống. Ba tầng này cộng lại đủ để viết bài có chi tiết cơ chế mà không
cần đọc được trang bị chặn. Ghi rõ trong report rằng nguồn nào bị chặn.

## Nối bài chéo trong cùng batch

Hai bài cùng nói về Super Intelligence (bài 1 và bài 5). Bài 5 **trỏ ngược** về bài
1 thay vì kể lại chuyện đổi thuật ngữ hay điều lệ. Cùng lúc, bài 1 nối tới bài đã có
(`ten-mien-si-super-intelligence.md`) bằng một câu về sắc lệnh đổi thuật ngữ. Đây là
`references/cross-article-consistency-grounding.md` áp dụng cho batch draft-only.

## Phần chưa làm phải nêu thẳng

Ba mục dưới đây đều bị bỏ có chủ đích trong draft-only, và cả ba đều phải nói ra
trong reply thay vì im lặng:

1. Bản sao lưu `working/Blog/Content/` + wikilink `news.md` (bài chưa lên blog).
2. Thumbnail (không có ảnh thật, không được bịa path).
3. Lịch đăng (chưa set `scheduledAt`).

Nêu cả ba cùng lúc, kèm đường dẫn script `backup-to-working-content.py` cho mục 1.