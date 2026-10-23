---
name: personal-blog-writer
description: "Write Julius personal blog articles (Astro, voice)."
version: 1.1.0
author: Markus (curator)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [blog, writing, astro, content, julius, vietnamese]
    related_skills: [coin68-writer, x-writer-skills]
---

# Personal Blog Writer (Julius)

Write or edit an article in Julius's personal blog
(`ai-labs/projects/personal-blog/`), an Astro static site, in his voice.
Distinct from Coin68 and X — this is his own publication, essay/opinion allowed.

## When to use

- User says "cho vào blog", "viết bài blog", "tóm tắt news này cho blog".
- Summarizing an external link (changelog, product launch, news) into a blog post.

## Location & slug

- Articles live in `src/content/writing/` under the blog project.
- Filename = kebab-case, ASCII only, no Vietnamese diacritics, ≤60 chars.
  Example: `cursor-origin-code-hosting.md`, `glm-5-3.md`.
- Frontmatter is validated at build time by `src/content.config.ts`.

## Frontmatter schema (exact — read content.config.ts if in doubt)

```yaml
---
title: "..."                       # <= 60 chars, never > 70 (see SEO section)
description: "..."                 # 110-155 chars; also shown as the lead paragraph
thumbnail: "/images/x.webp"        # OPTIONAL
thumbnailAlt: "..."                # required IFF thumbnail set
thumbnailCaption: "..."            # optional; requires thumbnail
publishedAt: 2026-08-17
updatedAt: 2026-08-18              # optional
kind: news          # news | essay | opinion
category: crypto    # ai | tech | crypto | finance (blog switched 2026-09-02 from ai-tech/crypto-finance)
featured: false
pinned: false
draft: false
sources: []         # array of URLs (primary source goes here)
readingMinutes: 3   # int, positive
---
```

## Voice (Julius)

- Vietnamese, natural, no machine-translation feel.
- **Fact-first**, then interpretation, then the "so what". Keep the ending on what
  the reader should take away — not a summary repeat.
- **Separate fact / interpretation / speculation** explicitly. Label speculation as
  speculation ("đó vẫn là speculation, không phải điều đã xảy ra").
- Humble, calm, no shill/hype/guru, no "this changes everything" / "end-game".
- Cite the primary source in `sources:`; don't invent facts.
- Khi chuyển brief thành bài, đọc lại nguồn được chọn và ưu tiên thông báo gốc trước khi mở rộng. Brief là danh sách đề tài, không phải bằng chứng; sửa cả tiêu đề, lead và kết luận nếu bản tóm tắt đã làm mất điều kiện hoặc mức độ chắc chắn. Đối chiếu ngày trên nguồn gốc với ngày của bản tin tổng hợp: một cảnh báo mới có thể dẫn nghiên cứu cũ. Nếu vẫn viết đề tài được chọn, nêu ngày công bố thật và không gọi đó là nghiên cứu vừa ra mắt; chỉ dùng mốc mới khi có diễn biến mới được xác minh.
- Giữ đúng trạng thái bằng chứng ngay cạnh số liệu: mục tiêu/kỳ vọng của hãng không phải kết quả đo; định giá dự kiến chưa phải định giá chốt; đề xuất/lộ trình chưa phải quyết định đã thông qua. Với doanh thu quy đổi năm, giải thích cơ sở tính trước khi so sánh; chênh lệch giữa hai con số báo cáo không tự chứng minh doanh thu đã sụt giảm. Với chi tiêu vốn, đọc nguồn số liệu mà bài dẫn, xác định đó là dự kiến hay đã chi và tổng chi tiêu của doanh nghiệp hay phần dành riêng cho AI; không đổi tổng chi tiêu vốn thành tiền đầu tư AI đã thực hiện chỉ vì headline dùng cách gọi ấy.
- **Độ dài tối thiểu 350–500 từ** (đếm theo body, không tính frontmatter). Bài
  ngắn hơn 350 từ phải được mở rộng — bổ sung bối cảnh, so sánh, hoặc phân tích
  để đạt mốc. Mốc 500+ vẫn ổn nếu nội dung có giá trị, không nhồi chữ.
