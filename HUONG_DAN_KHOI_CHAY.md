# HƯỚNG DẪN KHỞI CHẠY & SỬ DỤNG HỆ THỐNG NUTRIDSS V2 (HUONG_DAN_KHOI_CHAY.md)

Tài liệu này cung cấp hướng dẫn từng bước để cài đặt, khởi chạy và trải nghiệm toàn bộ các tính năng của hệ thống Hỗ trợ ra quyết định dinh dưỡng **NutriDSS V2**.

---

## 1. YÊU CẦU MÔI TRƯỜNG HỆ THỐNG

* **Hệ điều hành:** Windows 10/11, macOS, hoặc Linux.
* **Phiên bản Python:** Python 3.10 hoặc Python 3.11.
* **Bộ nhớ RAM:** Tối thiểu 2 GB (Mô hình AI siêu nhẹ, chỉ chiếm ~150 MB RAM khi chạy).
* **Phần cứng GPU:** **Không yêu cầu GPU**. Toàn bộ mô hình đã được nén tối ưu sang định dạng ONNX Runtime, chạy mượt mà 100% trên CPU phổ thông.

---

## 2. CÀI ĐẶT THƯ VIỆN & PHỤ THUỘC

Mở cửa sổ dòng lệnh (Terminal / PowerShell) tại thư mục gốc của dự án (`d:\Dự Án Dss`) và thực thi lệnh:

```powershell
pip install -r requirements.txt
```

*Các thư viện trọng yếu bao gồm:*
* `fastapi` & `uvicorn`: Web framework API hiệu năng cao.
* `onnxruntime`: Động cơ suy luận mô hình AI Computer Vision siêu tốc.
* `pillow` & `numpy`: Xử lý hình ảnh tiền xử lý.
* `pandas` & `scikit-learn`: Xử lý dữ liệu bảng và mô hình GBDT ranker.
* `passlib` & `python-jose`: Bảo mật và mã hóa JWT.
* `pytest`: Bộ kiểm thử tự động toàn diện.

---

## 3. KIỂM TRA TỆP MÔ HÌNH VÀ CƠ SỞ DỮ LIỆU

Trước khi chạy, hãy đảm bảo các tệp quan trọng đã có mặt đầy đủ:
1. `models/vnfood_mobilenet_v3.onnx` (**Dung lượng: ~6.5 MB**) — Mô hình nhận diện 103 món ăn Việt Nam.
2. `database/nutridss.db` — Cơ sở dữ liệu SQLite chứa công thức, nguyên liệu và giá siêu thị.
3. `data/vnfood_103_labels.json` — Danh mục 103 nhãn món ăn chính quy.

*(Nếu muốn chạy lại bộ kiểm thử tự động để kiểm tra toàn bộ 23 chức năng, gõ:)*
```powershell
python -m pytest tests/
```
Kết quả hiển thị `23 passed` là hệ thống đã sẵn sàng 100%.

---

## 4. LỆNH KHỞI CHẠY ỨNG DỤNG

Khởi chạy máy chủ Backend FastAPI kết hợp phục vụ Giao diện người dùng:

```powershell
uvicorn backend.main:app --reload --port 8000
```

