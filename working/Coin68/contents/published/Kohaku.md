---
title: "Kohaku - Bản nâng cấp tăng cường quyền riêng tư cho Ethereum"
source: "https://coin68.com/kohaku-la-gi/"
published: 2025-11-19
created: 2026-05-09
description: "Kohaku là bộ công cụ mã nguồn mở giúp tăng cường quyền riêng tư trên mạng lưới Ethereum, vừa được Vitalik Buterin giới thiệu tại Devconnect 2025."
tags:
  - "ethereum"
---
**Kohaku là bộ công cụ mã nguồn mở giúp tăng cường quyền riêng tư trên mạng lưới Ethereum, vừa được Vitalik Buterin giới thiệu tại Devconnect 2025. Với mục tiêu bảo vệ dữ liệu cá nhân, hỗ trợ giao dịch ẩn danh hợp pháp mà vẫn tuân thủ quy định pháp luật, Kohaku định vị mình là bản nâng cấp về privacy lớn nhất từ trước tới nay đối với hệ sinh thái Ethereum. Hãy cùng Coin68 tìm hiểu về bộ công cụ này trong bài viết dưới đây.**

![](https://cdn.coin68.com/images/20251119044106-e7763528-62a7-4f14-9c95-e84376b29c63-173.jpg) Kohaku là gì? Tìm hiểu về bản nâng cấp tăng cường quyền riêng tư cho Ethereum

## Kohaku là gì?

**Kohaku** là bộ công cụ mã nguồn mở giúp tăng cường quyền riêng tư trên mạng lưới [Ethereum](https://coin68.com/ethereum-la-gi/), cho phép người dùng thực hiện các giao dịch ẩn danh hợp pháp, bảo vệ dữ liệu cá nhân trong khi vẫn tuân thủ các quy định pháp lý và hỗ trợ cho các hoạt động kiểm toán khi cần thiết.

![](https://cdn.coin68.com/images/20251119044106-0f6d23d8-98eb-4038-901d-221449950c4a-198.jpg) Kohaku là gì?

Kohaku được Vitalik Buterin giới thiệu tại sự kiện Devconnect 2025 đang được tổ chức tại Argentina, mệnh danh là bản nâng cấp tập trung vào quyền riêng tư (privacy) lớn nhất mà mạng lưới từng đề ra, giúp người dùng tự do giao dịch mà không lo bị giám sát nhưng vẫn tuân thủ pháp luật, thúc đẩy sự phát triển bền vững của mạng lưới Ethereum trong tương lai.

Kohaku bao gồm hai sản phẩm chính:  

- **Kohaku SDK**: Đây là một bộ công cụ phát triển phần mềm được thiết kế với hệ thống plugin module, giúp các nhà phát triển dễ dàng tích hợp và tùy chỉnh các tính năng bảo mật quyền riêng tư vào sản phẩm của mình mà không cần phải xây dựng mới hoàn toàn từ đầu.
- **Kohaku Reference Wallet**: Đây là một ví trình duyệt mở rộng được phát triển từ một bản fork của ví Ambire, được dùng làm bản minh họa và tham chiếu cho SDK. Đây không phải là sản phẩm cuối dành cho người dùng phổ thông mà nhằm trình diễn các khả năng bảo mật và quyền riêng tư của SDK.

**Có thể bạn quan tâm:  
  
**
- [Vitalik Buterin trình làng Kohaku, giải pháp riêng tư cho giao dịch Ethereum](https://coin68.com/vitalik-buterin-trinh-lang-kohaku-giai-phap-rieng-tu-cho-giao-dich-ethereum/)
- [Seismic là gì? Blockchain EVM cho phép xử lý thông tin bí mật ngay trên chuỗi](https://coin68.com/seismic-la-gi/)

## Điểm khác biệt của Kohaku với các giải pháp ẩn danh khác

Kohaku được xem là khuôn mẫu bảo mật dành cho Ethereum, giống như một lớp bảo vệ nền tảng, được tích hợp trực tiếp vào hạ tầng ví và giao dịch, cho phép mỗi cá nhân, tổ chức tự chọn mức bảo mật và sự minh bạch phù hợp nhất với bản thân, hướng tới quyền riêng tư mặc định trên blockchain.

Khác với các giải pháp ẩn danh (privacy) truyền thống như Zcash, Monero, Firo,... Kohaku không chỉ bảo vệ giao dịch on-chain mà còn hướng đến khả năng bảo mật đầu cuối, giảm thiểu rò rỉ thông tin qua việc tương tác với node, mạng lưới, frontend, cũng như các yếu tố khác như khôi phục tài khoản và chữ ký phần cứng.

Hệ thống này còn tích hợp các công nghệ tiên tiến như Railgun và Privacy Pools, sử dụng cơ chế “proof of innocence” để chống rửa tiền và che giấu tài sản theo cách tuân thủ pháp lý. Từ đó, chuyển từ mọi thứ đều công khai và có thể liên kết, giám sát sang chỉ chia sẻ đúng thông tin cần thiết để hành động, còn lại được giữ kín.

## Cơ chế hoạt động của Kohaku

![](https://cdn.coin68.com/images/20251119064406-5a4f56da-e368-4392-b6cb-167ee91017ec-136.jpg) Mô tả cơ chế hoạt động của Kohaku

Khi có giao dịch chuyển tiền diễn ra, Kohaku sẽ tạo một cặp "khóa ẩn" (stealth keypair) liên kết với ví chính của người nhận.

Sau đó, người gửi sẽ dùng cặp khóa ẩn này để tạo ra một địa chỉ tạm thời dùng một lần (one-time stealth address) và thực hiển gửi tiền vào nó. Địa chỉ này không liên quan trực tiếp đến ví chính nên không thể bị theo dõi hoặc truy vết trên blockchain.

Sau khi giao dịch thành công, tiền sẽ được chuyển vào ví chính của người nhận, còn địa chỉ tạm thời sẽ bị xoá bỏ. Điều này đảm bảo tính ẩn danh tuyệt đối cho giao dịch khi nó không để lại mối liên hệ rõ ràng.

Cơ chế này được hỗ trợ bởi các phương pháp mật mã tiên tiến như zero-knowledge proofs, giúp bảo vệ thông tin giao dịch mà vẫn cho phép xác minh hợp lệ trên chuỗi.

## Lộ trình tương lai của Kohaku

Lộ trình phát triển của Kohaku tập trung vào xây dựng một môi trường bảo mật, riêng tư tích hợp sâu rộng cho người dùng Ethereum với các mục tiêu dài hạn sau:  

- **Native Ethereum Browser**: Tạo ra trình duyệt trên Ethereum tích hợp sẵn bảo mật ở mức độ gần với hệ điều hành, tăng cường an toàn cho giao diện dApp (ví dụ dApp lưu trên IPFS) và hỗ trợ tích hợp ngang hàng sâu hơn.
- **Local AI for Transaction Scoring**: Phát triển các mô hình AI trên thiết bị để đánh giá rủi ro giao dịch ngay trên máy người dùng, tránh rò rỉ dữ liệu riêng tư ra bên ngoài cho các dịch vụ phân tích.
- **Privacy-Preserving Account Abstraction**: Nghiên cứu và phát triển công nghệ cho phép một ví duy nhất có thể kiểm soát đồng thời cả quỹ công khai và quỹ riêng tư, với cải tiến các prover như client-side ZK-EVM hoặc ZK-RISC-V, hướng đến việc tích hợp trừu tượng tài khoản native trên Ethereum vào năm 2026.
- **Private Data Recovery**: Tìm hiểu các phương án phục hồi an toàn cho dữ liệu riêng tư như bí mật ví hay các token ZK POAPs (Proof of Attendance), nhằm vừa duy trì bảo mật vừa hỗ trợ người dùng lấy lại quyền kiểm soát tài sản khi cần thiết.

## Tổng kết

Trên đây là bài viết tổng hợp về Kohaku, bản nâng cấp mang tính chiến lược của Ethereum nhằm nâng cao quyền riêng tư của người dùng. Coin68 mong rằng bạn đọc sẽ có được cái nhìn tổng quan về xu hướng mới này.

> **Lưu ý**: Thông tin trong bài viết chỉ mang mục đích cung cấp thông tin, không được xem là lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định đầu tư nào của các bạn.