# Đích nguồn gốc thứ năm: trang chủ của chính hệ thống đo

Bổ sung cho `references/brief-item-to-primary-source-upgrade.md` (bốn đích có
sẵn). Quan sát 05/10/2026.

## Vì sao cần

Bốn đích đã có (trang công bố chính thức, bài X của bên đó, văn bản cơ quan nhà
nước, bài gốc của hãng an ninh/nghiên cứu) đều giả định "bên công bố" là một
công ty hoặc cơ quan. Nhưng khi tin mang dạng **"model X đạt kết quả Y trong
benchmark Z"**, bên công bố thật sự là chính trang của Z, không phải bài báo.

## Ví dụ

Tin "GPT-6 Astra thua ở StarCraft nên tải bot người để chơi thay". Bài báo chỉ kể
cốt truyện. Trang `starskirmish.com/bench` mới có phần bài cần: mỗi model được
**một giờ** viết bot Protoss bằng C++; thang điểm quy đổi về tỉ lệ thắng kỳ vọng
với Stardust = 100 và Four Gate Dragoon = 0; 1.830 ván đấu cho mỗi model;
Stardust thắng Astra **365 trên 366 ván**.

Con số cuối là phần đáng viết nhất: model đã viết ra bot mạnh nhất giải nhưng vẫn
không vượt được bot người viết tay. Bài báo không có chi tiết này.

Quy tắc: khi brief nói "đạt/hơn/vượt ... trong benchmark/chỉ số", mở trang của
chính benchmark và lấy điều kiện chạy, thang đo, và điểm đứng cuối bảng.

## Antibot: đừng coi là hết đường

Phiên này Kotaku chặn (`document_antibot`) — chính là nguồn gốc của tin. Không
bỏ tin. Thay bằng ba tầng cộng lại:

1. **Outlet đã trích nguyên văn.** The Verge tóm tắt chi tiết hành vi: đối thủ,
   thời điểm, và việc người tạo phải hoàn tác code.
2. **Nguồn gốc mà bài báo dẫn tới.** Các bài đăng X của người tạo benchmark.
3. **Trang gốc của hệ thống** (xem trên).

Đủ để viết bài có cơ chế. Và phải **nói rõ trong report** rằng nguồn nào bị chặn
và lấy gì thay.

## Nguồn thứ cấp chỉ để đối chiếu tiêu đề

Trong batch có The Hill trong candidate list cùng TechCrunch cho cùng một tin. Chỉ
dùng nó để kiểm tra tiêu đề khớp, không đưa số liệu. Khi một sự kiện có nhiều
outlet, lấy outlet có **chi tiết cấu trúc** (điều lệ, mốc thời gian, con số), các
outlet còn lại để kiểm chéo.

## Excerpt bị cắt thì phần định lượng cũng biến mất

Tin AMD trong brief chỉ có "cắt giảm 40-60% chi phí token". Bài gốc có đủ: mức tải
giả định 5,7 triệu token đầu vào và 574.000 token đầu ra mỗi người mỗi ngày,
500 máy tính AI PC, cấu hình 50/50 local-cloud, và so sánh ba năm 6.533 USD so với
81.108 USD.

Đó là phần biến một tin ngắn thành bài 800 từ. Cũng là lý do phải đọc bài gốc thay
vì viết từ excerpt. Và câu thừa nhận "số liệu dựa trên giả định của AMD" phải
đưa vào ngay sau đoạn số liệu, không dồn cuối bài.