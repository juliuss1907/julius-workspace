				File I/O — Đọc & Ghi File trong Python

---

## 🗺️ Bức tranh tổng thể File I/O

```
File I/O gồm 3 phần:
│
├── 1. Text file      → open/read/write
├── 2. JSON file      → json.dump / json.load   ← dùng nhiều nhất trong project
└── 3. Xử lý lỗi     → try/except/finally
```

---

## Phần 1 — Text File cơ bản

### Mở file — `open()`

```python
open(tên_file, mode, encoding)
```

| Mode | Ý nghĩa | File đã tồn tại? | File chưa tồn tại? |
|------|---------|-----------------|-------------------|
| `"r"` | Đọc | ✅ Mở bình thường | ❌ FileNotFoundError |
| `"w"` | Ghi (xóa sạch rồi ghi) | ✅ Xóa hết nội dung cũ | ✅ Tự tạo mới |
| `"a"` | Ghi thêm vào cuối | ✅ Giữ nội dung cũ | ✅ Tự tạo mới |
| `"r+"` | Đọc + Ghi | ✅ Giữ nội dung | ❌ FileNotFoundError |

```python
# ✅ Cách đúng — dùng "with" để tự đóng file
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("Dòng đầu tiên\n")
    f.write("Dòng thứ hai\n")

# File tự đóng sau khi ra khỏi block with
```

> **Tại sao dùng `with`?** 
Nếu không dùng `with`, phải gọi `f.close()` thủ công. Nếu quên → file bị lock, data có thể mất.

### Đọc file

```python
# Đọc toàn bộ
with open("notes.txt", "r", encoding="utf-8") as f:
    noi_dung = f.read()       # → string toàn bộ file
    print(noi_dung)

# Đọc từng dòng
with open("notes.txt", "r", encoding="utf-8") as f:
    for dong in f:
        print(dong.strip())   # strip() bỏ \n ở cuối

# Đọc thành list các dòng
with open("notes.txt", "r", encoding="utf-8") as f:
    cac_dong = f.readlines()  # → ["Dòng đầu tiên\n", "Dòng thứ hai\n"]
```

---

## Phần 2 — JSON File ⭐ Quan trọng nhất

### Tại sao JSON?

```
Text file:  Chỉ lưu được chuỗi thô
JSON file:  Lưu được dict, list, số, boolean → phù hợp để lưu data của app
```

Ví dụ thực tế trong Expense Tracker:
```python
# Dữ liệu trong Python
expenses = [
    {"ten": "Cà phê", "so_tien": 35000, "danh_muc": "Ăn uống"},
    {"ten": "Grab",   "so_tien": 50000, "danh_muc": "Di chuyển"}
]

# Muốn lưu xuống file → dùng JSON
```

### Ghi JSON — `json.dump()`

```python
import json

data = [
    {"ten": "Cà phê", "so_tien": 35000, "danh_muc": "Ăn uống"},
    {"ten": "Grab",   "so_tien": 50000, "danh_muc": "Di chuyển"}
]

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
#            ↑     ↑   ↑                   ↑
#          data   file  giữ tiếng Việt    dễ đọc
```

File `data.json` sau khi ghi:
```json
[
  {
    "ten": "Cà phê",
    "so_tien": 35000,
    "danh_muc": "Ăn uống"
  },
  {
    "ten": "Grab",
    "so_tien": 50000,
    "danh_muc": "Di chuyển"
  }
]
```

### Đọc JSON — `json.load()`

```python
import json

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)   # → trả về list/dict Python

print(data[0]["ten"])     # Cà phê
print(type(data))         # <class 'list'>
```

### `dump` vs `dumps` — `load` vs `loads`

| Hàm | Làm gì |
|-----|--------|
| `json.dump(data, f)` | Ghi vào **file** |
| `json.dumps(data)` | Chuyển thành **string** (không ghi file) |
| `json.load(f)` | Đọc từ **file** |
| `json.loads(chuoi)` | Đọc từ **string** |

```python
# dumps — dùng khi muốn xem JSON dạng string
import json
d = {"ten": "An", "tuoi": 25}
print(json.dumps(d, ensure_ascii=False))
# {"ten": "An", "tuoi": 25}
```

---

## Phần 3 — Xử lý lỗi với `try/except/finally`

### Tại sao cần?

```python
# ❌ Không có try/except → app crash
with open("data.json", "r") as f:
    data = json.load(f)
# → FileNotFoundError nếu file chưa tồn tại
```

### Cấu trúc đầy đủ

```python
try:
    # Code có thể gây lỗi
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

except FileNotFoundError:
    # Xử lý khi file không tồn tại
    print("File chưa có, tạo mới")
    data = []

except json.JSONDecodeError:
    # Xử lý khi file JSON bị hỏng
    print("File JSON lỗi, reset về rỗng")
    data = []

finally:
    # Luôn chạy dù có lỗi hay không
    print("Đã xử lý xong")
```

### Mental model `try/except/finally`

```
try      → "Thử làm việc này"
except   → "Nếu lỗi xảy ra, làm thế này thay"
finally  → "Dù sao cũng làm việc này trước khi kết thúc"
```

---

## 🔗 Kết nối thẳng vào Expense Tracker

Đây là đoạn code Julius sẽ cần viết trong `tracker.py`:

```python
import json

class Tracker:
    FILE = "data.json"

    def _load(self):
        """Đọc data khi khởi động app"""
        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)          # → list of dict
        except FileNotFoundError:
            return []                        # Lần đầu chạy, chưa có file

    def _save(self, expenses):
        """Ghi data sau mỗi thao tác"""
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(expenses, f, ensure_ascii=False, indent=2)
```

---

## ✅ Checklist kiến thức File I/O

```
□ Biết 4 mode: r / w / a / r+  và khi nào dùng cái nào
□ Luôn dùng "with open(...)" thay vì open() thủ công
□ Luôn có encoding="utf-8" khi file có tiếng Việt
□ json.dump()  → ghi object Python ra file JSON
□ json.load()  → đọc file JSON thành object Python
□ try/except FileNotFoundError khi đọc file có thể chưa tồn tại
```

---