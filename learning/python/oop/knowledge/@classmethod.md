# `@classmethod` — Giải thích từ đầu

## 🧠 Bắt đầu bằng vấn đề thực tế

Nhìn vào `Expense`, có **2 cách** muốn tạo object:

```python
# Cách 1: Tạo từ các tham số riêng lẻ (bình thường)
e1 = Expense("Cà phê", 35000, "Ăn uống", "15-04-2026")

# Cách 2: Tạo từ dict (khi đọc từ JSON)
data = {"ten": "Cà phê", "so_tien": 35000, "danh_muc": "Ăn uống", "ngay": "15-04-2026"}
e2 = ???  # làm thế nào?
```

Cách 2 cần một method đặc biệt — đó là lý do `@classmethod` tồn tại.

---

## 🔍 So sánh 3 loại method trong Python

```python
class Expense:

    # 1. Instance method — method thông thường
    def __str__(self):
        # self = object cụ thể đang gọi
        # Cần có object trước mới gọi được
        return f"{self.ten}"

    # 2. Class method — method của CLASS, không phải object
    @classmethod
    def from_dict(cls, data):
        # cls = class Expense (bản thân class, không phải object)
        # Không cần có object trước
        pass

    # 3. Static method — hàm độc lập, đặt trong class cho gọn
    @staticmethod
    def kiem_tra_so_tien(so_tien):
        # Không cần self, không cần cls
        return so_tien > 0
```

---

## 🎯 `cls` là gì?

> `cls` = **class** — tương tự `self` nhưng thay vì trỏ vào object, nó trỏ vào **bản thân class**.

```python
class Expense:
    @classmethod
    def from_dict(cls, data):
        print(cls)   # <class '__main__.Expense'>
        #  ↑ cls chính là Expense
```

Vậy `cls(...)` tương đương `Expense(...)`:

```python
@classmethod
def from_dict(cls, data):
    return cls(                  # = Expense(
        data["ten"],             #     "Cà phê",
        data["so_tien"],         #     35000,
        data["danh_muc"],        #     "Ăn uống",
        data["ngay"]             #     "15-04-2026"
    )                            # )
```

---

## 🔄 Flow đầy đủ khi dùng `from_dict`

```python
# Tình huống: đọc từ JSON xong
data = {"ten": "Cà phê", "so_tien": 35000,
        "danh_muc": "Ăn uống", "ngay": "15-04-2026"}

# Gọi classmethod — gọi trên CLASS, không phải object
e = Expense.from_dict(data)
#   ↑ không cần tạo object trước

# Bên trong from_dict:
# cls = Expense
# cls(data["ten"], ...) = Expense("Cà phê", 35000, "Ăn uống", "15-04-2026")
# → gọi __init__ bình thường
# → trả về Expense object mới

print(e)  # [15-04-2026] Cà phê — 35,000đ (Ăn uống)
```

---

## 🤔 Tại sao không dùng `__init__` thẳng?

```python
# ❌ Không tiện — phải unpack thủ công mỗi lần
data = {"ten": "Cà phê", "so_tien": 35000, ...}
e = Expense(data["ten"], data["so_tien"], data["danh_muc"], data["ngay"])

# ✅ Gọn hơn nhiều
e = Expense.from_dict(data)
```

Khi đọc 100 expense từ JSON, lợi ích càng rõ:

```python
# Đọc JSON → list of dict
with open("data.json") as f:
    all_data = json.load(f)   # [{"ten":...}, {"ten":...}, ...]

# Chuyển từng dict thành Expense object — 1 dòng
expenses = [Expense.from_dict(item) for item in all_data]
```

---

## 📌 Cách nhớ nhanh

| | `self` method | `cls` method |
|--|--------------|-------------|
| Decorator | *(không có)* | `@classmethod` |
| Tham số đầu | `self` = object | `cls` = class |
| Gọi như thế nào | `expense.to_dict()` | `Expense.from_dict(data)` |
| Cần object trước? | ✅ Có | ❌ Không |
| Dùng khi nào | Làm việc với object | Tạo object theo cách khác |

---
