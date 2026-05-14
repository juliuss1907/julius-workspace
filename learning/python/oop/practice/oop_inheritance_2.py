import math
from typing import Self

# ============================================================
# BÀI TẬP OOP INHERITANCE — BỘ 2
# ============================================================
# Mục tiêu: super(), ghi đè method, kế thừa nhiều tầng
# ============================================================


# ============================================================
# BÀI 1: Hình học 📐 ⭐⭐
# ============================================================
# Mục tiêu: Kế thừa nhiều tầng, ghi đè method tính toán
#
# Class HinhHoc (cha):
#   __init__(self, ten, mau)
#   __str__    : "Hình chữ nhật màu đỏ"
#   dien_tich(): Return 0
#   chu_vi()   : Return 0
#   mo_ta()    : In:
#       Hình chữ nhật màu đỏ
#       Diện tích : 50.00
#       Chu vi    : 30.00
#
# Class HinhChuNhat(HinhHoc):
#   __init__(self, mau, chieu_dai, chieu_rong)
#   → gọi super().__init__("Hình chữ nhật", mau)
#   dien_tich(): chieu_dai × chieu_rong
#   chu_vi()   : 2 × (chieu_dai + chieu_rong)
#
# Class HinhTron(HinhHoc):
#   __init__(self, mau, ban_kinh)
#   → gọi super().__init__("Hình tròn", mau)
#   dien_tich(): math.pi × ban_kinh²
#   chu_vi()   : 2 × math.pi × ban_kinh
#
# Class HinhVuong(HinhChuNhat):  ← kế thừa HinhChuNhat
#   __init__(self, mau, canh)
#   → gọi super().__init__(mau, canh, canh)
#   __str__: "Hình vuông màu vàng (cạnh 5)"

class HinhHoc:
    def __init__(self, ten, mau):
        self.ten = ten
        self.mau = mau

    def __str__(self):
        return f"{self.ten} màu {self.mau}"
    
    def dien_tich(self):
        return 0

    def chu_vi(self):
        return 0
    
    def mo_ta(self):
        print(self)
        print(f"Diện tích: {self.dien_tich():.2f}")
        print(f"Chu vi: {self.chu_vi():.2f}")

class HinhChuNhat(HinhHoc):
    def __init__(self, mau, chieu_dai, chieu_rong):
        super().__init__("Hình chữ nhật", mau)
        self.chieu_dai = chieu_dai
        self.chieu_rong = chieu_rong
    
    def dien_tich(self):
        return self.chieu_dai * self.chieu_rong
    
    def chu_vi(self):
        return (self.chieu_dai + self.chieu_rong)*2
    
    def mo_ta(self):
        return super().mo_ta()

class HinhTron(HinhHoc):
    def __init__(self, mau, ban_kinh):
        super().__init__("Hình tròn", mau)
        self.ban_kinh = ban_kinh
    
    def dien_tich(self):
        return math.pi*self.ban_kinh**2
    
    def chu_vi(self):
        return math.pi*self.ban_kinh*2
    
    def mo_ta(self):
        super().mo_ta()

class HinhVuong(HinhChuNhat):
    def __init__(self, mau, canh):
        super().__init__(mau, canh, canh)
        self.canh = canh

    def __str__(self):
        return f"Hình vuông màu {self.mau} (cạnh {self.canh})"

print("=== BÀI 1: Hình học ===")
h1 = HinhChuNhat("đỏ", 10, 5)
h2 = HinhTron("xanh", 7)
h3 = HinhVuong("vàng", 5)
h1.mo_ta()
print()
h2.mo_ta()
print()
h3.mo_ta()
print(h3)


