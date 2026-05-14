---
title: "Nava - Hạ tầng xác minh giao dịch dành cho AI agent"
source: "https://coin68.com/nava-la-gi/"
published: 2026-04-22
created: 2026-05-04
description: "Nava AI là nền tảng được thiết kế để giám sát và kiểm tra giao dịch on-chain do các AI agent thực hiện, nhằm ngăn chặn sai sót trước khi thực hiện giao dịch."
tags:
  - "ai"
---
**Nava là nền tảng hạ tầng xác minh được thiết kế để giám sát và kiểm tra giao dịch on-chain do các AI agent thực hiện nhằm ngăn chặn sai sót trước khi tiền thực sự bị di chuyển, trở thành lớp tin cậy cho nền kinh tế tự động hóa bằng AI. Hãy cùng Coin68 tìm hiểu về dự án này trong bài viết dưới đây.**

![](https://cdn.coin68.com/images/20260422024305-7994b1ff-377f-495f-bae4-aac6c0c8231b-176.jpg) Nava là gì? Tìm hiểu về hạ tầng xác minh giao dịch dành cho AI agent

## Nava AI là gì?

**Nava** là một lớp phần mềm trung gian giúp kiểm tra và xác minh việc thực thi giao dịch trên blockchain khi một AI agent muốn thực hiện một giao dịch như swap token, mở vị thế phái sinh, lending trên DeFi,.... trước khi bất kỳ khoản tiền nào thực sự bị di chuyển.

![](https://cdn.coin68.com/images/20260422024305-abe51830-d465-43dc-a240-80a3e0d115df-17.jpg) Nava là gì?

Nava giải quyết một vấn đề xuất phát từ thực tế, đó là các AI agent được sử dụng để giao dịch trên blockchain ngày càng nhiều nhưng lại không có cơ chế nào để đảm bảo rằng những gì agent được yêu cầu làm khớp với những gì chúng thực sự thực thi. Một agent có thể hiểu sai lệnh, đặt sai thông số (ví dụ đòn bẩy 20x thay vì 2x), tương tác với hợp đồng thông minh không an toàn hoặc bị khai thác bởi các cuộc tấn công từ kẻ xấu.

**Có thể bạn quan tâm:  
  
**
- [Spektr là gì? Tìm hiểu về nền tảng tuân thủ pháp lý cho doanh nghiệp bằng AI Agent](https://coin68.com/spektr-la-gi/)
- [Axis Robotics là gì? Tìm hiểu về hạ tầng phi tập trung dành cho AI vật lý](https://coin68.com/axis-robotics-la-gi/)

## Điểm nổi bật của Nava AI

### Xác minh giao dịch trước khi thực thi

Khác với các công cụ bảo mật truyền thống chỉ phát hiện vấn đề sau khi thiệt hại đã xảy ra, Nava chặn giao dịch trước khi chúng được gửi lên blockchain. Mỗi giao dịch do AI agent đề xuất đều phải đi qua một pipeline xác minh gồm nhiều lớp kiểm tra: đối chiếu ý định người dùng, xác thực token, kiểm tra trượt giá, sàng lọc danh sách trừng phạt và phát hiện hành vi xấu. Chỉ khi tất cả các bước kiểm tra đều đạt, giao dịch mới được phép thực thi.

### Không giới hạn khả năng sáng tạo của AI agent

Nava không hạn chế cách AI agent suy nghĩ hay lập chiến lược. Agent vẫn có thể hoạt động tự do với bất kỳ framework nào. Thay vì ràng buộc agent, Nava sử dụng một hệ thống AI riêng biệt gọi là Arbiter để đánh giá độc lập từng giao dịch, từ đó giúp bảo toàn lợi thế sáng tạo của AI trong khi vẫn đặt ra ranh giới an toàn rõ ràng.

### Ký quỹ thông minh

Nava cung cấp cơ chế escrow (ký quỹ) thông qua hợp đồng thông minh: tiền của người dùng được giữ lại cho đến khi cả AI agent và Arbiter cùng ký xác nhận. Nếu Arbiter từ chối giao dịch, không có khoản tiền nào bị di chuyển. Cơ chế này hoạt động theo mô hình phi lưu ký (non-custodial), tức Nava không nắm giữ bất kỳ tài sản nào của người dùng.

### Kiểm toán và minh bạch hoàn toàn

Mọi quyết định xác minh đều được ghi lại on-chain kèm theo lịch sử lý giải chi tiết về lý do phê duyệt hoặc từ chối giao dịch, bao gồm cả bước kiểm tra nào thất bại và tại sao. Điều này phục vụ cho mục đích tuân thủ pháp lý, giải quyết tranh chấp và chứng minh rằng agent đã hành động đúng.

### Hiệu ứng mạng lưới

Càng nhiều AI agent sử dụng Nava, dữ liệu giao dịch càng lớn, giúp nâng cao độ chính xác của hệ thống xác minh. Các mẫu lỗi được phát hiện bởi một agent sẽ tự động bảo vệ tất cả các agent khác trong mạng lưới.

## Sản phẩm chính của Nava AI

### Nava SDK

Đây là bộ công cụ phát triển phần mềm cho phép các nhà phát triển tích hợp khả năng xác minh của Nava vào AI agent của mình. SDK hỗ trợ TypeScript, Python và REST API, đồng thời hoạt động như một MCP Server (Model Context Protocol). Nhà phát triển chỉ cần gửi giao dịch đề xuất kèm ý định đến Nava, và nhận lại kết quả pass/fail cùng lý giải.

### Execution Escrow SDK

Đây là sản phẩm dành cho các tổ chức và các luồng giao dịch giá trị cao. Agent đề xuất giao dịch, escrow giữ tiền, Arbiter quyết định có cho phép thực thi hay không. Toàn bộ quy trình diễn ra non-custodial, người dùng vẫn giữ quyền kiểm soát private key và ví của mình.

### Nava Arbiter

Là một hybrid verification engine sử dụng các suy luận dựa trên mô hình ngôn ngữ lớn để đánh giá giao dịch dựa trên các tiêu chí như ý định người dùng, khả năng tuân thủ, an toàn giao thức và dấu hiệu tấn công.

### Nava Chain

Là blockchain chuyên dụng cho việc lưu trữ kết quả xác minh giao dịch đồng thời đóng vai trò như lớp thanh toán và phối hợp cho toàn bộ hệ thống.

### Nava Agents

Nava đang phát triển ba AI agent mã nguồn mở dự kiến ra mắt trên testnet:  

- **Polymarket Agent**: Giao dịch trên thị trường dự đoán, xác minh logic kết quả và ngăn đặt cược trùng lặp.
- **Hyperliquid Agent**: Giao dịch phái sinh vĩnh viễn (perp), kiểm soát giới hạn vị thế và yêu cầu ký quỹ.
- **Uniswap Agent**: Swap trên DEX, kiểm tra trượt giá, lỗi thập phân và phê duyệt token.

## Đội ngũ phát triển

![](https://cdn.coin68.com/images/20260422024305-84a2029a-affb-4317-8cbc-27092688f892-101.jpg) Đội ngũ phát triển của Nava

Đội ngũ kỹ sư của Nava đến từ các dự án lớn trong ngành, bao gồm:  

- **Vyas Krishnan - Co-founder & CEO**: Từng là Product Lead tại EigenLayer, một trong những giao thức hạ tầng quan trọng nhất của Ethereum.
- **Brianna Montgomery - Co-founder & COO**: Từng làm việc tại EigenLayer, Fei Protocol và Consensys.
- **Ding Zhao - Research Lead**: Phó Giáo sư Kỹ thuật Cơ khí tại Đại học Carnegie Mellon (CMU), đứng đầu phòng thí nghiệm Safe AI Laboratory, một cơ sở nghiên cứu hàng đầu thế giới về học tăng cường an toàn, hệ thống tự trị và xác minh AI.

## Nhà đầu tư và đối tác

![](https://cdn.coin68.com/images/20260422024305-0211ca4d-2618-4d21-91ab-5fdbb5d066d4-94.jpg) Các nhà đầu tư của Nava

Nava đã huy động 8,3 triệu USD tại vòng Seed vào tháng 04/2026, do Polychain và Archetype đồng dẫn đầu, các quỹ khác tham gia bao gồm Hack VC, FalconX, Seed Club Ventures cùng một số nhà đầu tư thiên thần khác.

## Tokenomics

Tại thời điểm viết bài, Nava chưa công bố thông tin về việc phát hành token. Coin68 sẽ cập nhật khi có thêm thông tin.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án Nava, Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.