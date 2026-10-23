# Oxford comma: cảnh báo có thể ĐÚNG, đừng bỏ cả nhóm

Bổ sung cho `references/oxford-comma-vietnamese-false-positive.md`. Bổ sung
mặt còn lại của vấn đề, sau khi đã có mặt "báo nhầm thường xuyên".

## Cả hai vế đều đúng

- Vế A: script báo nhầm trên mệnh đề ghép tiếng Việt. Rất nhiều. Đừng sửa hết.
- Vế B: **một danh sách liệt kê thật sẽ nằm trong cùng nhóm cảnh báo đó.**

Vì vậy `warn` không phải tín hiệu "bỏ qua". Nó là tín hiệu "đọc từng dòng".

## Ví dụ thật, 05/10/2026

Batch 4 bài, script báo kiểu `warn: N line(s) with a comma before 'và'/'and'`:

```
gpt-6-astra-cheat-starcraft.md: warn: 2 line(s)
  L17: Vấn đề không nằm ở việc Astra thua. Một hệ thống thua rồi thử chiến thuật khác...
  L21: Điểm chung là môi trường có luật, model tự tìm cách vượt luật, và việc phát hiện...
```

- L17: mệnh đề ghép ("Một hệ thống thua rồi thử chiến thuật khác là hành vi bình
  thường") → giữ nguyên.
- L21: **serial list thật** ba phần tử → bỏ dấu phẩy.

Sửa đúng một dòng. Còn lại giữ.

## Quy tắc hành động

1. Đọc **từng dòng** script liệt kê, không đọc đếm.
2. Hỏi: dòng này liệt kê 3+ phần tử cùng loại nối tiếp nhau bằng dấu phẩy
   không? Nếu có → bỏ dấu phẩy trước "và"/"and".
3. Nếu chỉ là hai vế của một mệnh đề phức tạp → giữ.
4. Không chạy lại script chỉ để xem cảnh báo biến mất — cảnh báo sẽ không biến
   mất hết vì phần lớn là mệnh đề ghép hợp lệ.

## Ngưỡng cảnh báo

Script chỉ cảnh báo khi vượt ngưỡng (mặc định > 2 dòng). Nghĩa là danh sách liệt kê
thật ở bài ngắn có thể **không hiện cảnh báo**. Vì vậy không dựa vào cảnh báo để
biết đã sạch: đọc lướt một lần sau khi viết, như `references/content-validation.md`
vẫn nhắc.