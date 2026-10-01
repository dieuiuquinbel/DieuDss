# NutriDSS — Đặc tả phần bắt buộc và MVP

# 1. TẦM NHÌN DỰ ÁN

NutriDSS là hệ hỗ trợ quyết định giúp người dùng trả lời một câu hỏi rất thực tế:

> **“Với mục tiêu dinh dưỡng của tôi, số tiền tôi muốn chi cho ăn uống, khẩu vị và các ràng buộc cá nhân hiện tại, hôm nay/tuần này/tháng này tôi có thể ăn gì?”**

Hệ thống phải hỗ trợ đồng thời nhiều kiểu sử dụng:

1. Người dùng muốn hệ thống tự đề xuất một bữa ăn.
2. Người dùng muốn hệ thống tự tạo thực đơn cả ngày.
3. Người dùng muốn tạo thực đơn theo tuần.
4. Người dùng muốn chuẩn bị thực đơn theo tháng.
5. Người dùng nhập một khoản tiền cụ thể và muốn xem trong phạm vi đó có thể ăn món gì.
6. Người dùng nhập món ăn mình đang muốn ăn để hệ thống đánh giá xem món đó phù hợp thế nào với mục tiêu đã chọn.
7. Người dùng không thích món được đề xuất và bấm **Đổi món** để nhận phương án khác.
8. Người dùng muốn tự nấu món ăn và xem hướng dẫn chế biến.
9. Người dùng muốn biết một món ăn hoặc cả thực đơn có quá nhiều calories, đường, chất béo, sodium... hay không.
10. Người dùng muốn đưa một món bất kỳ vào thực đơn của riêng mình rồi để hệ thống **đánh giá và tư vấn**, thay vì bắt buộc sử dụng thực đơn do AI sinh ra.

---

---

# 2. TRIẾT LÝ SẢN PHẨM

## 2.1. Không phải “AI quyết định thay người dùng”

NutriDSS là **Decision Support System**, không phải hệ thống ép người dùng ăn một món.

Luồng chính:

```text
Thông tin người dùng
        ↓
Phân tích nhu cầu
        ↓
Phân tích ngân sách
        ↓
Lọc ràng buộc
        ↓
Machine Learning / Scoring
        ↓
Danh sách đề xuất
        ↓
NGƯỜI DÙNG CHỌN
        ↓
Đổi món / chỉnh khẩu phần / thêm món
        ↓
Hệ thống đánh giá lại
```

Người dùng luôn có thể:

- chọn;
- bỏ qua;
- đổi món;
- thay khẩu phần;
- tìm món khác;
- tự thêm món;
- chỉnh thực đơn.

---

---

# 3. CƠ SỞ DINH DƯỠNG

WHO hiện xác định bốn nguyên tắc cốt lõi của chế độ ăn lành mạnh:

- **Đầy đủ (adequacy)**
- **Cân bằng (balance)**
- **Điều độ (moderation)**
- **Đa dạng (diversity)**

WHO cũng nêu rằng thành phần chế độ ăn phù hợp thay đổi theo đặc điểm cá nhân, mức độ vận động, bối cảnh văn hóa, thực phẩm sẵn có và thói quen ăn uống.

Nguồn:
https://www.who.int/news-room/fact-sheets/detail/healthy-diet

WHO cập nhật trang này ngày 26/01/2026 và nhấn mạnh thêm rằng chế độ ăn lành mạnh phải an toàn, hạn chế các yếu tố như chất béo không lành mạnh, đường tự do và sodium quá mức; thành phần cụ thể vẫn cần thay đổi theo cá nhân.  

**NutriDSS chỉ sử dụng các nguyên tắc trên làm cơ sở thiết kế hệ thống hỗ trợ dinh dưỡng, không thay thế tư vấn y khoa.**

---

---

# 4. PHẠM VI SỨC KHỎE MÀ NGƯỜI DÙNG CÓ THỂ CHỌN

## 4.1. Mục tiêu chính

Người dùng có thể chọn một hoặc nhiều mục tiêu:

### Mục tiêu cân nặng

- Giảm cân.
- Duy trì cân nặng.
- Tăng cân.

### Mục tiêu dinh dưỡng/lối sống

- Tăng cường protein.
- Cân bằng dinh dưỡng.
- Ăn uống đa dạng hơn.
- Kiểm soát năng lượng.
- Ưu tiên thực phẩm ít đường.
- Ưu tiên thực phẩm ít chất béo.
- Ưu tiên thực phẩm giàu chất xơ.

### Mục tiêu tăng trưởng

Có thể có lựa chọn:

> **Hỗ trợ dinh dưỡng cho tăng trưởng/chiều cao**

Nhưng hệ thống **không được tuyên bố rằng một món ăn hoặc thực đơn sẽ làm người dùng cao lên một cách chắc chắn**.

Logic nên là:

```text
Mục tiêu:
"Hỗ trợ tăng trưởng"
       ↓
Ưu tiên:
Protein
Canxi
Vitamin D
Vi chất phù hợp
Đủ năng lượng
Đa dạng thực phẩm
       ↓
Khuyến nghị chế độ ăn
```

Đối với trẻ em, người chưa trưởng thành hoặc trường hợp có bệnh lý, hệ thống nên hiển thị cảnh báo và khuyến nghị tham khảo chuyên gia phù hợp.

---

---

# 5. KHÔNG GIAN QUYẾT ĐỊNH CỦA HỆ THỐNG

NutriDSS có 3 loại quyết định chính.

## 5.1. QUYẾT ĐỊNH “ĂN GÌ?”

Ví dụ:

```text
Ngân sách: 50.000đ
Mục tiêu: giảm cân
Sở thích: thịt gà, trứng, rau
Không thích: cá
```

