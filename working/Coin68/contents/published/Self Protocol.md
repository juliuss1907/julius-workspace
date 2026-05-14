---
title: "Self Protocol - Giao thức xác minh danh tính bằng ZK Proof"
source: "https://coin68.com/self-protocol-la-gi/"
published: 2026-03-26
created: 2026-05-04
description: "Self Protocol là giao thức xác minh danh tính phi tập trung, cho phép người dùng chứng minh họ là người thật mà không cần tiết lộ bất kỳ thông tin cá nhân nào."
tags:
  - "DID"
  - "zero-knowledge"
---
**Self Protocol là giao thức xác minh danh tính phi tập trung, sử dụng công nghệ bằng chứng không kiến thức nhằm cho phép người dùng chứng minh họ là người thật mà không cần tiết lộ bất kỳ thông tin cá nhân nào. Hãy cùng Coin68 tìm hiểu về dự án này trong bài viết dưới đây.**

![](https://cdn.coin68.com/images/20260326035705-f3c9319f-ccd3-41cd-b1c6-ed5b3cc23471-17.jpg) Self Protocol là gì? Tìm hiểu về giao thức xác minh danh tính bằng ZK Proof

## Self Protocol là gì?

**Self Protocol** là giao thức xác minh danh tính mã nguồn mở, được xây dựng trên nền tảng [ZK proof](https://coin68.com/zero-knowledge-proof-la-gi/). Người dùng có thể quét hộ chiếu điện tử có chip NFC của mình, tạo ra một bằng chứng kỹ thuật số và chia sẻ bằng chứng đó với ứng dụng bên thứ ba mà không để lộ tên, ngày sinh hay bất kỳ dữ liệu nhạy cảm nào.

![](https://cdn.coin68.com/images/20260326035705-f618acf9-7b44-41b4-9189-9735fa53b263-173.jpg) Self Protocol là gì?

Vấn đề mà Self giải quyết nằm ở sự bùng nổ của [AI agent](https://coin68.com/ai-agent-la-gi/) và bot trên Internet. Khi hơn 50% lưu lượng truy cập trực tuyến đến từ tác nhân tự động, các nền tảng ngày càng khó phân biệt người dùng thật với máy móc. Self cung cấp lớp hạ tầng để trả lời câu hỏi đó, không phải thông qua việc thu thập dữ liệu mà thông qua việc xác minh có mật mã đảm bảo.

**Có thể bạn quan tâm:  
  
**
- [VeryAI là gì? Tìm hiểu về nền tảng xác minh quyền sở hữu AI Agent](https://coin68.com/very-ai-la-gi/)
- [Worldcoin (WLD) là gì? Dự án định danh bằng cách “quét võng mạc” người dùng](https://coin68.com/worldcoin-wld-la-gi/)

## Hệ sinh thái và các trường hợp sử dụng

Self hiện được tích hợp bởi nhiều dự án và tổ chức lớn, phục vụ các nhu cầu khác nhau:  

- **Google Cloud**: Dùng ZK proof của Self để xác minh người dùng thật khi phân phối token thử nghiệm qua Web3 Testnet Faucet, ngăn bot lấy tài nguyên.
- **Aave**: Tích hợp xác minh của Self để cung cấp lãi suất ưu đãi cho người dùng đã xác minh là người thật trên các pool USDT và WETH.
- **Velodrome**: Áp dụng Self để bảo vệ phần thưởng thanh khoản khỏi việc bị khai thác bởi bot hoặc địa chỉ ảo.
- **Uniswap, Morpho, Celo Names, Espresso, Lemonade**: Các giao thức và ứng dụng đã tích hợp Self để tăng tính bảo mật và chống Sybil.

Các trường hợp sử dụng phổ biến nhất bao gồm:  

- **Chống gian lận trong airdrop**: Ngăn địa chỉ ảo và bot nhận token phân phối.
- **Tuân thủ danh sách OFAC/trừng phạt**: Lọc người dùng trong khu vực bị hạn chế mà không thu thập dữ liệu.
- **Xác minh độ tuổi**: Cho phép truy cập tính năng giới hạn độ tuổi mà không cần chia sẻ ngày sinh.
- **Chống sybil trong quản trị**: Đảm bảo mỗi người dùng chỉ có một lá phiếu thật.
- **Danh tính cho AI agent**: Gắn thông tin agent với danh tính chủ sở hữu đã xác minh trong hệ sinh thái agentic.

## Sản phẩm và tính năng chính

### Self Pass

Self Pass là sản phẩm cốt lõi của giao thức, cho phép người dùng xác minh danh tính bằng cách quét chip NFC trên hộ chiếu điện tử hoặc căn cước công dân sinh trắc học. Toàn bộ dữ liệu từ hộ chiếu được xử lý trực tiếp trên thiết bị của người dùng.

Self không lưu trữ tài liệu gốc, không có cơ sở dữ liệu tập trung nào được tạo ra. Kết quả là một bằng chứng ZK có thể được chia sẻ với bên thứ ba để xác nhận các thuộc tính cụ thể như tuổi tác, quốc tịch hoặc trạng thái không nằm trong danh sách trừng phạt OFAC.

### Self Connect

Self Connect là công cụ xác minh nhẹ hơn dành cho các trường hợp không yêu cầu mức độ đảm bảo cao nhất. Người dùng xác minh thông qua số điện thoại di động, phù hợp với các ứng dụng cần quy trình đăng ký nhanh và đơn giản mà vẫn lọc được bot.

### Self Agent ID

Self Agent ID là sản phẩm mới nhất của Self, cho phép mỗi AI agent đăng ký một danh tính on-chain được neo vào một con người thật đã xác minh. Giải pháp này được xây dựng nhằm giải quyết vấn đề là đằng sau agent này là một người thật đã được xác minh, hay chỉ là một agent khác.

Nhờ tích hợp sẵn ZK proof, Self Agent ID cho phép các giao thức DeFi có thể cấp quyền truy cập hoặc phần thưởng ưu đãi cho agent đã được xác minh mà không cần thu thập hay lưu trữ dữ liệu cá nhân của người đó.

## Đội ngũ phát triển

Self Labs là công ty đứng sau Self Protocol, được thành lập vào đầu năm 2024 bởi các cựu thành viên cốt lõi của [Celo](https://coin68.com/celo-la-gi/), bao gồm:  

- **Rene Reinsberg (Co-founder & CEO)**: Cựu chủ tịch của Celo Foundation.
- **Eric Nakagawa (Co-founder)**: Cựu thành viên cốt lõi tại Celo.
- **Marek Olszewski (Co-founder)**: CEO của cLabs, đơn vị phát triển của Celo.

## Nhà đầu tư

![](https://cdn.coin68.com/images/20260326035705-8030a799-92d6-49cb-aa09-01396f8bc903-1.jpg) Các nhà đầu tư của Self Protocol

Self Labs đã huy động tổng cộng 9 triệu USD trong vòng Seed do Greenfield Capital dẫn đầu, cùng với sự tham gia của Startup Capital Ventures x SBI Fund (Softbank), Spearhead VC, Verda Ventures và Fireweed Ventures.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án Self Protocol, Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.