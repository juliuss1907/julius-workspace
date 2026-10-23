# SEO, GEO và AEO cho bài blog

Rút ra từ đợt rà soát edgenotes.net ngày 22/10/2026. Trên 350 bài, có 321 bài không có link sang bài khác trong thân bài, trung vị mô tả 184 ký tự, trung vị thẻ title 90 ký tự, 2 cặp bài trùng tin và 1 bài có H1 thứ hai. Mỗi quy tắc dưới đây sửa đúng một lỗi đã gặp. `validate-content.py` kiểm tra tự động các mục có ghi **[script]**.

GEO (Generative Engine Optimization) và AEO (Answer Engine Optimization) là việc tối ưu để ChatGPT, Perplexity hay AI Overviews của Google chọn trích dẫn bài. Hai loại công cụ này ưa cùng một kiểu bài như Google: trả lời thẳng, số liệu có ngày và nguồn, đoạn văn đọc riêng vẫn hiểu.

## 1. Tiêu đề **[script]**

- Tối đa 60 ký tự, không bao giờ quá 70. Thẻ title trên trang còn cộng thêm ` | Edge Notes` (13 ký tự), và Google cắt ở khoảng 60.
- Đặt tên riêng chính (công ty, sản phẩm, model, mã token) trong nửa đầu: người tìm gõ tên riêng trước.
- Một ý chính. Ý phụ chuyển xuống mô tả. Không giật tít, không dùng câu hỏi tu từ.

**Sai (85 ký tự):** `Anthropic đàm phán thêm thỏa thuận 45 tỷ USD với Nscale giữa sóng gió nợ vay neocloud`
**Đúng (54 ký tự):** `Anthropic đàm phán hợp đồng 45 tỷ USD thứ hai với Nscale`

## 2. Mô tả (`description`) **[script]**

- 110 đến 155 ký tự, một hoặc hai câu. Quá 160 ký tự là lỗi.
- Mô tả được dùng ở ba chỗ: thẻ meta description, thẻ OG khi chia sẻ link, và **đoạn mở đầu in đậm trên trang** (`ArticleLayout` in nó ngay dưới tiêu đề).
- Trả lời thẳng câu hỏi: ai, làm gì, con số chính, khi nào. Đây là câu AI hay trích nguyên văn.
- Vì mô tả đã hiện ngay trên trang, đoạn đầu thân bài không lặp lại nó mà đi tiếp ý. Script cảnh báo khi hai đoạn giống nhau từ 60% trở lên.

## 3. Slug

- ASCII, kebab-case, tối đa 60 ký tự (quy tắc chung của workspace), chứa tên riêng chính.
- Không đổi slug sau khi đã đăng. Nếu buộc phải đổi, thêm chuyển hướng 301 vào `public/_redirects`.

## 4. Cấu trúc bài **[script]**

- **Không dùng `#` (H1) trong thân bài.** Layout đã in tiêu đề thành H1; thân bài bắt đầu từ `##`.
- Bài từ 400 từ trở lên có ít nhất 3 heading `##`/`###`: đủ 3 thì trang tự hiện mục lục. Heading mô tả ý, theo quy tắc 2 của style guide.
- Mỗi đoạn tự đứng được: câu đầu đoạn nêu chủ ngữ đầy đủ ("Nscale", không phải "Công ty này"), số liệu đi kèm đơn vị, ngày và nguồn trong cùng câu. AI trích từng đoạn, không đọc cả bài.

## 5. Link nội bộ **[script]**

Mỗi bài có **2 đến 3 link** sang bài đã đăng trên blog, tối đa 5.