# ============================================================
# BÀI 2: Game nhân vật ⚔️ ⭐⭐
# ============================================================
# Mục tiêu: Objects tương tác với nhau, ghi đè logic chiến đấu
#
# Class NhanVat (cha):
#   __init__(self, ten, hp, hp_max, sat_thuong)
#   __str__          : "An | HP: 80/100"
#   tan_cong(doi_thu): doi_thu.hp -= sat_thuong
#                      In "[ten] tấn công [doi_thu.ten] gây [sat_thuong] sát thương!"
#                      Nếu doi_thu.hp <= 0 → in "[doi_thu.ten] đã bị đánh bại!"
#   hoi_phuc(so_hp)  : hp += so_hp, không vượt hp_max
#                      In "[ten] hồi [so_hp] HP"
#   con_song()       : Return True nếu hp > 0
#
# Class ChienSi(NhanVat):
#   __init__(self, ten, hp, hp_max, sat_thuong, giap)
#   __str__ : "An (Chiến Sĩ) | HP: 80/100 | Giáp: 20"
#   tan_cong(doi_thu): Nếu doi_thu có giáp → sát thương = sat_thuong - doi_thu.giao_giac (tối thiểu 1)
#                      Nếu không có giáp → sát thương bình thường
#   💡 Gợi ý: dùng hasattr(doi_thu, 'giap') để kiểm tra
#
# Class PhapSu(NhanVat):
#   __init__(self, ten, hp, hp_max, sat_thuong, mana)
#   __str__ : "Kira (Pháp Sư) | HP: 60/80 | Mana: 100"
#   phep_thuat(doi_thu): Tốn 30 mana, gây sat_thuong × 2
#                        Nếu không đủ mana "Không đủ mana!"

class NhanVat:
    def __init__(self, ten, hp, hp_max, sat_thuong):
        self.ten = ten
        self.hp = hp
        self.hp_max = hp_max
        self.sat_thuong = sat_thuong
    
    def __str__(self):
        return f"{self.ten} | HP: {self.hp}/{self.hp_max}"
    
    def tan_cong(self, doi_thu):
        doi_thu.hp -= self.sat_thuong
        print(f"{self.ten} tấn công {doi_thu.ten} gây {self.sat_thuong} sát thương!")
        if doi_thu.hp <= 0:
            print(f"{doi_thu.ten} đã bị đánh bại")
    
    def hoi_phuc(self, so_hp):
        self.hp += so_hp
        if self.hp >= self.hp_max:
            self.hp = self.hp_max
        print(f"{self.ten} hồi {so_hp} HP")
        return self.hp
    
    def con_song(self):
        if self.hp > 0:
            return True
        else:
            return False
        

class ChienSi(NhanVat):
    def __init__(self, ten, hp, hp_max, sat_thuong, giap):
        super().__init__(ten, hp, hp_max, sat_thuong)
        self.giap = giap
    
    def __str__(self):
        return f"{super().__str__()} | Giáp: {self.giap}"
    
    def tan_cong(self, doi_thu):
        if hasattr(doi_thu, 'giap'):
            doi_thu.hp -= (self.sat_thuong - doi_thu.giap)
            print(f"{self.ten} tấn công {doi_thu.ten} gây {self.sat_thuong - doi_thu.giap} sát thương!")
        else:
            super().tan_cong(doi_thu)
        
        return doi_thu.hp

class PhapSu(NhanVat):
    def __init__(self, ten, hp, hp_max, sat_thuong, mana):
        super().__init__(ten, hp, hp_max, sat_thuong)
        self.mana = mana
    
    def __str__(self):
        return f"{super().__str__()} | Mana: {self.mana}"
    
    def phep_thuat(self, doi_thu):
        if self.mana >= 30:
            doi_thu.hp -= self.sat_thuong*2
            self.mana -= 30
            print(f"{self.ten} tấn công {doi_thu.ten} gây {self.sat_thuong*2} sát thương!")
        else:
            print("Không đủ mana")

        return self.mana, doi_thu.hp

print("\n=== BÀI 2: Game nhân vật ===")
cs = ChienSi("An", 100, 100, 15, 20)
ps = PhapSu("Kira", 80, 80, 25, 100)
print(cs)
print(ps)
ps.phep_thuat(cs)
cs.tan_cong(ps)
cs.hoi_phuc(30)
print(cs)
print(ps)