Hệ thống trả:

```text
1. Cơm gạo lứt + ức gà + rau
2. Trứng + khoai lang + rau
3. Cơm + thịt gà + bông cải
4. Đậu phụ + trứng + rau
```

## 5.2. QUYẾT ĐỊNH “ĂN BAO NHIÊU?”

Người dùng có thể đổi:

```text
100g → 150g → 200g
```

Hệ thống tính lại:

- calories;
- protein;
- carbohydrate;
- fat;
- giá;
- tổng thực đơn.

## 5.3. QUYẾT ĐỊNH “MÓN NÀY CÓ PHÙ HỢP KHÔNG?”

Ví dụ người dùng tự nhập:

> “Trà sữa trân châu”

Hệ thống không nhất thiết loại bỏ món này. Hệ thống đánh giá:

```text
Calories: cao
Đường: cao
Protein: thấp

→ Nếu mục tiêu giảm cân:
   nên xem như món giới hạn/treat,
   cân nhắc khẩu phần hoặc tần suất.

→ Nếu người dùng vẫn muốn dùng:
   có thể đưa vào thực đơn,
   hệ thống cân đối các bữa còn lại.
```

Đây chính là chức năng **hỗ trợ quyết định**, không phải ép buộc.

---

---

# 6. NGÂN SÁCH — TẬP TRUNG ĐÚNG PHẠM VI

## 6.1. Không xây hệ quản lý tài chính cá nhân

KHÔNG đưa vào phạm vi:

- thu nhập;
- tiền nhà;
- tiền điện;
- tiền vay;
- tiền tiết kiệm;
- đầu tư;
- tài khoản ngân hàng;
- quản lý tài chính cá nhân.

Đây không phải lĩnh vực chính của đề tài.

## 6.2. Chỉ cần một biến rất quan trọng

> **Số tiền dự kiến chi cho thực phẩm/bữa ăn/thời gian lập kế hoạch.**

Người dùng có thể nhập:

```text
Ngân sách một bữa:       30.000đ
Ngân sách một ngày:      70.000đ
Ngân sách một tuần:     500.000đ
Ngân sách một tháng:  2.500.000đ
```

Hệ thống tự quy đổi và phân bổ.

---

---

# 7. KIỂU NGÂN SÁCH

Có thể hỗ trợ 4 cấp:

```text
MEAL
DAY
WEEK
MONTH
```

## 7.1. Một bữa

```text
Budget = 30.000đ
```

Hệ thống chỉ đề xuất một bữa.

## 7.2. Một ngày

```text
Budget = 70.000đ/ngày
```

Hệ thống chia:

- sáng;
- trưa;
- tối;
- snack nếu cần.

## 7.3. Một tuần

```text
Budget = 500.000đ
```

Hệ thống tạo tối đa 7 ngày.

## 7.4. Một tháng

```text
Budget = 2.500.000đ
```

Hệ thống tạo kế hoạch theo ngày/tuần và tổng hợp chi phí.

---

---

# 8. GIÁ THỰC PHẨM

## 8.1. Quan điểm dữ liệu

Giá thực phẩm là:

> **dữ liệu biến động theo thời gian**

Không được coi:

```text
Thịt gà = 90.000đ/kg
```

là giá cố định.

Phải có:

```text
food
store
location
package
price
collected_at
promotion
source
```

## 8.2. Giá để lập thực đơn

Hệ thống nên tính:

- giá thấp;
- giá trung vị;
- giá cao;
- thời điểm cập nhật;
- độ tin cậy.

Trong MVP:

> **Dùng giá trung vị từ các quan sát giá gần đây để lập thực đơn.**

Ví dụ:

```text
Thịt gà
80.000 ─ 92.000 ─ 105.000đ/kg

Giá dùng cho planner:
92.000đ/kg
```

Giao diện có thể hiển thị:

> Giá ước tính: 85.000–100.000đ/kg  
> Giá tính toán: 92.000đ/kg  
> Cập nhật: 30/09/2026

---

---

# 9. NGUỒN GIÁ SIÊU THỊ

## 9.1. AEON ESHOP

AEON ESHOP hiện có dữ liệu sản phẩm thực phẩm và giá trên các trang sản phẩm/danh mục.

Nguồn:
https://aeoneshop.com/

Ví dụ kết quả thực tế có hiển thị giá sản phẩm và quy cách, cho phép chuẩn hóa thành giá/kg hoặc giá/100g. 

## 9.2. GO! Vietnam

Có thể khai thác các nội dung giá/khuyến mại công khai trên kênh GO! Việt Nam khi điều kiện truy cập cho phép.

Nguồn:
https://go-vietnam.vn/

GO! cũng công bố các tài liệu/catalog khuyến mại có sản phẩm, quy cách và giá theo thời gian. Ví dụ các flyer năm 2026 có giá theo kg/gói/sản phẩm và khoảng thời gian áp dụng.  

## 9.3. Nguồn mở rộng

Sau MVP có thể bổ sung:

- WinMart;
- Lotte Mart;
- Bách Hóa XANH;
- Tops Market;
- các nguồn bán lẻ phù hợp khác.

## 9.4. Quy tắc scraping

AI Agent không được mặc định rằng website nào cũng được phép crawl.

Ưu tiên:

1. API chính thức.
2. Dataset công khai.
3. Catalog/flyer công khai.
4. Web scraping nếu Terms/robots/điều kiện truy cập cho phép.
5. Nhập thủ công cho dữ liệu khó lấy tự động.

Không vượt:

- CAPTCHA;
- authentication;
- rate limit;
- anti-bot;
- nội dung riêng tư.

Crawler cần:

- timeout;
- retry;
- delay;
- cache;
- request limit;
- User-Agent;
- log lỗi.