- **Chủ động search thêm thông tin và nâng cấp nguồn gốc**: khi nguồn chính quá ngắn, thiếu bối cảnh,
  hoặc bài báo dẫn liên kết tới thông cáo chính thức của sàn/dự án/cơ quan (như Binance announcement, SEC release, blog lab AI),
  chủ động dùng `web_extract` đọc thông cáo gốc để lấy các mốc kỹ thuật chính xác (giờ UTC, thời hạn rút tiền, điều kiện tài khoản).
  Ghi tất cả URL đã thực sự đọc vào `sources:`. Nếu một URL được gửi bị lỗi 404 hoặc bị chặn, tuyệt đối KHÔNG ghi vào `sources:`,
  và nêu rõ trong báo cáo là link bị lỗi để người dùng nắm được.

## Research cho tin sự kiện và ra mắt sản phẩm

- Khi anh yêu cầu thêm context bên ngoài, đọc thông báo gốc trước, theo các liên kết tài liệu kỹ thuật liên quan, rồi tìm và đọc ít nhất một tường thuật độc lập về cùng sự kiện nếu có. Nhiều blog cùng hãng bổ sung chi tiết nhưng không phải xác minh độc lập; nếu không tìm được nguồn độc lập đọc được, nói rõ giới hạn này.
- Trước khi viết, lập ghi chú trạng thái riêng cho từng tính năng: đã phát hành, preview, mở đặt trước, sắp triển khai; kèm điều kiện thiết bị, thị trường và thời điểm. Không dùng ngày công bố chung để suy tất cả tính năng đã khả dụng.
- Với AI cục bộ, tách nơi chạy mô hình khỏi quyền chạy công cụ và kết nối mạng. Phân biệt tham số tổng/hoạt động, kích thước trọng số/bộ nhớ đỉnh và kết quả hãng đo/kiểm thử độc lập; vì mỗi cặp trả lời một câu hỏi khác nhau về khả năng sử dụng thực tế.
- **Khai thác bài viết dài trên X (X Articles):** Với các bài phân tích dạng X Article (`x.com/i/article/...`), `web_extract` thường báo lỗi do dính lớp bảo vệ của X. Sử dụng `https://api.fxtwitter.com/<user>/status/<id>` qua Python hoặc curl để đọc cấu trúc `tweet.article`. Trường `content.blocks` chứa các đoạn văn bản, và trường `content.entityMap` chứa bảng biểu markdown hoàn chỉnh (`markdown`), giúp trích xuất chính xác bảng số liệu phức tạp mà không bị làm phẳng hay mất cấu trúc cột.

## SEO, GEO và AEO (bắt buộc)

Chi tiết và ví dụ: `references/seo-checklist.md`. `validate-content.py` kiểm tra tự động phần lớn các quy tắc dưới đây và in gợi ý bài liên quan (dòng `related:`).

- **Kiểm tra trùng trước khi viết.** Tìm tên riêng chính của tin trong các bài 10 ngày gần nhất. Cùng sự kiện mà không có thông tin mới thì không viết bài mới; báo anh và đề xuất cập nhật bài cũ. Có diễn biến mới thì viết bài tiếp nối và link về bài cũ. Script cảnh báo `possible duplicate story`; đọc lại cả hai bài trước khi bỏ qua.
- **Tiêu đề tối đa 60 ký tự** (lỗi khi quá 70), tên riêng chính nằm trong nửa đầu, một ý chính.
- **Mô tả 110 đến 155 ký tự** (lỗi khi quá 160), trả lời thẳng ai, làm gì, con số chính. Mô tả hiện trên trang thành đoạn mở đầu, nên đoạn đầu thân bài đi tiếp ý, không lặp lại.
- **Không dùng `#` trong thân bài**: layout đã in tiêu đề thành H1. Bài từ 400 từ có ít nhất 3 heading `##`/`###` để trang hiện mục lục.
- **2 đến 3 link nội bộ** dạng `[cụm từ có sẵn](/articles/<slug>/)`, chỉ tới bài đã đăng, gắn vào câu mà bài đích thật sự giúp người đọc hiểu thêm. Không link tới bản nháp, trừ khi bản nháp đó hẹn giờ đăng trước bài này. Không gắn link vào câu đầu tiên, heading, trích dẫn hay bảng.
- **Đoạn văn tự đứng được**: chủ ngữ đầy đủ ở đầu đoạn, số liệu kèm đơn vị, ngày và nguồn trong cùng câu, vì AI trích từng đoạn.
- **Tin phải có nguồn**: `sources: []` là lỗi với `kind: news`.

