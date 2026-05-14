# ============================================================
# BÀI TẬP OOP NÂNG CAO — Inheritance (Kế thừa)
# ============================================================
# Mục tiêu: Hiểu class cha/con, super(), ghi đè method
# Prerequisite: Đã nắm __init__, self, methods, __str__
# ============================================================


# ============================================================
# BÀI 1: Inheritance cơ bản — Động vật 🐾 ⭐⭐
# ============================================================
# Mục tiêu: Hiểu class cha/con, super(), ghi đè method
#
# Yêu cầu:
#   Tạo class DongVat (class cha) với:
#     - ten     (str)
#     - tuoi    (int)
#     - __str__      : "DongVat: Mimi, 3 tuổi"
#     - keu()        : In "..."  (chưa biết kêu gì)
#     - gioi_thieu() : In "Tôi là [ten], [tuoi] tuổi"
#
#   Tạo class Cho(DongVat) với:
#     - giong   (str) : Giống chó (Husky, Corgi...)
#     - __str__       : "Chó: Mimi (Husky), 3 tuổi"
#     - keu()         : In "Gâu gâu!"  (ghi đè)
#     - gioi_thieu()  : Gọi super() rồi thêm "Giống: [giong]"
#
#   Tạo class Meo(DongVat) với:
#     - mau_long (str)
#     - __str__       : "Mèo: Mimi (lông trắng), 3 tuổi"
#     - keu()         : In "Meo meo!"
#     - gioi_thieu()  : Gọi super() rồi thêm "Màu lông: [mau_long]"
#
# Test:
#   cho = Cho("Mimi", 3, "Husky")
#   meo = Meo("Kiki", 2, "trắng")
#   print(cho)
#   print(meo)
#   cho.keu()
#   meo.keu()
#   cho.gioi_thieu()
#   meo.gioi_thieu()

class DongVat:
    pass  # TODO

class Cho(DongVat):
    pass  # TODO

class Meo(DongVat):
    pass  # TODO

print("=== BÀI 1: Động vật ===")
cho = Cho("Mimi", 3, "Husky")
meo = Meo("Kiki", 2, "trắng")
print(cho)
print(meo)
cho.keu()
meo.keu()
cho.gioi_thieu()
meo.gioi_thieu()


# ============================================================
# BÀI 2: Super() trong thực tế — Nhân viên 👔 ⭐⭐
# ============================================================
# Mục tiêu: super() truyền tham số đúng cách, thêm thuộc tính riêng
#
# Yêu cầu:
#   Tạo class NhanVien (class cha) với:
#     - ho_ten     (str)
#     - ma_nv      (str)
#     - luong_cb   (float) : Lương cơ bản
#     - __str__            : "NV001 - Nguyen Van A"
#     - tinh_luong()       : Return luong_cb (chưa có thưởng)
#     - in_phieu_luong()   : In:
#         === PHIẾU LƯƠNG ===
#         Nhân viên : Nguyen Van A
#         Mã NV     : NV001
#         Lương     : 10,000,000 VNĐ
#
#   Tạo class NhanVienKinhDoanh(NhanVien) với:
#     - doanh_so   (float) : Doanh số đạt được
#     - hoa_hong   (float) : % hoa hồng (vd: 0.05 = 5%)
#     - tinh_luong()       : luong_cb + doanh_so × hoa_hong  (ghi đè)
#     - in_phieu_luong()   : Gọi super() rồi thêm dòng:
#         Doanh số  : 100,000,000 VNĐ
#         Hoa hồng  : 5,000,000 VNĐ
#
#   Tạo class NhanVienKyThuat(NhanVien) với:
#     - phu_cap    (float) : Phụ cấp kỹ thuật
#     - tinh_luong()       : luong_cb + phu_cap  (ghi đè)
#     - in_phieu_luong()   : Gọi super() rồi thêm dòng:
#         Phụ cấp KT: 2,000,000 VNĐ
#
# Test:
#   nv1 = NhanVienKinhDoanh("Nguyen Van A", "NV001", 10_000_000, 100_000_000, 0.05)
#   nv2 = NhanVienKyThuat("Tran Thi B", "NV002", 12_000_000, 2_000_000)
#   nv1.in_phieu_luong()
#   print(f"Tổng lương: {nv1.tinh_luong():,} VNĐ")
#   print()
#   nv2.in_phieu_luong()
#   print(f"Tổng lương: {nv2.tinh_luong():,} VNĐ")

class NhanVien:
    pass  # TODO

class NhanVienKinhDoanh(NhanVien):
    pass  # TODO

class NhanVienKyThuat(NhanVien):
    pass  # TODO

