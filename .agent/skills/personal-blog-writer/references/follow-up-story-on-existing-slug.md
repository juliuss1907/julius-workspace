# Brief item trùng chủ đề với bài đã có trên blog: viết tiếp hay bỏ?

Quan sát 2026-09-29. Bổ sung cho pitfall #2 trong `brief-item-selection-edge-cases.md`.

## Bước bắt buộc: search slug trước khi viết

Bài trong `src/content/writing/` có thể đã phủ đúng chủ đề. Search TRƯỚC khi viết,
không phải sau:

```bash
search_files(pattern="Astra|Bitget|THORChain|SoftBank|misalignment",
             path=".../personal-blog/src/content/writing", output_mode="files_only")
```

Sau đó đọc **12 dòng đầu** (title + description) của file trùng để biết bài cũ
đã nói gì và dừng ở đâu:

```bash
head -12 src/content/writing/<slug>.md
```

Quan sát 29/09: 5 tin được chọn, **2 trùng chủ đề với bài cũ**:

| Tin mới | Bài cũ đã có | Kết luận |
|---|---|---|
| Bitget mở lại rút BTC (28/09) | `bitget-hot-wallet-incident-351m.md` (25/09) | Viết tiếp, slug mới |
| OpenAI 9 sự cố lệch chuẩn (28/09) | `openai-huggingface-hack-report.md` (27/08) | Viết tiếp, slug mới |

Cả hai đều là **diễn biến mới của một sự kiện đã đưa**, không phải sự kiện lặp
lại: bài cũ viết về lúc Bitget phát hiện trộm và tạm dừng rút, bài mới viết về
lúc mở lại rút + cơ chế credential bên thứ ba. Bài cũ viết về báo cáo 130 trang
sau vụ Hugging Face, bài mới viết về trang công khai ghi nhận sự cố.

## Công thức cho bài viết tiếp

Bốn điểm giữ bài mới tách được khỏi bài cũ:

1. **Slug mới, không sửa bản cũ.** Không bao giờ patch bài đã publish để thêm
   diễn biến mới, và không xóa bản cũ.
2. **Mở bài nêu ngay đây là gì so với lần trước.** Ví dụ dùng mốc thời gian làm
   neo: "bốn ngày sau khi phải dừng mọi giao dịch rút tiền" — người đọc bài cũ
   hiểu ngay đây là chương tiếp theo, người chưa đọc cũng theo kịp.
3. **Con số cũ đặt cạnh con số mới, giải thích vì sao đổi.** Mức thiệt hại
   351,6 triệu USD rồi 388 triệu USD, kèm câu "sàn nói con số cập nhật này
   không phản ánh thêm giao dịch trái phép mới". Không để hai con số đứng
   trần cạnh nhau như mâu thuẫn.
4. **Bổ sung cơ chế, không lặp lại diễn biến.** Giá trị của bài mới là thứ mới
   biết: Bitget tiết lộ kẻ tấn công lấy credential qua sản phẩm bảo mật bên
   thứ ba chứ không cần khóa riêng tư. Đó là lý do bài mới đáng tồn tại.

## Áp dụng ngược lại: tin mới là tình huống thứ hai

Bài `openai-9-su-co-llech-chuan-agent.md` có thể bị hiểu là lặp `openai-huggingface-hack-report.md`.
Cách xử lý: đặt trọng tâm vào **cấu trúc mới** (trang công khai 9 mục, các
loại sự cố mà bài cũ không có) thay vì kể lại vụ Hugging Face. Chỉ nhắc bài cũ
một câu khi cần, không kể lại diễn biến.

## Cảnh báo: cùng sự kiện có thể xuất hiện ở nhiều nguồn trong brief

Một sự kiện có thể nằm ở nhiều mục của brief do nhiều outlet đưa. Trước khi viết,
so nhanh tiêu đề các mục đã chọn: trùng thì gộp còn một bài, giữ nguồn mạnh
nhất. Trong batch 29/09 không có mục trùng sau khi đã gộp ở tầng brief, nhưng
kiểm tra vẫn nên làm vì brief có thể tới từ nhiều nguồn khác nhau.
