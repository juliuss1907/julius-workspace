# The Defiant: bốn đường thất bại, đường thứ năm mới đúng

Quan sát 2026-10-01, mở rộng từ `defiant-js-body-workaround.md`.

Phiên này tôi thử bốn cách đọc toàn văn The Defiant và chỉ cách cuối mới ra
kết quả. Ghi lại để phiên sau không lặp lại ba lượt thử lãng phí.

| Lượt | Cách | Kết quả |
|---|---|---|
| 1 | `web_extract` trực tiếp | Chỉ tiêu đề + tóm tắt, body là `Loading this article…` |
| 2 | `browser_exec` với `new_tab` + `js()` | CLI in usage, không chạy code |
| 3 | `curl` UA trình duyệt + regex `<p>` | Chỉ bắt được khối CSS `@property` của Tailwind, 0 đoạn bài |
| 4 | `curl` tải file về + parse Next.js payload | Cũng chỉ có tiêu đề, payload không chứa body dạng portable text |
| 5 | **`curl https://thedefiant.io/rss`** | **Ra toàn văn, 100 item** |

## Đường đúng: RSS feed mang toàn văn

```bash
curl -sL --max-time 30 \
  "https://thedefiant.io/rss" -o feed.xml
```

Feed chứa **100 item** với `<description>` là toàn văn bài (không phải teaser).
`https://thedefiant.io/api/feed` và `https://thedefiant.io/feed` trỏ cùng nội
dung, ba URL này cho kết quả giống hệt nhau.

Bóc toàn văn:

```bash
python3 - <<'PY'
import re, html
raw = open('/tmp/feed.xml', encoding='utf-8', errors='replace').read()
for it in re.findall(r'<item>(.*?)</item>', raw, re.S):
    t = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', it, re.S)
    title = html.unescape(t.group(1)) if t else '?'
    if 'Daines' not in title and 'ESMA' not in title:
        continue
    b = re.search(r'<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>', it, re.S)
    body = html.unescape(re.sub(r'<[^>]+>', '\n', b.group(1)))
    print("=" * 60, title)
    print(re.sub(r'\n{2,}', '\n', body).strip()[:2600])
PY
```

Lọc theo từ khoá trong tiêu đề rồi bóc cả nhóm `<item>` một lượt, nhanh hơn đọc
từng bài.

## `browser_exec` không chạy được trong phiên cron

Lượt 2 thất bại với lỗi tương tự lượt 3 dù đã thử cả dạng có lệnh comment dẫn
đầu lẫn không có. CLI in nguyên khối usage ra stdout và exit 0, nên nhìn như
thành công nếu không đọc kỹ output.

**Không dùng `browser_exec` để vượt trang render bằng JavaScript trong phiên
cron.** Đây là giới hạn của môi trường cron, không phải kết luận về công cụ.
Trong phiên tương tác với người dùng thì hãy thử lại.

## Bài học rút ra: thử theo giá, đừng thử theo mẹo

Tôi lần theo đúng một workaround đã được ghi trong skill
(`r.jina.ai`, xem `defiant-js-body-workaround.md`) mà **không đọc reference đó**.
Hai lỗi cùng lúc: lãng phí 4 lượt gọi, và bỏ sót một đường đã biết là chạy.

Quy trình đúng khi nguồn trả về body rỗng:

1. Mở `references/defiant-js-body-workaround.md` và `references/source-discovery-and-verification.md` **trước khi** thử kỹ thuật mới.
2. Ưu tiên đường rẻ nhất, nhanh nhất: RSS feed của chính nhà xuất bản.
3. Chỉ chuyển sang đường tốn hơn (jina reader, syndication) khi đường trước thực sự hỏng.

Thứ tự giá đã xác nhận cho The Defiant:
RSS (`/rss`) < jina reader < nguồn thứ ba đăng lại.

## Ghi chú cho bài blog

Khi dùng RSS của The Defiant, vẫn đưa **URL bài gốc** vào `sources:`, không phải
URL feed, vì người đọc cần đến được trang bài. Trong reply nói rõ tên nguồn
đã đọc thật.