# Nguồn đo độc lập: tìm bên thứ ba đo, không chỉ đọc tự công bố

Observed 01/10/2026 khi viết bài Gemini 4 Argon. Bổ sung cho
`references/source-discovery-and-verification.md`.

## Vấn đề

Bài công bố của hãng model chỉ có số do chính hãng tự đo. Bài viết chỉ dùng số đó
thì không có gì để kiểm chứng, và đọc như một bản thông cáo được dịch lại.

Observed 01/10/2026: bản đầu tiên của bài Gemini 4 Argon toàn số do Google tự
công bố (DeepSWE 77,9%, CWE-bench 68%, AutomationBench 51,3%). Sau đó Julius đưa
thêm `artificialanalysis.ai/models/gemini-4-argon`, và bài viết lại dài hơn, tốt
hơn, và có một phần thật sự mới: **điểm đo của bên thứ ba**.

## Nguồn đo độc lập đáng dùng

| Trang | Cái nó đo | Ghi chú |
|---|---|---|
| `artificialanalysis.ai/models/<slug>` | Chỉ số trí tuệ tổng hợp, hạng, chi phí mỗi tác vụ, mức dài dòng, cửa sổ ngữ cảnh | Có FAQ ghi rõ cách tính tỷ lệ pha trộn giá |
| Artificial Analysis | Các bài đo thành phần (AA-Briefcase, Terminal-Bench, GDPval-AA...) | Trang model thường chỉ công bố điểm tổng hợp |
| `ai.google.dev/gemini-api/docs/pricing` | Bảng giá Gemini Developer API theo thời hạn | Chính thức, có ngày tăng giá |
| `platform.claude.com/docs/en/models/<model>/overview` | Giá + model ID + so sánh bảng trong cùng hệ | Chính thức, có cả dòng giá của model khác cùng hãng |
| `platform.openai.com/docs/pricing` | Bảng giá OpenAI theo nhóm ngữ cảnh ngắn/dài | Chính thức |

## Cách dùng

1. Tìm nguồn đo độc lập **trước khi viết**, không phải sau. Nếu viết xong mới
   tìm thì dễ phải viết lại cả bài.
2. Đặt số đo độc lập ở **giữa bài**, không nhét cuối. Số do hãng tự công bố để
   gần phần công bố; số đo bên thứ ba đặt cạnh phần phản biện để đối chiếu được.
3. Ghi rõ giới hạn: trang đo có thể chỉ công bố điểm tổng hợp, không tách từng
   bài kiểm tra. Đừng ghi "đo được 77,9% trên DeepSWE" nếu bên thứ ba không công
   bố con số đó.
4. Chỉ số dài dòng (output tokens) thường ít được nói nhưng ăn thẳng vào chi phí
   vận hành thực tế, đáng đưa lên thành điểm nhấn. Ở bài Gemini: 110 triệu token so
   với trung vị 82 triệu của nhóm cùng giá.
5. Số đo bên thứ ba **không bác bỏ** phần nội bộ không đồng ý (xem dưới).

## Kết hợp với nguồn phản biện

Cấu trúc bài mạnh nhất khi có cả ba loại, đặt cạnh nhau:

- **Số tự công bố** của hãng (ghi rõ là tự công bố, chưa kiểm chứng)
- **Số đo độc lập** của bên thứ ba (đo được, nhưng thường chỉ ở mức tổng hợp)
- **Phản biện nội bộ** từ báo chí có nguồn ẩn danh (người dùng thật bất đồng)

Ba tầng này đo ba thứ khác nhau và không mâu thuẫn: chỉ số tổng hợp cho biết model
đứng đâu, phản biện cho biết điểm đó có thành trải nghiệm thực tế hay không. Chỉ số
tổng hợp không đủ đại diện cho trải nghiệm hằng ngày, và nói thẳng điều đó trong
bài thay vì chọn một bên.

Khi cả hai vế của câu chuyện đều dựa trên nguồn ẩn danh (nhân viên nói một kiểu,
nhân viên khác phủ nhận kiểu khác), nói rõ cả hai vế đều chưa được kiểm chứng độc
lập thay vì chọn vế nghe hợp lý hơn.