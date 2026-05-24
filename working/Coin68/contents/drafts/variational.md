---
title: "Variational là gì? Tìm hiểu về giao thức phái sinh phi tập trung đa tài sản"
source: "https://coin68.com/variational-la-gi/"
published: 2025-12-01
created: 2026-05-22
description: "Variational là giao thức phái sinh phi tập trung tập trung vào việc tổng hợp thanh khoản từ cả thị trường crypto và truyền thống, cung cấp các sản phẩm như perpetuals và options thông qua hai ứng dụng chính là Omni và Pro."
tags:
  - "perp-dex"
  - "infrastructure"
---

**Variational là giao thức phái sinh phi tập trung (decentralized derivatives protocol) tập trung vào việc tổng hợp thanh khoản từ cả thị trường crypto và truyền thống. Dự án cung cấp các sản phẩm như perpetuals và options thông qua hai ứng dụng chính là Omni dành cho retail và Pro dành cho institutional. Hãy cùng Coin68 tìm hiểu dự án này trong bài viết dưới đây.**

## Variational là gì?

**Variational** là một giao thức giao dịch peer-to-peer cho các sản phẩm phái sinh bao gồm perpetual futures, options và các công cụ tổng quát hơn. Giao thức cho phép thanh toán và bù trừ (clearing) hoàn toàn on-chain trong các hợp đồng escrow riêng biệt.

Điểm độc đáo của Variational là khả năng tổng hợp thanh khoản từ nhiều nguồn khác nhau bao gồm CEXs, DEXs và các nhà cung cấp thanh khoản truyền thống (TradFi dealers). Điều này cho phép nền tảng cung cấp độ sâu thị trường tốt nhất có thể cho mỗi loại tài sản, từ crypto, cổ phiếu, hàng hóa đến ngoại hối.

Giao thức hiện đang vận hành hai ứng dụng chính:
- **Omni**: Sàn giao dịch perpetuals với phí 0% hướng đến retail traders
- **Pro**: Giải pháp settlement on-chain cho các giao dịch OTC derivatives tùy chỉnh dành cho institutional

**Có thể bạn quan tâm:**  
  