---

---

# 10. QUY TẮC “THỰC PHẨM CHUẨN”

Đây là quy tắc cốt lõi.

Hệ thống KHÔNG tạo ra hàng trăm thực phẩm khác nhau chỉ vì tên thương mại khác nhau.

Ví dụ:

```text
Ức gà thương hiệu A 500g
Ức gà thương hiệu B 400g
Ức gà hữu cơ C 300g
Ức gà premium D
```

đều phải được quy về:

```text
ỨC GÀ
```

nếu chúng thuộc cùng loại thực phẩm phù hợp với phạm vi thực đơn phổ thông.

## 10.1. Ví dụ taxonomy

```text
THỊT GIA CẦM
├── Thịt gà
└── Ức gà

THỊT LỢN
├── Thịt lợn
└── Thịt lợn nạc

THỊT BÒ
└── Thịt bò

CÁ
├── Cá rô phi
├── Cá thu
└── Cá hồi

TRỨNG
└── Trứng gà

TINH BỘT
├── Gạo trắng
├── Gạo lứt
├── Khoai lang
└── Khoai tây

RAU
├── Rau muống
├── Cải xanh
├── Cà rốt
└── Bông cải xanh

TRÁI CÂY
├── Chuối
├── Táo
├── Cam
└── Dưa hấu
```

Không cần phân biệt các biến thể thương mại không cần thiết cho mục tiêu meal planning.

---

---

# 11. CHUẨN HÓA TÊN SANG TIẾNG VIỆT

Tất cả dữ liệu bên ngoài phải được đưa về:

> **Tên thực phẩm chuẩn bằng tiếng Việt.**

Ví dụ:

| Tên nguồn | Tên chuẩn |
|---|---|
| Chicken | Thịt gà |
| Chicken meat | Thịt gà |
| Fresh chicken | Thịt gà |
| Chicken breast | Ức gà |
| Pork | Thịt lợn |
| Lean pork | Thịt lợn nạc |
| Beef | Thịt bò |
| Egg | Trứng gà |
| Rice | Gạo trắng |
| Brown rice | Gạo lứt |
| Sweet potato | Khoai lang |

Bảng mapping:

```text
food_aliases
------------
alias_id
food_id
alias_raw
normalized_name
source
```

Pipeline:

```text
Tên raw
  ↓
lowercase
  ↓
trim
  ↓
remove punctuation
  ↓
mapping dictionary
  ↓
fuzzy matching nếu cần
  ↓
Tên tiếng Việt chuẩn
  ↓
food_id
```

Không tự động merge khi độ tin cậy thấp.

Các trường hợp nghi ngờ:

```text
review_queue
```

để Admin kiểm tra.

## 11.1. Tiêu chí mapping

Alias được chuẩn hóa theo thứ tự: chữ thường → bỏ khoảng trắng/ký tự thừa → bỏ thông tin đóng gói → từ điển alias → fuzzy match. Chỉ tự động ghép khi điểm tin cậy đạt ngưỡng công bố, ví dụ `>= 0.90`; các bản ghi còn lại phải đi vào `review_queue.csv` kèm tên nguồn và lý do cần duyệt.

Không gộp “Ức gà” thành “Thịt gà” hoặc gộp các thực phẩm có phần ăn/chế biến khác nhau nếu nguồn không xác nhận tương đương. Mỗi lần mapping cần lưu `food_id`, `mapping_method`, `confidence`, `source` và `reviewed_at`.

---

---

# 12. DỮ LIỆU DINH DƯỠNG

## 12.1. Nguồn chính

### Bảng thành phần thực phẩm Việt Nam / Viện Dinh dưỡng

https://chuyentrang.viendinhduong.vn/viewfilenew/vi/thu-vien-sach-chuyen-nganh/189/1.html

Có thể dùng làm nguồn lõi cho thực phẩm Việt Nam.

### FAO/INFOODS

https://www.fao.org/food-composition/tables-and-databases/16/en

Dùng để tham khảo các bảng thành phần thực phẩm và metadata liên quan.

### USDA FoodData Central

https://fdc.nal.usda.gov/

https://fdc.nal.usda.gov/download-datasets/

https://fdc.nal.usda.gov/api-guide/

Dùng để:

- bổ sung;
- đối chiếu;
- tăng độ phủ thực phẩm;
- lấy nutrition qua API/CSV.

### Open Food Facts

https://openfoodfacts.github.io/documentation/

https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/

API v3 hiện là phiên bản được tài liệu chính thức khuyến nghị cho tích hợp mới.

### ANSES-CIQUAL

https://ciqual.anses.fr/cms/en/2025-anses-ciqual-table

Dùng bổ sung/đối chiếu dữ liệu thành phần.

## 12.2. Danh mục nguồn và dataset triển khai

| Loại dữ liệu | Nguồn ưu tiên | Cách dùng |
|---|---|---|
| Dinh dưỡng Việt Nam | Bảng thành phần thực phẩm Việt Nam của Viện Dinh dưỡng | nguồn lõi cho thực phẩm phổ biến tại Việt Nam |
| Dinh dưỡng bổ sung | USDA FoodData Central API/CSV | chỉ bổ sung thực phẩm thiếu; lưu `fdc_id`, URL và dataset version |
| Công thức | TheMealDB API hoặc dataset có license rõ ràng | lấy metadata/nguyên liệu rồi mapping về food master tiếng Việt |
| Thực phẩm đóng gói | Open Food Facts API | nguồn bổ sung có kiểm tra dữ liệu thiếu/không nhất quán |
| Giá | API, catalog công khai được phép hoặc nhập tay có kiểm soát | lưu quy cách, URL, ngày thu thập và cờ khuyến mãi |

