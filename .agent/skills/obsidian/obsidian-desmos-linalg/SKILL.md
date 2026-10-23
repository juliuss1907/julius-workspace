---
name: obsidian-desmos-linalg
description: Vẽ hình đại số tuyến tính (vector, phép cộng/trừ vector, hình bình hành, vector field/gradient, ma trận biến đổi) dưới dạng codeblock `desmos-graph` để dùng với plugin Desmos (github.com/nigecat/obsidian-desmos) trong Obsidian. LUÔN dùng skill này khi người dùng nhắc tới "Desmos trong Obsidian", "vẽ vector", "biểu diễn vector", "vector field", "gradient descent path", "ma trận biến đổi tuyến tính", hoặc bất kỳ yêu cầu vẽ hình toán/đại số tuyến tính nào có nhắc tới Obsidian/Desmos — kể cả khi người dùng không gõ chính xác cú pháp codeblock.
---

# Desmos Linear Algebra Diagrams cho Obsidian

Skill này tạo các codeblock ` ```desmos-graph ` để plugin [obsidian-desmos](https://github.com/nigecat/obsidian-desmos) render trực tiếp trong Obsidian, dùng để minh họa các khái niệm đại số tuyến tính: vector, phép cộng vector, không gian vector, vector field, gradient.

## Cú pháp chung của plugin

````
```desmos-graph
left=-2; right=6;
top=6; bottom=-2;
grid=true;
---
<phương trình 1>|<màu>|<style/label nếu có>
<phương trình 2>|...
```
````

- Phần trên dấu `---` là cấu hình khung nhìn (`left/right/top/bottom`, `grid`).
- Mỗi dòng dưới `---` là một phương trình LaTeX, các thuộc tính cách nhau bởi `|`: màu (`blue`, `red`, `green`, `black`...), `point` (để vẽ điểm thay vì đường), `label:...` (chỉ áp dụng cho `point`).
- Plugin không có sẵn mũi tên vector thật (không có arrowhead) — mọi vector được mô phỏng bằng đoạn thẳng tham số + điểm đánh dấu đầu/ngọn. Nếu người dùng cần mũi tên nhọn thật sự, gợi ý dùng TikZJax (`\draw[->]`) thay vì Desmos.

## Pattern 1 — Vẽ một vector đơn

Vector **v** = (a, b) từ gốc tọa độ: dùng dạng tham số `(a*t, b*t)` với `t` từ 0 đến 1.

````
```desmos-graph
left=-2; right=6;
top=6; bottom=-2;
grid=true;
---
(at,bt)|0<=t<=1|blue
(0,0)|point|black
(a,b)|point|blue|label:v=(a,b)
```
````

Thay `a`, `b` bằng số cụ thể. Luôn chỉnh `left/right/top/bottom` sao cho bao trọn vector (thường lấy min/max tọa độ ±2 làm biên).

## Pattern 2 — Cộng hai vector (tip-to-tail)

Vector **v1** = (a1, b1), **v2** = (a2, b2). Vector tổng = (a1+a2, b1+b2).

````
```desmos-graph
left=-2; right=6;
top=6; bottom=-2;
grid=true;
---
(a1*t,b1*t)|0<=t<=1|blue
(a1+a2*t,b1+b2*t)|0<=t<=1|green
((a1+a2)*t,(b1+b2)*t)|0<=t<=1|red
(0,0)|point|black
(a1,b1)|point|blue|label:v1
(a1+a2,b1+b2)|point|red|label:v1+v2
```
````

- Đoạn xanh dương: v1 từ gốc.
- Đoạn xanh lá: v2, dịch để bắt đầu từ ngọn v1 (chú ý cộng thêm `a1`/`b1` vào phương trình tham số).
- Đoạn đỏ: vector tổng, đi thẳng từ gốc đến điểm cuối — đây là đường chéo hình bình hành tạo bởi v1, v2.

### Biến thể: khép kín thành hình bình hành đầy đủ

Thêm 1 đoạn nữa vẽ v1 dịch chuyển từ ngọn v2 (cạnh đối song song):

```
(a2+a1*t,b2+b1*t)|0<=t<=1|blue
```

## Pattern 3 — Trừ hai vector

**v1 - v2**: vẽ như vector nối từ ngọn v2 đến ngọn v1 (khi cả hai đều xuất phát từ gốc).

```
(a2+(a1-a2)*t, b2+(b1-b2)*t)|0<=t<=1|purple
```

## Pattern 4 — Vector field / gradient đơn giản

Với field 2D nhỏ, vẽ nhiều vector ngắn tại các điểm lưới (x0,y0), hướng theo (fx(x0,y0), fy(x0,y0)) đã chuẩn hóa độ dài nhỏ (ví dụ scale 0.3) để không đè lên nhau:

```
(x0+0.3*fx*t, y0+0.3*fy*t)|0<=t<=1|blue
```

Lặp lại dòng này cho từng điểm lưới (x0, y0) muốn minh họa — thường dùng thủ công cho lưới nhỏ (3x3 đến 5x5 điểm) vì plugin không hỗ trợ vòng lặp.

## Quy tắc khi áp dụng skill

1. Luôn hỏi hoặc suy luận từ ngữ cảnh: các vector cụ thể là gì (tọa độ), cần minh họa gì (đơn lẻ, cộng, trừ, field).
2. Luôn tính lại `left/right/top/bottom` cho vừa khít dữ liệu, chừa lề khoảng 1-2 đơn vị.
3. Luôn giải thích ngắn gọn từng dòng code sau khi đưa ra, theo đúng phong cách đã dùng trong các ví dụ trước (không cần dài dòng).
4. Nếu người dùng cần độ chính xác cao / mũi tên thật / xuất bản học thuật → gợi ý chuyển sang TikZJax thay vì cố gắng ép Desmos.
