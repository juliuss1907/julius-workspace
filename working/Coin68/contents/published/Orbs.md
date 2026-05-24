---
title: "Orbs - Layer-3 cho giao dịch on-chain chuyên nghiệp"
source: "https://coin68.com/orbs-la-gi/"
published: 2026-05-20
created: 2026-05-21
description: "Orbs hoạt động như \"backend phi tập trung\" giúp nâng cấp khả năng cho smart contract mà không cần di chuyển thanh khoản sang chain mới."
tags:
  - "infrastructure"
  - "layer-3"
---
**Trong bối cảnh hệ sinh thái blockchain ngày càng phân mảnh, các giao thức DeFi vẫn phải đối mặt với nhiều hạn chế về khả năng thực thi của smart contract như thanh khoản rời rạc, thiếu các loại lệnh giao dịch nâng cao, đến việc phụ thuộc vào backend tập trung. Orbs hoạt động như "backend phi tập trung" giúp nâng cấp khả năng cho smart contract mà không cần di chuyển thanh khoản sang chain mới. Hãy cùng Coin68 tìm hiểu về dự án này trong bài viết dưới đây.**

![](https://cdn.coin68.com/images/20260520040358-5ae336d9-bd6f-43af-8903-5e935100ff41-114.jpg) Orbs là gì? Tìm hiểu về hạ tầng layer-3 cho giao dịch on-chain chuyên nghiệp

## Orbs Network là gì?

**Orbs Network** là một hạ tầng blockchain mở, phi tập trung, vận hành bởi mạng lưới validator sử dụng cơ chế đồng thuận [Proof-of-Stake](https://coin68.com/proof-of-stake-la-gi/) (PoS). Ra mắt mainnet từ năm 2019, Orbs tự định vị mình là một giao thức [layer-3](https://coin68.com/layer-3-la-gi/), tức là hoạt động bên trên các blockchain layer-1 và layer-2 hiện có, thay vì cạnh tranh trực tiếp với chúng.

![](https://cdn.coin68.com/images/20260520040358-6787e448-6108-4580-9a4b-530679186a45-166.jpg) Orbs là gì?

Khác với các layer-1 như Ethereum hay TON vốn tập trung vào bảo mật và phân quyền ở tầng nền tảng, hoặc các [layer-2](https://coin68.com/layer-2-la-gi-toan-tap-ve-layer-2-va-co-hoi-moi-nam-mot-lan/) như [Polygon](https://coin68.com/polygon-matic-la-gi/) hay [Arbitrum](https://coin68.com/arbitrum-arb-la-gi/) tập trung vào khả năng mở rộng giao dịch, Orbs đảm nhận vai trò Enhanced Execution, tăng cường khả năng thực thi cho smart contract. Nói cách khác, Orbs là một "máy chủ phi tập trung" giúp các dApp làm được những điều mà smart contract thông thường không thể tự thực hiện, từ việc tổng hợp thanh khoản, thực thi lệnh giao dịch thuật toán, đến vận hành các dịch vụ off-chain phức tạp, tất cả đều diễn ra một cách minh bạch và phi tập trung.

**Có thể bạn quan tâm:  
  
**
- [Xai (XAI) là gì? Giải pháp Layer 3 cho lĩnh vực gaming](https://coin68.com/xai-la-gi/)
- [Degen là gì? Tìm hiểu về memecoin xây dựng layer 3 trên Base](https://coin68.com/degen-chain-la-gi/)

## Kiến trúc và bảo mật

Điểm đặc biệt trong thiết kế của Orbs nằm ở cách nó đảm bảo tính bảo mật cho mạng lưới. Thay vì tự vận hành một cơ chế bầu chọn validator riêng, Orbs triển khai toàn bộ thuật toán PoS của mình dưới dạng smart contract trên chính Ethereum mainnet. Điều này có nghĩa là:  

- Validator được bầu chọn và quản lý thông qua smart contract trên Ethereum, không phải trên một chain riêng của Orbs.
- Bất kỳ ai cũng có thể tham gia làm validator hoặc ủy quyền stake (delegate) cho các validator.
- Kết quả bầu chọn validator có thể được kiểm chứng độc lập từ bên ngoài mà không cần tin tưởng vào bất kỳ bên thứ ba nào.

## Hỗ trợ đa chain

Orbs được thiết kế để tương thích chặt chẽ với hai hệ sinh thái blockchain lớn nhất hiện nay:

### EVM (Ethereum Virtual Machine)

Orbs hỗ trợ tất cả các blockchain tương thích EVM phổ biến như Ethereum mainnet, Polygon, BNB Chain, Avalanche, Fantom và các smart contract viết bằng Solidity. Điều này cho phép hàng nghìn dApp DeFi hiện có dễ dàng tích hợp các giải pháp của Orbs mà không cần thay đổi kiến trúc.

### TON (The Open Network)

Orbs hỗ trợ [TON](https://coin68.com/toncoin-la-gi/) mainnet và smart contract viết bằng FunC, được thiết kế để bổ trợ cho kiến trúc bất đồng bộ (asynchronous) đặc thù của TON. Đây là bước đi chiến lược giúp Orbs tiếp cận hệ sinh thái TON đang phát triển nhanh chóng.

## Bộ công cụ phát triển

Orbs cung cấp hai môi trường thực thi cho developer, tương tự như mô hình serverless và container của điện toán đám mây truyền thống nhưng hoàn toàn phi tập trung.

### Orbs Lambda: Serverless phi tập trung

Orbs Lambda là một nền tảng cloud function phi tập trung, tương tự như AWS Lambda. Developer có thể viết và triển khai các hàm xử lý bằng những ngôn ngữ phổ biến như JavaScript hoặc TypeScript mà không cần học thêm ngôn ngữ smart contract mới. Orbs Lambda đặc biệt phù hợp cho các dApp muốn loại bỏ backend tập trung mà không cần xây dựng hạ tầng phức tạp.

### Orbs VM: Container phi tập trung

Đối với các use-case phức tạp hơn, Orbs VM cung cấp môi trường máy ảo phi tập trung dựa trên Docker, tương tự như AWS EC2. Developer có thể sử dụng bất kỳ ngôn ngữ lập trình nào để xây dựng các dịch vụ always-on, không bị "ngủ đông" như serverless.

Orbs VM cho phép các dịch vụ liên tục theo dõi nhiều blockchain cùng lúc bằng cách đọc và phân tích block mới, lý tưởng cho các ứng dụng như oracle giá, bot giao dịch hoặc hệ thống thanh lý vị thế.

## Các sản phẩm của Orbs

Đây là mảng ứng dụng nổi bật nhất của Orbs, bao gồm một bộ các giao thức giao dịch nâng cao giúp các DEX và nền tảng DeFi đạt được trải nghiệm ngang tầm các sàn tập trung (CeFi).

### Liquidity Hub

Liquidity Hub giải quyết vấn đề phân mảnh thanh khoản của DeFi bằng cách hoạt động như một lớp tối ưu hóa phi tập trung cho [AMM](https://coin68.com/automated-market-marker-amm/), cho phép [DEX](https://coin68.com/dex-la-gi/) tiếp cận các nguồn thanh khoản bên ngoài thông qua hai cơ chế:  

- **On-chain solver auction**: Các solver bên thứ ba cạnh tranh để thực hiện giao dịch với mức giá tốt nhất, sử dụng thanh khoản on-chain từ các AMM pool hoặc inventory riêng.
- **Decentralized order API**: Cho phép các nhà tạo lập thị trường chuyên nghiệp gửi bid để cạnh tranh thực hiện giao dịch.

Ngoài ra, Liquidity Hub còn có cơ chế fallback, nếu không thể thực hiện giao dịch ở mức giá tốt hơn AMM, giao dịch sẽ tự động quay về AMM như bình thường. Điều này đảm bảo người dùng không bao giờ nhận được mức giá tệ hơn so với swap thông thường.

### Perpetual Hub

Perpetual Hub là bộ công cụ toàn diện của Orbs nhằm thúc đẩy sự phát triển của perpetual futures trên blockchain, bao gồm ba thành phần:  

- **Hedger**: Công nghệ cho phép market maker hoạt động như đối tác trong các giao dịch perpetual, có thể tận dụng thanh khoản từ các sàn tập trung như Binance để cung cấp mức giá cạnh tranh trên on-chain.
- **Liquidator**: Cơ chế thanh lý vị thế phi tập trung. Khi tài sản thế chấp của người dùng giảm xuống dưới ngưỡng duy trì, các liquidator sẽ được khuyến khích thanh lý vị thế và nhận phí.
- **Price Oracle:** Dịch vụ oracle giá phi tập trung, cung cấp dữ liệu cho việc tính toán lãi/lỗ chưa thực hiện (uPnL) và xác định ngưỡng thanh lý.

Perpetual Hub được phát triển với sự hợp tác của các dự án như SYMMIO và IntentX, những đơn vị đang tiên phong trong kiến trúc intent-based cho perpetual futures.

### dTWAP

dTWAP là giải pháp giúp giải quyết bài toán bất khả thi khi triển khai TWAP trên smart contract EVM do giới hạn của môi trường sandbox. Sản phẩm này gồm 2 thành phần chính:  

- **Maker**: Người tạo lệnh, thiết lập các tham số như thời lượng, kích thước giao dịch, khoảng cách giữa các lần thực thi.
- **Taker**: Các bên tham gia độc lập (bao gồm chính các validator của Orbs) cạnh tranh để tìm đường đi tối ưu cho từng phần của lệnh và gửi bid với mức phí thấp nhất.

dTWAP đã được tích hợp vào các DEX lớn như SushiSwap, QuickSwap và SpookySwap.

### dLIMIT

dLIMIT là phiên bản đặc biệt của dTWAP, giúp đảm bảo lệnh được thực thi ở mức giá tối ưu với mức phí hợp lý, khắc phục các lỗ hổng phổ biến của những triển khai limit order thiếu hoàn thiện trong DeFi.

### dSLTP

dSLTP là giải pháp stop order phi tập trung đầu tiên dành cho DEX, cho phép người dùng thiết lập lệnh stop-loss (cắt lỗ) và take-profit (chốt lời), những công cụ quản lý rủi ro thiết yếu vốn chỉ có trên các sàn tập trung. Người dùng có thể tùy chỉnh:  

- **Trigger price**: Mức giá kích hoạt lệnh.
- **Limit price**: Mức giá sàn (đối với limit order) để bảo vệ khỏi trượt giá quá sâu.
- **Thời gian hiệu lực của lệnh.**

Toàn bộ quá trình được vận hành bởi mạng lưới validator của Orbs, đảm bảo lệnh được theo dõi và thực thi 24/7 với độ dự phòng cao.

## Đội ngũ phát triển

Chưa có thông tin về các thành viên của Orbs. Coin68 sẽ cập nhật khi có thêm thông tin.

## Nhà đầu tư

![](https://cdn.coin68.com/images/20260520040358-68daa811-9de9-41b8-9e2a-ee63746d0815-108.jpg) Các nhà đầu tư của Orbs

Orbs đã huy động được 10 triệu USD từ DWF Labs vào tháng 03/2023.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án Orbs, một giao thức layer-3 với tham vọng mang trải nghiệm giao dịch cấp độ CeFi lên các nền tảng DeFi. Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.