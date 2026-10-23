# Content validation trước build

## Quy trình

1. Viết xong và đọc lại đúng tập bài được yêu cầu. Kiểm tra khẳng định với nguồn; validator không kiểm chứng sự thật.
2. Chạy script đóng gói từ thư mục blog hoặc worktree đang chứa bài:

```bash
python3 /home/julius/julius-workspace/.agent/skills/personal-blog-writer/scripts/validate-content.py src/content/writing/<slug>.md [các file khác]
```

Dùng trực tiếp qua terminal hoặc gọi terminal từ execute_code. Không chép hoặc dựng lại validator trong một đoạn Python ad-hoc: bản sao dễ lệch quy tắc, mức cảnh báo và cách đếm từ so với script được duy trì.

3. Sửa các lỗi FAIL, rồi chạy lại trên đúng tập bài. Đọc cảnh báo thủ công; giữ dấu phẩy trước "và" nếu nó ngăn cách hai mệnh đề, chỉ bỏ khi thực sự thừa trong chuỗi liệt kê.
4. Chỉ chạy `npm run build` sau khi validator PASS. Tiếp tục kiểm tra frontmatter và đối chiếu nguồn bằng mắt; PASS không thay thế các bước này.

Script cũng chạy các kiểm tra SEO trong `references/seo-checklist.md`: độ dài tiêu đề và mô tả, H1 trong thân bài, số heading, `sources` trống, số link nội bộ và link hỏng, bài nghi trùng tin. Các dòng `related:` là gợi ý bài để link, không phải lỗi. Với bản sao lưu nằm ngoài `src/content/writing`, thêm `--no-seo`.

## Checklist đọc thủ công

- Không dùng em-dash, en-dash, dấu ngoặc kép cong, ký tự CJK hoặc zero-width trong văn xuôi.
- Tránh dùng dấu chấm trong các từ viết tắt tiếng Anh (như U.S., e.g., i.e.) vì tokenizer tách câu của validator sẽ coi dấu chấm là kết thúc câu, làm cụm từ phía sau bị nhận nhầm thành câu cụt (< 5 từ). Dùng dạng không dấu chấm (như US) hoặc từ tiếng Việt tương đương.
- Không có khoảng trắng đôi ngoài thụt dòng Markdown; có khoảng trắng sau dấu câu. Không sửa URL hoặc số thập phân theo quy tắc văn xuôi.
- Body ít nhất 350 từ, không tính frontmatter; mở rộng bằng bối cảnh có nguồn và phân tích có nhãn, không nhồi chữ.
- Giữ tiếng Anh ở mức thấp. Tên riêng và thuật ngữ bắt buộc như token, LLM, API, AI agent, blockchain, stablecoin, DeFi có thể giữ; ưu tiên bộ nhớ đệm, triển khai, mạng chính, mạng thử nghiệm và hợp đồng thông minh khi phù hợp.
- Tránh câu cụt và lạm dụng cấu trúc "không chỉ... mà còn..." hoặc các khẩu hiệu AI.
- Kiểm tra tên, số liệu, ngày, mức độ chắc chắn và attribution ngay cạnh khẳng định. Số liệu tự công bố không phải kiểm chứng độc lập.

## Báo cáo và kiểm tra metadata

Lấy số từ body từ kết quả script cho bảng báo cáo; dùng cùng một cách đếm cho cả batch. Parse frontmatter bằng parser YAML thực sự. Vì blog là dự án Node.js có sẵn `js-yaml` trong `node_modules`, ưu tiên chạy script one-liner qua Node:
`node -e 'const yaml = require("js-yaml"); const fm = yaml.load(raw.split("---")[1]); ...'`
thay vì gọi Python (môi trường ngoài có thể thiếu thư viện `pyyaml` dẫn đến `ModuleNotFoundError`). Không dùng tìm chuỗi `draft: true` để thay thế kiểm tra giá trị boolean.

Với draft-only, xác nhận `draft === true`, không có khóa `scheduledAt` và slug không tồn tại dưới `dist/articles/`. Sau push, parse lại file đọc từ `origin/main` và so sánh toàn bộ nội dung với bản local đã kiểm tra. Đối chiếu tập slug với yêu cầu, không chỉ đếm số file.
