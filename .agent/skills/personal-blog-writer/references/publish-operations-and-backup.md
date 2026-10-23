# Vận hành publish & backup — 2026-08-29

## Meta line KHÔNG chứa thông tin vận hành

Julius phát hiện bản sao lưu có dòng Meta chứa workflow info và yêu cầu sửa:
> "Tại sao lại có dòng 'Bài đang ở trạng thái draft trên blog, hẹn tự động publish lúc 16:00 hôm nay.'"

Quy tắc: dòng `Meta:` trong `working/Blog/Content/<slug>.md` CHỈ tóm tắt nội dung
bài. Không bao giờ ghi trạng thái draft, lịch hẹn publish, hay bất kỳ thông tin
vận hành nào. Đó là chuyện của frontmatter `scheduledAt`/`draft`, không thuộc
nội dung bài.

Mẫu đúng (từ bài Thomson Reuters):
```
Meta: Công ty dữ liệu pháp lý và thuế xây LLM độc quyền từ nền open-source, tuyên bố ngang tầm frontier model với chi phí bằng một phần nhỏ. Bài viết lưu ý các con số hiệu năng do chính hãng công bố.
```

## Cloudflare Pages build delay — slug mới trả 404 ngay sau push

Sau khi `git push origin main`, Cloudflare Pages mất **~1-2 phút** để build +
deploy bản mới. Trong khoảng đó:

- Slug mới trả **HTTP 404** — KHÔNG phải bài chưa đăng, chỉ là deploy chưa xong.
- Slug cũ vẫn trả **HTTP 200** (serve bản build cũ) tới khi deploy mới hoàn tất.

Quy trình kiểm tra đúng:
1. `npm run build` local → xác nhận `dist/articles/<slug>/` tồn tại (đây là bằng chứng frontmatter hợp lệ + bài được tạo).
2. `git push` → **sleep 30-60s** → thử URL edgenotes.net lần nữa.
3. Chỉ kết luận "chưa lên" sau khi đợi ≥ 1-2 phút và vẫn 404.

Verification command:
```bash
curl -sL "https://edgenotes.net/articles/<slug>/" -w "HTTP %{http_code}\n"
# hoặc kiểm tra sitemap
curl -sL "https://edgenotes.net/sitemap-0.xml" | grep -o "<slug>"
```

## Độ dài news: baseline 400-500 từ tối thiểu

Khi Julius nói "hơi ngắn quá rồi. ít nhất phải 400 - 500 từ" — đây là ngưỡng
tối thiểu cho bài news, không phải mục tiêu. Xem `news-post-depth.md` cho yêu
cầu "chi tiết hơn" (600-900 từ + research nguồn gốc). Nếu bài chỉ ~250-300 từ
dạng tóm tắt, mở rộng ngay ở lượt viết đầu tiên: cơ chế hoạt động, bối cảnh
thương vụ, hệ quả cho người dùng, bức tranh ngành, bài học. Bump `readingMinutes`
lên 3-4.
