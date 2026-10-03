# HƯỚNG DẪN CLONE VÀ KHỞI CHẠY DỰ ÁN NUTRIDSS

Tài liệu này hướng dẫn chi tiết từng bước dành cho người dùng mới, cộng sự hoặc giảng viên để tải dự án từ GitHub về máy và khởi chạy thành công 100%.

---

## 📋 YÊU CẦU TIỀN ĐỀ TRÊN MÁY

1. **Git**: Đã cài đặt Git ([Tải tại git-scm.com](https://git-scm.com/)).
2. **Python**: Phiên bản **3.10** hoặc **3.11** ([Tải tại python.org](https://www.python.org/)).
   *(Lưu ý: Khi cài Python trên Windows, hãy tích chọn mục **"Add Python to PATH"**)*.

---

## 🚀 CÁC BƯỚC THỰC HIỆN TỪNG BƯỚC

### BƯỚC 1: Clone kho mã nguồn về máy

Mở **Terminal** (PowerShell, CMD trên Windows hoặc Terminal trên macOS/Linux) tại thư mục bạn muốn lưu dự án, sau đó chạy lệnh:

```bash
git clone https://github.com/dieuiuquinbel/DieuDss.git
```

Sau khi clone xong, chuyển vào thư mục dự án:

```bash
cd DieuDss
```

---

### BƯỚC 2: Tạo môi trường ảo (Virtual Environment) & Kích hoạt

Việc sử dụng môi trường ảo giúp cách ly thư viện, tránh xung đột phiên bản với hệ thống:

- **Trên Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(Nếu gặp lỗi script execution policy trên PowerShell, chạy lệnh: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` rồi kích hoạt lại)*.

- **Trên Windows (Command Prompt - CMD):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```

- **Trên macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

*(Khi kích hoạt thành công, bạn sẽ thấy tiền tố `(venv)` xuất hiện ở đầu dòng lệnh).*

---

### BƯỚC 3: Cài đặt các thư viện phụ thuộc

Cài đặt đầy đủ các gói cần thiết (FastAPI, Uvicorn, Pandas, Scikit-learn, ONNX Runtime, Pytest...):

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### BƯỚC 4: Khởi tạo Cơ sở dữ liệu NutriDSS V3

Dự án sử dụng một build pipeline tự động duy nhất để tạo cấu trúc bảng, nạp 30+ chỉ số dinh dưỡng WHO, 63 công thức nấu ăn mâm cơm Việt Nam và dữ liệu giá siêu thị thực (WinMart, GO!, AEON):

```bash
python -m database.build
```

**Kết quả thành công sẽ hiển thị:**
```text
============================================================
🚀 NUTRIDSS DATABASE BUILD PIPELINE V3
============================================================
...
[SUCCESS] All required tables and columns are strictly valid according to NutriDSS V3 Contract.
✅ NUTRIDSS DATABASE IS 100% READY AND VERIFIED!
```

---

### BƯỚC 5: Kiểm tra tính toàn vẹn hệ thống (Chạy Tests)

Trước khi khởi động web, bạn có thể chạy bộ kiểm thử tự động để xác nhận toàn bộ 30 test case đều vượt qua:

```bash
python -m pytest tests/ -v
```

Kết quả mong đợi: **`30 passed`** (100% thành công).

---

### BƯỚC 6: Khởi chạy Web Server NutriDSS

Khởi động máy chủ backend FastAPI:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Khi server khởi động thành công, terminal sẽ hiển thị:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

### BƯỚC 7: Mở giao diện ứng dụng trên trình duyệt

Mở trình duyệt web bất kỳ (Chrome, Edge, Cốc Cốc, Firefox) và truy cập vào địa chỉ:

👉 **[http://127.0.0.1:8000/static/index.html](http://127.0.0.1:8000/static/index.html)**

Hoặc trang tài liệu API tương tác Swagger:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🔑 TÀI KHOẢN ĐĂNG NHẬP MẪU (NẾU CẦN)

Hệ thống có sẵn tài khoản demo phục vụ trải nghiệm:
- **Tài khoản người dùng:**
  - Tên đăng nhập: `demouser`
  - Mật khẩu: `DemoUser@123`
- **Tài khoản quản trị:**
  - Tên đăng nhập: `admin`
  - Mật khẩu: `NutriDSS@2026`

*(Bạn cũng có thể tự đăng ký một tài khoản mới bất kỳ ngay trên giao diện web).*

---

## 🛠 XỬ LÝ LỖI PHỔ BIẾN (TROUBLESHOOTING)

1. **Lỗi `python: command not found`**:
   - Máy chưa cài Python hoặc chưa tích chọn "Add Python to PATH" lúc cài đặt.
2. **Lỗi cổng 8000 đã bị chiếm dụng (`Address already in use`)**:
   - Bạn có thể đổi sang cổng khác khi chạy uvicorn:
     ```bash
     uvicorn backend.main:app --reload --port 8080
     ```
     Sau đó truy cập: `http://127.0.0.1:8080/static/index.html`.