## Style guide (bắt buộc đọc trước khi viết)

Trước khi viết bài, đọc style guide: `skill_view(name='personal-blog-writer', file_path='references/blog-style-guide.md')`

Style guide chứa10 quy tắc rút ra từ việc so sánh bản draft và bản đã chỉnh sửa trên edgenotes.net.
Áp dụng cho mọi bài blog (news, essay, opinion). Không bỏ qua bước này.

## Thumbnail rule (hard)

- Never fabricate an image path. If there's no real image, LEAVE `thumbnail` empty
  and tell the user it's missing — they decide whether to add one or have you
  generate it (image-gen). The guideline is WebP 1200x800 in `public/images/`.

### Ba lớp ảnh — không gộp chúng khi báo cáo

- **Ảnh trong bài**: thẻ markdown `![mô tả](url)` cộng một dòng caption in nghiêng ghi nguồn. Được phép khi bài nguồn có ảnh dùng được. Đây là ảnh nhúng trực tiếp từ site nguồn, không phải asset của blog, nên URL có thể hỏng về sau nếu nguồn đổi đường dẫn — nêu rõ đánh đổi này thay vì trình bày như ảnh của blog.
- **`thumbnail` trong frontmatter**: ảnh bìa, phải là asset thật trong `public/images/`. Ảnh trong bài KHÔNG thay thế được; chưa có asset thì vẫn để trống.
- **Quy tắc báo cáo ảnh:** Phân biệt rõ ràng hai lớp này. Tránh ghi cụt ngủn "chưa thêm thumbnail" khi trong bài đã chèn ảnh markdown từ bài nguồn, vì người dùng sẽ thắc mắc bài có ảnh hay chưa. Luôn báo rõ: "Đã chèn ảnh nhúng trong bài (nguồn: ...), chưa có ảnh bìa/thumbnail (để trống trong frontmatter)". Chỉ ghi "chưa thêm ảnh" khi cả hai lớp đều không có.

## From working/Blog/Content (Coin68-style news)

Julius's news flow writes Coin68-voice drafts to `working/Blog/Content/<slug>.md` in the form `## title` + `Meta:` line + body (no frontmatter — see coin68-writer's "AI model launch news → Blog/Content" pitfall). To publish to the Astro blog, convert each into `src/content/writing/`:

- `## title` (H2) → frontmatter `title:`
- `Meta:` one-liner → frontmatter `description:`
- body verbatim (keep bold, Vietnamese, English tech terms, "So what:" endings)
- `kind: news`, `publishedAt` = today (YYYY-MM-DD)
- `category` mapping (blog switched 2026-09-02 from 2 to 4 categories): AI/model/agent/safety/policy → `ai`; hardware/software/internet/security → `tech`; token/stablecoin/exchange/on-chain-security/crypto-regulation → `crypto`; macro/rates/stocks/gold → `finance`. Legacy values `ai-tech`/`crypto-finance` still accepted by normalizeLegacyArticleCategory but use the new 4.
- `sources:` = the primary URL(s) actually read (for an SEC proposal, SEC.gov + the outlet that surfaced it; otherwise the one outlet read)
- `readingMinutes: 2` for ~300-400 word posts
- leave `thumbnail` empty unless a real image exists (see Thumbnail rule)
- use single-quoted YAML for `title`/`description` so inner double quotes (e.g. "Regulation Crypto Assets") and em dashes need no escaping

Then verify: `npm run build` exits 0. For immediate publication (`draft: false`), confirm the slug appears under `dist/articles/<slug>/`; for draft-only or scheduled drafts, confirm it is absent. Do not flip `draft` merely to satisfy a public-route check.

## Scheduled publishing from a news brief (default flow)

Blog có hệ thống schedule gốc (Cloudflare Worker `julius-personal-blog-scheduler`, deploy trên Cloudflare, quét GitHub mỗi phút). Worker tự flip `draft: false` và publish khi đến giờ — KHÔNG dùng cron Hermes cho lịch đăng bài blog.