print("\n=== BÀI 2: Nhân viên ===")
nv1 = NhanVienKinhDoanh("Nguyen Van A", "NV001", 10_000_000, 100_000_000, 0.05)
nv2 = NhanVienKyThuat("Tran Thi B", "NV002", 12_000_000, 2_000_000)
nv1.in_phieu_luong()
print(f"Tổng lương: {nv1.tinh_luong():,} VNĐ")
print()
nv2.in_phieu_luong()
print(f"Tổng lương: {nv2.tinh_luong():,} VNĐ")


# ============================================================
# BÀI 3: List chứa nhiều loại object — Cửa hàng 🏪 ⭐⭐⭐
# ============================================================
# Mục tiêu: Dùng inheritance để xử lý nhiều loại object trong 1 list
#
# Yêu cầu:
#   Tạo class SanPham (class cha) với:
#     - ten       (str)
#     - gia       (float)
#     - so_luong  (int)
#     - __str__          : "Phở bò - 50,000 VNĐ (còn 10)"
#     - tinh_tien(sl)    : Return gia × sl (chưa có giảm giá)
#     - con_hang()       : Return True nếu so_luong > 0
#
#   Tạo class SanPhamKhuyenMai(SanPham) với:
#     - giam_gia  (float) : Phần trăm giảm (0.1 = 10%)
#     - __str__           : "Phở bò - 50,000 VNĐ (giảm 10%) (còn 10)"
#     - tinh_tien(sl)     : gia × sl × (1 - giam_gia)  (ghi đè)
#
#   Tạo class CuaHang với:
#     - ten           (str)
#     - san_pham_list (list) : Khởi tạo rỗng
#     - them_sp(sp)          : Thêm object SanPham hoặc SanPhamKhuyenMai
#     - ban_hang(ten, sl)    : Tìm sản phẩm theo tên, trừ so_luong,
#                              in tổng tiền phải trả
#                              Nếu không đủ hàng → in cảnh báo
#     - hien_thi()           : In toàn bộ sản phẩm
#     - tong_doanh_thu()     : Tính tổng nếu bán hết tất cả (so_luong hiện tại)
#
# 💡 Key insight: ban_hang() gọi sp.tinh_tien() — Python tự biết
#    dùng tinh_tien() của SanPham hay SanPhamKhuyenMai tùy object!
#    Đây là sức mạnh của inheritance.
#
# Test:
#   ch = CuaHang("Quán ăn Julius")
#   ch.them_sp(SanPham("Phở bò", 50_000, 10))
#   ch.them_sp(SanPham("Cơm tấm", 45_000, 5))
#   ch.them_sp(SanPhamKhuyenMai("Trà đá", 5_000, 20, 0.5))  # giảm 50%
#   ch.hien_thi()
#   ch.ban_hang("Phở bò", 2)
#   ch.ban_hang("Trà đá", 3)
#   ch.ban_hang("Cơm tấm", 10)  # không đủ hàng

class SanPham:
    pass  # TODO

class SanPhamKhuyenMai(SanPham):
    pass  # TODO

class CuaHang:
    pass  # TODO

print("\n=== BÀI 3: Cửa hàng ===")
ch = CuaHang("Quán ăn Julius")
ch.them_sp(SanPham("Phở bò", 50_000, 10))
ch.them_sp(SanPham("Cơm tấm", 45_000, 5))
ch.them_sp(SanPhamKhuyenMai("Trà đá", 5_000, 20, 0.5))
ch.hien_thi()
print()
ch.ban_hang("Phở bò", 2)
ch.ban_hang("Trà đá", 3)
ch.ban_hang("Cơm tấm", 10)


# ============================================================
# BÀI 4: Kế thừa nhiều tầng — Phương tiện 🚗🚌✈️ ⭐⭐⭐
# ============================================================
# Mục tiêu: Inheritance nhiều cấp (cha → con → cháu)
#
# Yêu cầu:
#   Class PhuongTien (gốc):
#     - ten_pt      (str)
#     - van_toc_max (int) : km/h
#     - nhien_lieu  (str) : "xăng", "điện", "dầu"
#     - __str__           : "Toyota Camry | 180 km/h | xăng"
#     - thoi_gian(km)     : Return km / van_toc_max (giờ)
#     - mo_ta()           : In thông tin + thời gian đi 100km
#
#   Class XeMay(PhuongTien):  ← kế thừa PhuongTien
#     - bien_so     (str)
#     - __str__           : "Honda Wave [29A-12345] | 90 km/h | xăng"
#     - mo_ta()           : super().mo_ta() + "Biển số: [bien_so]"
#
#   Class XeDap(XeMay):  ← kế thừa XeMay (cháu của PhuongTien)
#     (XeDap không cần biển số nhưng kế thừa XeMay)
#     - __init__: gọi super().__init__ với bien_so="Không có"
#                 và nhien_lieu="sức người"
#     - keu()           : In "Chít chít!"
#     - mo_ta()         : super().mo_ta() + "Thân thiện môi trường!"
#
# 💡 Gợi ý: XeDap kế thừa XeMay → XeDap có tất cả
#    thuộc tính và methods của cả XeMay lẫn PhuongTien
#
# Test:
#   xe_may = XeMay("Honda Wave", 90, "xăng", "29A-12345")
#   xe_dap = XeDap("Giant", 25)
#   print(xe_may)
#   print(xe_dap)
#   xe_may.mo_ta()
#   print()
#   xe_dap.mo_ta()
#   xe_dap.keu()
#   print(f"Đi 50km mất: {xe_dap.thoi_gian(50):.1f} giờ")

