# PostHog Analytics trên blog Astro

Setup nhẹ (không cài package): snippet PostHog chèn trực tiếp trong
`src/layouts/BaseLayout.astro` (phần `<head>`), gate bằng env
`PUBLIC_POSTHOG_KEY`. Không có key → snippet không render, blog chạy y như cũ.

## Env vars (.env.example)
- `PUBLIC_POSTHOG_KEY` — để trống = tắt. Token thật nằm ở `.env.local` (gitignored, KHÔNG commit).
- `PUBLIC_POSTHOG_HOST` — mặc định `https://us.i.posthog.com` (Cloud US).

## Vì sao dùng env-gate
- Build phải pass cả khi không có token (không được phụ thuộc key).
- Dev local không bắn data rác khi chưa có key.
- Pattern tái dùng cho mọi analytics snippet (Plausible/Umami/GA4) vào blog static.

## Verify key trước khi tin nó hoạt động
Snippet render đúng ≠ key hợp lệ. Kiểm tra bằng API (chính là call SDK dùng):

```bash
# 1. /decide — SDK gọi khi load; HTTP 200 = key hợp lệ
curl -s -o /dev/null -w "%{http_code}\n" -X POST "https://us.i.posthog.com/decide/?v=3" \
  -H "Content-Type: application/json" \
  -d '{"api_key":"<key>","distinct_id":"test"}'
# 2. capture event — HTTP 200 = server nhận event thật
curl -s -o /dev/null -w "%{http_code}\n" -X POST "https://us.i.posthog.com/i/v0/e/" \
  -H "Content-Type: application/json" \
  -d '{"token":"<key>","event":"$pageview","properties":{"distinct_id":"verify","$current_url":"https://site/"}}'
```

Cũng verify build 2 chiều: `npm run build` rồi grep `dist/index.html` cho
`posthog.init` — có key thì xuất hiện, không key thì không.

## Lưu ý deploy Cloudflare Pages
- Blog là static site; analytics chạy client-side → ad-block có thể chặn vài request (giống mọi analytics client-side), không có server-side tracking.
- Cloudflare Pages cần set env `PUBLIC_POSTHOG_KEY` trong Dashboard (Project → Settings → Environment variables) — `.env.local` không đi deploy.
- Local test: `npm run dev` → mở page → xem dashboard **Live events**.

## `phc_` key là client-side, công khai theo thiết kế
Nằm trong JS của mọi trang, ai mở DevTools cũng thấy → KHÔNG phải secret (không như API key server-side). Rủi ro duy nhất: người khác tự gửi event giả làm nhiễu data — chấp nhận được cho blog.

## Tính năng đáng dùng cho blog (và không nên)
- Dùng: **Web Analytics** (traffic/source/web vitals), **autocapture** (click/scroll/thời gian đọc), **funnels** (đọc bài → click CTA → subscribe Substack), **surveys** (no-code popup).
- Session replay: chỉ bật sample 1% (free 5k recordings/tháng, traffic công khai cháy nhanh).
- KHÔNG dùng: feature flags / experiments (traffic blog thấp → không đủ statistical power), error tracking / AI observability (blog tĩnh không cần), CDP / data warehouse (overkill).
