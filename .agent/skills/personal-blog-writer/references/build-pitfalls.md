# Build Pitfalls — blog-index.md and blog-index.md

## blog-index.md causes `npm run build` to fail

**Observed:** 2026-09-16

A cron job (daily 09:15 ICT) generates `src/content/writing/blog-index.md` with
metadata and excerpts of all blog articles. This file does NOT have valid Astro
frontmatter — it uses a different format. When present during `npm run build`,
Astro's content layer rejects it:

```
[InvalidContentEntryDataError] writing → blog-index data does not match collection schema.
  title**: **title: Required
  description**: **description: Required
  publishedAt**: **publishedAt: Expected type "date", received "object"
```

### Fix (tested 2026-09-16)

Before build:
```bash
mv src/content/writing/blog-index.md blog-index.md
```

After build:
```bash
mv blog-index.md src/content/writing/blog-index.md
```

The file is in `.gitignore` so the move doesn't affect git state. The file needs
to be back in `src/content/writing/` for the cron job to update it next cycle.

### Why this happens

The blog-index.md is a utility file for CMS/reference purposes, not an Astro
content entry. The cron job writes it to `src/content/writing/` because that's
where it needs to be for the CMS to read it, but Astro's glob content loader
picks it up during build and tries to validate it as a content entry.

### Pattern

This is the same pattern as any non-content `.md` file that lands in the content
directory. If a future cron job or process writes other utility `.md` files into
`src/content/writing/`, they'll hit the same issue. The move-out/build/move-back
pattern is the general fix.

## blog-index.md: reference before writing

Separately, the blog-index.md is useful as a reference BEFORE writing new
articles — it shows what's been published and helps maintain style consistency.
Read it before starting a new batch.

## npm run build timeout do bước tạo ảnh OG (380+ bài viết)

**Hiện tượng:** Lệnh `npm run build` trong thư mục `personal-blog` bị ngắt với mã lỗi exit 124 (timeout) khi dùng timeout mặc định (120s hoặc 180s). Astro dừng lại ở giữa giai đoạn `generating static routes` khi đang render các tệp ảnh Open Graph (`/og/*.png` và `/en/og/*.png`).

**Cơ chế:** Blog hiện có hơn 380 trang tĩnh. Bước build tĩnh tạo ảnh OG động bằng thư viện Satori/resvg cho từng bài viết tiếng Việt và tiếng Anh, tiêu tốn khoảng 2 phút 30 giây đến 2 phút 50 giây CPU. Nếu terminal runner đặt timeout ≤ 180s, tiến trình sẽ bị giết và gây hiểu lầm là build bị treo hoặc vòng lặp vô tận.

**Khắc phục:**
Luôn truyền cờ `timeout: 300` hoặc `360` (giây) cho tool `terminal` khi gọi `npm run build`:
```bash
cd ai-labs/projects/personal-blog && npm run build
```
Đảm bảo lệnh chạy trọn vẹn ~165s cho tới khi xuất hiện `[build] Complete!`.

