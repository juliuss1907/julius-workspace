# ============================================================
# BÀI TẬP OOP — TUẦN 8
# ============================================================
# Mục tiêu: Làm quen với class, __init__, self, methods, __str__
# Chưa có inheritance ở bộ này — sẽ học sau.
# ============================================================


# ============================================================
# BÀI 1: Class đầu tiên — Xe hơi 🚗 ⭐
# ============================================================
# Mục tiêu: Viết class đầu tiên, hiểu __init__ và self
#
# Yêu cầu:
#   Tạo class XeHoi với:
#   Thuộc tính:
#     - hang_xe  (str) : Hãng xe (Toyota, Honda...)
#     - mau_xe   (str) : Màu xe
#     - nam_sx   (int) : Năm sản xuất
#   Methods:
#     - __str__        : "Toyota màu đỏ (2020)"
#     - tuoi_xe()      : Trả về số tuổi xe (2025 - nam_sx)
#     - mo_ta()        : In ra "Xe [hang] màu [mau], [tuoi] tuổi"
#
# Test:
#   xe1 = XeHoi("Toyota", "đỏ", 2020)
#   xe2 = XeHoi("Honda", "trắng", 2018)
#   print(xe1)             # Toyota màu đỏ (2020)
#   print(xe1.tuoi_xe())   # 5
#   xe2.mo_ta()            # Xe Honda màu trắng, 7 tuổi

class XeHoi:
    pass  # TODO: Viết code ở đây

# Test
print("=== BÀI 1: Xe hơi ===")
xe1 = XeHoi("Toyota", "đỏ", 2020)
xe2 = XeHoi("Honda", "trắng", 2018)
print(xe1)
print(xe1.tuoi_xe())
xe2.mo_ta()


# ============================================================
# BÀI 2: Class có logic — Tài khoản ngân hàng 💰 ⭐⭐
# ============================================================
# Mục tiêu: Methods thay đổi thuộc tính của object
#
# Yêu cầu:
#   Tạo class TaiKhoan với:
#   Thuộc tính:
#     - chu_tk   (str)   : Tên chủ tài khoản
#     - so_du    (float) : Số dư ban đầu
#   Methods:
#     - __str__          : "TK của Nguyen Van A | Số dư: 1,000,000 VNĐ"
#     - nap_tien(so_tien): Cộng vào số dư, in "Nạp 500,000 VNĐ thành công"
#     - rut_tien(so_tien): Trừ số dư nếu đủ tiền, in kết quả
#                          Nếu không đủ → in "Số dư không đủ!"
#     - xem_so_du()      : In "Số dư hiện tại: 1,000,000 VNĐ"
#
# Test:
#   tk = TaiKhoan("Nguyen Van A", 1_000_000)
#   print(tk)
#   tk.nap_tien(500_000)
#   tk.rut_tien(200_000)
#   tk.rut_tien(9_999_999)
#   tk.xem_so_du()

class TaiKhoan:
    pass  # TODO: Viết code ở đây

print("\n=== BÀI 2: Tài khoản ngân hàng ===")
tk = TaiKhoan("Nguyen Van A", 1_000_000)
print(tk)
tk.nap_tien(500_000)
tk.rut_tien(200_000)
tk.rut_tien(9_999_999)
tk.xem_so_du()


# ============================================================
# BÀI 3: Class với list — Giỏ hàng 🛒 ⭐⭐
# ============================================================
# Mục tiêu: Thuộc tính là list, methods thao tác với list
#
# Yêu cầu:
#   Tạo class GioHang với:
#   Thuộc tính:
#     - khach_hang (str)  : Tên khách hàng
#     - san_pham   (list) : List các dict {"ten": ..., "gia": ..., "so_luong": ...}
#                          Khởi tạo là list rỗng []
#   Methods:
#     - them_san_pham(ten, gia, so_luong=1)
#         Thêm sản phẩm vào giỏ
#         Nếu đã có → tăng số lượng
#         Nếu chưa có → thêm mới
#     - xoa_san_pham(ten)
#         Xóa sản phẩm khỏi giỏ
#         Nếu không có → in "Không tìm thấy [ten]"
#     - tinh_tong()
#         Return tổng tiền (gia × so_luong của tất cả sản phẩm)
#     - hien_thi()
#         In toàn bộ giỏ hàng theo format:
#         === GIỎ HÀNG của Julius ===
#         Phở bò     x2  →  100,000 VNĐ
#         Trà đá     x3  →   15,000 VNĐ
#         TỔNG CỘNG      →  115,000 VNĐ
#
# 💡 Gợi ý: __init__ phải tạo self.san_pham = [] (không dùng tham số)

class GioHang:
    pass  # TODO: Viết code ở đây

