---
title: "Orbs Network là gì? Tìm hiểu về hạ tầng Layer 3 cho giao dịch on-chain chuyên nghiệp"
source: ""
published: ""
created: 2026-05-19
description: "Orbs Network là một giao thức Layer 3 phi tập trung, hoạt động như lớp backend tăng cường khả năng thực thi cho smart contract trên EVM và TON, tập trung vào các giải pháp giao dịch nâng cao."
tags:
  - infrastructure
  - defi
  - layer-1
---

**Trong bối cảnh hệ sinh thái blockchain ngày càng phân mảnh, các giao thức DeFi vẫn phải đối mặt với nhiều hạn chế về khả năng thực thi của smart contract — từ thanh khoản rời rạc, thiếu các loại lệnh giao dịch nâng cao, đến việc phụ thuộc vào backend tập trung. Orbs Network xuất hiện như một giải pháp Layer 3, hoạt động như "backend phi tập trung" giúp nâng cấp khả năng cho smart contract mà không cần di chuyển thanh khoản sang chain mới. Hãy cùng Coin68 tìm hiểu về dự án này trong bài viết dưới đây.**

## Orbs Network là gì?

**Orbs Network** là một hạ tầng blockchain mở, phi tập trung, vận hành bởi mạng lưới validator không cần cấp phép (*permissionless*) sử dụng cơ chế đồng thuận Proof-of-Stake (PoS). Ra mắt mainnet từ năm 2019, Orbs tự định vị mình là một giao thức Layer 3 (L3) — tức là hoạt động *bên trên* các blockchain Layer 1 và Layer 2 hiện có, thay vì cạnh tranh trực tiếp với chúng.

Khác với các L1 như Ethereum hay TON vốn tập trung vào bảo mật và phân quyền ở tầng nền tảng, hoặc các L2 như Polygon hay Arbitrum tập trung vào khả năng mở rộng giao dịch, Orbs đảm nhận vai trò *Enhanced Execution* — tăng cường khả năng thực thi cho smart contract. Nói cách khác, Orbs là một "máy chủ phi tập trung" giúp các dApp làm được những điều mà smart contract thông thường không thể tự thực hiện — từ việc tổng hợp thanh khoản, thực thi lệnh giao dịch thuật toán, đến vận hành các dịch vụ off-chain phức tạp — tất cả đều diễn ra một cách minh bạch và phi tập trung.

## Kiến trúc và bảo mật

Điểm đặc biệt trong thiết kế của Orbs nằm ở cách nó đảm bảo tính bảo mật cho mạng lưới. Thay vì tự vận hành một cơ chế bầu chọn validator riêng, Orbs triển khai toàn bộ thuật toán PoS của mình dưới dạng smart contract trên chính Ethereum mainnet. Điều này có nghĩa là:

- **Validator (Guardians)** được bầu chọn và quản lý thông qua smart contract trên Ethereum — không phải trên một chain riêng của Orbs.
- **Hơn 100 triệu USD** giá trị được stake vào các hợp đồng PoS của Orbs trên Ethereum và Polygon.
- Bất kỳ ai cũng có thể tham gia làm validator hoặc ủy quyền stake (delegate) cho các Guardian.
- Kết quả bầu chọn validator là *objectively auditable* — tức có thể được kiểm chứng độc lập từ bên ngoài mà không cần tin tưởng vào bất kỳ bên thứ ba nào.

Mô hình này tận dụng chính tính bảo mật của Ethereum để bảo vệ mạng lưới Orbs, tạo ra một lớp tin cậy vững chắc mà không cần phải "phát minh lại bánh xe".

## Hỗ trợ đa chain: EVM và TON

Orbs được thiết kế để tương thích chặt chẽ với hai hệ sinh thái blockchain lớn nhất hiện nay:

### EVM (Ethereum Virtual Machine)

Orbs hỗ trợ tất cả các blockchain tương thích EVM phổ biến như Ethereum mainnet, Polygon, BNB Chain, Avalanche, Fantom và các smart contract viết bằng Solidity. Điều này cho phép hàng nghìn dApp DeFi hiện có dễ dàng tích hợp các giải pháp của Orbs mà không cần thay đổi kiến trúc.