Dataset tối thiểu cho lần chạy đầu gồm 80–150 thực phẩm chuẩn, 40–80 công thức/bữa ăn có định lượng và ít nhất hai quan sát giá hợp lệ cho thực phẩm chính. Bản ghi không xác định được khối lượng không được dùng để tính giá/kg hoặc giá/100 g.

---

---

# 13. DỮ LIỆU CÔNG THỨC NẤU ĂN

Người dùng có nhu cầu:

> “Tôi đã chọn món này, hướng dẫn tôi cách nấu.”

Do đó hệ thống cần Recipe Repository.

## 13.1. TheMealDB

https://www.themealdb.com/api.php

Có API tìm món theo tên, xem chi tiết món, nguyên liệu, hướng dẫn và một số bộ lọc.

API công khai hiện có endpoint tìm kiếm món và lookup chi tiết món; API cũng có điều kiện khác nhau giữa truy cập miễn phí và sản phẩm thương mại. 

## 13.2. Cookpad Việt Nam

https://cookpad.com/vn/

Cookpad hỗ trợ tìm công thức theo tên món hoặc nguyên liệu, phù hợp làm nguồn tham khảo/tìm kiếm công thức.

Tuy nhiên:

> **Không mặc định sao chép toàn bộ nội dung công thức/ảnh từ Cookpad hoặc website bên thứ ba vào database.**

Chỉ sử dụng scraping nếu điều khoản và phương thức truy cập cho phép. Nếu không, lưu:

- tên món;
- source;
- source_url;
- metadata cần thiết;

và dẫn người dùng tới nguồn gốc.

## 13.3. Dataset recipe

Có thể bổ sung:

- RecipeNLG;
- Food.com dataset;
- các dataset recipe có license rõ ràng.

---

---

# 14. RECIPE PIPELINE

```text
Recipe API / Dataset / Public Website
              ↓
          Raw Recipe
              ↓
      Ingredient Parser
              ↓
      Vietnamese Mapping
              ↓
      Food Master Matching
              ↓
       Nutrition Mapping
              ↓
          Recipe DB
```

Ví dụ:

```text
Recipe:
Chicken Rice Bowl

Ingredients:
Chicken breast
Rice
Carrot

             ↓

Canonical:
Ức gà
Gạo trắng
Cà rốt
```

Sau đó lấy nutrition và giá từ Food Master.

---

---

# 15. HƯỚNG DẪN NẤU ĂN

Mỗi recipe nên có:

```text
recipe_id
name_vi
description
servings
prep_time
cook_time
difficulty
source
source_url
```

Và:

```text
recipe_steps
------------
recipe_id
step_no
instruction
```

Nếu source/license không cho phép lưu full instructions:

```text
source_url
```

được lưu để người dùng bấm:

> **Xem hướng dẫn gốc**

Nếu source cho phép lưu và phân phối nội dung, có thể lưu nội dung theo điều kiện license.

---

---

# 16. TÍNH DINH DƯỠNG CỦA MÓN

Ví dụ:

```text
Ức gà 200g
Gạo lứt 100g
Cà rốt 80g
Dầu ăn 10g
```

Công thức:

```text
Nutrient_recipe =
Σ(quantity_g / 100 × nutrient_per_100g)
```

Tính cho:

- calories;
- protein;
- carbohydrate;
- fat;
- fiber;
- sugar;
- sodium;
- nutrient khác nếu có dữ liệu.

Sau đó:

```text
Nutrition_per_serving =
Nutrition_total / servings
```

---

---

# 17. TÍNH GIÁ MÓN ĂN

```text
Cost_recipe =
Σ(quantity_i × normalized_price_i)
```

Nếu:

```text
Ức gà = 92.000đ/kg
```

thì:

```text
200g = 18.400đ
```

Tương tự với các nguyên liệu khác.

Từ đó:

```text
Recipe Cost
+
Preparation
+
Serving Size
        ↓
Meal Cost
```

---

---

# 18. LẬP THỰC ĐƠN

Hệ thống phải hỗ trợ:

```text
Một món
↓
Một bữa
↓
Một ngày
↓
Một tuần
↓
Một tháng
```

## 18.1. Một món

Người dùng chọn:

```text
Ức gà áp chảo
```

hệ thống đánh giá:

- calories;
- protein;
- fat;
- cost;
- target compatibility.

## 18.2. Một bữa

Ví dụ:

```text
Ức gà
+
Cơm
+
Rau
```

Tính tổng:

```text
Calories
Protein
Carb
Fat
Cost
```

## 18.3. Một ngày

```text
Breakfast
Lunch
Dinner
Snack optional
```

## 18.4. Một tuần

7 ngày.

## 18.5. Một tháng

Tạo kế hoạch theo tuần rồi tổng hợp thành lịch tháng.

Không nhất thiết sinh 30 ngày hoàn toàn khác nhau. Có thể lặp có kiểm soát để giảm độ phức tạp và phù hợp thực tế.

---

---

# 19. KHẨU PHẦN ĂN

Người dùng phải có thể điều chỉnh:

```text
0.5 serving
1 serving
1.5 serving
2 serving
```

hoặc:

```text
100g
150g
200g
250g
```

Hệ thống tính lại ngay:

```text
Calories
Protein
Cost
```

Ví dụ:

```text
Ức gà 100g
165 kcal
31g protein
9.200đ

Ức gà 200g
330 kcal
62g protein
18.400đ
```

---

---

# 20. TÍNH NĂNG “ĐỔI MÓN”

Đây là chức năng trọng tâm.

Người dùng thấy:

```text
Trưa:
Cơm + ức gà + rau

[ Đổi món ]
```

Bấm đổi món.

Hệ thống:

```text
Giữ:
- calories gần tương đương
- protein gần tương đương
- budget còn lại
- allergy
- preferences

Thay:
- món chính
```

Ví dụ:

```text
Ức gà áp chảo
        ↓
Thịt lợn nạc luộc
        ↓
Cá rô phi
```

Không tạo lại toàn bộ ngày nếu chỉ cần đổi một món.

---

---

# 21. NGƯỜI DÙNG TỰ CHỌN MÓN

Đây là chức năng bắt buộc.

Ví dụ người dùng tìm:

> “Phở bò”

Sau đó:

```text
[ Thêm vào thực đơn ]
```

Hệ thống phải:

```text
Món mới
 ↓
Nutrition analysis
 ↓
Cost estimate
 ↓
Target comparison
 ↓
Current plan impact
```

Ví dụ:

```text
THÊM PHỞ BÒ

Calories: 550 kcal
Protein: 28g
Fat: 18g
Cost: 45.000đ

Ảnh hưởng hôm nay:
Calories: +550
Budget: +45.000đ
```

---

---

# 22. ĐÁNH GIÁ MÓN NGƯỜI DÙNG TỰ CHỌN

Kết quả phải phân biệt:

```text
Good
Acceptable
Needs moderation
Not suitable under current constraints
```

Không nên dùng ngôn ngữ tuyệt đối kiểu:

> “Món này độc hại.”

Nên hiển thị:

```text
- Năng lượng khá cao.
- Hàm lượng chất béo cao.
- Nếu mục tiêu là giảm cân, nên cân nhắc khẩu phần.
- Nếu vẫn muốn ăn, hệ thống có thể giảm năng lượng ở các bữa khác.
```

---

---

# 23. RULE ENGINE CHO TƯ VẤN

## 23.1. Calories

Nếu:

```text
meal_calories > target_meal_calories × threshold
```

thì:

```text
warning:
"Khẩu phần này cung cấp năng lượng cao hơn mức dự kiến cho bữa hiện tại."
```

## 23.2. Đường

Nếu lượng đường cao:

```text
"Đây là món có lượng đường cao; nếu mục tiêu của bạn là kiểm soát cân nặng hoặc giảm lượng đường, nên cân nhắc khẩu phần/tần suất."
```

## 23.3. Chất béo

Nếu fat cao:

```text
"Khẩu phần này có hàm lượng chất béo tương đối cao. Có thể cân nhắc giảm dầu, chiên/rán hoặc đổi phương pháp chế biến."
```

## 23.4. Sodium

Nếu sodium cao:

```text
"Khẩu phần này có lượng sodium cao; nên cân nhắc các món ít mặn hơn ở những bữa còn lại."
```

## 23.5. Đường từ đồ uống

Ví dụ:

```text
Nước ngọt + 1 bữa
```

Hệ thống phải ghi rõ:

```text
Năng lượng từ đồ uống:
xxx kcal

Tỷ trọng trong tổng năng lượng bữa:
xx%
```

Nếu cao:

> “Lượng năng lượng từ đồ uống đang chiếm tỷ trọng lớn trong bữa này.”

---

---

# 24. KHÔNG ĐƯA RA CHẨN ĐOÁN Y KHOA

Hệ thống không được đưa ra:

```text
"Bạn bị béo phì."
"Bạn bị tiểu đường."
"Bạn thiếu chất X."
"Bạn sẽ cao thêm X cm."
```

Nếu có nhu cầu tư vấn y khoa:

```text
Hiển thị cảnh báo:
"Thông tin này chỉ nhằm hỗ trợ lựa chọn thực phẩm.
Nếu bạn có bệnh lý hoặc nhu cầu dinh dưỡng đặc biệt,
hãy trao đổi với chuyên gia y tế/dinh dưỡng."
```

---

---

# 25. MÁY HỌC

ML không chịu trách nhiệm duy nhất cho nutrition safety.

Kiến trúc:

```text
User Input
   ↓
Hard Constraint Filter
   ↓
Feature Engineering
   ↓
ML Model
   ↓
Preference / Acceptance Score
   ↓
Recommendation Ranking
```

## 25.1. Bài toán ML chính

### Food/Meal Acceptance Prediction

Dự đoán:

```text
P(user accepts food/meal)
```

Target:

```text
0 = reject
1 = accept
```

Có thể mở rộng regression:

```text
Rating 1–5
```

nếu có đủ dữ liệu.

---

---

# 26. MODEL

Bắt buộc thử:

- Logistic Regression;
- KNN;
- Decision Tree;
- Random Forest.

Tùy dữ liệu có thể thử:

- Gradient Boosting;
- XGBoost.

ANN chỉ là tùy chọn, không bắt buộc.

## 26.1. Phương án ML chính thức cho tiểu luận

Do yêu cầu tiểu luận có **Linear Regression**, bài toán chính dùng target hồi quy:

```text
compatibility_rating: 1 đến 5
```

Nhãn được thu qua khảo sát tình huống: người tham gia xem hồ sơ gồm mục tiêu, ngân sách, sở thích/ràng buộc và một bữa ăn, sau đó chấm mức phù hợp. Dataset nhãn cần có `respondent_id`, `scenario_id`, `goal`, `budget_vnd`, các đặc trưng dinh dưỡng/chi phí/thời gian và `compatibility_rating`.

Các model so sánh chính thức là `DummyRegressor`, `LinearRegression`, `KNeighborsRegressor`, `DecisionTreeRegressor`, `RandomForestRegressor` và `MLPRegressor` (ANN) khi số mẫu đủ. Nhánh `accept/reject` ở phần 25 vẫn được giữ như hướng bổ sung; chỉ đánh giá bằng Accuracy, Precision, Recall, F1 và ROC-AUC khi thực sự xây classifier riêng.