# ============================================================
# BÀI 3: Phương tiện vận chuyển 🚢✈️ ⭐⭐⭐
# ============================================================
# Mục tiêu: super() trong phép tính, thêm chi phí vào nhau
#
# Class PhuongTienVanChuyen (cha):
#   __init__(self, ten, tai_trong, gia_cuoc_km)
#   __str__                   : "Xe tải ABC | Tải trọng: 10 tấn"
#   tinh_cuoc(km, hang_hoa)   : Return km × gia_cuoc_km × hang_hoa
#                               Nếu hang_hoa > tai_trong → in cảnh báo, return None
#   in_bao_gia(km, hang_hoa)  : In:
#       === BÁO GIÁ VẬN CHUYỂN ===
#       Phương tiện : Xe tải ABC
#       Quãng đường : 100 km
#       Hàng hóa   : 3 tấn
#       Chi phí    : 1,500,000 VNĐ
#
# Class XeTai(PhuongTienVanChuyen):
#   __init__(self, ten, tai_trong, gia_cuoc_km, phi_xang)
#   tinh_cuoc(km, hang_hoa): super().tinh_cuoc() + phi_xang × km
#
# Class TauBien(PhuongTienVanChuyen):
#   __init__(self, ten, tai_trong, gia_cuoc_km, phi_cang)
#   tinh_cuoc(km, hang_hoa): super().tinh_cuoc() + phi_cang
#
# Class MayBay(PhuongTienVanChuyen):
#   __init__(self, ten, tai_trong, gia_cuoc_km, hang)
#   hang: "economy" hoặc "business"
#   tinh_cuoc(km, hang_hoa): "business" → nhân 1.5 | "economy" → giữ nguyên

class PhuongTienVanChuyen:
    def __init__(self, ten, tai_trong, gia_cuoc_km):
        self.ten = ten
        self.tai_trong = tai_trong
        self.gia_cuoc_km = gia_cuoc_km
    def __str__(self):
        return f"{self.ten} | Tải trọng: {self.tai_trong} tấn"
    def tinh_cuoc(self, km, hang_hoa):
        if hang_hoa > self.tai_trong:
            print("Vượt quá tải trọng!")
            return None
        else:
            return km*self.gia_cuoc_km*hang_hoa

    def in_bao_gia(self, km, hang_hoa):
        if hang_hoa > self.tai_trong:
            print("Không thể chở hàng hóa này!")
        else:
            print("=== BÁO GIÁ VẬN CHUYỂN ===")
            print(f"Phương tiện : {self.ten}")
            print(f"Quãng đường : {km} km")
            print(f"Hàng hóa    :  {hang_hoa} tấn")
            print(f"Chi phí     : {self.tinh_cuoc(km, hang_hoa):,} VNĐ")

class XeTai(PhuongTienVanChuyen):
    def __init__(self, ten, tai_trong, gia_cuoc_km, phi_xang):
        super().__init__(ten, tai_trong, gia_cuoc_km)
        self.phi_xang = phi_xang
        
    def tinh_cuoc(self, km, hang_hoa):
        if super().tinh_cuoc(km, hang_hoa) != None:
            return super().tinh_cuoc(km, hang_hoa) + self.phi_xang

class TauBien(PhuongTienVanChuyen):
    def __init__(self, ten, tai_trong, gia_cuoc_km, phi_cang):
        super().__init__(ten, tai_trong, gia_cuoc_km)
        self.phi_cang = phi_cang
    
    def tinh_cuoc(self, km, hang_hoa):
        if super().tinh_cuoc(km, hang_hoa) != None:
            return super().tinh_cuoc(km, hang_hoa) + self.phi_cang

class MayBay(PhuongTienVanChuyen):
    def __init__(self, ten, tai_trong, gia_cuoc_km, hang):
        super().__init__(ten, tai_trong, gia_cuoc_km)
        self.hang = hang
    
    def tinh_cuoc(self, km, hang_hoa):
        if self.hang == "business":
            return super().tinh_cuoc(km, hang_hoa)*1.5
        elif self.hang == "economy":
            return super().tinh_cuoc(km, hang_hoa)

print("\n=== BÀI 3: Phương tiện vận chuyển ===")
xe      = XeTai("Xe tải ABC", 10, 5_000, 2_000)
tau     = TauBien("Tàu Hải Long", 500, 1_000, 5_000_000)
may_bay = MayBay("VietJet VJ123", 20, 50_000, "business")
xe.in_bao_gia(100, 3)
print()
tau.in_bao_gia(1_000, 200)
print()
may_bay.in_bao_gia(500, 5)