- Cú pháp: `[cụm từ có sẵn trong câu](/articles/<slug>/)`. Luôn dùng đường dẫn tương đối `/articles/...`, kể cả khi bài liên quan đã có bản tiếng Anh. Bản tiếng Anh tự đổi link sang `/en/articles/...` lúc build, còn bộ dịch yêu cầu URL giữ nguyên.
- Chọn bài: đọc các dòng `related:` mà script in ra, rồi mở bài đích để chắc nó giúp người đọc **đúng câu đó**: bối cảnh, diễn biến trước, bài tiếp nối, hoặc bài giải thích thuật ngữ. Trùng chủ đề thôi là chưa đủ.
- Chữ gắn link: cụm 2 đến 8 chữ mô tả bài đích, ví dụ "thỏa thuận 45 tỷ USD đầu tiên với Nscale". Không dùng "tại đây", "bài viết này", một con số đứng riêng, hay tên công ty mà cả bài đang nói tới.
- Không đặt link trong câu đầu tiên, heading, trích dẫn hay bảng. Mỗi bài đích chỉ link một lần, mỗi đoạn tối đa một link.
- **Bẫy bài nháp:** chỉ link tới bài đã đăng (`draft: false`). Bài đích là bản nháp chỉ được chấp nhận khi cả hai bài cùng hẹn giờ và bài đích đăng trước hoặc cùng lúc (`scheduledAt` sớm hơn hoặc bằng). Nếu không, link sẽ hỏng khi bài nguồn lên trước, và `tests/internal-links.test.ts` sẽ làm workflow dịch thất bại.
- Link về bài cũ là bình thường. Khi viết tin tiếp nối, có thể đề xuất thêm link từ bài cũ sang bài mới, nhưng sửa bài cũ là việc riêng, phải được anh đồng ý. Bài cũ có bản dịch tiếng Anh còn khớp thì phải sửa cả bản tiếng Anh và `sourceHash`, theo `scripts/internal-links/apply.mjs`.

## 6. Kiểm tra trùng tin **[script]**

Trước khi viết một tin từ brief, tìm xem blog đã đưa tin này chưa:

```bash
grep -il "<tên riêng chính>" src/content/writing/*.md | xargs grep -l "publishedAt: 2026-10-1"   # đổi theo tháng hiện tại
```

Sau khi viết, script cảnh báo `possible duplicate story` khi một bài trong vòng 10 ngày có tiêu đề giống từ 50% trở lên, hoặc chung từ 3 điểm tên riêng hiếm kèm tiêu đề giống từ 30%. Đây là cảnh báo để **đọc lại**, không tự động là trùng; chuỗi báo cáo kho bạc hàng tuần chẳng hạn sẽ luôn bị cảnh báo.

- Cùng một sự kiện, không có thông tin mới: không viết bài mới. Báo anh và đề xuất cập nhật bài cũ (thêm `updatedAt`).
- Có diễn biến mới: viết bài tiếp nối, nói rõ phần mới trong tiêu đề và mô tả, và link về bài cũ ngay đoạn nhắc tới diễn biến trước.
- Nếu hai bài trùng đã cùng lên: giữ bài mới hơn, thêm slug bài cũ vào `src/content/disabled-articles.json` (đây cũng là nút Disable của CMS), và thêm chuyển hướng 301 trong `public/_redirects` cho `/articles/<slug>`, `/articles/<slug>/` và hai URL `/en/` tương ứng nếu có bản dịch.

## 7. Nguồn **[script]**

- Tin (`kind: news`) phải có ít nhất một nguồn trong `sources:`; để trống là lỗi. Với essay và opinion, để trống chỉ bị cảnh báo, nhưng có số liệu thì vẫn phải ghi nguồn.
- Trang bài in danh sách nguồn ở cuối bài và đưa vào JSON-LD `citation`. Đó là tín hiệu tin cậy mà cả Google lẫn AI đều đọc.

## 8. Ảnh

- `thumbnailAlt` mô tả nội dung ảnh, không lặp lại tiêu đề. Ảnh trong bài có alt và một dòng chú thích ghi nguồn.

## Khi script báo lỗi trên bài cũ

Các kiểm tra SEO áp dụng cho bài **mới hoặc đang sửa**. Gần như mọi bài cũ đều FAIL vì thiếu link nội bộ và có mô tả dài. Đừng tự sửa hàng loạt bài cũ để script hết báo: link nội bộ cho bài cũ được làm theo đợt (xem `internal-links-for-codex.md` trong repo blog). Với bản sao lưu nằm ngoài `src/content/writing`, chạy kèm `--no-seo`.