Quy trình mặc định khi Julius yêu cầu viết news từ một News Brief (sau khi /news-brief-agent chạy xong):

1. **Chọn 4 tin quan trọng nhất** từ brief để viết draft (nếu Julius không chỉ định số lượng/tin cụ thể). Bỏ qua tin blog đã đưa trong 10 ngày gần nhất nếu không có diễn biến mới (xem mục SEO); nêu rõ trong báo cáo tin nào bị bỏ vì trùng.
2. Viết draft như bình thường, nhưng đặt `draft: true` kèm trường `scheduledAt` trong frontmatter:
   - Format bắt buộc (validator sẽ từ chối khác format này): `"YYYY-MM-DDTHH:mm:ss.sssZ"` — ISO UTC đủ mili giây, ví dụ `"2026-08-25T09:00:00.000Z"`.
   - Lịch đăng: bài đầu = thời điểm viết xong + 30 phút (đệm build/push), các bài sau cách nhau đúng 2 giờ.
   - `publishedAt` vẫn là ngày đăng dự kiến (YYYY-MM-DD).
3. Chạy content validation (xem mục **Content validation** bên dưới), sửa nếu FAIL.
4. Build verify (`npm run build`, draft không ra dist là đúng), commit + push từng bài như thường lệ.
5. Sau khi push xong tất cả, **báo cáo với Julius**: danh sách bài, slug, giờ đăng từng bài (quy đổi sang ICT).
6. Tạo bản sao lưu vào `working/Blog/Content/<slug>.md` (đường dẫn chuẩn là `working/Blog/Content/`, không phải `working/blog/content`): dùng script đã đóng gói `python3 /home/julius/julius-workspace/.agent/skills/personal-blog-writer/scripts/backup-to-working-content.py <slug>` (nếu viết trong worktree thì copy file sang repo hoặc truyền `--project <worktree-path>`). Script sẽ tự parse frontmatter, tạo bản sao đúng khối metadata YAML (`- Ngày đăng`, `- Loại bài`, `- Category: #ai|#tech|#crypto|#finance` hashtag, `- Nguồn:`) kèm `## title` + `Meta:` + body, đồng thời thêm wikilink `[[<slug>]]` vào đầu file index `working/Blog/Content/news/news.md`. Bản sao này local-only, không commit.

Lưu ý:
- KHÔNG tạo cron Hermes song song cho các bài đã có `scheduledAt` — trùng lặp cơ chế, dễ publish hai lần.
- Nếu Worker lỗi không tự publish (bài vẫn `draft: true` quá lâu sau giờ hẹn), fallback thủ công: flip `draft: false` rồi build + push như publish tay.
- Kiểm tra worker sống: `npx wrangler deployments list --config wrangler.scheduler.jsonc` từ thư mục personal-blog.

### Chế độ draft-only ("không publish")

Cụm "đăng draft", "đăng lên blog dạng draft" hoặc "KHÔNG publish" kích hoạt draft-only: đặt `draft: true` và bỏ hẳn `scheduledAt`. Commit và push theo quyền được duyệt; không để bài chỉ ở local khi yêu cầu là đưa draft lên blog.

- Khi anh bổ sung một URL hoặc nói "thêm news này" vào batch đang làm, kế thừa chế độ đăng đã chốt của batch. Batch draft-only vẫn dùng `draft: true`, bỏ `scheduledAt`; không áp lại lịch mặc định chỉ vì tin bổ sung không lặp chữ "draft". Chỉ đổi chế độ khi anh yêu cầu rõ.
- Không tự tạo bản sao `working/Blog/Content/` trong chế độ này; backup thuộc luồng publish, trừ khi anh yêu cầu riêng. Khi báo cáo, nói đúng thực trạng: nếu bản sao đã có từ lượt viết theo luồng mặc định trước đó rồi mới chuyển sang draft-only thì ghi là đã có, đừng lặp câu "chưa tạo backup".
- Sau build, xác nhận từng slug **không tồn tại** dưới `dist/articles/`; build thành công không đủ chứng minh bài còn là draft.
- Sau push, chạy `git fetch origin`, đọc từng file bằng `git show origin/main:src/content/writing/<slug>.md`, parse YAML và xác nhận `draft === true`, không có khóa `scheduledAt`, nội dung khớp bản đã kiểm tra. Ưu tiên parse YAML bằng Node (`node -e 'const yaml = require("js-yaml"); ...'`) vì `personal-blog` có sẵn `js-yaml` trong `node_modules`, tránh gọi Python khi môi trường có thể thiếu `pyyaml`. Đối chiếu tập file với danh sách tin được yêu cầu, không chỉ đếm tổng.
- Báo cáo bảng số tin → slug → category → số từ body, commit và trạng thái draft-only. Không dùng link bài công khai để chứng minh một draft đã lên repo.

