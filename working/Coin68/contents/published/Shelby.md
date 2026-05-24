---
title: "Shelby - Hệ thống lưu trữ phi tập trung trên Aptos"
source: "https://coin68.com/shelby-la-gi/"
published: 2025-11-01
created: 2026-05-21
description: "Shelby là hệ thống lưu trữ blob phi tập trung hiệu suất cao trên blockchain Aptos, được phát triển để phục vụ các ứng dụng cần truy xuất lượng dữ liệu lớn."
tags:
  - "store"
  - "Aptos"
---
**Shelby là hệ thống lưu trữ blob phi tập trung hiệu suất cao trên blockchain Aptos, được phát triển để phục vụ các ứng dụng cần truy xuất lượng dữ liệu lớn như phát trực tuyến video, đào tạo AI, phân tích dữ liệu, game, DePIN và nhiều lĩnh vực khác. Hãy cùng Coin68 tìm hiểu trong bài viết dưới đây.**

![](https://cdn.coin68.com/images/20251101033019-1e050267-5298-4928-966b-f10e0be9468c-57.jpg) Shelby là gì? Tìm hiểu về hệ thống lưu trữ blob phi tập trung trên Aptos

## Shelby là gì?

**Shelby** là một hệ thống lưu trữ phi tập trung hiệu suất cao trên blockchain Aptos, được thiết kế cho các khối lượng công việc cần đọc dữ liệu lớn như: phát trực tuyến video, đào tạo và suy luận AI, và phân tích dữ liệu quy mô lớn. Shelby tập trung vào việc cung cấp dung lượng lưu trữ mạnh, băng thông đọc cao với chi phí hợp lý, đồng thời đảm bảo quyền kiểm soát dữ liệu cho người dùng.

![](https://cdn.coin68.com/images/20251101033019-6b80e64e-770e-4a5f-a85e-5710093efc3e-174.jpg) Shelby là gì?

Shelby kết hợp tốc độ của hạ tầng Web2 và tính bảo mật và quyền sở hữu của Web3, tạo nền tảng cho ứng dụng đòi hỏi dữ liệu lớn, tốc cao và tương tác liên tục như stream video, tải tài nguyên game, AI model, truyền dữ liệu cảm biến… ngay trên blockchain.

**Có thể bạn quan tâm:  
  
**
- [Aptos (APT) là gì? Tìm hiểu chi tiết về dự án Aptos](https://coin68.com/aptos-la-gi/)
- [Amnis Finance (AMI) là gì? Tìm hiểu về dự án liquid staking trên Aptos](https://coin68.com/amnis-finance-la-gi/)

## Điểm nổi bật của Shelby

Shelby phù hợp với các ứng dụng Web3 hiện đại nhờ vào các ưu điểm sau:  

- **Lưu trữ trên quy mô lớn**: Shelby cung cấp khả năng lưu trữ blockchain tốc độ cao, thời gian thực cho các ứng dụng Web3 cần truy xuất dữ liệu lớn, liên tục như streaming, game, AI, DePIN.
- **Hỗ trợ đa blockchain**: Ban đầu Shelby khởi chạy trên Aptos, nhưng dự kiến sẽ mở rộng sang nhiều blockchain lớn khác, giúp dự án trở thành lớp hạ tầng lưu trữ linh hoạt cho Web3.
- **Hệ thống hạ tầng mạnh mẽ**: Shelby có tốc độ cao, độ trễ cực thấp, được thiết kế xử lý khối lượng dữ liệu lớn và đảm bảo tính ổn định cho các hoạt động cần truyền, nhận dữ liệu liên tục.
- **Cơ chế thưởng bằng lượt đọc**: Người vận hành node, nhà cung cấp lưu trữ, nhà sáng tạo đều được thưởng khi lưu trữ và cung cấp dữ liệu cho người dùng, thúc đẩy mạng lưới hoạt động hiệu quả.
- **Bảo toàn dữ liệu & khả năng phục hồi**: Hệ thống của Shelby được thiết kế phân tán cùng mã hóa xóa Clay (Clay erasure coding), giúp bảo vệ khỏi nguy cơ mất dữ liệu và có thể được phục hồi nhanh chóng khi gặp sự cố.

## Kiến trúc của Shelby

![](https://cdn.coin68.com/images/20251101033019-7f9459d3-14be-48ba-af35-80d8a884a06e-53.jpg) Cấu trúc của Shelby

Các thành phần chính trong kiến trúc Shelby gồm:

### Aptos Smart Contract

Đóng vai trò xương sống trong hệ thống của Shelby, là một hợp đồng thông minh được triển khai trực tiếp trên blockchain Aptos. Nó không chỉ quản lý trạng thái tổng thể của toàn bộ hệ thống mà còn đảm nhận các nhiệm vụ quan trọng như:  

- Kiểm tra tính chính xác của dữ liệu (auditing) để đảm bảo mọi thông tin được lưu trữ đều đáng tin cậy.
- Xác minh các giao dịch lưu trữ, đảm bảo tính minh bạch và chống giả mạo.
- Điều khiển thanh toán cho việc lưu trữ và truy xuất dữ liệu, tạo ra một mô hình kinh tế bền vững.

### Storage Provider (SP) Servers

Là các máy chủ phân tán chịu trách nhiệm lưu trữ dữ liệu của người dùng. Với mỗi blob dữ liệu mà người dùng tải lên, Shelby sẽ chia nhỏ chúng thành nhiều phần, sau đó chia cho nhiều máy chủ khác nhau để lưu trữ. Điều này giúp nâng cao độ an toàn cao, chống lại rủi ro mất mát dữ liệu do sự cố phần cứng hoặc tấn công, đảm bảo rằng dữ liệu luôn có thể được khôi phục nhanh chóng.

### Shelby RPC Servers

Là cửa sổ giao tiếp giữa người dùng và hệ thống Shelby, các máy chủ RPC này xử lý mọi yêu cầu từ bên ngoài qua internet như:  

- Xử lý yêu cầu ghi và đọc dữ liệu.
- Quản lý thanh toán vi mô (micropayment).
- Xác thực và tổng hợp dữ liệu trước khi phản hồi kết quả cho người dùng.

Ngoài ra, Shelby RPC Servers còn có thể kết nối trực tiếp với Smart Contract để lấy siêu dữ liệu (metadata) và định vị chính xác các Storage Provider chứa dữ liệu cần thiết.

### Private Network

Là một mạng riêng tư tốc độ cao chịu trách nhiệm kết nối các Shelby RPC với Storage Provider, giúp truyền tải dữ liệu giữa các node mà không lộ ra bên ngoài, ngăn chặn rủi ro từ các mối đe dọa bên thứ ba.

## Đội ngũ phát triển

Shelby được phát triển bởi Aptos Labs và [Jump Crypto](https://coin68.com/jump-crypto-la-gi/), quỹ đầu tư mạo hiểm đã từng đầu tư vào với nhiều dự án hàng đầu trong thị trường như Aptos, Sui, Injective hay Celestia.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án Shelby, Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết không được xem là lời khuyên đầu tư, Coin68 không chịu trách nhiệm với bất kỳ quyết định nào của các bạn.