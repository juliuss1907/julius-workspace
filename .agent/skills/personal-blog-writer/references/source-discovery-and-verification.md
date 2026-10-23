# Tìm và xác minh nguồn tin khi viết bài — 2026-09-07

## Đừng đoán URL từ headline Google News RSS

Google News RSS chỉ trả về tiêu đề + tên outlet + URL redirect `news.google.com/rss/articles/...`.
KHÔNG tự chế URL thật kiểu `investing.com/news/...-93CH-4391283` hay
`indiatoday.in/...-2790512-2026-09-07` bằng cách đoán từ slug trong tiêu đề.

Observed 2026-09-07 (bài Jensen Huang "AGI has arrived"):
- URL đoán theo slug investing.com → trả về bài "Quantum Base extends retail offer"
  (hoàn toàn không liên quan).
- URL đoán theo slug indiatoday.in → trả về bài Gujarat Navratri (không liên quan).
- Yahoo Finance / CNBC TV18 / kobaran theo RSS → content rỗng hoặc trang khác.

## Quy trình đúng khi chỉ có tiêu đề

1. `web_search("<tiêu đề chính xác của bài>")` — kết quả trả URL thật + outlet.
2. Chọn outlet uy tín trong kết quả (Business Insider, Guardian, Reuters...).
3. `web_extract` URL thật → verify tiêu đề bài khớp tiêu đề từ RSS trước khi dùng.
4. Nếu outlet đầu trả rỗng/404/antibot, thử outlet tiếp theo trong kết quả
   search, KHÔNG quay lại đoán URL.

## Lệnh web_search từ execute_code (khi web tools ngoài không chạy)

```python
from hermes_tools import web_search
r = web_search("Jensen Huang \"AGI has arrived\" GPT-6 Astra", limit=8)
for w in r.get('data',{}).get('web',[]):
    print('-', w.get('title','')[:100]); print(' ', w.get('url',''))
```

## Cache đầy đủ khi bị truncate

`web_extract` truncate trang dài (head+tail) nhưng lưu full text vào
`.hermes/cache/web/<domain>-<hash>.md`. Khi cần phần giữa bài (thường bị mất
do price widgets ở đầu trang Decrypt), đọc file cache bằng `search_files`
(pattern theo từ khóa) rồi `read_file` với offset tìm được — đừng đoán nội dung.

## web_search trả rỗng → rút truy vấn xuống 2-4 từ khoá

Truy vấn dài, nhiều từ mô tả theo văn nói hay trả về `{"web": []}`, trong khi
cùng câu hỏi đó rút còn vài từ khoá trần lại ra kết quả đầy đủ. Gặp kết quả rỗng
thì thử lại ngay bằng 2-4 từ khoá (tên riêng + danh từ chính) trước khi kết luận
"không có nguồn" và bỏ qua bước research. Ví dụ cùng một chủ đề:
"Cointelegraph seeks buyer Google penalty traffic 2026" → rỗng;
"Cointelegraph buyer sale" → 8 kết quả dùng được.

## Phản biện là một nguồn giá trị

Tin "CEO tuyên bố X" nên kèm nguồn phản biện (Gary Marcus Substack, benchmark
độc lập ARC Prize...). Google News RSS thường hiện bài phản biện trong cùng
kết quả — đọc luôn để bài cân bằng, không chỉ tường thuật một chiều.