Chi tiết phạm vi: `references/draft-only-mode-scope.md`.

### Đăng lại các draft đã viết ở lượt trước ("đăng các bài draft của ngày X")

Yêu cầu dạng này thường KHÔNG cần viết bài mới: bài đã tồn tại, chỉ chưa lên remote. Đừng kết luận "không có gì để đăng" chỉ vì `git status` của repo sạch — draft do lượt trước viết có thể còn untracked trong một bản clone tạm của repo (`.hermes/cache/scratch/<clone>/src/content/writing/`).

1. Tìm draft của ngày đó ở phạm vi workspace, không chỉ trong repo: quét file `.md` sửa trong ngày và grep `publishedAt: <YYYY-MM-DD>` (bỏ `node_modules`, `.git`).
2. Đối chiếu từng slug với `origin/main` — slug nào chưa có trên remote mới là việc cần làm. Đọc cả tập file, không chỉ đếm.
   - **Bẫy file đã bị xóa trên remote:** Không tự động coi mọi file có trong local/scratch nhưng vắng mặt trên `origin/main` là bài sót cần đẩy lên. Kiểm tra `git log -5 origin/main` hoặc `git log --diff-filter=D -1 origin/main -- <path>`. Nếu file vừa bị xóa trên remote, đó là hành động xóa có chủ đích của người dùng (ví dụ: xóa bản cũ để viết lại với nguồn mới); tuyệt đối không tự hồi sinh file đã xóa. Nếu người dùng vừa đính kèm liên kết/yêu cầu viết mới trước khi phiên bị gián đoạn, viết bản mới theo nguồn mới thay vì nhặt lại file cũ.
3. Copy đúng tập file đó sang repo thật, chạy content validation, build, rồi stage **chỉ** các path đó và đối chiếu `git diff --cached --name-only` với tập slug.
4. Giữ `draft: true`, bỏ `scheduledAt` khi yêu cầu là "dưới dạng draft"; xác nhận slug vắng mặt trong `dist/articles/`, push `HEAD:main`, rồi đọc lại file trên `origin/main` để xác nhận trạng thái và nội dung khớp.
5. Báo cáo kèm bảng tin → slug → category → số từ, và nói rõ lượt này chỉ kiểm tra + đẩy bản có sẵn hay có viết lại nội dung. Nguồn trong frontmatter là bản ghi từ lượt viết trước nếu lượt này không đọc lại chúng — nói thẳng giới hạn đó thay vì để hiểu là đã xác minh.

Lệnh tìm draft và recipe publish từ worktree: `references/draft-only-mode-scope.md`.

**Yêu cầu không nhắc gì tới việc đăng** ("Viết news 1, 10, 11, 13 kèm thêm news: ...") vẫn đi **luồng mặc định** ở trên: `draft: true` + `scheduledAt`. Tín hiệu chuyển sang draft-only là chữ "draft" hoặc một phủ định ("KHÔNG publish"); thiếu tín hiệu KHÔNG phải draft-only. Chốt luồng mặc định rồi chạy tiếp — đừng dừng lại hỏi Julius, cũng đừng tự hạ xuống draft-only cho "an toàn", vì im lặng là dạng phổ biến nhất của yêu cầu brief → blog nên coi là mơ hồ sẽ chặn mọi batch. Chỉ cần nêu rõ trong report: "tôi đi luồng mặc định (tự đăng theo lịch); muốn để nguyên draft thì nói một câu là tôi bỏ `scheduledAt`" — đổi lại chỉ tốn một lượt.

