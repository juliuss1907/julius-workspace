---
title: "Metric là gì? Tìm hiểu về sàn DEX với mô hình Active Pools"
source:
  - "https://metric.xyz/"
  - "https://docs.metric.xyz/"
published:
created: 2026-10-26
description: "Metric là sàn giao dịch phi tập trung (DEX) áp dụng mô hình Active Pools, cho phép tách biệt định giá và phân bổ thanh khoản để tối ưu hóa hiệu quả sử dụng vốn."
tags:
  - "DEX"
  - "DeFi"
  - "metric"
---

**Metric là sàn giao dịch phi tập trung (DEX) tiên phong ứng dụng mô hình Active Pools, cho phép phân tách hoàn toàn giữa logic định giá và lớp lưu ký thanh khoản. Thông qua việc tự động điều chỉnh các vùng thanh khoản bám sát giá tham chiếu từ oracle, nền tảng giúp nhà cung cấp thanh khoản tối ưu hóa hiệu suất sinh lời mà không cần can thiệp tái cân bằng thủ công. Hãy cùng Coin68 tìm hiểu chi tiết về Metric qua bài viết dưới đây!**

## Metric là gì?

**Metric** là một sàn giao dịch phi tập trung (DEX) hoạt động theo mô hình Active Pools, được thiết kế nhằm nâng cao hiệu quả sử dụng vốn cho các nhà tạo lập thị trường và nhà cung cấp thanh khoản (LP). Nền tảng cho phép dòng tiền được điều phối liên tục theo biến động thị trường thực tế mà không cần LP phải liên tục nạp rút vốn như các giao thức AMM truyền thống. Tính đến nay, Metric đã ghi nhận tổng khối lượng giao dịch tích luỹ vượt mốc **25,7 tỷ USD**.

Khác với mô hình Concentrated Liquidity AMM (thanh khoản tập trung) điển hình như Uniswap v3 vốn cố định phạm vi giá tuyệt đối, Metric phân tách độc lập giữa bộ cung cấp giá (Price Provider) và bể thanh khoản (Liquidity Pool). Nhờ đó, các khoảng thanh khoản tự động tịnh tiến theo giá tham chiếu thị trường, bảo toàn vị thế cho LP và hạn chế tối đa nguy cơ cạn kiệt thanh khoản khi thị trường biến động mạnh.

**Có thể bạn quan tâm:**