# ============================================================
# BÀI 4: Hệ thống khóa học 📚 ⭐⭐⭐
# ============================================================
# Mục tiêu: 4 tầng kế thừa, ghi đè dang_ky() có điều kiện
#
# Class KhoaHoc (cha):
#   __init__(self, ten, gia, so_bai) → hoc_vien = []
#   __str__          : "Python cơ bản | 500,000 VNĐ | 20 bài"
#   dang_ky(ten_hv)  : Thêm vào hoc_vien, in "✅ [ten_hv] đã đăng ký [ten]"
#   so_hoc_vien()    : Return len(hoc_vien)
#   doanh_thu()      : Return gia × so_hoc_vien()
#
# Class KhoaHocOnline(KhoaHoc)
#   __init__(self, ten, gia, so_bai, link_zoom)
#   __str__          : "... | Online"
#   dang_ky(ten_hv)  : super().dang_ky() + in "   Link học: [link_zoom]"
#
# Class KhoaHocOffline(KhoaHoc):
#   __init__(self, ten, gia, so_bai, dia_diem, suc_chua)
#   __str__          : "... | Offline tại [dia_diem]"
#   dang_ky(ten_hv)  : Kiểm tra còn chỗ không, nếu đầy → in "❌ Lớp đã đầy!"
#
# Class KhoaHocVIP(KhoaHocOnline):  ← cháu của KhoaHoc
#   __init__(self, ten, gia, so_bai, link_zoom, mentor)
#   __str__          : "... | VIP (mentor: Julius)"
#   dang_ky(ten_hv)  : super().dang_ky() + in "   Mentor của bạn: [mentor]"

class KhoaHoc:
    def __init__(self, ten, gia, so_bai):
        self.ten = ten
        self.gia = gia
        self.so_bai = so_bai
        self.hoc_vien = []
    
    def __str__(self):
        return f"{self.ten} | {self.gia} VNĐ | {self.so_bai} bài"
    
    def dang_ky(self, ten_hv):
        self.hoc_vien.append(ten_hv)
        print(f"✅ {ten_hv} đã đăng ký {self.ten}")
    
    def so_hoc_vien(self):
        return len(self.hoc_vien)
    
    def doanh_thu(self):
        return self.gia*self.so_hoc_vien()

class KhoaHocOnline(KhoaHoc):
    def __init__(self, ten, gia, so_bai, link_zoom):
        super().__init__(ten, gia, so_bai)
        self.link_zoom = link_zoom
    
    def __str__(self):
        return f"{super().__str__()} | Online"
    
    def dang_ky(self, ten_hv):
        super().dang_ky(ten_hv)
        print(f"Link học: {self.link_zoom}")
        return self.hoc_vien

class KhoaHocOffline(KhoaHoc):
    def __init__(self, ten, gia, so_bai, dia_diem, suc_chua):
        super().__init__(ten, gia, so_bai)
        self.dia_diem = dia_diem
        self.suc_chua = suc_chua

    def __str__(self):
        return f"{super().__str__} | Offline tại {self.dia_diem}"
    
    def dang_ky(self, ten_hv):
        if len(self.hoc_vien) < self.suc_chua:
            super().dang_ky(ten_hv)
        else:
            print("❌ Lớp đã đầy!")
        return self.hoc_vien

class KhoaHocVIP(KhoaHocOnline):
    def __init__(self, ten, gia, so_bai, link_zoom, mentor):
        super().__init__(ten, gia, so_bai, link_zoom)
        self.mentor = mentor
    def __str__(self):
        return f"{super().__str__()} | VIP (mentor: {self.mentor})"

    def dang_ky(self, ten_hv):
        super().dang_ky(ten_hv)
        print(f"Mentor của bạn: {self.mentor}")
        return self.hoc_vien


print("\n=== BÀI 4: Hệ thống khóa học ===")
k1 = KhoaHocOnline("Python cơ bản", 500_000, 20, "zoom.us/abc123")
k2 = KhoaHocOffline("ML thực chiến", 2_000_000, 15, "Hà Nội", 3)
k3 = KhoaHocVIP("AI Engineering", 5_000_000, 30, "zoom.us/vip", "Julius")
k1.dang_ky("An")
k1.dang_ky("Binh")
k2.dang_ky("Chau")
k2.dang_ky("Dung")
k2.dang_ky("Em")
k2.dang_ky("Phong")   # ← lớp đã đầy
k3.dang_ky("Alice")
print()
for k in [k1, k2, k3]:
    print(f"{k.ten}: {k.so_hoc_vien()} HV | Doanh thu: {k.doanh_thu():,} VNĐ")


