---
title: "Lightcone - Nền tảng Impact Market trên Solana"
source: "https://coin68.com/lightcone-la-gi/"
published: 2026-02-04
created: 2026-05-04
description: "Lightcone xây dựng thị trường tác động (Impact Market), cho phép người dùng giao dịch mức độ ảnh hưởng của các sự kiện lên giá trị tài sản."
tags:
  - "prediction-market"
  - "solana"
---
**Lightcone là một giao thức xây dựng thị trường tác động (Impact Market) trên hệ sinh thái Solana, cho phép người dùng giao dịch dựa trên mức độ ảnh hưởng của các sự kiện lên giá trị tài sản thay vì chỉ dự đoán xác suất xảy ra của chúng. Dự án định vị mình là một lớp hạ tầng quan trọng trong tầm nhìn xây dựng Internet Capital Market (ICM) của Solana. Hãy cùng Coin68 tìm hiểu về dự án này trong bài viết dưới đây.**

**![](https://cdn.coin68.com/images/20260204043726-79ff72d9-c84f-451a-b3da-939865214b96-173.jpg)** Lightcone là gì? Tìm hiểu về nền tảng Impact Market trên Solana

## Lightcone là gì?

Lightcone là nền tảng tập trung vào mô hình Impact Market (thị trường tác động) trên Solana. Khác với các [Prediction Market](https://coin68.com/prediction-market-la-gi/) (thị trường dự đoán) truyền thống nơi người dùng đặt cược vào việc một sự kiện có xảy ra hay không, Lightcone cho phép người dùng giao dịch "tác động" của sự kiện đó đối với một tài sản cụ thể nếu nó thực sự xảy ra.

![](https://cdn.coin68.com/images/20260204043726-d768465e-9adb-42db-abd1-2579a4a82d0f-143.jpg) Lightcone là gì?

Trong các thị trường dự đoán thông thường, giá của một "shares" (cổ phần dự đoán) thường phản ánh xác suất xảy ra của sự kiện. Tuy nhiên, thị trường lại thiếu công cụ để trả lời câu hỏi: "Nếu sự kiện này xảy ra, nó sẽ tác động đến giá trị của tài sản X như thế nào?". Lightcone giải quyết vấn đề này bằng cách:  

- **Tách biệt xác suất và tác động**: Cho phép giao dịch giá trị tài sản trong các "thế giới giả định" nơi sự kiện đã chắc chắn xảy ra 100%.
- **Cung cấp dữ liệu định lượng**: Thay vì dựa vào các báo cáo phân tích chủ quan, dữ liệu từ Lightcone cung cấp cái nhìn khách quan từ thị trường về mức độ ảnh hưởng của tin tức.

**Có thể bạn quan tâm:  
  
**
- [Solana ETF là gì? Những điều bạn cần biết về Solana ETF](https://coin68.com/solana-etf-la-gi/)
- [Prediction market là gì? Top 5 dự án prediction market nổi bật hiện nay](https://coin68.com/prediction-market-la-gi/)

## Sản phẩm và tính năng chính của dự án

Lightcone hoạt động thông qua một cấu trúc bao gồm các thành phần chính sau:

### Impact Trading

Đây là sản phẩm cốt lõi cho phép người dùng mua bán các hợp đồng đại diện cho giá trị của một tài sản trong các kịch bản khác nhau. Ví dụ: Giá của SOL nếu một quỹ ETF được phê duyệt so với giá của SOL nếu quỹ đó bị từ chối.

### Cơ chế Multiverse

Lightcone sử dụng mô hình "Multiverse" để token hóa các nhánh kết quả khác nhau. Mỗi nhánh đại diện cho một thế giới giả định nơi một kết quả cụ thể đã xảy ra.  

- **Conditional Token (Token có điều kiện)**: Các tài sản này chỉ có giá trị thực tế sau khi sự kiện được xác thực.
- **Prop-AMM**: Các hồ thanh khoản được tối ưu hóa để xử lý việc hoán đổi giữa các nhánh kết quả này.

### Cổng dữ liệu thị trường

Lightcone tổng hợp các tín hiệu từ giao dịch để tạo ra một nguồn dữ liệu (feed) về tác động giá, giúp các dự án DeFi khác có thể tích hợp để quản trị rủi ro hoặc tạo ra các sản phẩm phái sinh mới.

## Cơ chế vận hành của Lightcone

Lightcone vận hành dựa trên mô hình Impact Market, cho phép người dùng giao dịch giá trị tương lai của một tài sản dựa trên các kịch bản thực tế. Cơ chế này được thực hiện qua 3 bước đơn giản:  

- **Chia tách tài sản**: Thay vì để bạn đặt cược "Đúng" hay "Sai", Lightcone sẽ "chia" một tài sản có sẵn (ví dụ: 1 đồng SOL) thành các phiên bản khác nhau gắn liền với một sự kiện.
- **Giao dịch theo kỳ vọng**: Người dùng sẽ mua hoặc bán các "nhánh" tài sản này dựa trên phân tích cá nhân về tác động của sự kiện. Giá của các nhánh này sẽ biến động liên tục theo nhu cầu thị trường, phản ánh việc mọi người nghĩ tài sản đó sẽ đáng giá bao nhiêu nếu kịch bản đó xảy ra.
- **Tất toán kết quả**: Khi sự kiện thực tế diễn ra và có kết quả cuối cùng: Nhánh đúng sẽ được chuyển đổi lại thành 1 đồng SOL thực tế (giá trị toàn vẹn). Nhánh sai sẽ trở về giá trị bằng 0.

## Lộ trình phát triển

Dự án hiện đang ở giai đoạn đầu và tập trung vào các cột mốc sau:  

- **Giai đoạn 1**: Ra mắt bản thử nghiệm trên devnet của Solana để kiểm tra cơ chế Multiverse.
- **Giai đoạn 2**: Tích hợp các nguồn dữ liệu thực tế thông qua các đối tác Oracle.
- **Giai đoạn 3**: Mở rộng danh mục tài sản hỗ trợ từ tiền mã hóa sang các tài sản thế giới thực (RWA).

## Nhà đầu tư

Hiện tại, thông tin chi tiết về các vòng gọi vốn của Lightcone chưa được công bố rộng rãi. Tuy nhiên, dự án nhận được sự quan tâm và ủng hộ lớn từ hệ sinh thái.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án Lightcone, Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.