## Verify giá đối thủ qua docs chính thức

Bảng giá dễ sai nhất ở chỗ nhầm tên model trong cùng một hệ sinh thái. Observed 30/09/2026: viết Claude Opus 5.5 là 2/20 trong khi đó là giá của Sonnet 5.5; Opus 5.5 thật sự là 4/20 (nguồn: `platform.claude.com/docs/en/models/opus-5-5/overview`).

Trước khi điền bất kỳ hàng giá nào không lấy trực tiếp từ trang công bố của hãng đó, hãy mở docs chính thức và đọc bảng giá. Tìm kết quả từ blog review hoặc site so sánh giá thì không đủ, vì chúng hay gộp nhầm các model cùng hệ sinh thái. Bảng giá chỉ nên đưa vào bài khi bài đó thực sự cần so sánh; với tin không liên quan giá thì bỏ qua.

## Content validation (mandatory, pre-build)

SAU khi viết file xong, TRƯỚC khi `npm run build`, chạy content validation.

- Load reference: `skill_view(name='personal-blog-writer', file_path='references/content-validation.md')`
- Dùng script đã đóng gói, không chép lại bộ kiểm tra trong reference: `python3 /home/julius/julius-workspace/.agent/skills/personal-blog-writer/scripts/validate-content.py src/content/writing/<slug>.md [các file khác]`. Chạy một lượt trên đúng tập bài mới; có thể gọi terminal qua `execute_code`.
- Đọc từng cảnh báo thủ công: dấu phẩy trước "và" trong câu ghép không nhất thiết là lỗi liệt kê. Không bỏ dấu phẩy chỉ để làm sạch cảnh báo.
- **Dấu chấm trong từ viết tắt tiếng Anh (U.S., e.g., i.e.) và lỗi câu ngắn (< 5 từ):** Tokenizer tách câu của validator dùng dấu chấm kèm khoảng trắng để nhận diện ranh giới câu. Khi gặp từ viết tắt có dấu chấm như `U.S. Stablecoins` hoặc `U.S. dollar`, dấu chấm sau `S.` bị hiểu nhầm là kết thúc câu, biến cụm từ đi sau (như `Stablecoins (GENIUS) Act`) thành một câu cụt 2-3 từ và kích hoạt lỗi `error: short sentence (< 5 words)`. Cách xử lý: không dùng dấu chấm trong viết tắt tiếng Anh trong văn xuôi tiếng Việt — viết `US`, hoặc dùng từ tiếng Việt tự nhiên (`Mỹ`, `ví dụ như` thay vì `e.g.`, `tức là` thay vì `i.e.`).
- **Tên dự án dạng domain, hậu tố pháp lý và lỗi thiếu khoảng trắng:** Các tên riêng chứa dấu chấm như `io.net`, `dydx.exchange`, `Binance.US`, `FTX.US` sẽ kích hoạt regex `missing space after punctuation` do chữ cái thường trước dấu chấm và chữ cái liền sau. Không xóa hay viết sai tên chuẩn; hãy định dạng chúng thành liên kết markdown có URL đầy đủ như `[Binance.US](https://binance.us)` hoặc `[io.net](https://io.net)` (trình kiểm tra tự động bỏ qua các dòng có URL hợp lệ nhờ regex `HAS_URL`), hoặc dùng tên thương hiệu không có dấu chấm như `Binance US` khi không cần đặt link.
- **Ký tự en-dash (–) và em-dash (—):** Validator kiểm tra nghiêm ngặt và sẽ FAIL nếu văn xuôi chứa en-dash (U+2013) hoặc em-dash (U+2014), kể cả trong tên thuật ngữ / người ghép (ví dụ `Lenstra-Lenstra-Lovasz` thay vì dùng en-dash) hoặc các cặp từ đối lập (`đúng và sai` thay vì `đúng–sai`). Hãy dùng gạch nối tiêu chuẩn ASCII (`-`) hoặc diễn đạt bằng từ liên kết.
- **Lỗi SEO** (tiêu đề, mô tả, H1, nguồn, link nội bộ) sửa như mọi lỗi khác. Chọn link từ các dòng `related:` nhưng phải mở bài đích để kiểm tra; điểm số của script chỉ dựa trên tên riêng chung.
- Đối chiếu khẳng định với nguồn trước khi build; PASS của script chỉ xác nhận hình thức và độ dài, không xác nhận tính đúng của tin.
- Nếu FAIL: sửa từng vấn đề, chạy lại cho đến khi PASS
- Nếu PASS: proceed to build

