---
title: "HumidiFi là gì? Tìm hiểu về sàn DEX với mô hình AMM kiểu mới"
source: "https://coin68.com/humidifi-la-gi/"
published: 2025-12-02
created: 2026-05-09
description: "Dù ra mắt chưa đầy 6 tháng, nhưng HumidiFi hiện đang sàn DEX lớn nhất của Solana tính theo khối lượng, xử lý hơn 1 tỷ đô la khối lượng hàng ngày."
tags:
  - "dex"
  - "solana"
---
**Dù ra mắt chưa đầy 6 tháng, nhưng HumidiFi hiện đang sàn DEX lớn nhất của Solana tính theo khối lượng, xử lý hơn 1 tỷ đô la khối lượng giao dịch hàng ngày. Không giống như các AMM truyền thống, các pool LP của HumidiFi được vận hành bởi các tổ chức thay vì người dùng phổ thông, mang lại mức chênh lệch thấp, trượt giá ít hơn và khớp lệnh tốt hơn so với các đối thủ khác. Hãy cùng Coin68 tìm hiểu về HumidiFi trong bài viết dưới đây.**

**![](https://cdn.coin68.com/images/20251202084448-9b832b1b-8b06-4eb6-a3c7-4a7e72496e7f-41.jpg)** HumidiFi là gì? Tìm hiểu về sàn DEX với mô hình AMM kiểu mới trên Solana

## HumidiFi là gì?

**HumidiFi** là một AMM DEX trên Solana, hoạt động như một nhà cung cấp thanh khoản ẩn (dark liquidity provider) cho các router như Jupiter, giúp người dùng cuối swap token với mức trượt giá thấp mà không cần tương tác trực tiếp với giao diện của nó. HumidiFi hướng tới việc tái định nghĩa giao dịch DEX bằng cách kết hợp hiệu quả vốn, quyền riêng tư giao dịch và tối ưu cho các nhà tạo lập thị trường (MM) chuyên nghiệp.

![](https://cdn.coin68.com/images/20251202084449-100f973a-57c3-41a4-b366-439562fc0830-86.jpg) HumidiFi là gì?

Khác với các AMM truyền thống như [UniSwap](https://coin68.com/humidifi-la-gi/Uniswap%20\(UNI\)%20l%C3%A0%20g%C3%AC?%20T%C3%ACm%20hi%E1%BB%83u%20v%E1%BB%81%20s%C3%A0n%20DEX%20h%C3%A0ng%20%C4%91%E1%BA%A7u%20trong%20th%E1%BB%8B%20tr%C6%B0%E1%BB%9Dng%20crypto), Orca hay Raydium, HumidiFi sử dụng một mô hình AMM hoàn toàn mới mang tên proprietary AMM (prop AMM). Trong mô hình này, người cung cấp thanh khoản và vận hành pool sẽ là các tổ chức chuyên nghiệp thay vì là người dùng phổ thông như các DEX truyền thống. Điều này mang lại các lợi ích như sau:  

- **Giá tốt hơn cho cặp token lớn**: Do MM chuyên nghiệp có thể đặt spread hẹp, tập trung thanh khoản quanh giá oracle và chủ động rebalance, nên trade size lớn vẫn giữ slippage thấp.
- **Chống MEV tốt hơn**: Vì HumidiFi đóng vai trò như một dark liquidity provider, nơi giá cho từng cặp giao dịch thường được MM quyết định riêng, nên sẽ có ít lộ cơ hội cho các bot MEV kiếm được lợi nhuận.

**Có thể bạn quan tâm:  
  
**
- [Jupiter (JUP) là gì? Nền tảng DEX Aggregator trên Solana airdrop cho gần 1 triệu ví của người dùng](https://coin68.com/jupiter-jup-la-gi/)
- [Raydium (RAY) là gì? Tìm hiểu về AMM đầu tiên của hệ sinh thái Solana](https://coin68.com/raydium-ray-la-gi/)

## Điểm nổi bật của HumidiFi

### Thanh khoản chủ động

Giá do HumidiFi cung cấp được tạo từ dữ liệu thị trường real-time và mô hình rủi ro nội bộ, không chỉ từ công thức AMM tĩnh. Nhờ vậy, đem lại chênh lệch ít hơn và trượt giá thấp hơn cho các lệnh lớn trên những cặp thanh khoản cao như SOL‑USD. Ngoài ra, thanh khoản của giao thức cũng được tái cân bằng liên tục nhằm giảm rủi ro bị arbitrage và nâng hiệu quả sử dụng vốn so với AMM cổ điển.

### Kết hợp xử lý cả on-chain và off-chain

HumidiFi lưu trữ tài sản, xử lý thanh toán,… hoàn toàn trên Solana, nên ai cũng có thể kiểm tra được và dễ tích hợp với các giao thức DeFi khác. Còn những phần nặng như mô hình giao dịch tần suất cao, mô hình dự đoán giá, xử lý dữ liệu lớn lấy từ sàn CEX/DEX thì chuyển ra chạy trên hệ thống bên ngoài blockchain để khỏi làm tắc mạng.

### Hạn chế MEV và các giao dịch độc hại

HumidiFi có thể nhận diện và tách riêng các giao dịch của người dùng thật với các bot và điều chỉnh giá sao cho người dùng được hưởng mức chênh lệch giá tốt hơn và ít phải tranh phí gas nhất có thể. Nhờ tận dụng thanh khoản ẩn (dark liquidity) và mô hình prop AMM, HumidiFi làm giảm đáng kể ảnh hưởng của bot MEV lên giao dịch, giúp lệnh khớp sạch hơn, ít bị trượt giá và sát với giá thị trường hơn.

## Lộ trình phát triển

Lộ trình phát triển của HumidiFi như sau:  

- **Quý 3/2025**: Triển khai trên Jupiter DTF, hoàn thiện module thanh khoản, thử nghiệm thêm các chiến lược tạo lập thị trường tự động.
- **Quý 4/2025**: Ra mắt token, khởi động thanh khoản ban đầu, thu hút những người cung cấp thanh khoản và nhóm người dùng đầu tiên.
- **Quý 1/2026**: Triển khai các pool LP nâng cao và tích hợp với các giao thức DeFi trên Solana.
- **Quý 2/2026**: Mở rộng kiến trúc multi-pool, tối ưu AMM và mở rộng hợp tác trong hạ tầng giao dịch Solana.

## Tokenomics

### Thông tin token

| **Tên token** | HumidiFi |
| --- | --- |
| **Ký hiệu** | WET |
| **Blockchain** | Solana |
| **Contract** | Đang cập nhật... |
| **Tổng cung** | 1.000.000.000 |

### Tỷ lệ phân bổ token

![](https://cdn.coin68.com/images/20251202084449-8edca122-84ad-4eff-a41d-993a9fbb8f16-110.jpg) Tỷ lệ phân bổ token WET

Token WET được phân bổ theo tỷ lệ như sau:  

- **ICO - 10%**: Mở khoá 100% tại TGE.
- **Foundation - 40%**: Mở khoá 8% tại TGE, phần còn lại mở khoá trong vòng 24 tháng.
- **Ecosystem - 25%**: Mở khóa 5% tại TGE, phần còn lại mở khoá sau 6 tháng và vesting trong vòng 24 tháng.
- **Labs - 25%**: Khoá 6 tháng và vesting trong vòng 24 tháng.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án HumidiFi, Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý**: Thông tin trong bài viết chỉ mang mục đích cung cấp thông tin thị trường, không được xem là lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định nào của các bạn.