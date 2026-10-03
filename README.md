# NutriDSS - Decision Support System for Personalized Nutrition & Meal Planning

NutriDSS là Hệ hỗ trợ ra quyết định (Decision Support System - DSS) cá nhân hóa thực đơn dinh dưỡng và ngân sách, kết hợp:

1. **Rule-Based Engine (Ràng buộc y tế nghiêm ngặt):**
   - Loại trừ 100% nguyên liệu dị ứng (Hard Constraints). Từ chối nghiêm ngặt bất kỳ mã dị ứng lạ hoặc chưa kiểm chứng để bảo vệ tính mạng người dùng.
   - Kiểm tra tính khả thi của ngân sách (Budget Hard Constraints). Tự động cảnh báo khi ngân sách không đủ chi trả cho 3 bữa ăn tối thiểu.
   - Cảnh báo sức khỏe theo khuyến nghị của Tổ chức Y tế Thế giới (WHO) về Natri, đường tự do, chất béo bão hòa và năng lượng bữa ăn.
2. **Machine Learning Ranking Engine:**
   - So sánh đa mô hình hồi quy (Linear Regression, KNN, Decision Tree, Random Forest, MLPRegressor) so với baseline DummyRegressor.
   - Đánh giá chéo 5-Fold Cross Validation với độ chính xác cao ($R^2 > 0.91$).
   - Tối ưu hóa đa mục tiêu: calo mục tiêu cá nhân, tỷ lệ đạm và chi phí kinh tế.
3. **Smart Replacement & Custom Food Evaluator:**
   - Đổi món thông minh giữ cân bằng calo, đạm và kiểm soát ngân sách còn lại.
   - Đánh giá món ăn tự chọn, phân tích tỷ trọng calo/ngân sách ngày, phòng chống lỗi chia cho 0 và phòng thủ XSS phía frontend.

---

## 🚀 Hướng Dẫn Clone & Khởi Chạy Nhanh

> 📖 **Xem hướng dẫn chi tiết từng bước:** [HUONG_DAN_CLONE_VA_CAI_DAT.md](file:///d:/D%E1%BB%B1%20%C3%81n%20Dss/HUONG_DAN_CLONE_VA_CAI_DAT.md)

### 1. Clone mã nguồn về máy
```bash
git clone https://github.com/dieuiuquinbel/DieuDss.git
cd DieuDss
```

### 2. Thiết lập môi trường ảo & Cài đặt thư viện (Python 3.10+)
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### 3. Khởi tạo Cơ sở Dữ liệu NutriDSS V3 (Pipeline duy nhất)
```bash
python -m database.build
```

### 4. Chạy Kiểm Thử Tự Động (Toàn bộ 30 Tests)
```bash
python -m pytest tests/ -v
```

### 5. Khởi chạy Web Server
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Truy cập giao diện: 👉 **`http://127.0.0.1:8000/static/index.html`**

---

## 📁 Cấu Trúc Dự Án

NutriDSS/
├── backend/
│ ├── main.py # FastAPI server & route handlers
│ ├── schemas/dss_schemas.py # Pydantic schemas với strict validation
│ └── services/
│ ├── nutrition_service.py # BMI, BMR, TDEE, Macro targets & Medical advice
│ ├── rule_engine.py # Allergy filtering & WHO health warnings
│ ├── recommender_service.py # ML ranking pipeline & recipe pricing
│ └── meal_optimizer.py # 3 options generator, replacement & evaluator
├── data/
│ ├── generate_datasets.py # Sinh dữ liệu dinh dưỡng, giá siêu thị & khảo sát
│ └── processed/ # CSV datasets chuẩn hóa
├── database/
│ ├── schema.sql # Cấu trúc CSDL SQLite
│ └── seed.py # Nạp dữ liệu vào SQLite nutridss.db
├── frontend/
│ └── index.html # Giao diện tương tác DSS (XSS-safe)
├── models/
│ ├── train_ml_models.py # Pipeline huấn luyện 5 ML model + baseline
│ ├── best_recipe_ranker.joblib # Best model artifact
│ └── model_metadata.json # Metadata phiên bản & metrics của mô hình
├── tests/
│ └── test_nutridss_pipeline.py # Bộ kiểm thử tự động toàn diện
└── README.md