Khi màn hình xuất hiện thông báo:
```text
[FoodVisionService] Successfully loaded ONNX model: vnfood_mobilenet_v3.onnx
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Bạn hãy mở trình duyệt web (Chrome, Edge, Firefox) và truy cập vào đường dẫn:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 5. HƯỚNG DẪN TRẢI NGHIỆM CHI TIẾT 7 TABS TRÊN GIAO DIỆN

### 👤 Tab 1: Hồ Sơ Thể Trạng & Chỉ Số Sức Khỏe
1. Nhập chiều cao, cân nặng, độ tuổi, giới tính và mức độ vận động.
2. Chỉ số **BMI, BMR, TDEE** và **Mục tiêu năng lượng (Kcal), chất đạm (Protein)** được tính toán thời gian thực theo chuẩn WHO / Bộ Y Tế.
3. Tại ô **Dị ứng thực phẩm**: Gõ thử *"tôm"*, *"cá"* hoặc *"đậu phộng"* để thêm thẻ loại trừ. Toàn bộ thực đơn được sinh sau đó sẽ loại bỏ 100% các món gây dị ứng.
4. Bấm **[ Cập Nhật Hồ Sơ & Tính Toán Lại ]**.

### 🍚 Tab 2: Tạo Một Bữa Lẻ Chuẩn Việt (Single Meal)
1. Chọn bữa cần ăn: **Bữa Sáng**, **Bữa Trưa**, hoặc **Bữa Tối**.
2. Nhập ngân sách cho bữa ăn đó (ví dụ: `35000` VNĐ).
3. Chọn kiểu mâm cơm: *Tiêu chuẩn 3 món (1 cơm + 1 mặn + 1 canh)*, *Mâm gia đình 4 món*, hoặc *Eat-Clean*.
4. Bấm **[ TẠO MÂM CƠM KHỚP NGÂN SÁCH ]**. Hệ thống sẽ xuất hiện 3 phương án A, B, C kèm nút **`[ 💾 Lưu Mâm Cơm Này ]`**.

### 📅 Tab 3: Lập Thực Đơn Ngày & Đổi Món Tại Chỗ 🔄
1. Nhập ngân sách ăn uống cả ngày (ví dụ: `70000` VNĐ) và bấm **[ SINH 3 PHƯƠNG ÁN MÂM CƠM DSS ]**.
2. Hệ thống sinh 3 phương án: *Tiết kiệm nhất*, *Cân bằng khuyên dùng*, và *Giàu đạm*.
3. **Trải nghiệm nút tròn 🔄 đổi món tại chỗ:**
   * Trên mỗi món ăn (ví dụ món mặn hoặc món canh), bấm vào biểu tượng nút tròn **🔄**.
   * Một cửa sổ mở ra với danh sách các món thay thế có cùng vai trò, khớp ngân sách và calo.
   * Bấm **[ Chọn ]** để hoán đổi món ăn ngay lập tức mà không làm xáo trộn các món khác trên mâm cơm.
4. Bấm **`[ 💾 Lưu Thực Đơn ]`** để lưu toàn bộ mâm cơm vào cơ sở dữ liệu.

### 📋 Tab 4: Thực Đơn Đã Lưu Của Tôi
1. Danh sách các thực đơn bạn vừa lưu từ Tab 2 và Tab 3 sẽ xuất hiện đầy đủ tại đây.
2. **`[ 👁️ Xem Chi Tiết ]`**: Mở cửa sổ bóc tách toàn diện: từng món ăn, bảng nguyên liệu gam thật và đơn giá siêu thị, cùng các bước hướng dẫn nấu ăn chi tiết.
3. **`[ 🚀 Áp Dụng ]`**: Đánh dấu áp dụng thực đơn cho ngày hôm nay.
4. **`[ 🗑️ Xóa ]`**: Xóa thực đơn khỏi danh sách lưu trữ.

### 🔎 Tab 5: Tìm Món & Nhận Diện Ảnh AI (MobileNetV3 ONNX)
1. **Tìm kiếm bằng từ khóa:** Gõ tên món ăn (ví dụ *"bún bò"*, *"canh chua"*...) để gợi ý tức thì và phân tích nhanh dinh dưỡng & giá tiền.
2. **Nhận diện bằng hình ảnh AI:**
   * Kéo thả hoặc chọn một tệp ảnh đĩa thức ăn từ máy tính/điện thoại.
   * Bấm nút **[ 📸 NHẬN DIỆN MÓN ĂN VỚI AI ]**.
   * Mô hình AI MobileNetV3 6.5MB sẽ nhận diện món ăn trong ~0.03 giây, hiển thị tên món, độ tin cậy %, bảng Calo/Protein/Béo/Carb và chi phí ước tính từ siêu thị.
   * Bấm **[ Xem Công Thức Chi Tiết ]** để xem cách chế biến.

### 👨‍🍳 Tab 6: Sổ Tay Công Thức & Cách Nấu
1. Tra cứu thư viện các món ăn gia đình Việt Nam.
2. Lọc nhanh theo vai trò: *Món mặn chính, Món canh/rau, Tinh bột, Điểm tâm sáng, Món chay*.
3. Bấm vào bất kỳ món ăn nào để xem **Bảng bóc tách chi phí siêu thị minh bạch** (từng gam thịt, thìa mắm, tép tỏi theo giá WinMart, GO!, AEON) và các bước nấu ăn (Step-by-step).

### 🛒 Tab 7: Bảng Giá Siêu Thị & Dinh Dưỡng
1. Tra cứu bảng thực phẩm hạt nhân, giá tham chiếu thị trường (Median) và hàm lượng 30+ vi chất dinh dưỡng.
2. Xem bảng quy chuẩn khẩu phần tương đương theo khuyến nghị của Viện Dinh Dưỡng Quốc Gia.

---

## 6. TÀI LIỆU API CHO LẬP TRÌNH VIÊN (SWAGGER UI)

Hệ thống cung cấp sẵn trang tài liệu kiểm thử API trực quan chuẩn OpenAPI:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

Tại đây bạn có thể kiểm tra trực tiếp 31 endpoints bao gồm:
* `POST /api/profile/calculate`: Tính BMI, BMR, TDEE.
* `POST /api/meal-plans/single-meal`: Tạo 1 bữa lẻ.
* `POST /api/meal-plans/generate`: Lập thực đơn 3 phương án A/B/C.
* `POST /api/meal-plans/replace-item`: Đổi món thông minh.
* `POST /api/meal-plans/save`: Lưu thực đơn vào CSDL.
* `GET /api/meal-plans`: Lấy danh sách thực đơn đã lưu.
* `POST /api/vision/predict-food`: Nhận diện ảnh món ăn bằng MobileNetV3 ONNX.
* `GET /api/recipes/{id}`: Xem chi tiết công thức và bóc tách chi phí siêu thị.