# ============================================================
# BÀI 5: Hệ thống thông báo 🔔 ⭐⭐⭐⭐
# ============================================================
# Mục tiêu: OOP + Inheritance + File I/O kết hợp
#
# Class ThongBao (cha):
#   __init__(self, tieu_de, noi_dung, nguoi_nhan) → da_gui = False
#   __str__ : "[EMAIL] Julius | Chào mừng"  ← dùng self.loai()
#   loai()  : Return "THÔNG BÁO"
#   gui()   : da_gui = True
#             Ghi vào file "lich_su_tb.txt" (mode "a"):
#               "[LOAI] → [nguoi_nhan] | [tieu_de]"
#             In "Đã gửi [loai()] đến [nguoi_nhan]"
#
# Class Email(ThongBao):
#   loai(): Return "EMAIL"
#   gui() : super().gui() + in "Nội dung: [noi_dung]"
#
# Class SMS(ThongBao):
#   __init__(self, tieu_de, noi_dung, nguoi_nhan, so_dien_thoai)
#   loai(): Return "SMS"
#   gui() : Nếu len(noi_dung) > 160 → in cảnh báo, cắt bớt còn 160 ký tự
#           Rồi super().gui()
#
# Class PushNotification(ThongBao):
#   __init__(self, tieu_de, noi_dung, nguoi_nhan, app_id)
#   loai(): Return "PUSH"
#   gui() : super().gui() + in "App: [app_id]"
#
# Function doc_lich_su():
#   Đọc và in toàn bộ file "lich_su_tb.txt"
#   Nếu chưa có file → in "Chưa có lịch sử thông báo nào."

LICH_SU_FILE = "lich_su_tb.txt"

class ThongBao:
    def __init__(self, tieu_de, noi_dung, nguoi_nhan):
        self.tieu_de = tieu_de
        self.noi_dung = noi_dung
        self.nguoi_nhan = nguoi_nhan
        self.da_gui = False

    def loai(self):
        return "THÔNG BÁO"

    def __str__(self):
        return f"{self.loai()} {self.ten} | {self.noi_dung}"

    def gui(self):
        self.da_gui = True
        with open("lich_su_tb.txt", "a", encoding="utf-8") as f:
            f.write(f"{self.loai()} --> {self.nguoi_nhan} --> {self.tieu_de}\n")
        print(f"Đã gửi {self.loai()} đến {self.nguoi_nhan}")

class Email(ThongBao):
    def __init__(self, tieu_de, noi_dung, nguoi_nhan):
        super().__init__(tieu_de, noi_dung, nguoi_nhan)
    
    def loai(self):
        return "EMAIL"
    
    def gui(self):
        super().gui()
        print(f"Nội dung: {self.noi_dung}")

class SMS(ThongBao):
    def __init__(self, tieu_de, noi_dung, nguoi_nhan, so_dien_thoai):
        super().__init__(tieu_de, noi_dung, nguoi_nhan)
        self.so_dien_thoai = so_dien_thoai
    
    def loai(self):
        return "TIN NHẮN"
    
    def gui(self):
        if len(self.noi_dung) > 160:
            print("⚠️ Nội dung vượt 160 ký tự, đã cắt bớt")
            self.noi_dung = self.noi_dung[:160]
        super().gui()

class PushNotification(ThongBao):
    def __init__(self, tieu_de, noi_dung, nguoi_nhan, app_id):
        super().__init__(tieu_de, noi_dung, nguoi_nhan)
        self.app_id = app_id
    
    def loai(self):
        return "PUSH"
    
    def gui(self):
        super().gui()
        print(f"App: {self.app_id}")

def doc_lich_su():
    try:
        with open("lich_su_tb.txt", "r", encoding="utf-8") as f:
            for dong in f:
                print(dong.strip())
    except FileNotFoundError:
        print("Chưa có lịch sử thông báo nào.")


print("\n=== BÀI 5: Hệ thống thông báo ===")
open(LICH_SU_FILE, "w").close()  # reset file trước khi test
tb1 = Email("Chào mừng", "Chào Julius, chúc mừng đã đăng ký!", "Julius")
tb2 = SMS("Mã OTP", "Mã OTP của bạn là 123456", "Julius", "0901234567")
tb3 = PushNotification("Có tin nhắn mới", "An vừa nhắn tin cho bạn", "Julius", "app_001")
tb1.gui()
tb2.gui()
tb3.gui()
print("\n--- Lịch sử thông báo ---")
doc_lich_su()