print("\n=== BÀI 3: Giỏ hàng ===")
gio = GioHang("Julius")
gio.them_san_pham("Phở bò", 50_000, 2)
gio.them_san_pham("Trà đá", 5_000, 3)
gio.them_san_pham("Phở bò", 50_000, 1)  # tăng thêm 1
gio.hien_thi()
gio.xoa_san_pham("Trà đá")
gio.xoa_san_pham("Không có món này")
gio.hien_thi()


# ============================================================
# BÀI 4: Nhiều objects tương tác — Sinh viên & Lớp học 🎓 ⭐⭐⭐
# ============================================================
# Mục tiêu: Một class chứa list các object của class khác
#
# Yêu cầu:
#   Tạo class SinhVien với:
#     - ten   (str)
#     - diem  (float)
#     - __str__: "An (8.5)"
#     - xep_loai(): "Giỏi" / "Khá" / "Trung bình" / "Yếu"
#
#   Tạo class LopHoc với:
#     - ten_lop    (str)
#     - sinh_vien  (list) : list các object SinhVien, khởi tạo rỗng
#     - them_sv(sinh_vien): Thêm object SinhVien vào lớp
#     - diem_tb_lop()     : Tính điểm TB của cả lớp, return float
#     - sv_gioi_nhat()    : Trả về object SinhVien có điểm cao nhất
#     - thong_ke()        : In thống kê lớp:
#         === LỚP 10A1 ===
#         An     : 8.5 - Giỏi
#         Binh   : 7.0 - Khá
#         Chau   : 4.5 - Yếu
#         Điểm TB lớp : 6.67
#         Giỏi nhất   : An (8.5)
#
# 💡 Gợi ý: sv_gioi_nhat() dùng max() với key=lambda

class SinhVien:
    pass  # TODO: Viết code ở đây

class LopHoc:
    pass  # TODO: Viết code ở đây

print("\n=== BÀI 4: Sinh viên & Lớp học ===")
sv1 = SinhVien("An", 8.5)
sv2 = SinhVien("Binh", 7.0)
sv3 = SinhVien("Chau", 4.5)

lop = LopHoc("10A1")
lop.them_sv(sv1)
lop.them_sv(sv2)
lop.them_sv(sv3)
lop.thong_ke()


# ============================================================
# BÀI 5: Tổng hợp — Quản lý thư viện sách 📚 ⭐⭐⭐
# ============================================================
# Mục tiêu: OOP thực tế, kết hợp với kiến thức cũ
#
# Yêu cầu:
#   Tạo class Sach với:
#     - ma_sach  (str)
#     - tieu_de  (str)
#     - tac_gia  (str)
#     - con_lai  (int) : Số bản còn có thể mượn
#     - __str__        : "[S001] Python cơ bản - Nguyen Van A (còn 3)"
#     - co_the_muon()  : Return True nếu con_lai > 0
#
#   Tạo class ThuVien với:
#     - ten        (str)
#     - sach_list  (list) : list các object Sach, khởi tạo rỗng
#     - them_sach(sach)   : Thêm object Sach vào thư viện
#     - tim_sach(keyword) : Tìm sách có tieu_de chứa keyword
#                           Return list các object Sach tìm được
#     - muon_sach(ma_sach): Giảm con_lai đi 1 nếu còn sách
#                           In kết quả thành công/thất bại
#     - tra_sach(ma_sach) : Tăng con_lai lên 1
#                           In kết quả
#     - hien_thi()        : In toàn bộ sách trong thư viện
#
# Test:
#   tv = ThuVien("Thư viện AI")
#   tv.them_sach(Sach("S001", "Python cơ bản", "Nguyen Van A", 3))
#   tv.them_sach(Sach("S002", "Machine Learning", "Tran Thi B", 2))
#   tv.them_sach(Sach("S003", "Python nâng cao", "Nguyen Van A", 1))
#   tv.hien_thi()
#   tv.muon_sach("S003")
#   tv.muon_sach("S003")  # hết sách
#   ket_qua = tv.tim_sach("Python")
#   for sach in ket_qua:
#       print(sach)

class Sach:
    pass  # TODO: Viết code ở đây

class ThuVien:
    pass  # TODO: Viết code ở đây

print("\n=== BÀI 5: Quản lý thư viện ===")
tv = ThuVien("Thư viện AI")
tv.them_sach(Sach("S001", "Python cơ bản", "Nguyen Van A", 3))
tv.them_sach(Sach("S002", "Machine Learning", "Tran Thi B", 2))
tv.them_sach(Sach("S003", "Python nâng cao", "Nguyen Van A", 1))
tv.hien_thi()
tv.muon_sach("S003")
tv.muon_sach("S003")  # hết sách
print("\n--- Tìm sách chứa 'Python' ---")
ket_qua = tv.tim_sach("Python")
for sach in ket_qua:
    print(sach)