Không dùng nhãn do rule score tự sinh làm kết quả ML chính thức. Dữ liệu synthetic chỉ đặt trong fixture để kiểm tra kỹ thuật và phải ghi rõ trong báo cáo.

---

---

# 27. USER INTERACTION DATA

Dữ liệu có thể được tạo từ:

- khảo sát;
- người dùng demo;
- interaction trong app.

Action:

```text
LIKE
DISLIKE
SKIP
SAVE
COOKED
RATED
ADD_TO_PLAN
REMOVE_FROM_PLAN
```

Bảng:

```text
food_interactions
-----------------
id
user_id
food_id
action
rating
created_at
```

---

---

# 28. COLD START

Người dùng mới:

```text
Onboarding
 ↓
Goal
 ↓
Budget
 ↓
Preference
 ↓
Allergy
 ↓
Content-based + Rules
```

Sau khi có interaction:

```text
History
 ↓
ML score
 ↓
Personalized ranking
```

---

---

# 29. SCORING

Có thể sử dụng:

```text
TotalScore =
    w1 * NutritionScore
  + w2 * PreferenceScore
  + w3 * BudgetScore
  + w4 * MLScore
  + w5 * VarietyScore
  + w6 * ConvenienceScore
```

Tất cả score:

```text
0 → 1
```

Không cần công bố điểm cho người dùng nếu điểm làm UX phức tạp. Frontend có thể dùng:

```text
Phù hợp cao
Khá phù hợp
Có thể cân nhắc
```

và giải thích lý do.

---

---

# 30. HARD CONSTRAINT

Các điều kiện sau phải loại trước ML/ranking:

```text
Allergy
Forbidden food
Invalid food
Budget hard limit nếu người dùng yêu cầu
Diet restriction
```

Ví dụ:

```text
User allergy = đậu phộng

Food contains peanut
        ↓
REJECT
```

Không được để model “bù điểm” cho món có dị ứng.

---

---

# 31. SOFT CONSTRAINT

Có thể tối ưu:

- khẩu vị;
- calories gần mục tiêu;
- protein gần mục tiêu;
- giá;
- thời gian nấu;
- đa dạng;
- độ tiện lợi.

---

---

# 32. TỐI ƯU THỰC ĐƠN

Có thể dùng OR-Tools.

Mục tiêu:

```text
Minimize:
NutritionDeviation
+ CostDeviation
+ PreferencePenalty
+ RepetitionPenalty
+ PreparationTimePenalty
```

Constraints:

```text
Calories ≈ Target
Protein ≥ Minimum
Budget ≤ User Budget
Allergy = 0 violations
Forbidden food = 0
```

Không cần Genetic Algorithm trong phiên bản chính.

---

---

# 33. TỐI ƯU GIÁ

Đối với cùng một món có nhiều nguồn giá:

```text
AEON
GO!
WinMart
...
```

hệ thống có thể:

```text
Food
 ↓
Current observed prices
 ↓
Normalize
 ↓
Median
 ↓
Estimated price
```

Nếu user muốn tiết kiệm:

```text
Budget Priority ↑
```

Nếu user muốn đa dạng/dễ nấu:

```text
Convenience / Preference ↑
```

---

---

# 34. GIÁ TRỊ DINH DƯỠNG TRÊN CHI PHÍ

Có thể tính:

```text
ProteinPer1000VND =
Protein(g) / (Price(VND) / 1000)
```

và:

```text
CaloriesPer1000VND =
Calories / (Price(VND) / 1000)
```

Các chỉ số này dùng cho phân tích, không phải tiêu chí duy nhất.

---

---

# 59. NOTEBOOK

```text
notebooks/
│
├── 01_data_collection.ipynb
├── 02_data_cleaning.ipynb
├── 03_food_name_normalization.ipynb
├── 04_price_normalization.ipynb
├── 05_eda.ipynb
├── 06_feature_engineering.ipynb
├── 07_ml_models.ipynb
├── 08_model_evaluation.ipynb
├── 09_recommendation.ipynb
└── 10_meal_optimization.ipynb
```

---

---

# 60. EDA

Phải có:

### Food

- phân bố calories;
- protein;
- carbohydrate;
- fat;
- fiber;
- sodium.

### Price

- price/kg;
- price/100g;
- price theo food group;
- biến động theo thời gian;
- price distribution.

### Recipe

- calories/recipe;
- cost/recipe;
- prep time;
- cooking time;
- ingredient count.

### Relationship

- protein vs cost;
- calories vs cost;
- protein vs calories.

---

---

# 61. MODEL EVALUATION

Các model:

```text
Logistic Regression
KNN
Decision Tree
Random Forest
XGBoost (optional)
```

Metrics:

```text
Accuracy
Precision
Recall
F1
ROC-AUC
```

Recommendation:

```text
Precision@K
Recall@K
NDCG@K
```

Không đánh giá hệ thống chỉ bằng accuracy.

## 61.1. Metric theo bài toán chính thức

Với target `compatibility_rating`, chia train/test theo `respondent_id` hoặc `scenario_id`, cố định `random_state` và dùng cross-validation trên train. Báo cáo test bằng:

```text
MAE
RMSE
R²
```

Model được chọn phải so sánh với `DummyRegressor`; pipeline tiền xử lý, phiên bản dataset, seed, metric và ngày train được lưu cùng model. Chạy tối thiểu năm tình huống mới trong Notebook/demo để chứng minh model xử lý được dữ liệu chưa thấy.

---

---

# 62. SYSTEM EVALUATION

Đánh giá thêm:

## Nutrition

```text
Calories deviation
Protein deviation
```

## Budget

```text
Budget deviation
Budget violation count
```

## Safety

