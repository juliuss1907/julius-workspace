# Đọc `thedefiant.io`: body là JS, phải dùng jina reader

Observed 2026-09-30. Cần cho mọi bản tin nguồn The Defiant (bao gồm mục nhãn
`Converge` của họ).

## Triệu chứng

`web_extract` trả về `error: null` và nội dung **không rỗng**, nên trông như thành
công. Nhưng toàn bộ phần bài viết bị thay bằng dòng `Loading this article…`,
kèm newsletter pitch và khối "Most read". Không có đoạn nào của bài.

Đây là bẫy: nếu chỉ kiểm tra `error is None` thì sẽ tưởng đã đọc được rồi viết
bài từ trích đoạn RSS mà không biết mình đang bịa nội dung.

## Dấu hiệu nhận biết

Trong output có đúng chuỗi này là body đã bị bỏ trống:

```
Loading this article…
```

## Workaround: đọc qua jina reader

```bash
curl -sL --max-time 45 "https://r.jina.ai/<url>" | head -c 3500
```

Trả về Markdown sạch, có `Published Time:` và toàn văn. Nhanh, không cần API key.
Tăng `head -c` nếu cần phần giữa bài.

Một số bài hiện báo `You have 2 free articles remaining.` ngay sau metadata —
nội dung vẫn đọc được qua jina. Đừng tưởng mình bị chặn.

## Quy trình

1. `web_extract` bình thường cho batch.
2. Kết quả nào chứa `Loading this article…` → chuyển sang `curl r.jina.ai`.
3. Đưa URL gốc (không phải URL jina) vào `sources:` cho người đọc tự tra.
4. Không bao giờ dùng `source_excerpt` của RSS làm nguồn duy nhất khi chưa thử
   workaround — ghi nhãn `Chỉ dựa trên trích đoạn nguồn` thay vì bịa.

## Cùng kỹ thuật cho The Verge / TechCrunch bị cắt giữa

`web_extract` hay bị truncate và lưu full text vào
`.hermes/cache/web/<domain>-<hash>.md`. Dùng `read_file` với offset để đọc phần
giữa thay vì đoán nội dung.