### TON (The Open Network)

TON là blockchain được phát triển bởi anh em nhà Durov (Telegram), hướng đến quy mô hàng tỷ người dùng với triết lý mobile-first. Orbs hỗ trợ TON mainnet và smart contract viết bằng FunC, được thiết kế để bổ trợ cho kiến trúc bất đồng bộ (*asynchronous*) đặc thù của TON. Đây là bước đi chiến lược giúp Orbs tiếp cận hệ sinh thái TON đang phát triển nhanh chóng.

## Bộ công cụ phát triển: Orbs Lambda và Orbs VM

Orbs cung cấp hai môi trường thực thi cho developer, tương tự như mô hình serverless và container của điện toán đám mây truyền thống — nhưng hoàn toàn phi tập trung.

### Orbs Lambda — Serverless phi tập trung

Orbs Lambda là một nền tảng cloud function phi tập trung, tương tự như AWS Lambda. Developer có thể viết các hàm xử lý bằng JavaScript hoặc TypeScript — những ngôn ngữ phổ biến mà không cần học thêm ngôn ngữ smart contract mới — sau đó triển khai lên mạng lưới Orbs. Các hàm này được thực thi tự động bởi các Guardian dựa trên các trigger được thiết lập sẵn:

- **Định thời gian** (giống cron job)
- **Sự kiện on-chain** từ nhiều blockchain (log, thay đổi trạng thái)
- **HTTP requests**

Orbs Lambda đặc biệt phù hợp cho các dApp muốn loại bỏ backend tập trung mà không cần xây dựng hạ tầng phức tạp. Theo tài liệu dự án, việc viết và triển khai một hàm Lambda có thể hoàn thành chỉ trong 30 phút.

### Orbs VM — Container phi tập trung

Đối với các use-case phức tạp hơn, Orbs VM cung cấp môi trường máy ảo phi tập trung dựa trên Docker — tương tự như AWS EC2. Developer có thể sử dụng bất kỳ ngôn ngữ lập trình nào (Go, C++, Rust, JavaScript, Python, Java...) để xây dựng các dịch vụ *always-on*, không bị "ngủ đông" như serverless.

Orbs VM cho phép các dịch vụ liên tục theo dõi nhiều blockchain cùng lúc bằng cách đọc và phân tích block mới — lý tưởng cho các ứng dụng như oracle giá, bot giao dịch, hoặc hệ thống thanh lý vị thế.

## Hệ sinh thái giao thức giao dịch "Powered by Orbs"

Đây là mảng ứng dụng nổi bật nhất của Orbs, bao gồm một bộ các giao thức giao dịch nâng cao giúp các DEX và nền tảng DeFi đạt được trải nghiệm ngang tầm các sàn tập trung (CeFi).

### 1. Liquidity Hub — Tổng hợp thanh khoản cho DEX

Vấn đề phân mảnh thanh khoản là một trong những thách thức lớn nhất của DeFi. Thanh khoản bị rải rác qua nhiều chain, nhiều AMM và nhiều pool khác nhau, dẫn đến trượt giá cao và tỷ giá kém hấp dẫn cho người dùng.

Liquidity Hub giải quyết vấn đề này bằng cách hoạt động như một lớp tối ưu hóa phi tập trung cho DEX-AMM, cho phép DEX tiếp cận các nguồn thanh khoản bên ngoài thông qua hai cơ chế:

- **On-chain solver auction**: Các solver bên thứ ba cạnh tranh để thực hiện giao dịch với mức giá tốt nhất, sử dụng thanh khoản on-chain từ các AMM pool hoặc inventory riêng.
- **Decentralized order API**: Cho phép các nhà tạo lập thị trường chuyên nghiệp gửi bid để cạnh tranh thực hiện giao dịch.