Không bỏ qua bước này. Bài không qua validation không được commit.

## Verify

- `cd ai-labs/projects/personal-blog && npx vitest run tests/internal-links.test.ts` khi file test này có trong repo: nó bắt link nội bộ hỏng, link tới chính bài và link tới bài đã disable.
- `cd ai-labs/projects/personal-blog && npm run build` (validates frontmatter; đặt timeout terminal tối thiểu 300s vì bước tạo ảnh OG cho 380+ bài mất ~2.5 - 3 phút).
- `npm run dev` for the CMS/preview.

## Sửa bài đã có và bản draft CMS

1. Trước khi sửa một slug đã có, fetch remote và đọc cả `origin/main:src/content/writing/<slug>.md` lẫn `origin/cms/<slug>:src/content/writing/<slug>.md` nếu nhánh CMS tồn tại. Chọn đúng phiên bản đang được biên tập; không mặc định `main` là bản mới nhất.
2. Nếu hai bản khác nhau và yêu cầu chưa chỉ rõ nơi sửa, xác nhận với anh trước khi ghi. Khi anh chọn bản CMS, tách worktree từ chính `origin/cms/<slug>`, giữ nguyên phần anh chỉnh, ảnh, embed và trạng thái đăng; push lại đúng nhánh đó, không tự merge hoặc publish lên `main`.
3. Với yêu cầu thêm một đoạn, patch đúng vị trí thay vì viết lại toàn bài. Đọc nguồn bổ sung, thêm URL đã đọc và rà các câu cũ liên quan để tránh mâu thuẫn với bằng chứng mới; không sửa lan sang kết bài hay bản dịch nếu chưa được yêu cầu.
4. Sau push, fetch và đọc lại file trên **đúng nhánh đích**, xác nhận nội dung khớp cùng trạng thái draft/lịch đăng. Báo rõ sửa ở CMS hay `main`; push lên nhánh CMS không chứng minh editor đang mở đã tải bản mới.
5. **Asset ảnh tải lên từ CMS:** CMS commit ảnh WebP vào `public/images/articles/<slug>/` trên nhánh CMS. Nếu đồng bộ nội dung từ nhánh CMS sang `main`, phải kiểm tra và mang theo toàn bộ asset trong thư mục ảnh đó (`git restore --source=<cms-branch> -- public/images/articles/<slug>/`), không chỉ copy riêng file markdown để tránh lỗi 404/broken link.

Chi tiết thao tác đồng thời và phân biệt dữ liệu Git với bản lưu trong trình duyệt: `references/cms-github-draft-conflict.md`.

## Commit

personal-blog is its OWN standalone git repo — nested under julius-workspace but with its own `.git` and remote `git@github.com:juliuss1907/the-blog-of-julius.git` (`git rev-parse --show-toplevel` resolves to `ai-labs/projects/personal-blog`, NOT the workspace root). Run `git` from inside the project dir.

- Trước khi viết, kiểm tra nhánh, working tree và `origin/main`. Luôn ưu tiên tách worktree độc lập từ `origin/main` (`git worktree add --detach <scratch>/<worktree-name> origin/main` kèm symlink `node_modules`). Thao tác này cách ly hoàn toàn khỏi nhánh CMS, đồng thời ngăn ngừa rủi ro đẩy nhầm các commit thử nghiệm chưa hoàn thiện trên nhánh `main` nội bộ (khi local `main` đang ahead `origin/main`) lên remote khi chạy `git push`. Recipe chi tiết: `references/cms-branch-and-concurrent-edit-2026-09-30.md`, mục worktree.
- Stage ONLY the new `.md` — never `git add .`. Verify with `git diff --cached --name-only` and compare the exact staged path set with the requested slug set; equal counts alone do not prove correct scope.
- Khi push bị `fetch first`, chạy `git fetch origin`, kiểm tra thay đổi remote rồi `git rebase origin/main` trong worktree bài mới. Nếu có sửa giao nhau, giải quyết hoặc hỏi trước khi tiếp tục; slug mới không bảo đảm toàn bộ rebase không xung đột. Chạy lại validation/build trên trạng thái sau rebase, rồi `git push origin HEAD:main` — cú pháp này dùng được cả khi worktree ở detached HEAD. Fetch và đọc lại đúng file remote trước khi báo hoàn tất; build trước rebase chưa kiểm tra mã vừa nhận từ remote.
- Misread trap: `git diff --name-only HEAD origin/main` lists files differing in EITHER direction, so your own new files appear in it even though they do NOT exist upstream. To confirm a slug isn't a duplicate, run `git show origin/main:<slug>.md` — "exists on disk but not in origin/main" means local-only, not a remote duplicate.