- [DefiTuna là gì? Nền tảng Fusion AMM tiên tiến trên Solana](https://coin68.com/defituna-la-gi/)
- [Ambient Finance - Dự án AMM DEX thế hệ mới trên Ethereum](https://coin68.com/ambient-finance-la-gi/)

## Điểm nổi bật của Metric

### Cơ chế Active Pools và phân tách định giá

Metric giải quyết hạn chế cố hữu của AMM truyền thống bằng cách tách rời hợp đồng định giá khỏi hợp đồng lưu ký tài sản. Các thông số giá bid, ask và giá tham chiếu được Price Provider liên tục cập nhật từ các nguồn oracle phi tập trung uy tín hoặc thuật toán riêng biệt. Nhờ cấu trúc này, thanh khoản trong pool luôn phản ánh sát sao cung cầu thực tế của thị trường mà không phụ thuộc vào các giao dịch chênh lệch giá (arbitrage) để cân bằng lại tỷ giá.

### Tối ưu hiệu quả sử dụng vốn cho LP

Trong các AMM tập trung thông thường, khi giá tài sản vượt ra ngoài khoảng thiết lập, vốn của nhà cung cấp thanh khoản lập tức rơi vào trạng thái ngừng sinh phí và chuyển hoàn toàn thành một loại token có giá trị thấp hơn. Ở Metric, toàn bộ các vùng thanh khoản được tính theo tỷ lệ phần trăm lệch quanh giá tham chiếu thay vì các mức giá danh nghĩa cố định. Khi giá tham chiếu dịch chuyển, vị thế của LP tự động trượt theo mà không làm thay đổi số lượng token hay tỷ lệ sở hữu tài sản ban đầu, giúp loại bỏ chi phí giao dịch tái cấu trúc và nguy cơ tổn thất vô thường kéo dài.

### Phân tầng rủi ro và tiêu chuẩn Anchored Pricing

Hệ thống phân tầng rủi ro (Pool Tiers) của Metric thiết lập tiêu chuẩn minh bạch cho người tham gia thị trường thông qua bốn cấp độ bảo vệ rõ ràng. Nhóm hồ thanh khoản Best Practices yêu cầu giá tham chiếu phải được neo độc lập (Anchored Pricing) qua Chainlink hoặc Pyth với tần suất cập nhật dưới 15 giây, đi kèm công cụ StopLoss bất biến giới hạn mức sụt giảm tối đa 15% mỗi ngày. Các nhóm Neutral, High Risk và Private phân loại chi tiết mức độ tin cậy của bên quản lý chiến lược (curator) và quyền hạn rút vốn, tạo cơ sở để LP lựa chọn mức độ rủi ro tương ứng.

## Sản phẩm và tính năng của Metric

### Swap và định tuyến thanh khoản

Người dùng phổ thông có thể thực hiện giao dịch hoán đổi token nhanh chóng với độ trượt giá tối thiểu nhờ thanh khoản tập trung sâu quanh giá tham chiếu. Thay vì chỉ trông chờ vào giao diện người dùng trực tiếp, Metric định tuyến phần lớn dòng lệnh thông qua các DEX aggregator và solver mạng lưới lớn như 1inch, 0x, CoW Swap, OKX và KyberSwap. Hệ thống cũng liên kết sâu với các block builder hàng đầu như Titan hay BuilderNet nhằm đưa giao dịch vào khối với tốc độ tối ưu, hạn chế tối đa nguy cơ bị tấn công MEV và chạy trước lệnh (front-running).

### Cung cấp thanh khoản (Liquidity Provision)

Nhà cung cấp thanh khoản tham gia gửi token vào các pool mở để nhận phần chia phí giao dịch phát sinh từ dòng lệnh của mạng lưới. Giao diện nền tảng hiển thị chi tiết các thông số về độ rộng vùng giá, nguồn cấp giá tham chiếu, lịch sử trượt giá và phân tầng bảo mật của từng pool. Khi nạp vốn, người dùng nhận được phần chia tỷ lệ sở hữu minh bạch và có thể linh hoạt rút lại cả hai đầu tài sản gốc bất cứ lúc nào nếu pool không cài đặt giới hạn rút tiền đặc biệt.

### Private Pools dành cho Market Maker

Private Pools là giải pháp chuyên biệt hướng đến các tổ chức tạo lập thị trường chuyên nghiệp và các quỹ đầu tư muốn triển khai chiến lược định giá độc quyền. Tính năng này cho phép các đơn vị market maker tự cung ứng toàn bộ nguồn vốn thanh khoản mà không mở cổng nhận nạp từ người dùng bên ngoài. Đổi lại, họ có toàn quyền tuỳ biến công thức toán học của Price Provider, điều chỉnh spread theo thời gian thực và quản trị rủi ro thanh khoản theo mô hình định lượng riêng.

### Hỗ trợ tài sản token hóa (RWA) và Tokenized Stocks

Metric cung cấp hạ tầng giao dịch tối ưu cho các tài sản thế giới thực được mã hóa (RWA), đặc biệt là nhóm cổ phiếu token hóa như Robinhood Stock Tokens hay B20 Assets trên Robinhood Chain. Thông qua Multiplier Oracle chuyên dụng, nền tảng có khả năng xử lý chính xác các sự kiện chia tách cổ phiếu, điều chỉnh cổ tức và giờ đóng mở cửa của thị trường chứng khoán truyền thống. Nhờ đó, người dùng Web3 có thể giao dịch các sản phẩm tài chính truyền thống on-chain với thanh khoản liền mạch và tỷ giá chuẩn xác theo giờ thị trường toàn cầu.

## Cơ chế hoạt động của Metric

Cơ chế vận hành của Metric xoay quanh sự tương tác nhịp nhàng giữa ba thành phần kỹ thuật cốt lõi: Price Provider, Liquidity Pool và các Extension quản trị.

Price Provider đóng vai trò như bộ não định giá của pool thanh khoản. Đây là một smart contract độc lập nhận dữ liệu giá tham chiếu (reference price) theo thời gian thực từ các hệ thống oracle đáng tin cậy như Pyth Network hay Chainlink. Price Provider tính toán ra các mức giá mua vào (bid) và bán ra (ask) tối ưu, tạo thành một khung định giá động cho toàn bộ pool.

Bể lưu ký Liquidity Pool chịu trách nhiệm bảo quản tài sản của LP và phân bổ nguồn vốn này vào các "bin" (ngăn thanh khoản). Mỗi bin tương ứng với một khoảng phần trăm độ lệch (deviation) xác định so với giá tham chiếu, thay vì gắn chặt vào một mốc giá USD cụ thể. Khi thị trường biến động và Price Provider cập nhật giá tham chiếu mới, toàn bộ hệ thống bin này tự động dịch chuyển đồng pha theo trục giá mới. Quá trình tịnh tiến diễn ra ngay trong logic tính toán giao dịch mà không làm phát sinh chi phí gas tái cân bằng vị thế, đồng thời giữ nguyên vẹn cơ cấu số lượng token của LP.

Để bảo vệ an toàn dòng vốn trước những biến động đột ngột hoặc lỗi nguồn cấp giá, Metric tích hợp các tiện ích mở rộng (Extensions). Tiêu biểu trong số đó là tiện ích StopLoss bất biến, có nhiệm vụ liên tục theo dõi độ chênh lệch giữa giá giao dịch và giá tham chiếu neo chuẩn. Nếu mức độ sụt giảm tài sản chạm ngưỡng quy định (chẳng hạn 15%/ngày) hoặc khi nguồn cấp giá mất tín hiệu cập nhật quá thời gian cho phép, cơ chế StopLoss sẽ tự động kích hoạt chế độ đóng băng giao dịch để bảo toàn vốn cho LP.

## Đội ngũ phát triển

Thông tin chi tiết về danh tính đội ngũ sáng lập và các thành viên phát triển cốt lõi của Metric hiện chưa được công bố rộng rãi trên các kênh truyền thông chính thức. Người dùng và các đối tác có thể liên hệ trực tiếp với dự án thông qua hòm thư hỗ trợ (contact@metric.xyz) hoặc kênh thảo luận cộng đồng trên nền tảng Discord.

## Nhà đầu tư và đối tác

Thông tin gọi vốn của Metric không được dự án công bố chính thức. Coin68 sẽ cập nhật thêm khi có thông báo mới nhất từ phía dự án.

Về mặt tích hợp và đối tác chiến lược, Metric đã xây dựng mạng lưới kết nối sâu rộng với hầu hết các DEX aggregator và trading bot phổ biến trên thị trường như 1inch, 0x, OKX, KyberSwap, CoW Swap, Velora, PancakeSwap, Banana Gun và GMGN. Bên cạnh đó, dự án hợp tác chặt chẽ cùng các đơn vị block builder hàng đầu gồm Titan, Quasar, BuilderNet, Eureka, Bombora, 48 Club và BlockRazor trên mạng lưới Ethereum và BNB Chain nhằm đảm bảo việc cập nhật giá của market maker luôn được ưu tiên thực thi trước các giao dịch thông thường.

## Tokenomics

Hiện tại, Metric **chưa phát hành token chính thức** và chưa công bố bất kỳ kế hoạch phân bổ tokenomics nào ra công chúng. 

Mọi hoạt động giao dịch và cung cấp thanh khoản trên nền tảng đều đang được vận hành thông qua các tài sản cơ sở của từng cặp giao dịch (như ETH, BNB, USDT, USDC hoặc các tài sản RWA liên kết). Người dùng cần đặc biệt cẩn trọng trước các hành vi giả mạo token mang tên Metric trên các sàn giao dịch phi tập trung để phòng tránh rủi ro lừa đảo.

## Bảo mật và kiểm toán

Metric đặt trọng tâm lớn vào tính an toàn của các hợp đồng thông minh thông qua việc thực hiện liên tiếp **5 đợt kiểm toán bảo mật chuyên sâu** từ các đơn vị uy tín hàng đầu ngành:

- **Zellic**: Thực hiện đợt kiểm toán toàn diện mã nguồn vào tháng 06/2026 và tiến hành tái kiểm toán (re-audit) hoàn thiện vào tháng 09/2026.
- **Sherlock**: Hoàn thành đợt thẩm định bảo mật độc lập trong giai đoạn tháng 05-06/2026, tổ chức chương trình thi săn lỗi nhận thưởng (bug bounty contest) công khai vào tháng 07/2026 và tiến hành kiểm toán bổ sung hệ thống hợp đồng ngoại vi (periphery) vào tháng 09/2026.

Việc trải qua nhiều vòng rà soát mã nguồn khắt khe từ hai tổ chức bảo mật lớn giúp giảm thiểu tối đa các lỗ hổng kỹ thuật trong logic tính toán bin và cơ chế kết nối oracle.

## Tổng kết

Metric mang đến một bước tiến đáng kể trong thiết kế sàn DEX thế hệ mới thông qua mô hình Active Pools. Bằng việc phân tách rõ ràng giữa thuật toán định giá và lớp thanh khoản, Metric giải quyết bài toán nhức nhối về chi phí tái cấu trúc vị thế và rủi ro trượt vùng giá của các nhà cung cấp thanh khoản trong mô hình AMM truyền thống.

Khả năng hỗ trợ song song cả tài sản tiền mã hóa bản địa lẫn các sản phẩm tài chính token hóa (RWA, cổ phiếu token hóa) trên nhiều chuỗi như Ethereum, BNB Chain và Robinhood Chain mở ra tiềm năng mở rộng lớn cho dự án. Tuy nhiên, do dự án vẫn đang trong giai đoạn phát triển và phụ thuộc mật thiết vào tính liên tục của hệ thống oracle cũng như hạ tầng block builder, người dùng và LP cần tìm hiểu kỹ thông tin phân tầng bảo mật trước khi tham gia cung cấp vốn.

> **Lưu ý:** Thông tin trong bài viết chỉ mang mục đích cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.

## 🔍 Kiểm chứng thông tin (NỘI BỘ)

| Mục | Trạng thái | Ghi chú |
|-----|-----------|--------|
| Mô hình Active Pools & phân tách Price Provider / Liquidity Pool | ✅ | Xác minh từ tài liệu chính thức docs.metric.xyz |
| Tổng khối lượng giao dịch tích luỹ vượt 25,7 tỷ USD | ✅ | Xác minh trực tiếp từ trang chủ metric.xyz |
| Triển khai mạng lưới: Ethereum, BNB Chain, Robinhood Chain | ✅ | Xác minh từ docs.metric.xyz (Chain ID 1, 56, 4663) |
| Định tuyến & tích hợp Aggregator: 1inch, 0x, OKX, KyberSwap, CoW Swap... | ✅ | Xác minh từ docs.metric.xyz |
| Hạ tầng Block Builder: Titan, Quasar, BuilderNet, 48 Club... | ✅ | Xác minh từ tài liệu kỹ thuật Metric |
| Phân tầng hồ thanh khoản (Pool Tiers: Best Practices, Neutral, High Risk, Private) | ✅ | Xác minh từ docs.metric.xyz |
| Kiểm toán bảo mật (5 đợt kiểm toán từ Zellic và Sherlock) | ✅ | Xác minh từ báo cáo kiểm toán của Zellic và Sherlock (05-09/2026) |
| Đội ngũ phát triển chưa công bố danh tính | ✅ | Chưa công bố công khai, liên hệ qua contact@metric.xyz |
| Nhà đầu tư & vòng gọi vốn chưa công bố | ✅ | Dùng câu fallback chính thức của Coin68 |
| Trạng thái token (chưa phát hành token) | ✅ | Dự án xác nhận chưa phát hành token chính thức |