Quan trọng nhất, Liquidity Hub hoạt động theo cơ chế *fallback*: nếu không thể thực hiện giao dịch ở mức giá tốt hơn AMM, giao dịch sẽ tự động quay về AMM như bình thường. Điều này đảm bảo người dùng không bao giờ nhận được mức giá *tệ hơn* so với swap thông thường.

### 2. Perpetual Hub — Công cụ cho perpetual futures

Thị trường perpetual futures (hợp đồng tương lai vĩnh cửu) trên các sàn tập trung có khối lượng giao dịch lớn hơn spot gấp nhiều lần, nhưng mảng on-chain perpetuals vẫn còn chiếm tỷ trọng nhỏ trong DeFi. Perpetual Hub là bộ công cụ toàn diện của Orbs nhằm thúc đẩy sự phát triển của perpetual futures trên blockchain, bao gồm ba thành phần:

- **Hedger**: Công nghệ cho phép market maker hoạt động như đối tác trong các giao dịch perpetual, có thể tận dụng thanh khoản từ các sàn tập trung như Binance để cung cấp mức giá cạnh tranh trên on-chain.
- **Liquidator**: Cơ chế thanh lý vị thế phi tập trung. Khi tài sản thế chấp của người dùng giảm xuống dưới ngưỡng duy trì, các bên thứ ba (liquidator) sẽ được khuyến khích thanh lý vị thế và nhận phí.
- **Price Oracle**: Dịch vụ oracle giá phi tập trung, cung cấp dữ liệu cho việc tính toán lãi/lỗ chưa thực hiện (uPnL) và xác định ngưỡng thanh lý.

Perpetual Hub được phát triển với sự hợp tác của các dự án như SYMMIO và IntentX, những đơn vị đang tiên phong trong kiến trúc intent-based cho perpetual futures.

### 3. dTWAP — TWAP/DCA phi tập trung

TWAP (Time-Weighted Average Price) hay DCA (Dollar Cost Averaging) là chiến lược giao dịch thuật toán phổ biến trong CeFi, giúp chia nhỏ lệnh lớn thành nhiều lệnh nhỏ và thực hiện theo khoảng thời gian cố định để giảm tác động giá. Tuy nhiên, việc triển khai TWAP trên smart contract EVM là bất khả thi do giới hạn của môi trường sandbox.

dTWAP giải quyết bài toán này bằng kiến trúc hai tác nhân:

- **Maker**: Người tạo lệnh, thiết lập các tham số như thời lượng, kích thước giao dịch, khoảng cách giữa các lần thực thi.
- **Taker**: Các bên tham gia độc lập (bao gồm chính các Guardian của Orbs) cạnh tranh để tìm đường đi tối ưu cho từng phần của lệnh và gửi bid với mức phí thấp nhất.

dTWAP đã được tích hợp vào các DEX lớn như SushiSwap, QuickSwap (DEX lớn nhất trên Polygon) và SpookySwap (lớn nhất trên Fantom), với khối lượng giao dịch hàng triệu USD.

### 4. dLIMIT — Lệnh giới hạn phi tập trung

dLIMIT là phiên bản đặc biệt của dTWAP, trong đó tổng kích thước lệnh bằng đúng kích thước của một giao dịch đơn lẻ — tức là một lệnh limit order thông thường. Điểm khác biệt là dLIMIT đảm bảo lệnh được thực thi ở mức giá tối ưu với mức phí hợp lý, khắc phục các lỗ hổng phổ biến của những triển khai limit order thiếu hoàn thiện trong DeFi.

### 5. dSLTP — Stop-loss/Take-profit phi tập trung

dSLTP là giải pháp stop order phi tập trung đầu tiên dành cho DEX, cho phép người dùng thiết lập lệnh stop-loss (cắt lỗ) và take-profit (chốt lời) — những công cụ quản lý rủi ro thiết yếu vốn chỉ có trên các sàn tập trung. Người dùng có thể tùy chỉnh:

- **Trigger price**: Mức giá kích hoạt lệnh
- **Limit price**: Mức giá sàn (đối với limit order) để bảo vệ khỏi trượt giá quá sâu
- **Thời gian hiệu lực** của lệnh

