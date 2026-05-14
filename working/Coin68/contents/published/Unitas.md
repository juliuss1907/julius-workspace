---
title: "Unitas - Lớp hạ tầng sinh lời cho stablecoin"
source: "https://coin68.com/unitas-la-gi/"
published: 2026-03-19
created: 2026-05-04
description: "Unitas là giao thức DeFi với sản phẩm cốt lõi là USDu, stablecoin tự động tạo ra lợi nhuận thông qua chiến lược trung lập thị trường."
tags:
  - "stablecoin"
  - "infrastructure"
---
**Unitas là giao thức DeFi với sản phẩm cốt lõi là USDu, stablecoin tự động tạo ra lợi nhuận thông qua chiến lược trung lập thị trường. Điểm khác biệt chính của Unitas so với các stablecoin thông thường nằm ở chỗ phần tài sản đảm bảo không nằm im mà được triển khai vào các chiến lược giao dịch có thể kiểm chứng trên chuỗi, mang lại lợi suất thực cho người nắm giữ. Hãy cùng Coin68 tìm hiểu về dự án này trong bài viết dưới đây.**

![](https://cdn.coin68.com/images/20260319041952-1252205f-dce1-4468-addf-9c128086a592-106.jpg) Unitas là gì? Tìm hiểu về lớp hạ tầng sinh lời cho stablecoin

## Unitas là gì?

**Unitas** là giao thức stablecoin sinh lời hoạt động trên Solana và BNB Chain. Thay vì chỉ phát hành một stablecoin neo theo USD và để tài sản đảm bảo nhàn rỗi như các mô hình truyền thống, Unitas triển khai tài sản đảm bảo đó vào chiến lược giao dịch [delta-neutral](https://coin68.com/delta-hedging-la-gi/) để tạo ra lợi suất bền vững.

![](https://cdn.coin68.com/images/20260319041953-15dccbf8-8a60-497c-bc86-40305b0fe63f-54.jpg) Unitas là gì?

Vấn đề mà Unitas hướng đến giải quyết là một thực tế phổ biến trong DeFi: phần lớn stablecoin nằm im trong ví hoặc trên sàn giao dịch mà không tạo ra bất kỳ giá trị nào, trong khi các chiến lược sinh lời hiện có thường thiếu minh bạch, khó xác minh hoặc tiềm ẩn rủi ro cao do phụ thuộc vào bên thứ ba tập trung.

Sản phẩm chủ lực hiện tại của Unitas là USDu, một stablecoin neo theo USD với tổng giá trị tài sản khóa trong giao thức (TVL) đã vượt 80 triệu USD. Người dùng nắm giữ USDu có thể stake để nhận sUSDu, phiên bản tích lũy lợi nhuận tự động của USDu.

**Có thể bạn quan tâm:  
  
**
- [Stablecoin là gì? Tìm hiểu về các loại stablecoin phổ biến trong thị trường crypto](https://coin68.com/stablecoin-la-gi/)
- [USD1 là gì? Tìm hiểu về đồng stablecoin của World Liberty Financial](https://coin68.com/usd1-la-gi/)

## Sản phẩm và tính năng chính

### USDu

USDu là stablecoin neo theo đồng USD, được phát hành khi người dùng nạp tài sản đảm bảo vào giao thức. Khác với các stablecoin truyền thống, USDu được thiết kế để tự động tạo lợi nhuận cho người nắm giữ thông qua cơ chế vận hành nội tại của giao thức, không phụ thuộc vào lãi suất từ ngân hàng hay bên trung gian tập trung.

Tính ổn định của USDu được đảm bảo bởi cơ chế delta hedging, trong đó tài sản thế chấp đằng sau mỗi USDu được triển khai vào các vị thế thị trường trung lập

### sUSDu

Khi stake USDu vào giao thức, người dùng nhận lại sUSDu. Tỷ giá quy đổi giữa sUSDu và USDu tăng dần theo thời gian khi giao thức phân phối doanh thu vào pool staking. Điều này có nghĩa là người nắm giữ sUSDu có thể tăng giá trị của tài sản không cần làm gì thêm.

### xGLD

xGLD là sản phẩm tiếp theo trong lộ trình phát triển của Unitas. Đây là tài sản vàng token hóa có khả năng sinh lời, sử dụng chiến lược carry trade để tạo yield trong khi vẫn duy trì tỷ giá với giá vàng thật. xGLD được thiết kế để có thể tích hợp với các giao thức lending, liquidity pools và các dự án DeFi khác. Người dùng có thể sử dụng xGLD làm tài sản thế chấp để tăng hiệu quả sử dụng vốn, mở ra nhiều cơ hội chiến lược trong thị trường.

## Cơ chế hoạt động

Cơ chế cốt lõi của Unitas xoay quanh chiến lược trung lập thị trường với Jupiter Liquidity Pool (JLP), pool thanh khoản của Jupiter Perp trên Solana. Khi một người dùng dùng [USDC](https://coin68.com/usdc-la-gi/) làm tài sản thế chấp để phát hành USDu, dòng tiền đó được phân bổ thành hai phần và vận hành song song.

### Phần 1: Mua token JLP (80%)

Khoảng 80% lượng USDC nạp vào được chuyển từ Fund Vault đến một DEX trên Solana ([Jupiter](https://coin68.com/jupiter-jup-la-gi/) hoặc [Orca](https://coin68.com/orca-orca-coin/)) để mua Jupiter Perpetuals Liquidity Provider Token (JLP). Lượng token này được lưu trữ trong ví đa chữ ký, đóng vai trò tài sản đảm bảo chính cho toàn bộ USDu đang lưu hành.

JLP tạo ra doanh thu từ bốn nguồn chính:  

- Phí giao dịch trên Jupiter Perp.
- Phí thanh lý khi vị thế của trader bị đóng.
- Phí price impact từ các lệnh giao dịch lớn.
- Lợi nhuận từ sự tăng giá của các tài sản cơ bản trong rổ JLP (SOL, ETH, WBTC, USDC).

Đáng chú ý là việc người nắm giữ token JLP được hưởng 75% toàn bộ phí giao dịch của nền tảng Jupiter Perp. Do đó, đây là nguồn thu chính tạo nên lợi suất của sUSDu..

### Phần 2: Quỹ phòng ngừa rủi ro (20%)

Khoảng 20% còn lại được gửi đến dịch vụ lưu ký tài sản số CEFFU. Đơn vị này sử dụng công nghệ MirrorX để hiển thị số dư này vào tài khoản phụ Binance của Unitas và cho phép mở vị thế giao dịch, tuy nhiên tiền thật vẫn nằm ở CEFFU, không phải trên sàn.

Phần ký quỹ này được dùng để mở vị thế bán khống (short) tương đương với giá trị JLP đang nắm giữ. Đòn bẩy của phần hedging thường từ 2x đến 4x. Hệ thống tự động theo dõi tỷ lệ đòn bẩy và phát cảnh báo khi tiệm cận ngưỡng giới hạn, kích hoạt việc bổ sung ký quỹ để duy trì tỷ lệ an toàn.

Hai vị thế mua JLP dài hạn và short trên Binance sẽ triệt tiêu rủi ro biến động giá của nhau, nhưng vẫn giữ nguyên dòng thu nhập từ phí JLP và phí funding rate từ vị thế short.

![](https://cdn.coin68.com/images/20260319041953-fb8da85e-48ee-42c0-9bad-e0f8dfd6596c-106.jpg) Sơ đồ cơ chế hoạt động của Unitas

Tóm lại, vòng tuần hoàn vốn đầy đủ khi người dùng thực hiện mint USDu gồm các bước sau:  

- **Bước 1**: Người dùng nạp USDC để mint USDu.
- **Bước 2**: USDC được chuyển vào Fund Vault.
- **Bước 3**: 80% số USDC được dùng để mua JLP và lưu trữ trong ví multisig on-chain, 20% còn lại được gửi đến CEFFU làm ký quỹ.
- **Bước 4**: Unitas mở vị thế short JLP trên Binance bù trừ rủi ro giá.
- **Bước 5**: Doanh thu từ phí JLP và funding rate tích lũy liên tục.
- **Bước 6**: Doanh thu được nạp vào hợp đồng staking, đẩy tỷ giá sUSDu/USDu tăng dần.

Toàn bộ doanh thu được phân phối theo tỷ lệ:  

- **80%** dành cho pool staking sUSDu.
- **10%** dành cho quỹ bảo hiểm.
- **10%** dành cho việc mua lại token của giao thức.

## Lộ trình phát triển

Theo thông tin từ roadmap 2026, Unitas đang hướng tới mở rộng danh mục sản phẩm và hạ tầng:  

- **Qúy 2/2026**: Ra mắt tài sản vàng sinh lời xGLD, duy trì tiếp xúc với giá vàng trong khi tạo lợi nhuận thông qua chiến lược carry trade (chênh lệch lãi suất). xGLD sẽ tương thích với các giao thức cho vay và cung cấp thanh khoản trong DeFi.
- **Trong năm 2026**: Mở rộng hạ tầng hỗ trợ thêm BTC và các [Real World Assets (RWAs)](https://coin68.com/tim-hieu-ve-real-world-asset-rwa/) như vàng, bạc và các hàng hóa khác.
- **Tương lai**: Mở rộng tích hợp với các ví và nền tảng lớn, nâng cấp hệ thống thực thi và quản lý tài sản đảm bảo để hỗ trợ quy mô triển khai vốn lớn hơn.

## Đội ngũ phát triển

Thông tin công khai về đội ngũ lãnh đạo cụ thể của Unitas Labs hiện chưa được công bố. Coin68 sẽ cập nhật khi có thêm thông tin.

## Nhà đầu tư

![](https://cdn.coin68.com/images/20260319041953-8de1221d-3bd2-4e65-933c-970c72aa7ba7-141.jpg) Các nhà đầu tư của Unitas

Unitas đã huy động thành công 13,33 triệu USD trong vòng Seed từ các quỹ đầu tư như Awaken, Amber Group, Blockchain Builders Fund, Taisu Ventures, SevenX Ventures, Bixin Ventures.

## Tokenomics

### Thông tin token

| **Tên dự án** | Unitas |
| --- | --- |
| **Ký hiệu token** | UP |
| **Blockchain** | Đang cập nhật… |
| **Địa chỉ hợp đồng** | Đang cập nhật… |
| **Tổng cung** | Đang cập nhật… |

### Tỷ lệ phân bổ token UP

![](https://cdn.coin68.com/images/20260319041953-d272fc29-2fc9-4683-bced-3cd2afbc1a60-96.jpg) Tỷ lệ phân bổ token UP

Token UP được phân bổ theo tỷ lệ sau:  

- **Hệ sinh thái & Cộng đồng - 45%**: Một phần dành cho airdrop cho người nắm giữ Units, phần còn lại hỗ trợ tích hợp giao thức và ưu đãi dành cho đối tác. Lịch mở khóa sẽ được thông báo khi TGE.
- **Thanh khoản & Chương trình sàn giao dịch - 18%**: Không có thời gian khóa, mở khóa theo lịch do quản trị quyết định.
- **Nhà đầu tư - 22%**: Khóa 12 tháng, vesting tuyến tính trong 24 tháng tiếp theo.
- **Đội ngũ & Cố vấn - 15%**: Khóa 12 tháng, vesting tuyến tính trong 24 tháng tiếp theo.

### Token use case

- Nhận doanh thu giao thức thông qua staking.
- Bỏ phiếu quản trị.
- Tham gia vào các cơ hội và sản phẩm đặc biệt dành riêng cho người nắm giữ token.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án Unitas, Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.