## Pitfalls

- **Batch publish: write ONLY the items the user asked for.** When converting a news brief into posts ("viết news 2, 3, 4, 8, 10 và 12"), list the exact requested numbers → slugs BEFORE writing, then verify the written set against the request before committing. Observed failure: 3 unrequested posts were written alongside the 6 requested and had to be rescued by setting `draft: true` before push plus a disclosure to Julius. Rescue order if it happens: `draft: true` the extras, disclose plainly, offer deletion.
- **English-term density triggers a full rewrite**: stacking English terms in Vietnamese prose (output token, power user, adoption, cached tokens, traffic, traction...) made Julius demand a rewrite ("Có nhiều thuật ngữ tiếng Anh quá"). First pass rule: keep only unavoidable terms (token, agent AI, LLM, product names like Codex/Zapier) and translate the rest naturally — bộ nhớ đệm (cache), nạp trước (pre-fill), lượng truy cập (traffic), nhóm dùng mạnh/nhóm dẫn đầu (power user/top decile). One short gloss in parentheses on first use is fine; stacking is not.
- **Long single writes can time out mid-stream**: very large write_file payloads (multi-KB article bodies, several articles in one turn) have hit stream timeouts twice in one session. Write ONE file per call, keep each call small; make follow-up edits with patch instead of rewriting whole files.
- **YAML frontmatter apostrophe trap**: single-quoted YAML (`title: '...'`) breaks when the title contains an apostrophe (e.g. "We're Back"). The `\'` escape is NOT valid in YAML single-quoted strings — the `'` before `re` terminates the string early, causing a js-yaml parse error during build. Fix: use double-quoted YAML with `\"` escapes for inner double quotes, or rephrase the title to avoid apostrophes. Observed 2026-08-31 on `strategy-bitcoin-saylor-return.md`.
- **Cloudflare Pages deploy lag (~1-2 min)**: after `git push`, the new article returns 404 for 1-2 minutes while Pages rebuilds. Do NOT immediately report "article not found" to Julius. Wait 30-60s, then verify via `curl -sL "https://edgenotes.net/articles/<slug>/"` or check the sitemap at `https://edgenotes.net/sitemap-0.xml` (the old `the-blog-of-julius.pages.dev` host only 308-redirects to edgenotes.net now). Hard refresh (Ctrl+Shift+R) if the user sees an old version. Observed on 2026-08-29 (avici slot) and 2026-08-31 (rain-cards).
- **`working/Blog/` is NOT git-tracked in the workspace repo** (verified 2026-08-29): under `working/` only `clients/`, `Coin68/`, `Substack/`, `X/` are tracked — the entire `Blog/` subtree shows as `??` in `git status`. Backup copies + index updates in `working/Blog/Content/` are local-only by design: do NOT stage/commit them, and do NOT treat a `?? working/Blog/Content/news/` status as something to fix. Only the personal-blog repo (`src/content/writing/`) gets committed and pushed.
 - **Never reconstruct a source URL you did not load**: `sources:` is a record of what you actually read, so when a piece arrived through a syndication host (`finance.yahoo.com`, `cryptonews.net`, `panews.io`) that host's URL is the correct entry, not the publisher's. Building the publisher's canonical URL from a plausible slug produces a fabricated citation that looks identical to a real one at commit time and only 404s later. Rule: every URL in `sources:` must be one you passed to `web_extract` this session. Detail: `references/blocked-primary-sources-and-figure-selection.md`.