- [Hyperliquid là gì? Tìm hiểu chi tiết về sàn phái sinh trên blockchain](https://coin68.com/hyperliquid-la-gi/)
- [Perpetual Protocol (PERP) là gì? Tìm hiểu về giao thức phái sinh trên Ethereum](https://coin68.com/perpetual-protocol-la-gi/)

## Sản phẩm và tính năng chính

### Variational Omni

**Omni** là ứng dụng đầu tiên được xây dựng trên Variational Protocol, mang đến trải nghiệm giao dịch perpetuals với nhiều điểm độc đáo:

**Zero Fees (Phí 0%)**

Omni không thu phí giao dịch. Thay vào đó, nền tảng tạo ra doanh thu bằng cách giữ lại yield từ market making thay vì chia cho các market makers bên thứ ba. Cấu trúc này cho phép Omni duy trì mô hình zero fees vĩnh viễn.

**Thanh khoản từ nhiều nguồn**

Omni Liquidity Provider (OLP) truy cập trực tiếp vào thanh khoản từ CEXs, DEXs và các dealer truyền thống. Điều này cho phép nền tảng cung cấp spread chặt chẽ nhất có thể trên các thị trường crypto và RWA (Real World Assets).

**Hơn 450 thị trường**

Bằng cách kết nối với thanh khoản hiện có thay vì tạo order book mới, Omni có thể niêm yết và duy trì nhiều thị trường hơn hẳn so với sàn order book truyền thống. Hiện tại có hơn 450 thị trường crypto và RWA đang hoạt động, với kế hoạch thêm 100+ thị trường RWA trong mùa hè 2025.

**Tích hợp nhiều tài sản trong một tài khoản**

Ngưởi dùng có thể giao dịch crypto, cổ phiếu và hàng hóa trong một tài khoản cross-margined duy nhất. Đòn bẩy tối đa lên đến 50x và ngưởi dùng có thể sử dụng nhiều token khác nhau làm collateral.

**Thống kê hiện tại của Omni:**
- Tổng volume: $46B+
- Open Interest: $173M+
- Số thị trường: 213+
- Số trader duy nhất: 50K+
- Doanh thu chia sẻ cho trader: $6M+

### Variational Pro

**Pro** là giải pháp cho thị trường OTC derivatives trị giá hàng nghìn tỷ USD, hiện đang vận hành chủ yếu thông qua các kênh chat Telegram và quy trình thủ công.

**Vấn đề Pro giải quyết**

Theo đội ngũ Variational, giao dịch OTC derivatives hiện tại:
- Được thương lượng qua Telegram chat và các kênh không chính thức
- Settlement được thực hiện thủ công và hậu tố
- Quy trình margin call chậm, tạo rủi ro counterparty lớn

Các nền tảng như Paradigm và Deribit chỉ hỗ trợ options trên các coin lớn (BTC, ETH, SOL) và thiếu khả năng tùy chỉnh, mặc dù vẫn xử lý hơn $1 nghìn tỷ volume hàng năm.

**Các tính năng chính của Pro:**

1. **Custom Derivatives**: Tạo futures và options tùy chỉnh cho bất kỳ tài sản nào có price feed
2. **Modernize OTC Flows**: Thay thế Telegram và spreadsheets bằng hệ thống tự động toàn diện
3. **Mitigate Counterparty Risk**: Đối mặt trực tiếp với counterparty thay vì pool rủi ro trên sàn, bảo vệ với margin và liquidation engine configurable
4. **Deep Liquidity**: RFQ (Request for Quote) tổng hợp từ nhiều nguồn
5. **Full Automation**: Tự động hóa toàn bộ quy trình booking, clearing, settlement, risk management và reporting

Pro hiện đang trong giai đoạn waitlist và sắp ra mắt.

## Cơ chế hoạt động

### Tổng hợp thanh khoản

Variational hoạt động như một layer cơ sở hạ tầng trung gian giữa traders và các nguồn thanh khoản. Thay vì tạo order book riêng, giao thức request quotes từ nhiều nhà cung cấp thanh khoản đồng thờ và trả về giá tốt nhất cho trader.

### Request-for-Quote (RFQ)

Hệ thống RFQ cho phép trader nhận được giá tốt nhất cho mọi giao dịch mà không cần chạm vào order book. Điều này đặc biệt hữu ích cho các giao dịch lớn hoặc các thị trường ít thanh khoản.

### On-chain Settlement

Tất cả các giao dịch đều được thanh toán và bù trừ on-chain trong các hợp đồng escrow riêng biệt. Điều này đảm bảo tính minh bạch và loại bỏ rủi ro counterparty.

### Margin và Liquidation Engine

Cả Omni và Pro đều sử dụng margin engine configurable có thể điều chỉnh theo yêu cầu của từng trader hoặc institution. Hệ thống liquidation tự động được kích hoạt khi tỷ lệ margin giảm xuống dưới ngưỡng an toàn.

## Đội ngũ phát triển

Variational được đồng sáng lập bởi **Lucas Schuermann** và **Edward Yu**, hai cựu sinh viên và nghiên cứu sinh tại Columbia University.

Trước khi thành lập Variational, cả hai đã cùng nhau sáng lập Qu Capital - một quỹ phòng hộ (hedge fund) tập trung vào crypto vào năm 2017. Năm 2019, Qu Capital được Digital Currency Group (DCG) mua lại, và Lucas cùng Edward lần lượt trở thành Phó Chủ tịch Kỹ thuật (VP of Engineering) và Phó Chủ tịch Giao dịch Định lượng (VP of Quant Trading) tại Genesis Trading.

Tại Genesis, họ đã xử lý hàng trăm tỷ USD khối lượng giao dịch khi Genesis là một trong những sàn giao dịch lớn nhất trong ngành. Năm 2021, sau khi tích lũy đủ kinh nghiệm và hiểu biết sâu sắc về thị trường, Lucas và Edward rồi Genesis để thành lập công ty giao dịch riêng: Variational.

## Nhà đầu tư và gọi vốn

Variational đã gọi thành công **tổng cộng $61.8 triệu USD** qua 3 vòng gọi vốn:

### Vòng Series A (Tháng 5/2026) - $50 triệu USD

**Lead investor:** Dragonfly Capital  
**Các nhà đầu tư tham gia:** Bain Capital Crypto, Coinbase Ventures, Peak XV Partners  
**Mục đích sử dụng vốn:** Mở rộng infrastructure, phát triển thị trường tài sản thế giới thực (RWA), và tăng cường thanh khoản

Đây là vòng gọi vốn lớn nhất của dự án, diễn ra khi Variational đã chứng minh được khả năng tạo ra doanh thu ổn định từ hoạt động giao dịch và sẵn sàng mở rộng quy mô. Thông tin chi tiết về vòng gọi vốn này đã được Coin68 đưa tin tại [bài viết này](https://coin68.com/variational-huy-dong-50-trieu-usd-de-dua-thanh-khoan-pho-wall-len-blockchain/).

### Vòng Strategic (Tháng 6/2025) - $1.5 triệu USD

**Các nhà đầu tư:** Mirana Ventures, Caladan, Zoku Ventures  
**Mục đích:** Hỗ trợ phát triển chiến lược và mở rộng mối quan hệ đối tác

### Vòng Seed (Tháng 10/2024) - $10.3 triệu USD

**Lead investors:** Bain Capital Crypto, Peak XV Partners (trước đây là Sequoia Capital India & SEA)  
**Các nhà đầu tư tham gia:** Coinbase Ventures, Dragonfly Capital, Hack VC, North Island Ventures (NIV)  
**Mục đích:** Xây dựng MVP của giao thức, tuyển dụng core team, và khởi động development

Vòng Seed đã giúp Variational Phát triển giao thức ban đầu và ra mắt Omni - sản phẩm flagship dành cho thị trường retail.

Các quỹ này đều có danh tiếng mạnh trong việc đầu tư vào các dự án infrastructure và DeFi tại giai đoạn sớm.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án Variational — một giao thức phái sinh phi tập trung với khả năng tổng hợp thanh khoản độc đáo từ cả crypto và truyền thống. Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lợi khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.

## 🔍 Kiểm chứng thông tin (NỘI BỘ)

| Mục | Trạng thái | Ghi chú |
|-----|-----------|--------|
| Tổng volume $46B+ | ✅ Đã xác minh | Nguồn: docs.variational.io và variational.io/omni |
| Open Interest $173M+ | ✅ Đã xác minh | Nguồn: docs.variational.io |
| 450+ thị trường | ✅ Đã xác minh | Nguồn: docs.variational.io |
| 50K+ unique traders | ✅ Đã xác minh | Nguồn: docs.variational.io |
| Revenue share $6M+ | ✅ Đã xác minh | Nguồn: docs.variational.io |
| Đòn bẩy tối đa 50x | ✅ Đã xác minh | Nguồn: variational.io/omni |
| Tên founders và LinkedIn | ✅ Đã xác minh | Nguồn: variational.io/about |
| Danh sách nhà đầu tư | ✅ Đã xác minh | Nguồn: docs.variational.io và variational.io |
| Pro đang waitlist | ✅ Đã xác minh | Nguồn: variational.io/pro |