Toàn bộ quá trình được vận hành bởi mạng lưới Guardian của Orbs, đảm bảo lệnh được theo dõi và thực thi 24/7 với độ dự phòng cao.

## Điểm mạnh

- **Kiến trúc L3 thông minh**: Không cạnh tranh với L1/L2 mà bổ trợ — tận dụng bảo mật của Ethereum, mở rộng khả năng cho smart contract hiện có.
- **Mainnet lâu đời**: Hoạt động từ 2019 với hàng chục validator độc lập và hơn 100 triệu USD stake — minh chứng cho độ ổn định và tin cậy.
- **Hệ sinh thái sản phẩm đa dạng**: Từ tổng hợp thanh khoản (Liquidity Hub), phái sinh (Perpetual Hub) đến bộ lệnh giao dịch nâng cao (dTWAP/dLIMIT/dSLTP) — bao phủ gần như mọi nhu cầu của một nền tảng giao dịch chuyên nghiệp.
- **Hỗ trợ cả EVM và TON**: Vị thế độc đáo khi là một trong số ít giao thức L3 phục vụ cả hai hệ sinh thái lớn.
- **Developer-friendly**: Lambda (JavaScript/TypeScript, triển khai 30 phút) và VM (Docker, mọi ngôn ngữ) giúp giảm rào cản tiếp cận.

## Thách thức

- **Cạnh tranh gay gắt**: Mảng L3 và infrastructure cho DeFi đang có nhiều đối thủ, từ Chainlink (với oracle và CCIP), các giải pháp intent-based khác, đến chính các L2 đang dần tích hợp thêm tính năng tương tự.
- **Độ phụ thuộc vào Ethereum**: Việc PoS chạy trên Ethereum là điểm mạnh về bảo mật, nhưng cũng là điểm yếu nếu Ethereum gặp sự cố hoặc phí gas tăng đột biến.
- **Adoption còn khiêm tốn**: Mặc dù đã tích hợp với một số DEX lớn như QuickSwap và SpookySwap, tổng khối lượng giao dịch qua các giao thức của Orbs vẫn chưa thực sự bùng nổ so với tiềm năng.
- **Token ORBS**: Mô hình tokenomics và vai trò cụ thể của token ORBS trong hệ sinh thái cần được làm rõ hơn để đánh giá toàn diện.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án Orbs Network — một giao thức Layer 3 với tham vọng mang trải nghiệm giao dịch cấp độ CeFi lên các nền tảng DeFi. Với kiến trúc phi tập trung được bảo vệ bởi chính Ethereum, mạng lưới validator đã vận hành ổn định từ năm 2019, cùng bộ giao thức giao dịch toàn diện, Orbs đang định vị mình như một lớp hạ tầng không thể thiếu cho thế hệ DEX tiếp theo. Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.

---

## 🔍 Kiểm chứng thông tin (NỘI BỘ)

| Mục | Trạng thái | Ghi chú |
|-----|-----------|--------|
| Mainnet từ 2019, $100M+ stake | ✅ Xác nhận từ docs | Nguồn: docs.orbs.network/v3 |
| PoS chạy trên Ethereum/Polygon | ✅ Xác nhận từ docs | Whitepaper có đề cập |
| QuickSwap, SpookySwap, SushiSwap tích hợp dTWAP | ✅ Xác nhận từ docs | Cần kiểm chứng thêm on-chain volume |
| Hợp tác SYMMIO, IntentX (Perpetual Hub) | ⚠️ Từ docs dự án | Cần xác nhận từ phía đối tác |
| Đội ngũ phát triển | ❌ Chưa có | Docs không đề cập chi tiết team |
| Nhà đầu tư / Gọi vốn | ❌ Chưa có | Cần Julius bổ sung |
| Tokenomics token ORBS | ❌ Chưa đề cập | Cần Julius bổ sung nếu muốn đào sâu |
| Số lượng validator hiện tại | ⚠️ Docs ghi "dozens" | Cần tra cứu số liệu cụ thể trên explorer |
