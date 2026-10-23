# Cross-article consistency & grounding — 2026-09-03

Ba bài học từ batch publish 5 bài news (03/09/2026, từ một news brief):

## 1. Số liệu chéo giữa các bài cùng brief phải nhất quán

Khi nhiều bài viết từ cùng một brief đề cập cùng một sự kiện/chỉ số
(ETF flow, market cap, giá token), kiểm tra số liệu GIỮA các bài trước khi
commit. Nếu hai nguồn báo khác nhau cho cùng một ngày, hoặc ghi rõ attribution
từng nguồn, hoặc nêu chênh lệch.

Ca thực tế: bài 4 (nguồn The Defiant/Farside: spot BTC ETF +8,4M, sơ bộ chưa
đầy đủ) và bài 7 (nguồn Wu Blockchain/SoSoValue: -236M đã chốt) trái ngược cho
cùng phiên 1/9. Sửa bằng cách patch bài 4: thêm "theo số liệu Farside tại thời
điểm viết bài... chưa công bố đầy đủ" + "Dữ liệu SoSoValue công bố sau đó cho
thấy...". Quy tắc: khi số liệu sơ bộ vs chốt khác nhau, luôn kèm attribution +
timing (sơ bộ/chốt), không để hai bài trong cùng repo tự mâu thuẫn.

## 2. Bối cảnh mở rộng phải từ nguồn đã đọc, không từ trí nhớ

Khi nguồn chính quá ngắn và mở rộng bằng "bối cảnh khu vực/ngành", context đó
phải đến từ URL thực sự đã đọc (web_extract/web_search), KHÔNG phải kiến thức
chung. Viết "SEC Thái Lan... bối cảnh Singapore/Nhật/Ấn/FATF" mà chưa đọc nguồn
nào là vi phạm grounding — bị phát hiện và phải viết lại toàn bài.

Nếu không tìm được nguồn bổ sung, đánh dấu đoạn đó là diễn giải (interpretation)
thay vì claim theo kiểu factual, hoặc bỏ hẳn.

## 3. Kiểm tra độ dài body TRƯỚC khi stage, không sau

News baseline ≥ 400-500 từ (xem publish-operations-and-backup.md). Lần này bài
ETF ra 386 từ, dưới sàn 400, phải mở rộng thêm một đoạn phân tích. Đếm từ body
(phần sau `---` thứ hai, không tính frontmatter) bằng vòng lặp shell qua các
slug mới trước khi `git add`, cùng lúc kiểm tra em-dash/en-dash = 0:

```bash
for f in <new slugs>.md; do
  echo "=== $f ==="
  grep -c $'\u2014' "$f" || true   # em-dash count, must be 0
  grep -c $'\u2013' "$f" || true   # en-dash count, must be 0
  awk 'BEGIN{inbody=0} /^---$/{c++; next} c==2 && !/^---$/{inbody=1} inbody{n+=NF} END{print "body words:", n}' "$f"
done
```

Mở rộng ở lượt đầu nếu dưới sàn; không đợi đến lúc verify sau build.
