# Nguồn chính bị chặn và cách chọn con số — 2026-09-29

Bổ sung cho `references/source-discovery-and-verification.md`. Áp dụng khi viết
news có nguồn Reuters/Forbes (bị chặn) hoặc có số liệu tài chính từ nhiều outlet.

## Reuters và Forbes chặn scraper, nhưng tin vẫn viết được

`web_extract` trả `document_antibot` cho reuters.com và forbes.com. Đây là antibot
phía server, KHÔNG phải lỗi cấu hình và KHÔNG phải lý do để bỏ tin. Bản syndication
giữ nguyên văn bản gốc, chỉ bị bọc thêm quảng cáo.

| Nguồn gốc | URL syndication đã xác nhận đọc được (2026-09-29) |
|---|---|
| reuters.com (business/finance) | `finance.yahoo.com/technology/ai/articles/exclusive-<slug>-<id>.html` |
| reuters.com (mục khác) | `devdiscourse.com/article/international/<id>-<slug>` |
| reuters.com (risk/safety) | `livemint.com/technology/exclusive<reuters-headline>-<id>.html` |
| forbes.com | `livemint.com/companies/people/<headline>-<id>.html`, `benzinga.com`, `tldrdailynews.com` |

Cách tìm: `web_search("<tiêu đề Reuters đầy đủ>")` rồi đọc description của kết quả —
snippet thường đã chứa các con số chính. Bản syndication dài cũng giữ lại các link
dẫn chéo ở giữa bài (hai bài Reuters cùng chủ đề được dẫn chéo), đọc kỹ vì có chi
tiết bản gốc mà snippet không có.

Quy tắc bất biến: `sources:` chỉ ghi URL **thực sự đọc được**, và reply phải nói
thẳng "link Reuters bị chặn, tôi dùng bản syndication". Không ghi URL không đọc.

## Khi Julius tải bản gốc về dạng attachment

Khi Reuters/Forbes bị chặn, Julius đôi khi tải trang về rồi gửi file `.md` export
trong `.hermes/attachments/`. Đây là bản gốc đáng tin hơn mọi bản syndication.
Khi nhận được:

1. Đọc file attachment TRƯỚC, đối chiếu từng con số đang có trong draft.
2. Bản gốc thường có chi tiết mà syndication cắt mất, và chi tiết đó có thể đảo
   ngược cách hiểu cả bài. Quan sát 2026-09-29:
   - Bài AMD: syndication (CNBC + press release) thiếu câu "World Labs raised
     $1 billion earlier this year including an investment from AMD". Chi tiết này
     biến thương vụ từ "hai công ty bất ngờ gặp nhau" thành "AMD nâng mức đầu tư
     lên mức mua cả công ty".
   - Bài IPO Anthropic: syndication thiếu mối Amazon + Google vừa là nhà cung cấp
     hạ tầng đám mây vừa là nhà đầu tư, tức một phần lớn trong 518 tỷ USD cam kết
     quay về dòng tiền của chính những bên đang tài trợ. Đây là điểm phân tích đáng
     kể nhất của bài.
3. Thêm URL canonical (bản reuters.com) vào `sources:`, đặt đầu danh sách — nhưng chỉ
   khi URL đó có thật trong tay (attachment Julius gửi, hoặc kết quả search trả về).
   KHÔNG dựng lại URL canonical từ slug đoán. URL đoán sai trả 404, và `sources:` là
   bản ghi những gì đã đọc, không phải danh sách nguồn mong muốn. Khi chỉ đọc được bản
   syndication, ghi đúng URL syndication (`finance.yahoo.com`, `cryptonews.net`,
   `panews.io`) và nói rõ trong reply rằng nguồn gốc bị chặn.
4. Chạy lại validation + build + push, đồng bộ lại backup `working/Blog/Content/`.

## Con số tài chính: chọn phiên gần nhất, không cộng dồn

Khi nhiều outlet đưa hai mốc khác nhau cho cùng một biến động (Yahoo: giảm
8,9 tỷ USD thứ Sáu; Livemint: thêm 10,9 tỷ USD thứ Hai, tổng "gần 20 tỷ USD"):

- **Tiêu đề và đoạn mở dùng con số của phiên gần nhất** ("gần 11 tỷ USD ngày
  28/09"). Quan sát 2026-09-29: Julius yêu cầu sửa khi tôi để tổng hai phiên
  trong tiêu đề.
- Phiên trước giữ trong thân bài, đóng vai trò "mồi lửa" (ví dụ báo cáo Goldman
  phát hành thứ Sáu 25/09 mới là nguyên nhân cú giảm thứ Hai).
- Nếu thật sự mâu thuẫn không hòa giải được, nêu rõ trong bài và trong reply,
  đừng tự chọn một bên im lặng.

## Đừng viết lại tiếng Việt đúng chỉ để làm im bộ đếm

Bộ đếm Oxford comma (`oxford_count > 2`) gần như luôn bắn khi viết batch 4 bài vì
dấu phẩy nối hai mệnh đề là cách viết đúng của tiếng Việt. Quy trình đúng:

1. In tất cả dòng khớp regex trong một lần, đọc một mạch.
2. Nếu tất cả đều là mệnh đề ghép (không phải danh sách A, B, và C) → false
   positive, đi thẳng sang build.
3. Chỉ sửa khi có đúng một danh sách nối tiếp.

Sửa prose vốn đúng chỉ để làm im bộ đếm tốn vòng patch và dễ sinh lỗi chính tả mới.

```bash
python3 - <<'PY'
import re
for i,l in enumerate(open(p).read().splitlines(),1):
    for m in re.finditer(r'.{0,60},\s*(và|and)\s.{0,40}',l,re.I):
        print(f'L{i}: ...{m.group(0)}...')
PY
```

Áp dụng cho mọi check có nhiều dòng: double-space, missing-space, oxford comma.