```text
Allergy violation = 0
```

## UX

Có thể khảo sát:

- thời gian tạo thực đơn;
- số lần user phải sửa thực đơn;
- rating;
- tỷ lệ chấp nhận đề xuất.

---

---

# 74. PHÂN CẤP HỆ THỐNG

## MỨC 1 — BẮT BUỘC CHO TIỂU LUẬN

```text
Food dataset
Recipe dataset
Price dataset
Preprocessing
EDA
ML
Evaluation
Jupyter
Demo
```

## MỨC 2 — MỤC TIÊU CHÍNH

```text
Mức 1
+
MySQL
+
User account
+
Profile
+
Goal
+
Budget
+
Preference
+
Allergy
+
Recipe
+
Meal Plan
+
Food Search
+
Manual Add
+
Meal Evaluation
+
Replace Meal
+
Authentication
```

## MỨC 3 — CHỌN LỌC

Chỉ nên thêm:

```text
Hybrid Recommendation
OR-Tools
What-if
SHAP / Feature Importance
Feedback Loop
Price Confidence
Meal Variety
```

Không cần:

```text
Multi-language
LLM chatbot
Computer Vision
Mobile app
Social network
Marketplace
Deep recommender
```

trong phạm vi hiện tại.

---

---

# 75. ROADMAP TRIỂN KHAI

## PHASE 1 — Requirements

- chốt use case;
- chốt input/output;
- chốt data model;
- chốt mục tiêu dinh dưỡng.

## PHASE 2 — Data

- nutrition;
- recipe;
- price;
- aliases;
- allergen.

## PHASE 3 — Preprocessing

- missing;
- duplicate;
- units;
- Vietnamese normalization;
- price normalization.

## PHASE 4 — EDA

- nutrition;
- price;
- recipe;
- correlation.

## PHASE 5 — ML

- baseline;
- model comparison;
- evaluation;
- save model.

## PHASE 6 — DSS

- Rule Engine;
- scoring;
- recommendation;
- user selection.

## PHASE 7 — Meal Planner

- meal;
- day;
- week;
- month;
- budget;
- portion;
- replace.

## PHASE 8 — Manual Selection

- search;
- add food;
- add recipe;
- analyze;
- advice.

## PHASE 9 — Recipe

- recipe source;
- instructions;
- source URL;
- recipe mapping.

## PHASE 10 — Database

- MySQL;
- constraints;
- indexes;
- relations.

## PHASE 11 — Backend

FastAPI.

## PHASE 12 — Frontend

Dashboard + planner.

## PHASE 13 — Security

- auth;
- RBAC;
- password hashing;
- validation;
- injection prevention.

## PHASE 14 — Evaluation

- ML;
- recommendation;
- budget;
- nutrition;
- UX.

## PHASE 15 — Report

20–30 pages + notebook + demo.

---

---

# 76. BỘ CÔNG NGHỆ

| Thành phần | Công nghệ |
|---|---|
| Language | Python |
| Notebook | Jupyter |
| Data processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| ML | Scikit-learn |
| Optional ML | XGBoost |
| Explainability | SHAP |
| Optimization | OR-Tools |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Database | MySQL 8 |
| DB Tool | MySQL Workbench |
| Frontend MVP | Streamlit |
| Frontend nâng cao | React |
| Auth | Session/JWT |
| Password | Argon2id |
| Testing | Pytest |
| Version control | Git/GitHub |

---

---

# 79. UX PRINCIPLES

## Phải nhanh

Người dùng không nên đi qua quá nhiều màn.

## Phải trực quan

Hiển thị:

```text
Calories
Protein
Cost
Goal compatibility
```

ở ngay thẻ món ăn.

## Phải linh hoạt

Người dùng có thể:

```text
Đổi món
Đổi khẩu phần
Tìm món
Thêm món
Xóa món
```

## Phải minh bạch

Hiển thị:

```text
Giá ước tính
Ngày cập nhật
Nguồn
```

## Phải có khả năng giải thích

Không chỉ:

> “AI đề xuất.”

mà:

> “Vì món này phù hợp ngân sách, protein gần mục tiêu và phù hợp sở thích của bạn.”

---

---

# 80. GỢI Ý GIAO DIỆN

## Home

```text
[Mục tiêu]
[Ngân sách]
[Thực đơn hôm nay]

Gợi ý:
🍗 Ức gà
🥚 Trứng
🥦 Bông cải

[ Tạo thực đơn ]
```

## Planner

```text
HÔM NAY

Sáng
[ Món ]
[Đổi]

Trưa
[ Món ]
[Đổi]

Tối
[ Món ]
[Đổi]

Tổng:
1.720 kcal
92g protein
68.500đ
```

## Search

```text
Tìm món:
[ Phở bò                     ]

Kết quả
Phở bò
[Thêm vào thực đơn]

[Phân tích]
```

---

---

# 81. KỊCH BẢN DEMO CHÍNH

## Demo 1 — Tự tạo thực đơn

Input:

```text
Mục tiêu: giảm cân
Ngân sách: 70.000đ/ngày
Không thích cá
Dị ứng đậu phộng
Thích gà và trứng
```

System:

```text
Generate
```

Output:

```text
Breakfast
Lunch
Dinner
```

## Demo 2 — Đổi món

User:

```text
Không thích món trưa.
```

Click:

```text
Đổi món
```

System trả 3 lựa chọn khác trong ngân sách.

## Demo 3 — Đổi khẩu phần

User:

```text
Ức gà:
150g → 200g
```

System tính lại:

- calories;
- protein;
- cost.

## Demo 4 — Tự thêm món

User:

```text
Thêm trà sữa
```

System:

```text
Calories tăng
Sugar tăng
Budget tăng
```

