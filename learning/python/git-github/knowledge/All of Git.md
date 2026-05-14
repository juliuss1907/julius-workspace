
---

## 🧠 Mental model — Git là gì?

> Git là hệ thống **lưu lịch sử thay đổi** của code. Mỗi lần commit = 1 snapshot của toàn bộ project tại thời điểm đó.

Hình dung như này:

```
Thời gian →→→

Snapshot 1      Snapshot 2      Snapshot 3
"Add Expense"   "Add Tracker"   "Add CLI"
    ●───────────────●───────────────●
    
Nếu code bị hỏng ở snapshot 3
→ có thể quay lại snapshot 2 bất cứ lúc nào
```

**Không có Git:** Lỡ xóa file, lỡ sửa lung tung → mất hết.
**Có Git:** Mọi thay đổi đều có thể khôi phục.

---

## 🗂️ 3 vùng quan trọng của Git

Đây là điều Julius **cần hiểu nhất** — vì đây là lý do tại sao có nhiều lệnh khác nhau:

```
┌─────────────────┐    git add    ┌──────────────┐    git commit    ┌───────────────┐
│ Working          │ ──────────►  │ Staging Area │ ──────────────► │ Local Repo    │
│ Directory        │              │ (index)      │                  │ (.git folder) │
│ (đang chỉnh sửa) │ ◄──────────  │ (chuẩn bị   │                  │ (lịch sử đã   │
│                  │  git restore │  commit)     │                  │  lưu vĩnh viễn│
└─────────────────┘              └──────────────┘                  └───────────────┘
                                                                            │
                                                                      git push
                                                                            │
                                                                            ▼
                                                                    ┌───────────────┐
                                                                    │   GitHub      │
                                                                    │  (Remote)     │
                                                                    └───────────────┘
```

**Giải thích đơn giản:**
- **Working Directory:** Nơi Julius đang viết code
- **Staging Area:** "Giỏ hàng" — chọn file nào sẽ vào commit tiếp theo
- **Local Repo:** Lịch sử commit đã lưu trên máy Julius
- **GitHub:** Bản sao trên internet

---

## 📋 Các lệnh cần biết — chia theo nhóm

### Nhóm 1 — Kiểm tra trạng thái (dùng nhiều nhất)

```bash
git status
# Xem file nào đang thay đổi, file nào đã add vào staging

git log --oneline
# Xem lịch sử commit ngắn gọn
# VD: a3f2c1 feat: add Expense class
#     b9d4e2 init: project setup

git diff
# Xem chi tiết những gì đã thay đổi nhưng chưa add
```

---

### Nhóm 2 — Workflow hàng ngày

```bash
# Bước 1: Xem có gì thay đổi
git status

# Bước 2: Thêm file vào staging
git add ten_file.py          # add 1 file cụ thể
git add .                    # add TẤT CẢ file thay đổi

# Bước 3: Commit với message rõ ràng
git commit -m "feat: add Tracker class with JSON save"

# Bước 4: Đẩy lên GitHub
git push
```

**Quy ước message commit** (Julius nên dùng ngay từ bây giờ):
```
feat:     thêm tính năng mới
fix:      sửa bug
refactor: cải thiện code, không thêm tính năng
docs:     cập nhật README, comment
chore:    việc lặt vặt (cài thư viện, config...)
```

---

### Nhóm 3 — Branch (nhánh)

```bash
# Tại sao cần branch?
# main = bản ổn định, luôn chạy được
# branch mới = nơi thử nghiệm tính năng mới

git branch                    # xem đang ở branch nào
git checkout -b feature/json  # tạo branch mới + chuyển sang
git checkout main             # quay về main
git merge feature/json        # gộp branch vào main
```

**Mental model branch:**
```
main:    ●────────────────────────────●
          \                          /
feature:   ●──●──●──● (viết code)  ● (merge về main)
```

---

### Nhóm 4 — Kết nối GitHub

```bash
# Lần đầu setup
git remote add origin https://github.com/USERNAME/repo.git
git push -u origin main      # -u = set upstream, chỉ cần làm 1 lần

# Từ lần sau chỉ cần
git push

# Kéo code mới từ GitHub về (khi làm nhiều máy)
git pull
```

---

### Nhóm 5 — Xử lý khi lỡ tay

```bash
# Lỡ add nhầm file vào staging → bỏ ra
git restore --staged ten_file.py

# Lỡ sửa file, muốn phục hồi về lần commit cuối
git restore ten_file.py

# Xem commit trước trông như thế nào (không phá code)
git log --oneline            # lấy mã commit VD: a3f2c1
git show a3f2c1              # xem nội dung commit đó
```

---

## 🔄 Flow thực tế khi làm Expense Tracker

```
Hôm nay Julius làm việc:

1. Mở project, viết code expense.py
   → git status  (xem thay đổi)

2. Xong class Expense
   → git add expense.py
   → git commit -m "feat: add Expense class"

3. Viết tiếp tracker.py
   → git add tracker.py
   → git commit -m "feat: add Tracker with save/load"

4. Cuối buổi push lên GitHub
   → git push

5. Hôm sau muốn thêm tính năng phân tích → tạo branch
   → git checkout -b feature/analytics
   → (viết code)
   → git add . && git commit -m "feat: add Pandas analysis"
   → git checkout main
   → git merge feature/analytics
   → git push
```

---