class PhuongTien:
    pass  # TODO

class XeMay(PhuongTien):
    pass  # TODO

class XeDap(XeMay):
    pass  # TODO

print("\n=== BÀI 4: Phương tiện ===")
xe_may = XeMay("Honda Wave", 90, "xăng", "29A-12345")
xe_dap = XeDap("Giant", 25)
print(xe_may)
print(xe_dap)
xe_may.mo_ta()
print()
xe_dap.mo_ta()
xe_dap.keu()
print(f"Đi 50km mất: {xe_dap.thoi_gian(50):.1f} giờ")


# ============================================================
# BÀI 5: Tổng hợp — Hệ thống tài khoản ngân hàng 🏦 ⭐⭐⭐⭐
# ============================================================
# Mục tiêu: OOP + Inheritance + File I/O kết hợp
#
# Yêu cầu:
#   Class TaiKhoan (cha):
#     - so_tai_khoan (str)
#     - chu_tai_khoan(str)
#     - so_du        (float)
#     - lich_su      (list) : list string ghi lại giao dịch
#     - __str__             : "[TK001] Nguyen Van A - 10,000,000 VNĐ"
#     - nap_tien(so_tien)   : Cộng tiền, lưu lịch sử "Nạp: +X VNĐ"
#     - xem_lich_su()       : In toàn bộ lịch sử giao dịch
#
#   Class TaiKhoanTietKiem(TaiKhoan):
#     - lai_suat (float) : vd 0.06 = 6%/năm
#     - __str__          : "[TK001] Nguyen Van A - 10,000,000 VNĐ (Tiết kiệm 6%)"
#     - tinh_lai(thang)  : Return so_du × lai_suat × (thang/12)
#     - tat_toan(thang)  : Tính lãi + cộng vào số dư + in kết quả
#                          Lưu lịch sử "Tất toán [thang] tháng: +X VNĐ tiền lãi"
#
#   Class TaiKhoanThanhToan(TaiKhoan):
#     - han_muc_chi (float) : Hạn mức chi tiêu mỗi lần
#     - __str__             : "[TK002] Tran Thi B - 5,000,000 VNĐ (Thanh toán, hạn mức: 2,000,000)"
#     - rut_tien(so_tien)   : Rút tiền nếu đủ số dư VÀ không vượt hạn mức
#                             Lưu lịch sử "Rút: -X VNĐ"
#                             Nếu vượt hạn mức → in cảnh báo, không rút
#
# Test:
#   tk1 = TaiKhoanTietKiem("TK001", "Nguyen Van A", 10_000_000, 0.06)
#   tk2 = TaiKhoanThanhToan("TK002", "Tran Thi B", 5_000_000, 2_000_000)
#   print(tk1)
#   print(tk2)
#   tk1.nap_tien(5_000_000)
#   tk1.tat_toan(6)           # tất toán sau 6 tháng
#   tk1.xem_lich_su()
#   print()
#   tk2.rut_tien(1_500_000)   # OK
#   tk2.rut_tien(2_500_000)   # vượt hạn mức
#   tk2.xem_lich_su()

class TaiKhoan:
    pass  # TODO

class TaiKhoanTietKiem(TaiKhoan):
    pass  # TODO

class TaiKhoanThanhToan(TaiKhoan):
    pass  # TODO

print("\n=== BÀI 5: Hệ thống tài khoản ngân hàng ===")
tk1 = TaiKhoanTietKiem("TK001", "Nguyen Van A", 10_000_000, 0.06)
tk2 = TaiKhoanThanhToan("TK002", "Tran Thi B", 5_000_000, 2_000_000)
print(tk1)
print(tk2)
tk1.nap_tien(5_000_000)
tk1.tat_toan(6)
tk1.xem_lich_su()
print()
tk2.rut_tien(1_500_000)
tk2.rut_tien(2_500_000)
tk2.xem_lich_su()
