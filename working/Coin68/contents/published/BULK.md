---
title: "BULK - Sàn Perp DEX hiệu suất cao trên Solana"
source: "https://coin68.com/bulk-la-gi/"
published: 2026-03-18
created: 2026-05-04
description: "BULK là sàn Perp DEX trên Solana với kiến trúc thực thi hoàn toàn mới, rút ngắn khoảng cách hiệu năng giữa sàn giao dịch phi tập trung và sàn tập trung."
tags:
  - "perp-dex"
  - "solana"
---
**BULK là một sàn giao dịch hợp đồng vĩnh cửu được xây dựng trên Solana với kiến trúc thực thi hoàn toàn mới, nhắm đến mục tiêu rút ngắn khoảng cách hiệu năng giữa sàn giao dịch phi tập trung và sàn tập trung. Thay vì dùng các giải pháp layer-2 hay cầu nối thông thường, BULK tích hợp trực tiếp vào lớp validator của Solana để đạt độ trễ khớp lệnh dưới 20 mili giây. Hãy cùng Coin68 tìm hiểu về dự án này trong bài viết dưới đây.**

![](https://cdn.coin68.com/images/20260318042928-a163cb2b-65ba-4fcf-b340-f0b638a77302-161.jpg) BULK là gì? Tìm hiểu về sàn Perp DEX hiệu suất cao trên Solana

## BULK là gì?

**BULK** là một nền tảng giao dịch phái sinh phi tập trung ([Perp DEX](https://coin68.com/perp-dex-la-gi/)) được xây dựng trên blockchain [Solana](https://coin68.com/solana-la-gi/). Dự án được thiết kế từ nền tảng với mục tiêu tạo ra một môi trường giao dịch có hiệu suất ngang tầm với các sàn tập trung (CEX), trong khi vẫn đảm bảo tính phi tập trung, khả năng chống kiểm duyệt và người dùng tự giữ tài sản.

![](https://cdn.coin68.com/images/20260318042929-ea85cef9-6bc2-451e-8d66-d510d69fd908-105.jpg) Bulk là gì?

Các perp DEX đã tăng trưởng mạnh trong những năm gần đây, nhưng vẫn tồn tại một khoảng cách lớn về hiệu năng so với sàn tập trung như độ trễ và phí gas cao, tình trạng front-running hay rủi ro về cầu nối cross-chain. BULK giải quyết các vấn đề trên bằng cách xây dựng một lớp thực thi chuyên biệt ngay bên trong hạ tầng validator của Solana, thay vì đặt thêm tầng bên trên.

**Có thể bạn quan tâm:  
  
**
- [Hyperliquid là gì? Tìm hiểu về sàn giao dịch phái sinh phi tập trung dẫn đầu thị trường](https://coin68.com/hyperliquid-la-gi/)
- [Based là gì? Tìm hiểu về Web3 SuperApp trên Hyperliquid](https://coin68.com/based-la-gi/)

## Sản phẩm và tính năng chính

### Bulk T1

Bulk T1 là lớp thực thi chuyên biệt của BULK, được tích hợp trực tiếp vào phần mềm validator của Solana. Toàn bộ logic khớp lệnh, quản lý rủi ro và thanh lý đều được xử lý trong bộ nhớ RAM của từng validator, tách biệt khỏi giới hạn tốc độ của Solana on-chain. Sau khi xử lý, kết quả được gói gọn và ghi định kỳ lên blockchain chính.

Điểm đặc biệt của Bulk T1 là hoàn toàn không dùng sequencer tập trung hay cross-chain bridge, loại bỏ hai nguồn rủi ro phổ biến nhất trong các hệ thống DEX hiện nay.

### BULK Exchange

BULK Exchange là giao diện giao dịch dành cho người dùng cuối, hoạt động theo mô hình sổ lệnh tập trung (CLOB — Central Limit Order Book) tương tự các sàn tập trung lớn. Người dùng không tốn phí mạng lưới khi đặt lệnh, có thể sử dụng đòn bẩy, đặt lệnh chốt lời/cắt lỗ tự động, trong khi toàn bộ tài sản ký quỹ vẫn được lưu giữ trực tiếp bên trong ví Solana của họ, không cần bất kỳ bên trung gian nào.

## Cơ chế hoạt động nổi bật

### Cơ chế đồng thuận phân tán

Không giống các hệ thống dùng một validator dẫn đầu để tạo khối, BULK sử dụng cơ chế đồng thuận phân tán dựa trên chữ ký ngưỡng BLS, một loại chữ ký cho phép kết hợp nhiều chữ ký thành một.

Sau mỗi chu kỳ khớp lệnh, tất cả validator đều tự tính toán kết quả và bỏ phiếu bằng cách ký tên vào kết quả đó. Hệ thống sau đó đếm xem bao nhiêu phần trăm đồng ý với cùng một kết quả:  

- **Trên 80%**: Hệ thống tin tưởng ngay lập tức và xác nhận trong một vòng duy nhất.
- **Từ 60 – 79%**: Hệ thống mở thêm một vòng bỏ phiếu thứ hai để thu thập thêm chữ ký trước khi xác nhận.
- **Dưới 60%**: Quá ít validator đồng thuận, hệ thống sẽ bỏ qua chu kỳ đó và thực hiện một chu kỳ mới để xử lý lại.

### Khớp lệnh theo thứ tự

Toàn bộ lệnh trên BULK được xử lý theo nguyên tắc First In, First Out dựa trên khóa mật mã học. Điều này loại bỏ hoàn toàn khả năng can thiệp thứ tự lệnh, đảm bảo mọi lệnh được xử lý công bằng theo đúng thứ tự thời gian.

## Đội ngũ phát triển

![](https://cdn.coin68.com/images/20260318042929-338f54e8-6a27-4f56-b165-2c53fc779b9a-87.jpg) Đội ngũ phát triển của BULK

Đội ngũ phát triển của BULK gồm:  

- **Kobie McGlashan (Co-founder & CEO)**: Đồng sáng lập SuperteamUK và BEExperience, một công ty tuyển dụng web3 vào năm 2022.
- **Junaid Peer (Co-founder & CTO)**: Thành viên sáng lập Avian Network, từng đóng góp cho ETH-Research từ 2018, MakerDAO và Gitcoin DAO từ 2021.

## Nhà đầu tư

![](https://cdn.coin68.com/images/20260318042929-00baff18-bebd-4c63-ba08-f136d5d8f595-49.jpg) Các nhà đầu tư của BULK

BULK đã huy động tổng cộng 8 triệu USD trong vòng Seed do Robot Ventures, 6th Man Ventures dẫn đầu, cùng với sự tham gia của của nhiều quỹ đầu tư khác như Chapter One, Wintermute Ventures, Mirana Ventures, Big Brain Holdings.

## Tổng kết

Trên đây là toàn bộ thông tin về dự án BULK, Coin68 hy vọng bạn đọc sẽ nắm được những thông tin cơ bản để hiểu rõ hơn về dự án và cách hoạt động. Chúc bạn có thêm nhiều kiến thức hữu ích!

> **Lưu ý:** Thông tin trong bài viết mang tính chất cung cấp kiến thức và tổng hợp thông tin công khai về dự án, không phải lời khuyên đầu tư. Coin68 không chịu trách nhiệm với bất kỳ quyết định tài chính nào của bạn.