và đưa lời khuyên phù hợp với mục tiêu.

## Demo 5 — Tìm công thức

User:

```text
Ức gà áp chảo
```

System:

```text
Nutrition
Cost
Recipe
Cooking time
Instructions / source
```

---

---

# 84. BÁO CÁO TIỂU LUẬN 20–30 TRANG

## Chương 1 — Tổng quan

- lý do chọn đề tài;
- bài toán;
- mục tiêu;
- phạm vi.

## Chương 2 — Cơ sở lý thuyết

- DSS;
- Machine Learning;
- recommendation;
- nutrition;
- optimization.

## Chương 3 — Thu thập và xử lý dữ liệu

- nguồn;
- scraping/API;
- normalization;
- food master;
- price pipeline;
- recipe pipeline.

## Chương 4 — Phân tích dữ liệu

- EDA;
- visualization;
- price;
- nutrition.

## Chương 5 — Machine Learning

- feature;
- train;
- model;
- evaluation.

## Chương 6 — Xây dựng DSS

- architecture;
- rule engine;
- recommendation;
- optimizer;
- meal planner.

## Chương 7 — Hệ thống và database

- ERD;
- MySQL;
- API;
- frontend.

## Chương 8 — Bảo mật và đánh giá

- authentication;
- authorization;
- privacy;
- testing;
- performance.

## Chương 9 — Kết luận và phát triển

---

---

# 85. CHECKLIST HOÀN THÀNH

## Data

- [ ] Nutrition dataset
- [ ] Recipe dataset
- [ ] Price dataset
- [ ] Vietnamese canonical names
- [ ] Units standardized
- [ ] Price normalization
- [ ] Source tracking

## ML

- [ ] Preprocessing
- [ ] EDA
- [ ] Feature engineering
- [ ] Logistic Regression
- [ ] KNN
- [ ] Decision Tree
- [ ] Random Forest
- [ ] Evaluation
- [ ] Saved model

## DSS

- [ ] Goal
- [ ] Budget
- [ ] Allergy
- [ ] Preference
- [ ] Recommendation
- [ ] Meal
- [ ] Day
- [ ] Week
- [ ] Month
- [ ] Portion control
- [ ] Replace item
- [ ] Manual add
- [ ] Analyze selected food
- [ ] Recipe guidance

## Database

- [ ] Users
- [ ] Profiles
- [ ] Preferences
- [ ] Allergies
- [Foods
- [ ] Nutrients
- [ ] Prices
- [ ] Recipes
- [ ] Meal plans
- [ ] Interaction
- [ ] Model versions
- [ ] Audit logs

## Security

- [ ] Password hashing
- [ ] Auth
- [ ] RBAC
- [ ] Validation
- [ ] SQL injection prevention
- [ ] Secret management
- [ ] Audit log

## UX

- [ ] Quick onboarding
- [ ] Fast recommendation
- [ ] Replace meal
- [ ] Change portion
- [ ] Search food
- [ ] Add food
- [ ] Nutrition summary
- [ ] Cost summary
- [ ] Recipe instructions/source
- [ ] Clear explanation

---

---

# 86. NGUYÊN TẮC KHÔNG ĐƯỢC PHÁ VỠ

1. Dị ứng là **hard constraint**.
2. Không để ML bỏ qua safety constraints.
3. Giá phải gắn với thời điểm cập nhật.
4. Giá thực phẩm phải chuẩn hóa theo kg/100g hoặc đơn vị tương đương.
5. Không lấy một sản phẩm premium làm đại diện cho toàn bộ loại thực phẩm.
6. Tên thực phẩm chuẩn trong hệ thống là **tiếng Việt**.
7. Không tạo taxonomy quá chi tiết nếu không phục vụ meal planning.
8. Người dùng phải luôn có quyền đổi món.
9. Người dùng phải có quyền tự thêm món.
10. Món người dùng tự thêm phải được phân tích lại.
11. Không bắt buộc user phải theo thực đơn AI.
12. Không lưu thông tin tài chính ngoài phạm vi food budget nếu không cần.
13. Không lưu plaintext password.
14. Không commit secrets vào Git.
15. Scraping phải tuân thủ điều kiện của nguồn.
16. Không sao chép recipe/ảnh có bản quyền nếu không có quyền sử dụng.
17. Không đưa ra chẩn đoán y khoa.
18. Không tuyên bố chắc chắn rằng một món ăn làm người dùng cao thêm, giảm cân một cách chắc chắn, hoặc chữa bệnh.
19. Ưu tiên trải nghiệm người dùng hơn việc nhồi quá nhiều công nghệ.
20. ML là một thành phần của DSS, không phải toàn bộ DSS.

---

---

# 87. MỤC TIÊU CUỐI CÙNG

NutriDSS phải tạo cảm giác:

```text
"Tôi có 50.000đ.
Tôi muốn ăn món này.
Tôi không thích món kia.
Tôi đang muốn giảm cân.
Tôi dị ứng đậu phộng.
Tôi chỉ có 20 phút để nấu.

→ Hệ thống đưa cho tôi vài lựa chọn.
→ Tôi chọn một món.
→ Tôi thấy calories + dinh dưỡng + giá.
→ Tôi có thể đổi khẩu phần.
→ Tôi có thể đổi món.
→ Tôi có thể xem cách nấu.
→ Tôi có thể thêm món khác.
→ Hệ thống tính lại cả ngày/tuần."
```

Đó là mục tiêu sản phẩm.

Không phải:

> “AI tự quyết định tôi phải ăn gì.”

Mà là:

> **“AI + dữ liệu + luật + giá + tối ưu hóa giúp tôi đưa ra lựa chọn ăn uống tốt hơn trong hoàn cảnh của chính mình.”**
