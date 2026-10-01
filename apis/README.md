# APIs

Thư mục này chỉ chứa client gọi các nguồn dữ liệu bên ngoài đã được phê duyệt trong đặc tả MVP. Dữ liệu trả về vẫn là dữ liệu thô; các bước mapping sang tên thực phẩm tiếng Việt, chuẩn hóa đơn vị và kiểm tra chất lượng thực hiện ở `src/` hoặc Notebook.

| File | Nguồn | Mục đích |
|---|---|---|
| `usda_fooddata_client.py` | [USDA FoodData Central](https://fdc.nal.usda.gov/api-guide/) | tìm và lấy chi tiết dữ liệu dinh dưỡng bổ sung |
| `themealdb_client.py` | [TheMealDB](https://www.themealdb.com/api.php) | tìm món và lấy metadata công thức |
| `base_client.py` | dùng chung | JSON HTTP, timeout và lỗi truy vấn |

## Cách dùng

Đặt `USDA_FDC_API_KEY` trong biến môi trường trước khi gọi USDA. Không ghi key vào file mã nguồn, notebook hoặc Git. TheMealDB trong MVP sử dụng test key công khai của API cho mục đích học tập; khi đưa sản phẩm lên môi trường công khai, cần dùng key phù hợp theo điều kiện của TheMealDB.

```python
from apis.themealdb_client import search_meals
from apis.usda_fooddata_client import search_foods

meals = search_meals("chicken")
foods = search_foods("chicken breast")
```

Client hiện không tự động retry hay lưu cache. Chỉ bổ sung hai cơ chế này khi đã có yêu cầu cập nhật định kỳ ở giai đoạn mở rộng; fixture/offline dataset vẫn là đường chạy mặc định cho Notebook và demo.

## Khi thêm nguồn giá

Tạo `price_catalog_client.py` chỉ khi nguồn đó có API hoặc điều khoản cho phép thu thập tự động. Client phải trả về tối thiểu các trường sau trước khi pipeline được phép lưu vào `data/raw/`:

```text
product_name_raw, price_vnd, quantity, unit, promotion_flag,
source, source_url, collected_at
```

Không thêm client để vượt CAPTCHA, yêu cầu đăng nhập, giới hạn request hoặc điều khoản sử dụng của nguồn.
