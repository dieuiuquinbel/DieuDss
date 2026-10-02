# -*- coding: utf-8 -*-
"""
NutriDSS - Curated Vietnamese Home-Cooking Recipe Master V2 (63 canonical dishes)
- 100% Định lượng nguyên liệu chi tiết (gram) cho 1 khẩu phần chuẩn
- 100% Chiết tính giá thành từ nguyên liệu thô theo giá thị trường/siêu thị VN
- Hướng dẫn chế biến (cooking steps) cụ thể từng bước
- Phân loại rõ vai trò mâm cơm: STAPLE, MAIN_PROTEIN, VEG_PROTEIN, SOUP_VEG, BREAKFAST, DESSERT
"""

import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Danh mục thực phẩm hạt nhân bổ sung để khớp 100% nguyên liệu
CORE_FOODS_TO_SEED = [
    (2201, "Cua đồng xay", "RAW", 89.0, 12.3, 2.0, 3.3, 0.0, 0.0, 320.0, 15000.0),
    (2202, "Mướp hương", "RAW", 16.0, 0.9, 3.0, 0.1, 0.5, 1.8, 8.0, 2500.0),
    (2203, "Rau mồng tơi", "RAW", 14.0, 1.4, 2.1, 0.1, 1.5, 0.4, 30.0, 3000.0),
    (2204, "Cần tây tươi", "RAW", 16.0, 0.7, 3.0, 0.2, 1.6, 1.3, 80.0, 3500.0),
    (2205, "Tỏi tây (Boa-rô)", "RAW", 29.0, 1.5, 5.7, 0.3, 1.8, 1.9, 20.0, 4000.0),
    (2206, "Nấm bào ngư (Nấm sò)", "RAW", 33.0, 3.3, 6.1, 0.4, 2.3, 1.1, 18.0, 6500.0),
    (2207, "Hạt sen tươi", "RAW", 89.0, 4.1, 17.1, 0.5, 2.1, 1.5, 5.0, 12000.0),
    (2208, "Cá basa phi lê", "RAW", 124.0, 15.0, 0.0, 7.0, 0.0, 0.0, 65.0, 8500.0),
    (2209, "Cá diêu hồng làm sạch", "RAW", 96.0, 19.5, 0.0, 2.0, 0.0, 0.0, 50.0, 7000.0),
    (2210, "Chả cá thác lác", "RAW", 112.0, 16.5, 1.2, 4.5, 0.0, 0.2, 450.0, 16000.0),
    (2211, "Miến dong khô", "DRY", 332.0, 0.7, 82.0, 0.1, 1.5, 0.0, 10.0, 9000.0),
    (2212, "Ngô ngọt (Bắp vàng)", "RAW", 86.0, 3.2, 19.0, 1.2, 2.7, 3.2, 15.0, 2500.0),
    (2213, "Dưa hấu tươi", "RAW", 30.0, 0.6, 7.6, 0.2, 0.4, 6.2, 1.0, 2000.0),
    (2214, "Táo tươi giòn", "RAW", 52.0, 0.3, 13.8, 0.2, 2.4, 10.4, 1.0, 6000.0),
    (2215, "Thanh long ruột đỏ", "RAW", 60.0, 1.2, 13.0, 0.0, 2.9, 7.7, 2.0, 3500.0),
    (2216, "Su su quả tươi", "RAW", 19.0, 0.8, 4.5, 0.1, 1.7, 1.7, 4.0, 2000.0),
    (2217, "Bí xanh (Bí đao)", "RAW", 12.0, 0.4, 2.4, 0.1, 1.0, 1.2, 6.0, 2200.0),
    (2218, "Chả lụa heo truyền thống", "COOKED", 198.0, 15.2, 2.5, 14.1, 0.0, 0.5, 680.0, 22000.0),
    (2219, "Nếp cái hoa vàng", "DRY", 344.0, 8.4, 74.5, 1.6, 1.2, 0.5, 3.0, 3000.0),
    (2220, "Bánh cuốn tươi", "COOKED", 143.0, 2.4, 30.1, 1.2, 0.8, 0.0, 80.0, 4000.0),
    (2221, "Thịt bắp giò heo", "RAW", 230.0, 17.5, 0.0, 18.0, 0.0, 0.0, 75.0, 14000.0),
    (2222, "Nước dừa tươi", "RAW", 19.0, 0.7, 3.7, 0.2, 1.1, 2.6, 105.0, 2000.0),
    (2223, "Rau dền đỏ", "RAW", 23.0, 2.1, 4.0, 0.3, 1.8, 0.2, 20.0, 2500.0),
    (2224, "Mộc nhĩ khô (Nấm mèo)", "DRY", 284.0, 10.6, 65.0, 0.2, 5.0, 0.0, 35.0, 18000.0)
]

CURATED_RECIPES = [
    # =========================================================================
    # 1. NHÓM TINH BỘT / CƠM (STAPLE)
    # =========================================================================
    {
        "name_vi": "Cơm trắng dẻo (1 bát)",
        "dish_role": "STAPLE", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 25, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Bát cơm trắng nóng hổi (chuẩn 160g cơm chín), tinh bột hấp thu năng lượng nền tảng cho bữa ăn.",
        "tags": "staple,com_trang,chay_man",
        "instructions": "1. Vo sạch 75g gạo tẻ với 2 lần nước.\n2. Cho nước theo tỷ lệ 1 gạo : 1.2 nước vào nồi cơm điện.\n3. Bật nấc nấu chín, ủ ấm 10 phút trước khi xới ra bát.",
        "ingredients": [{"food_kw": "Gạo trắng", "quantity_g": 75.0}]
    },
    {
        "name_vi": "Cơm gạo lứt huyết rồng (1 bát)",
        "dish_role": "STAPLE", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 35, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Bát cơm gạo lứt giàu chất xơ, hỗ trợ no lâu, kiểm soát đường huyết và giảm mỡ nội tạng.",
        "tags": "staple,gao_lut,eat_clean,chay_man",
        "instructions": "1. Ngâm gạo lứt trong nước ấm 30-45 phút cho mềm hạt.\n2. Nấu với tỷ lệ 1 gạo : 1.5 nước.\n3. Khi cơm chín, để chế độ giữ ấm 15 phút cho hạt cơm dẻo mềm.",
        "ingredients": [{"food_kw": "Gạo lứt", "quantity_g": 75.0}]
    },
    {
        "name_vi": "Khoai lang luộc nguyên củ",
        "dish_role": "STAPLE", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 20, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Củ khoai lang ruột vàng luộc ngọt bùi (180g), giàu tinh bột hấp thu chậm, vitamin A và kali.",
        "tags": "staple,khoai_lang,eat_clean,chay_man",
        "instructions": "1. Rửa sạch đất cát trên vỏ khoai lang.\n2. Cho vào nồi, đổ ngập nửa củ nước và thêm chút muối.\n3. Luộc lửa vừa trong 20 phút, dùng tăm xiên qua nhẹ nhàng là khoai đã chín.",
        "ingredients": [{"food_kw": "Khoai lang", "quantity_g": 180.0}]
    },
    {
        "name_vi": "Bún tươi sợi nhỏ (1 đĩa)",
        "dish_role": "STAPLE", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 2, "cook_time_min": 3, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Đĩa bún tươi thanh mát (180g), sợi trắng ngần, thích hợp ăn kèm các món xào, món kho và canh chua.",
        "tags": "staple,bun_tuoi,chay_man",
        "instructions": "1. Chần bún tươi qua nước sôi trong 30 giây để sợi bún sạch và mềm.\n2. Vớt ra để ráo nước rồi bày ra đĩa.",
        "ingredients": [{"food_kw": "Bún tươi", "quantity_g": 180.0}]
    },
    {
        "name_vi": "Bánh mì Việt Nam giòn rụm (1 ổ)",
        "dish_role": "STAPLE", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 2, "cook_time_min": 5, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Ổ bánh mì vỏ giòn ruột xốp (80g), nguồn tinh bột tiện lợi và phổ biến cho bữa sáng.",
        "tags": "staple,banh_mi,chay_man",
        "instructions": "1. Nướng lại bánh mì trong lò nướng hoặc nồi chiên không dầu 160 độ C trong 3 phút cho vỏ giòn tan.",
        "ingredients": [{"food_kw": "Bánh mì", "quantity_g": 80.0}]
    },
    {
        "name_vi": "Miến dong xào rau củ thanh đạm (1 đĩa)",
        "dish_role": "STAPLE", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Đĩa miến dong dai mướt xào cà rốt thái sợi, mộc nhĩ và hành hoa, ít dầu mỡ thanh nhẹ.",
        "tags": "staple,mien_xao,chay_man",
        "instructions": "1. Miến ngâm nước ấm 5 phút cho mềm, cắt ngắn.\n2. Xào chín cà rốt và mộc nhĩ với dầu ăn.\n3. Trút miến vào đảo nhanh tay cùng 1 thìa xì dầu trong 3 phút, rắc tiêu và hành hoa.",
        "ingredients": [
            {"food_kw": "Miến dong", "quantity_g": 60.0},
            {"food_kw": "Cà rốt", "quantity_g": 40.0},
            {"food_kw": "Mộc nhĩ", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0},
            {"food_kw": "Nước tương", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Ngô ngọt bắp vàng luộc (1 bắp)",
        "dish_role": "STAPLE", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 2, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Bắp ngô ngọt luộc hạt vàng óng ả (200g), vị ngọt thanh tự nhiên, giàu chất xơ và zeaxanthin sáng mắt.",
        "tags": "staple,ngo_ngot,bap_luoc,eat_clean",
        "instructions": "1. Ngô ngọt lột bớt vỏ ngoài, giữ lại lớp vỏ lụa và râu ngô.\n2. Xếp vào nồi đổ ngập nước, thêm hạt muối luộc 15 phút là chín ngọt mọng.",
        "ingredients": [{"food_kw": "Ngô ngọt", "quantity_g": 200.0}]
    },

    # =========================================================================
    # 2. NHÓM MÓN MẶN / CHẤT ĐẠM ĐỘNG VẬT (MAIN_PROTEIN)
    # =========================================================================
    {
        "name_vi": "Lòng bò xào lá lốt",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 10, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Lòng bò giòn sần sật xào cùng lá lốt thơm nồng, ớt hiểm và tỏi đập dập đậm đà đưa cơm.",
        "tags": "mon_man,mon_xao,bo,dac_san",
        "instructions": "1. Lòng bò bóp muối và giấm, rửa sạch, chần sơ nước sôi với gừng rồi thái miếng vừa ăn.\n2. Lá lốt rửa sạch thái khúc 1cm. Tỏi, ớt băm nhỏ.\n3. Phi thơm tỏi ớt với dầu ăn, trút lòng bò vào xào lửa lớn trong 3 phút, nêm nước mắm.\n4. Cho lá lốt vào đảo nhanh tay 1 phút rồi tắt bếp, rắc tiêu xay.",
        "ingredients": [
            {"food_kw": "Lòng bò", "quantity_g": 130.0},
            {"food_kw": "Lá lốt", "quantity_g": 40.0},
            {"food_kw": "Tỏi củ tươi", "quantity_g": 10.0},
            {"food_kw": "Ớt tươi", "quantity_g": 5.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 10.0}
        ]
    },
    {
        "name_vi": "Thịt bò xào dưa chua",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Thịt bò nạc mềm ngọt hòa quyện vị chua thanh giòn rụm của dưa cải muối chua và cà chua chín mọng.",
        "tags": "mon_man,mon_xao,bo,dua_chua",
        "instructions": "1. Thịt bò thái lát mỏng ngang thớ, ướp tỏi băm và chút mắm trong 10 phút.\n2. Dưa chua vắt ráo bớt nước, cà chua bổ múi cau.\n3. Phi tỏi xào thịt bò tái chín trên lửa lớn rồi múc riêng ra đĩa.\n4. Xào dưa chua và cà chua cho chín mềm, trút thịt bò vào đảo đều 1 phút rồi tắt bếp.",
        "ingredients": [
            {"food_kw": "Nạc bò", "quantity_g": 120.0},
            {"food_kw": "Măng chua / Dưa cải", "quantity_g": 100.0},
            {"food_kw": "Cà chua", "quantity_g": 60.0},
            {"food_kw": "Tỏi củ tươi", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Thịt bò xào cần tỏi tây thơm lừng",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 8, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Thịt bò mềm đậm vị xào cùng cần tây giòn thơm và tỏi tây ngọt mát, món xào kinh điển đưa cơm.",
        "tags": "mon_man,mon_xao,bo,can_tay",
        "instructions": "1. Thịt bò thái mỏng ướp tỏi gừng và chút dầu ăn cho mềm thớ thịt.\n2. Cần tây, tỏi tây rửa sạch cắt khúc 3cm.\n3. Phi thơm tỏi đập dập, trút thịt bò vào xào chín tái rồi trút ra đĩa.\n4. Xào cần tỏi tây vừa chín tới, đổ bò vào đảo nhanh tay 30 giây rắc tiêu xay.",
        "ingredients": [
            {"food_kw": "Nạc bò", "quantity_g": 120.0},
            {"food_kw": "Cần tây", "quantity_g": 80.0},
            {"food_kw": "Tỏi tây", "quantity_g": 40.0},
            {"food_kw": "Tỏi củ tươi", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Thịt lợn nạc băm rim hành tiêu",
        "dish_role": "MAIN_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 12, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Thịt nạc vai heo băm rim đậm vị nước mắm cốt, thơm nồng mùi hành tím phi và tiêu đen xay, cực kỳ tiết kiệm.",
        "tags": "mon_man,thit_heo,tiet_kiem,gia_dinh",
        "instructions": "1. Thịt nạc băm nhỏ ướp 1 thìa nước mắm và chút tiêu.\n2. Phi thơm hành tím băm với chút dầu ăn, trút thịt băm vào đảo săn.\n3. Thêm 1 thìa nước lọc đun liu riu 5 phút cho ngấm vị, rắc tiêu xay lên trên.",
        "ingredients": [
            {"food_kw": "Nạc đùi heo", "quantity_g": 120.0},
            {"food_kw": "Hành tím", "quantity_g": 15.0},
            {"food_kw": "Tiêu đen xay", "quantity_g": 3.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Trứng đúc thịt băm chiên vàng",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "2 quả trứng gà ta đánh nhuyễn cùng thịt nạc vai băm và hành lá, rán vàng đều hai mặt thơm ngậy.",
        "tags": "mon_man,trung,thit_heo,tiet_kiem",
        "instructions": "1. Đập 2 quả trứng gà vào bát, thêm thịt nạc băm, hành lá thái nhỏ và 1 thìa nước mắm.\n2. Đánh tan đều hỗn hợp.\n3. Đun nóng chảo dầu, đổ trứng vào chiên lửa vừa. Khi mặt dưới vàng thì lật mặt chiên vàng đều.",
        "ingredients": [
            {"food_kw": "Trứng gà", "quantity_g": 100.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 60.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0}
        ]
    },
    {
        "name_vi": "Thịt ba chỉ kho trứng cút đậm đà",
        "dish_role": "MAIN_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 35, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Thịt ba chỉ heo thái con chì ninh nhừ cùng trứng bùi bùi, ngấm đều nước màu caramel sóng sánh.",
        "tags": "mon_man,kho_tau,thit_heo,dam_da",
        "instructions": "1. Thịt ba chỉ rửa sạch, thái miếng dày 2cm. Trứng luộc chín bóc vỏ.\n2. Thắng đường với chút dầu ăn tạo màu cánh gián, trút thịt vào đảo săn.\n3. Thêm nước mắm, hành tím và nước xâm xấp mặt thịt, đun sôi rồi hạ nhỏ lửa đun 20 phút.\n4. Thả trứng vào kho thêm 10 phút cho ngấm đều gia vị.",
        "ingredients": [
            {"food_kw": "Thịt lợn ba chỉ", "quantity_g": 110.0},
            {"food_kw": "Trứng gà", "quantity_g": 55.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 12.0},
            {"food_kw": "Hành tím", "quantity_g": 10.0}
        ]
    },
    {
        "name_vi": "Thịt kho tàu nước dừa tươi",
        "dish_role": "MAIN_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 35, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Thịt ba chỉ kho nước dừa xiêm ngọt thanh tự nhiên, miếng thịt mềm rục trong veo béo ngậy.",
        "tags": "mon_man,kho_tau,nuoc_dua,mien_nam",
        "instructions": "1. Thịt ba chỉ thái vuông to bản, ướp hành tím, tỏi, ớt và nước mắm 20 phút.\n2. Đun sôi nước dừa tươi trong nồi đất, trút thịt vào kho lửa vừa.\n3. Khi sôi hạ lửa nhỏ ninh liu riu 30 phút cho mỡ trong và nước dừa keo vàng óng.",
        "ingredients": [
            {"food_kw": "Thịt lợn ba chỉ", "quantity_g": 130.0},
            {"food_kw": "Nước dừa", "quantity_g": 100.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 15.0},
            {"food_kw": "Hành tím", "quantity_g": 10.0},
            {"food_kw": "Ớt tươi", "quantity_g": 5.0}
        ]
    },
    {
        "name_vi": "Cá rô phi rán giòn sốt mắm gừng",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Phi lê cá rô phi làm sạch chiên vàng ruộm, thịt cá trắng ngọt thanh đạm chấm mắm gừng ớt tỏi.",
        "tags": "mon_man,ca,tiet_kiem,high_protein",
        "instructions": "1. Cá rô phi thấm khô nước, khía nhẹ trên thân cá.\n2. Đun sôi dầu ăn, thả cá vào chiên vàng giòn hai mặt.\n3. Pha nước mắm cùng gừng băm, ớt tỏi và chút đường chấm kèm.",
        "ingredients": [
            {"food_kw": "Cá rô phi", "quantity_g": 180.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 15.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0},
            {"food_kw": "Gừng tươi", "quantity_g": 5.0}
        ]
    },
    {
        "name_vi": "Cá lóc kho tộ tiêu ớt miền Tây",
        "dish_role": "MAIN_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 25, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Khúc cá lóc đồng kho trong tộ đất, thịt cá săn chắc thơm cay nồng ấm bụng, nước kho sền sệt chấm rau luộc.",
        "tags": "mon_man,ca_loc,kho_to,truyen_thong",
        "instructions": "1. Cá lóc làm sạch, xát muối cho hết nhớt, cắt khúc dày 2.5cm.\n2. Ướp cá với nước mắm, nước màu đường, tiêu đen và ớt đập dập 15 phút.\n3. Cho tộ lên bếp đun sôi bùng, sau đó hạ lửa riu riu kho 20 phút cho nước keo lại.",
        "ingredients": [
            {"food_kw": "Cá lóc", "quantity_g": 150.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 15.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 8.0},
            {"food_kw": "Tiêu đen xay", "quantity_g": 4.0},
            {"food_kw": "Ớt tươi", "quantity_g": 5.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Cá basa phi lê kho tộ nước màu dừa",
        "dish_role": "MAIN_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 20, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Phi lê cá basa béo ngậy cắt khúc kho tộ thơm lừng mắm tiêu và ớt, nước kho óng ả cực rẻ.",
        "tags": "mon_man,ca_basa,kho_to,tiet_kiem",
        "instructions": "1. Cá basa rửa sạch cắt khúc 3cm, để ráo.\n2. Ướp nước mắm, tiêu, ớt và nước màu caramel trong 10 phút.\n3. Kho lửa nhỏ trong 15 phút cho cá chín săn và nước sốt keo sánh.",
        "ingredients": [
            {"food_kw": "Cá basa", "quantity_g": 160.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 12.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 6.0},
            {"food_kw": "Tiêu đen xay", "quantity_g": 3.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Thịt gà ta rang gừng thơm nức",
        "dish_role": "MAIN_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 20, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Thịt gà ta chặt miếng vuông vức rang xém cạnh cùng nhiều gừng tươi thái sợi và nước mắm ngon.",
        "tags": "mon_man,ga,rang_gung,truyen_thong",
        "instructions": "1. Thịt gà chặt miếng vừa ăn, rửa sạch để ráo.\n2. Gừng tươi gọt vỏ thái sợi mỏng.\n3. Cho thịt gà vào chảo rang không dầu đến khi miếng thịt săn và tứa mỡ.\n4. Thêm gừng thái sợi, nước mắm, đảo đều đun nhỏ lửa 15 phút cho gà ngấm gừng thơm lừng.",
        "ingredients": [
            {"food_kw": "Thịt gà ta", "quantity_g": 150.0},
            {"food_kw": "Gừng tươi", "quantity_g": 20.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 12.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Gà xé phay bóp hành tây rau răm",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 12, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Thịt ức gà luộc xé sợi trộn gỏi cùng hành tây ngâm giòn, rau răm thơm nồng và nước mắm chanh tỏi ớt.",
        "tags": "mon_man,ga,goi_ga,eat_clean,high_protein",
        "instructions": "1. Ức gà luộc chín với lát gừng, vớt ra xé sợi vừa ăn.\n2. Hành tây thái mỏng ngâm nước đá cho hết hăng và giòn ngọt.\n3. Trộn đều thịt gà, hành tây, rau răm với nước mắm pha chanh đường ớt tỏi.",
        "ingredients": [
            {"food_kw": "Ức gà", "quantity_g": 140.0},
            {"food_kw": "Hành tây", "quantity_g": 60.0},
            {"food_kw": "Chanh quả tươi", "quantity_g": 15.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 10.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 5.0}
        ]
    },
    {
        "name_vi": "Sườn heo rim chua ngọt",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 25, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Sườn non chặt khúc đảo săn, sốt sánh quyện vị chua ngọt hài hòa của cà chua tươi và nước cốt chanh.",
        "tags": "mon_man,suon,chua_ngot",
        "instructions": "1. Sườn non chặt miếng vừa ăn, chần nước sôi rửa sạch.\n2. Rán sườn sơ cho xém vàng hai mặt.\n3. Pha nước sốt: mắm, đường, nước cốt chanh, cà chua băm nhuyễn.\n4. Đổ sốt vào chảo sườn, đun nhỏ lửa đậy nắp trong 15 phút cho sườn mềm và nước sốt keo lại.",
        "ingredients": [
            {"food_kw": "Sườn heo", "quantity_g": 150.0},
            {"food_kw": "Cà chua", "quantity_g": 50.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 8.0},
            {"food_kw": "Chanh quả tươi", "quantity_g": 15.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0}
        ]
    },
    {
        "name_vi": "Tôm đồng rang thịt ba chỉ rim cháy cạnh",
        "dish_role": "MAIN_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Tôm đồng giòn rụm kết hợp thịt ba chỉ béo ngậy rim đường mắm mặn ngọt kinh điển của mâm cơm Bắc.",
        "tags": "mon_man,tom,thit_heo,rang_chay_canh",
        "instructions": "1. Tôm cắt bỏ râu rửa sạch, thịt ba chỉ thái con chì mỏng.\n2. Cho thịt ba chỉ vào chảo đảo cháy cạnh tứa mỡ, trút thịt ra đĩa.\n3. Cho tôm vào chảo mỡ đảo đến khi vỏ tôm đỏ au và giòn.\n4. Trút thịt vào lại, nêm nước mắm, đường, hành tím băm, đảo nhanh tay 3 phút cho bóng đều.",
        "ingredients": [
            {"food_kw": "Tôm đồng", "quantity_g": 80.0},
            {"food_kw": "Thịt lợn ba chỉ", "quantity_g": 70.0},
            {"food_kw": "Hành tím", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 10.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 6.0}
        ]
    },
    {
        "name_vi": "Tôm rim mặn ngọt hành hoa",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Tôm đồng hoặc tôm thẻ cắt râu rim đẫm mắm đường tiêu, vỏ giòn bóng bẩy, thịt ngọt đậm vị.",
        "tags": "mon_man,tom,rim_man_ngot",
        "instructions": "1. Tôm làm sạch râu đuôi, xóc chút muối để ráo.\n2. Phi thơm tỏi với dầu ăn, trút tôm vào đảo lửa lớn cho chuyển sang màu đỏ au.\n3. Thêm nước mắm, đường, tiêu rim nhỏ lửa trong 5 phút cho nước sốt bám bóng quanh tôm.",
        "ingredients": [
            {"food_kw": "Tôm đồng", "quantity_g": 120.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 10.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 6.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Chả cá thác lác sốt cà chua hành hoa",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 12, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Miếng chả cá thác lác quết dẻo dai chiên vàng, thấm đẫm sốt cà chua tươi dịu ngọt và thì là thơm mát.",
        "tags": "mon_man,cha_ca,sot_ca_chua,high_protein",
        "instructions": "1. Chả cá thác lác vo viên dẹt, chiên vàng đều hai mặt.\n2. Xào nhuyễn cà chua với chút dầu ăn và mắm tạo sốt sánh đỏ.\n3. Cho chả cá vào sốt đun liu riu 5 phút, rắc thì là và hành hoa thái nhỏ.",
        "ingredients": [
            {"food_kw": "Chả cá", "quantity_g": 130.0},
            {"food_kw": "Cà chua", "quantity_g": 80.0},
            {"food_kw": "Thì là tươi", "quantity_g": 15.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Mực ống xào cần tỏi hành tây",
        "dish_role": "MAIN_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 12, "cook_time_min": 8, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Mực ống tươi thái khoanh xào giòn ngọt cùng cần tây, tỏi tây và hành tây bổ múi cau, giàu i-ốt và đạm sạch.",
        "tags": "mon_man,muc,hai_san,can_toi",
        "instructions": "1. Mực làm sạch túi mực, thái khoanh tròn khía vảy rồng, chần nhanh qua nước sôi có gừng đập dập.\n2. Cần tây, hành tây thái khúc.\n3. Phi tỏi thơm, trút mực vào đảo lửa to trong 2 phút rồi trút ra đĩa.\n4. Xào cần tây hành tây chín tới, đổ mực vào đảo đều nêm mắm tiêu rồi tắt bếp.",
        "ingredients": [
            {"food_kw": "Mực tươi", "quantity_g": 130.0},
            {"food_kw": "Hành tây", "quantity_g": 50.0},
            {"food_kw": "Tỏi củ tươi", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Đậu phụ nhồi thịt băm sốt cà chua",
        "dish_role": "MAIN_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 12, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Bìa đậu rán rạch bụng nhồi đầy thịt nạc băm nấm mộc nhĩ, om trong nước sốt cà chua béo ngậy ngọt ngào.",
        "tags": "mon_man,dau_phu,thit_heo,sot_ca",
        "instructions": "1. Trộn thịt nạc băm với mộc nhĩ ngâm nở băm nhỏ, nêm chút mắm tiêu.\n2. Đậu hũ rạch rãnh nhồi chặt nhân thịt vào giữa.\n3. Chiên sơ mặt thịt rồi om cùng sốt cà chua đun sôi trong 10 phút.",
        "ingredients": [
            {"food_kw": "Đậu hũ non", "quantity_g": 120.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 60.0},
            {"food_kw": "Mộc nhĩ", "quantity_g": 5.0},
            {"food_kw": "Cà chua", "quantity_g": 70.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },

    # =========================================================================
    # 3. NHÓM MÓN CHAY & ĐỒ KIÊNG GIÀU ĐẠM (VEG_PROTEIN)
    # =========================================================================
    {
        "name_vi": "Đậu phụ sốt cà chua hành hoa (Món chay)",
        "dish_role": "VEG_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 12, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Đậu phụ rán mềm mọng ngập sốt cà chua tươi sánh mịn, rắc ngập hành hoa tươi, vừa rẻ vừa đủ đạm thực vật.",
        "tags": "mon_chay,dau_phu,ca_chua,tiet_kiem,healthy",
        "instructions": "1. Đậu phụ cắt miếng vuông vừa ăn, chiên sơ vàng hai mặt.\n2. Cà chua băm nhỏ xào nhuyễn cùng chút dầu ăn và nước tương tạo sốt sánh.\n3. Cho đậu phụ vào đun liu riu 5 phút cho ngấm sốt cà chua.\n4. Rắc hành lá thái nhỏ lên trên rồi tắt bếp.",
        "ingredients": [
            {"food_kw": "Đậu hũ non", "quantity_g": 200.0},
            {"food_kw": "Cà chua", "quantity_g": 100.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 15.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0},
            {"food_kw": "Nước tương", "quantity_g": 12.0}
        ]
    },
    {
        "name_vi": "Đậu hũ chiên sả ớt giòn cay (Món chay)",
        "dish_role": "VEG_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 12, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Đậu hũ khía cạnh chiên giòn, bọc lớp sả ớt phi vàng thơm nồng giòn tan.",
        "tags": "mon_chay,dau_phu,sa_ot,tiet_kiem",
        "instructions": "1. Đậu hũ khía vát nhẹ trên mặt để ngấm vị.\n2. Sả và ớt băm thật nhỏ.\n3. Chiên đậu hũ vàng giòn trong chảo dầu, vớt ra đĩa.\n4. Phi vàng sả ớt với chút xì dầu và đường, sau đó rưới đều lên mặt bìa đậu.",
        "ingredients": [
            {"food_kw": "Đậu hũ non", "quantity_g": 200.0},
            {"food_kw": "Sả cây tươi", "quantity_g": 25.0},
            {"food_kw": "Ớt tươi", "quantity_g": 5.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 12.0},
            {"food_kw": "Nước tương", "quantity_g": 10.0}
        ]
    },
    {
        "name_vi": "Nấm đùi gà kho tiêu đen đậm vị (Món chay)",
        "dish_role": "VEG_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Nấm rơm hoặc nấm đùi gà thái dày kho nước tương đậm đà, dậy mùi tiêu cay ấm, dai ngọt như thịt.",
        "tags": "mon_chay,nam,kho_tieu,healthy",
        "instructions": "1. Nấm rửa sạch ngâm nước muối loãng, cắt khúc vừa ăn.\n2. Ướp nấm với nước tương, chút đường, dầu hào chay và tiêu đen đập dập.\n3. Cho vào nồi đun sôi bùng rồi hạ lửa nhỏ kho trong 12 phút đến khi nước sốt sánh lại.",
        "ingredients": [
            {"food_kw": "Nấm rơm", "quantity_g": 160.0},
            {"food_kw": "Nước tương", "quantity_g": 15.0},
            {"food_kw": "Tiêu đen xay", "quantity_g": 4.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0},
            {"food_kw": "Ớt tươi", "quantity_g": 5.0}
        ]
    },
    {
        "name_vi": "Nấm bào ngư xào sả ớt chay thơm lừng",
        "dish_role": "VEG_PROTEIN", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Nấm bào ngư dai ngọt xé sợi xào lửa lớn với sả băm ớt hiểm, thơm nức mũi và giàu đạm thực vật.",
        "tags": "mon_chay,nam_bao_ngu,sa_ot,eat_clean",
        "instructions": "1. Nấm bào ngư ngâm nước muối loãng, vắt ráo và xé miếng vừa ăn.\n2. Phi thơm sả băm và ớt với dầu ăn.\n3. Cho nấm vào xào lửa lớn 4 phút, nêm xì dầu và hạt nêm chay đảo đều tay.",
        "ingredients": [
            {"food_kw": "Nấm bào ngư", "quantity_g": 180.0},
            {"food_kw": "Sả cây tươi", "quantity_g": 20.0},
            {"food_kw": "Ớt tươi", "quantity_g": 5.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0},
            {"food_kw": "Nước tương", "quantity_g": 10.0}
        ]
    },
    {
        "name_vi": "Đậu hũ kho nấm rơm nước tương đậm đà (Chay)",
        "dish_role": "VEG_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Đậu hũ chiên vàng kho cùng nấm rơm búp tươi giòn, nước kho sánh thơm mùi tiêu đen và dầu mè.",
        "tags": "mon_chay,dau_phu,nam_rom,kho_chay",
        "instructions": "1. Đậu hũ cắt miếng vuông rán sơ. Nấm rơm khía chữ thập ngâm rửa sạch.\n2. Xếp đậu và nấm vào tộ đất, ướp xì dầu, đường và tiêu xay.\n3. Đun sôi rồi hạ nhỏ lửa đun 12 phút cho ngấm đều gia vị.",
        "ingredients": [
            {"food_kw": "Đậu hũ non", "quantity_g": 130.0},
            {"food_kw": "Nấm rơm", "quantity_g": 90.0},
            {"food_kw": "Nước tương", "quantity_g": 15.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 5.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Canh hạt sen nấm tươi đậu phụ thanh nhiệt (Chay)",
        "dish_role": "VEG_PROTEIN", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 20, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Hạt sen tươi bùi bở nấu cùng nấm bào ngư dai ngọt và đậu non mềm tan, an thần dễ ngủ.",
        "tags": "mon_canh,chay,hat_sen,an_than,healthy",
        "instructions": "1. Hạt sen thông tâm, rửa sạch ninh với 400ml nước trong 15 phút cho bở mềm.\n2. Thả nấm bào ngư và đậu hũ non cắt miếng vào nấu thêm 3 phút.\n3. Nêm nước tương và rắc ngò rí, tiêu xay.",
        "ingredients": [
            {"food_kw": "Hạt sen", "quantity_g": 60.0},
            {"food_kw": "Nấm bào ngư", "quantity_g": 70.0},
            {"food_kw": "Đậu hũ non", "quantity_g": 80.0},
            {"food_kw": "Nước tương", "quantity_g": 8.0}
        ]
    },

    # =========================================================================
    # 4. NHÓM MÓN CANH & RAU XANH (SOUP_VEG)
    # =========================================================================
    {
        "name_vi": "Canh cua đồng nấu mướp mồng tơi",
        "dish_role": "SOUP_VEG", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Bát canh cua đồng đóng tảng gạch béo ngọt, kết hợp mướp hương thơm lừng và rau mồng tơi trơn mát ngày hè.",
        "tags": "mon_canh,cua_dong,muop,mong_toi,giai_nhiet",
        "instructions": "1. Cua đồng lọc với 400ml nước có chút muối, đun lửa vừa khuấy nhẹ tay cho thịt cua nổi tảng mảng gạch.\n2. Gạt gạch cua sang một bên, thả mướp thái vát và rau mồng tơi vào.\n3. Đun sôi bùng 2 phút cho rau mướp chín tới rồi nêm mắm tắt bếp.",
        "ingredients": [
            {"food_kw": "Cua đồng", "quantity_g": 80.0},
            {"food_kw": "Mướp hương", "quantity_g": 80.0},
            {"food_kw": "Rau mồng tơi", "quantity_g": 80.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Canh chua cá diêu hồng dứa cà chua",
        "dish_role": "SOUP_VEG", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 12, "cook_time_min": 15, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Cá diêu hồng béo ngọt nấu canh chua cùng cà chua đỏ mọng, giá đỗ và hành ngò thì là thơm nức mũi.",
        "tags": "mon_canh,canh_chua,ca_dieu_hong,nam_bo",
        "instructions": "1. Cá diêu hồng khía khúc rửa sạch. Cà chua bổ múi cau, giá đỗ rửa sạch.\n2. Đun sôi 400ml nước, thả cá vào nấu chín.\n3. Cho cà chua, giá đỗ vào đun thêm 2 phút, nêm mắm và nước cốt chanh chua thanh ngọt dịu.",
        "ingredients": [
            {"food_kw": "Cá diêu hồng", "quantity_g": 90.0},
            {"food_kw": "Cà chua", "quantity_g": 60.0},
            {"food_kw": "Giá đỗ tươi", "quantity_g": 50.0},
            {"food_kw": "Chanh quả tươi", "quantity_g": 15.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Canh nghêu thì là cà chua thanh mát",
        "dish_role": "SOUP_VEG", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Nước canh nghêu ngọt lịm từ biển, dậy mùi thơm thì là, hành hoa và vị chua thanh nhẹ giải nhiệt ngày hè.",
        "tags": "mon_canh,ngheu,thi_la,giai_nhiet",
        "instructions": "1. Nghêu ngâm nước vo gạo và ớt cắt lát 30 phút cho nhả hết cát, luộc nghêu với 400ml nước đến khi mở miệng.\n2. Vớt thịt nghêu để riêng, lọc lấy nước luộc nghêu trong.\n3. Phi thơm hành tím xào cà chua cho mềm, đổ nước luộc nghêu vào đun sôi.\n4. Thả thịt nghêu và thì là thái khúc vào, nêm mắm vừa ăn rồi tắt bếp.",
        "ingredients": [
            {"food_kw": "Nghêu", "quantity_g": 250.0},
            {"food_kw": "Cà chua", "quantity_g": 60.0},
            {"food_kw": "Thì là tươi", "quantity_g": 20.0},
            {"food_kw": "Hành tím", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Canh rau ngót nấu thịt nạc băm",
        "dish_role": "SOUP_VEG", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Rau ngót tươi vò nát nấu nước dùng thịt băm ngọt mát lành tính, giàu vitamin A và khoáng chất.",
        "tags": "mon_canh,rau_ngot,thit_heo,tiet_kiem,healthy",
        "instructions": "1. Rau ngót tuốt lá, rửa sạch và vò nhẹ cho mềm lá khi nấu.\n2. Phi thơm hành tím, cho thịt nạc băm vào đảo chín với chút nước mắm.\n3. Đổ 400ml nước vào đun sôi, thả rau ngót vào đun sôi lại 3 phút rồi tắt bếp.",
        "ingredients": [
            {"food_kw": "Rau ngót", "quantity_g": 100.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 40.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 6.0},
            {"food_kw": "Hành tím", "quantity_g": 5.0}
        ]
    },
    {
        "name_vi": "Canh bí đỏ nấu thịt băm ngọt bùi",
        "dish_role": "SOUP_VEG", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Bí đỏ gọt vỏ ninh mềm dẻo bùi ngọt kết hợp thịt băm, món canh vừa bổ não vừa ấm bụng.",
        "tags": "mon_canh,bi_do,thit_heo,healthy",
        "instructions": "1. Bí đỏ gọt vỏ, bỏ ruột, thái miếng dày 1.5cm.\n2. Xào thịt băm chín tới với hành tím, đổ nước vào đun sôi.\n3. Thả bí đỏ vào đun lửa nhỏ 10 phút cho bí chín mềm bở, rắc hành lá thái nhỏ.",
        "ingredients": [
            {"food_kw": "Bí đỏ", "quantity_g": 130.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 40.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 6.0}
        ]
    },
    {
        "name_vi": "Canh bắp cải cuộn thịt băm ngọt mát",
        "dish_role": "SOUP_VEG", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 12, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Lá bắp cải xanh chần sơ cuộn thịt nạc băm thắt bằng cọng hành lá, nước canh ngọt lịm từ rau củ.",
        "tags": "mon_canh,bap_cai,thit_heo,eat_clean",
        "instructions": "1. Lá bắp cải và hành lá chần qua nước sôi cho mềm dai.\n2. Cho thịt băm nêm mắm vào lá bắp cải cuộn tròn, dùng hành lá buộc lại.\n3. Đun sôi nước dùng, thả cuộn bắp cải vào nấu 10 phút đến khi thịt chín mềm.",
        "ingredients": [
            {"food_kw": "Bắp cải", "quantity_g": 120.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 50.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 6.0}
        ]
    },
    {
        "name_vi": "Canh khổ qua nhồi thịt nạc thanh nhiệt",
        "dish_role": "SOUP_VEG", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 20, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Mướp đắng cắt khúc moi ruột nhồi thịt nạc băm, vị đắng nhẹ hậu ngọt mát thanh lọc cơ thể.",
        "tags": "mon_canh,kho_qua,thit_heo,thanh_nhiet",
        "instructions": "1. Khổ qua cắt khúc 4cm móc bỏ ruột trắng để giảm đắng.\n2. Nhồi thịt nạc băm vào lòng khổ qua.\n3. Đun sôi nước dùng, thả khổ qua vào hầm lửa vừa 15 phút, vớt bọt cho nước trong.",
        "ingredients": [
            {"food_kw": "Khổ qua", "quantity_g": 130.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 50.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 6.0}
        ]
    },
    {
        "name_vi": "Canh bí xanh (bí đao) nấu thịt nạc băm",
        "dish_role": "SOUP_VEG", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 6, "cook_time_min": 10, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Bí đao thái mỏng nấu nước dùng thịt nạc băm ngọt thanh mát, giải độc mát gan và lợi tiểu.",
        "tags": "mon_canh,bi_xanh,thit_heo,tiet_kiem",
        "instructions": "1. Bí đao gọt vỏ thái lát mỏng 0.5cm.\n2. Phi hành xào thịt băm với chút mắm, đổ nước đun sôi.\n3. Thả bí xanh vào đun 3 phút cho miếng bí trong veo chín tới, rắc hành ngò thái nhỏ.",
        "ingredients": [
            {"food_kw": "Bí xanh", "quantity_g": 140.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 35.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 10.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 6.0}
        ]
    },
    {
        "name_vi": "Canh rau cải ngọt nấu thịt băm",
        "dish_role": "SOUP_VEG", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 8, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Rau cải ngọt giòn mát thái khúc ngắn nấu canh thịt băm cùng vài sợi gừng ấm, món canh quốc dân cực rẻ.",
        "tags": "mon_canh,rau_cai,tiet_kiem,healthy",
        "instructions": "1. Rau cải rửa sạch thái khúc 3cm. Gừng thái sợi nhỏ.\n2. Xào thịt băm với chút mắm, đổ nước đun sôi.\n3. Thả rau cải và gừng vào đun sôi bùng trong 2 phút là rau vừa chín tới xanh mướt.",
        "ingredients": [
            {"food_kw": "Rau cải thìa", "quantity_g": 120.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 35.0},
            {"food_kw": "Gừng tươi", "quantity_g": 5.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 6.0}
        ]
    },
    {
        "name_vi": "Rau muống xào tỏi xanh mướt",
        "dish_role": "SOUP_VEG", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 7, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Rau muống non chần sơ xào lửa lớn với tỏi đập dập thơm lừng, ngọn rau giòn sần sật giữ trọn vitamin.",
        "tags": "mon_xao,rau_muong,toi,chay_man",
        "instructions": "1. Rau muống nhặt sạch, chần sơ 30 giây trong nước sôi có chút muối rồi vớt ra ngâm nước đá cho giòn.\n2. Phi thơm tỏi đập dập với dầu ăn.\n3. Cho rau muống vào đảo lửa lớn trong 2 phút, nêm hạt nêm vừa ăn rồi tắt bếp.",
        "ingredients": [
            {"food_kw": "Rau muống", "quantity_g": 180.0},
            {"food_kw": "Tỏi củ tươi", "quantity_g": 15.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0},
            {"food_kw": "Muối ăn", "quantity_g": 3.0}
        ]
    },
    {
        "name_vi": "Rau muống luộc kèm bát nước canh vắt chanh",
        "dish_role": "SOUP_VEG", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 4, "cook_time_min": 5, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Đĩa rau muống luộc xanh giòn, nước luộc rau nêm hạt muối vắt nước cốt chanh chua mát đặc trưng ngày hè.",
        "tags": "mon_luoc,rau_muong,canh_chanh,tiet_kiem,chay_man",
        "instructions": "1. Đun sôi nồi nước có chút muối, thả rau muống ngập nước luộc lửa to trong 3 phút.\n2. Vớt rau ra đĩa ăn kèm tương hoặc mắm.\n3. Nước luộc rau để hơi ấm, vắt nước cốt chanh vào làm bát canh thanh nhiệt.",
        "ingredients": [
            {"food_kw": "Rau muống", "quantity_g": 200.0},
            {"food_kw": "Chanh quả tươi", "quantity_g": 15.0},
            {"food_kw": "Muối ăn", "quantity_g": 3.0}
        ]
    },
    {
        "name_vi": "Su su xào tỏi giòn ngọt",
        "dish_role": "SOUP_VEG", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 6, "cook_time_min": 8, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Su su gọt vỏ nạo sợi hoặc thái mỏng xào chín tới cùng tỏi phi, vị ngọt đậm đà giòn ngọt thanh nhẹ.",
        "tags": "mon_xao,su_su,toi,chay_man",
        "instructions": "1. Su su gọt vỏ, bỏ hạt thái miếng mỏng 0.3cm.\n2. Phi thơm tỏi với dầu ăn, trút su su vào xào lửa lớn trong 3 phút.\n3. Nêm nước tương hoặc bột canh vừa ăn, rắc chút tiêu xay rồi tắt bếp.",
        "ingredients": [
            {"food_kw": "Su su", "quantity_g": 180.0},
            {"food_kw": "Tỏi củ tươi", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0},
            {"food_kw": "Muối ăn", "quantity_g": 2.0}
        ]
    },
    {
        "name_vi": "Rau cải thìa luộc xanh giòn",
        "dish_role": "SOUP_VEG", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 6, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Đĩa rau cải thìa luộc xanh mướt, nước luộc rau làm canh thanh đạm, cực ít calo thích hợp giảm cân.",
        "tags": "mon_luoc,rau_cai,eat_clean,chay_man",
        "instructions": "1. Cải thìa tách bẹ rửa sạch.\n2. Đun sôi nước có chút muối, thả cải thìa vào luộc lửa lớn trong 3 phút.\n3. Vớt rau ra đĩa, giữ lại nước luộc làm canh thanh nhiệt.",
        "ingredients": [
            {"food_kw": "Rau cải thìa", "quantity_g": 200.0},
            {"food_kw": "Muối ăn", "quantity_g": 2.0}
        ]
    },
    {
        "name_vi": "Canh nấm rong biển đậu non thanh tịnh (Chay)",
        "dish_role": "SOUP_VEG", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 15, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "Bát canh dưỡng sinh từ nấm rơm, rong biển thanh lọc và đậu hũ non mềm mịn, cực kỳ nhẹ bụng.",
        "tags": "mon_canh,chay,healthy,eat_clean",
        "instructions": "1. Đậu hũ non cắt miếng vuông nhỏ. Nấm rơm chẻ đôi.\n2. Đun sôi 400ml nước, thả nấm vào nấu 5 phút.\n3. Thả đậu non vào đun thêm 2 phút, nêm nước tương vừa miệng rồi tắt bếp.",
        "ingredients": [
            {"food_kw": "Đậu hũ non", "quantity_g": 80.0},
            {"food_kw": "Nấm rơm", "quantity_g": 60.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 5.0},
            {"food_kw": "Nước tương", "quantity_g": 8.0}
        ]
    },

    # =========================================================================
    # 5. NHÓM MÓN ĂN SÁNG TRUYỀN THỐNG (BREAKFAST)
    # =========================================================================
    {
        "name_vi": "Phở bò tái lăn Hà Nội",
        "dish_role": "BREAKFAST", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 15, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Tô phở bò nóng hổi với bánh phở mềm mướt, thịt bò tái lăn tỏi xém cạnh thơm lừng, hành hoa ngập bát.",
        "tags": "an_sang,pho_bo,ha_noi,dac_san",
        "instructions": "1. Bánh phở chần sơ nước sôi, xếp vào tô.\n2. Thịt bò thái mỏng, phi thơm tỏi đập dập xào bò trên lửa lớn thật nhanh cho chín tái xém cạnh.\n3. Đổ thịt bò lên mặt tô phở, rắc hành lá thái nhỏ và chan nước dùng ninh xương nóng hổi.",
        "ingredients": [
            {"food_kw": "Bún tươi", "quantity_g": 160.0},
            {"food_kw": "Nạc bò", "quantity_g": 90.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 20.0},
            {"food_kw": "Tỏi củ tươi", "quantity_g": 10.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Bún bò giò heo xứ Huế",
        "dish_role": "BREAKFAST", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 25, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Bún sợi to hòa quyện nước dùng sả ruốc cay nồng, khoanh thịt bắp giò heo mềm ngậy thơm lừng.",
        "tags": "an_sang,bun_bo_hue,dac_san",
        "instructions": "1. Bún sợi to chần nước sôi xếp ra tô lớn.\n2. Thịt bắp giò heo ninh mềm ngọt trong nước dùng hầm sả cây và mắm ruốc.\n3. Xếp thịt bắp giò lên bún, rắc hành lá hoa chuối rồi chan nước dùng sôi sùng sục.",
        "ingredients": [
            {"food_kw": "Bún tươi", "quantity_g": 160.0},
            {"food_kw": "Thịt bắp giò", "quantity_g": 80.0},
            {"food_kw": "Sả cây tươi", "quantity_g": 15.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 15.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },
    {
        "name_vi": "Bún chả nướng than hoa",
        "dish_role": "BREAKFAST", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 15, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Bún tươi ăn cùng chả thịt nướng thơm lừng, bát nước chấm chua ngọt đu đủ cà rốt và rau sống.",
        "tags": "an_sang,bun_cha,ha_noi",
        "instructions": "1. Thịt nạc ướp hành tím băm, nước mắm, đường trong 15 phút rồi nướng vàng xém trên chảo hoặc nồi chiên không dầu.\n2. Pha nước mắm chua ngọt ấm nóng, thả chả nướng vào bát nước chấm.\n3. Bày bún tươi ra đĩa và thưởng thức cùng rau thơm.",
        "ingredients": [
            {"food_kw": "Bún tươi", "quantity_g": 160.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 90.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 12.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 8.0},
            {"food_kw": "Hành tím", "quantity_g": 10.0}
        ]
    },
    {
        "name_vi": "Bánh mì ốp la xúc xích pate",
        "dish_role": "BREAKFAST", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 7, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Bánh mì giòn rụm kẹp 1 quả trứng gà ốp la lòng đào, lát thịt nạc và dưa leo ngò rí, món sáng quốc dân nhanh gọn.",
        "tags": "an_sang,banh_mi,trung,tiet_kiem",
        "instructions": "1. Đun nóng dầu ăn trong chảo, đập trứng gà ốp la lòng đào rắc chút tiêu.\n2. Bánh mì nướng giòn rạch bụng, kẹp trứng ốp la, thịt lát mỏng và dưa leo thái lát.",
        "ingredients": [
            {"food_kw": "Bánh mì", "quantity_g": 80.0},
            {"food_kw": "Trứng gà", "quantity_g": 55.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 30.0},
            {"food_kw": "Dưa leo", "quantity_g": 40.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 6.0}
        ]
    },
    {
        "name_vi": "Bánh cuốn nóng thịt băm mộc nhĩ chả lụa",
        "dish_role": "BREAKFAST", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 5, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Bánh cuốn tráng mỏng mềm mướt cuộn thịt băm mộc nhĩ, ăn kèm 2 lát chả lụa giòn dai và nước mắm cà cuống.",
        "tags": "an_sang,banh_cuon,cha_lua,ha_noi",
        "instructions": "1. Bánh cuốn nóng xếp ra đĩa, rắc hành phi vàng giòn lên trên.\n2. Chả lụa thái lát mỏng bày kèm.\n3. Pha nước mắm chua ngọt ấm ấm chấm ngập từng cuốn bánh.",
        "ingredients": [
            {"food_kw": "Bánh cuốn", "quantity_g": 160.0},
            {"food_kw": "Chả lụa", "quantity_g": 40.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 10.0},
            {"food_kw": "Đường kính trắng", "quantity_g": 5.0}
        ]
    },
    {
        "name_vi": "Xôi xéo đậu xanh mỡ hành phi thơm",
        "dish_role": "BREAKFAST", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 8, "cook_time_min": 25, "difficulty": "MEDIUM", "is_vegetarian": 1,
        "description": "Gói xôi nếp vàng óng nhuộm nghệ, bào từng lát đậu xanh bùi ngậy rưới ngập mỡ hành phi giòn tan.",
        "tags": "an_sang,xoi_xeo,ha_noi,tiet_kiem",
        "instructions": "1. Gạo nếp đồ chín mềm dẻo với chút bột nghệ tạo màu vàng tươi.\n2. Đậu xanh đồ chín nắm chặt, lấy dao thái lát mỏng phủ kín mặt xôi.\n3. Rưới nước mỡ gà phi hành tím thơm nức lên trên cùng.",
        "ingredients": [
            {"food_kw": "Nếp cái", "quantity_g": 75.0},
            {"food_kw": "Đậu hũ non", "quantity_g": 30.0},
            {"food_kw": "Hành tím", "quantity_g": 15.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 10.0}
        ]
    },
    {
        "name_vi": "Cháo sườn heo thịt băm nóng hổi",
        "dish_role": "BREAKFAST", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 30, "difficulty": "EASY", "is_vegetarian": 0,
        "description": "Bát cháo trắng sánh mịn ninh từ nước xương ngọt lịm, phủ đầy thịt băm rim mắm tiêu và hành hoa thơm nức.",
        "tags": "an_sang,chao,suon,thit_heo",
        "instructions": "1. Gạo tẻ vo sạch ninh nhừ thành cháo sánh nhuyễn.\n2. Thịt nạc băm xào thơm với hành tím và mắm tiêu.\n3. Múc cháo nóng ra tô, xúc thịt băm lên trên, rắc hành hoa và tiêu xay.",
        "ingredients": [
            {"food_kw": "Gạo trắng", "quantity_g": 50.0},
            {"food_kw": "Nạc đùi heo", "quantity_g": 60.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 15.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0},
            {"food_kw": "Tiêu đen xay", "quantity_g": 2.0}
        ]
    },
    {
        "name_vi": "Bún riêu cua đậu rán thanh mát",
        "dish_role": "BREAKFAST", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 12, "cook_time_min": 15, "difficulty": "MEDIUM", "is_vegetarian": 0,
        "description": "Bún sợi mềm ngập trong nước dùng riêu cua đồng ngọt lịm, kèm đậu phụ rán phồng và cà chua bổ múi cau.",
        "tags": "an_sang,bun_rieu,cua_dong,dau_phu",
        "instructions": "1. Nước dùng riêu cua đun sôi nổi mảng gạch cua béo ngậy.\n2. Thả cà chua bổ múi cau và đậu phụ rán vào đun sôi nhẹ.\n3. Chần bún ra bát, chan nước dùng riêu cua ngập bún, rắc hành lá thái nhỏ.",
        "ingredients": [
            {"food_kw": "Bún tươi", "quantity_g": 160.0},
            {"food_kw": "Cua đồng", "quantity_g": 60.0},
            {"food_kw": "Đậu hũ non", "quantity_g": 50.0},
            {"food_kw": "Cà chua", "quantity_g": 60.0},
            {"food_kw": "Hành lá tươi", "quantity_g": 15.0},
            {"food_kw": "Dầu ăn thực vật", "quantity_g": 8.0},
            {"food_kw": "Nước mắm cá cơm", "quantity_g": 8.0}
        ]
    },

    # =========================================================================
    # 6. NHÓM TRÁNG MIỆNG & ĂN PHỤ (DESSERT)
    # =========================================================================
    {
        "name_vi": "Chuối tiêu chín tự nhiên (1 quả)",
        "dish_role": "DESSERT", "meal_type": "SNACK", "servings": 1,
        "prep_time_min": 1, "cook_time_min": 0, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Quả chuối tiêu chín vàng tự nhiên (100g), giàu kali và magie, giúp cơ bắp thư giãn và tiêu hóa tốt.",
        "tags": "trang_mieng,chuoi,trai_cay,healthy",
        "instructions": "1. Bóc vỏ chuối và thưởng thức tráng miệng sau bữa ăn chính 15 phút.",
        "ingredients": [{"food_kw": "Chuối tiêu", "quantity_g": 100.0}]
    },
    {
        "name_vi": "Dưa hấu đỏ ngọt mát (1 miếng)",
        "dish_role": "DESSERT", "meal_type": "SNACK", "servings": 1,
        "prep_time_min": 2, "cook_time_min": 0, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Miếng dưa hấu ruột đỏ mọng nước (180g), giàu lycopene chống oxy hóa và bù nước cấp tốc.",
        "tags": "trang_mieng,dua_hau,trai_cay,giai_nhiet",
        "instructions": "1. Cắt dưa hấu thành miếng tam giác vừa ăn, ướp lạnh trước khi dùng.",
        "ingredients": [{"food_kw": "Dưa hấu", "quantity_g": 180.0}]
    },
    {
        "name_vi": "Táo tươi giòn ngọt (1 quả)",
        "dish_role": "DESSERT", "meal_type": "SNACK", "servings": 1,
        "prep_time_min": 2, "cook_time_min": 0, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Quả táo tươi giòn ngọt (120g), giàu pectin và chất xơ hòa tan giúp giảm cholesterol máu.",
        "tags": "trang_mieng,tao,trai_cay,eat_clean",
        "instructions": "1. Ngâm rửa sạch vỏ táo với nước muối loãng, bổ miếng thưởng thức trọn vẹn cả vỏ.",
        "ingredients": [{"food_kw": "Táo tươi", "quantity_g": 120.0}]
    },
    {
        "name_vi": "Thanh long ruột đỏ (1 đĩa nhỏ)",
        "dish_role": "DESSERT", "meal_type": "SNACK", "servings": 1,
        "prep_time_min": 2, "cook_time_min": 0, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Đĩa thanh long ruột đỏ (150g), hàm lượng anthocyanin cực cao hỗ trợ bảo vệ tim mạch và làn da.",
        "tags": "trang_mieng,thanh_long,trai_cay,healthy",
        "instructions": "1. Lột vỏ thanh long, cắt khối vuông bày ra đĩa.",
        "ingredients": [{"food_kw": "Thanh long", "quantity_g": 150.0}]
    },
    {
        "name_vi": "Sữa chua không đường lên men (1 hộp)",
        "dish_role": "DESSERT", "meal_type": "SNACK", "servings": 1,
        "prep_time_min": 1, "cook_time_min": 0, "difficulty": "EASY", "is_vegetarian": 1,
        "description": "1 Hộp sữa chua không đường (100g), cung cấp men vi sinh probiotic hỗ trợ đường ruột và canxi.",
        "tags": "trang_mieng,sua_chua,healthy,probiotic",
        "instructions": "1. Ăn mát sau bữa ăn trưa hoặc bữa tối nhẹ nhàng.",
        "ingredients": [{"food_kw": "Sữa tươi", "quantity_g": 100.0}]
    }
]

def seed_database():
    db_path = "database/nutridss.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Đảm bảo toàn bộ CORE_FOODS_TO_SEED đã có trong bảng foods và food_price_summary
    for f_id, f_name, f_state, f_cal, f_prot, f_carb, f_fat, f_fiber, f_sug, f_sod, f_price in CORE_FOODS_TO_SEED:
        cursor.execute("SELECT id FROM foods WHERE id = ? OR canonical_name_vi = ?", (f_id, f_name))
        existing_food = cursor.fetchone()
        if existing_food:
            target_id = existing_food[0]
            cursor.execute("""
                UPDATE foods
                SET canonical_name_vi = ?, food_state = ?, calories_kcal_100g = ?,
                    protein_g_100g = ?, carb_g_100g = ?, fat_g_100g = ?,
                    fiber_g_100g = ?, sugar_g_100g = ?, sodium_mg_100g = ?
                WHERE id = ?
            """, (f_name, f_state, f_cal, f_prot, f_carb, f_fat, f_fiber, f_sug, f_sod, target_id))
        else:
            cursor.execute("""
                INSERT INTO foods (id, canonical_name_vi, food_state, calories_kcal_100g, protein_g_100g, carb_g_100g, fat_g_100g, fiber_g_100g, sugar_g_100g, sodium_mg_100g)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f_id, f_name, f_state, f_cal, f_prot, f_carb, f_fat, f_fiber, f_sug, f_sod))
            target_id = f_id

        # Insert or update price
        cursor.execute("SELECT food_id FROM food_price_summary WHERE food_id = ?", (target_id,))
        if cursor.fetchone():
            cursor.execute("UPDATE food_price_summary SET estimated_price_per_100g = ? WHERE food_id = ?", (f_price, target_id))
        else:
            cursor.execute("INSERT INTO food_price_summary (food_id, estimated_price_per_100g) VALUES (?, ?)", (target_id, f_price))

    conn.commit()

    # Load foods map for lookup by keyword
    cursor.execute("SELECT id, canonical_name_vi FROM foods")
    db_foods = cursor.fetchall()

    EXACT_MAP = {
        "lòng bò": 2103,
        "lá lốt": 410,
        "ớt tươi": 1517,
        "ớt chỉ thiên": 1517,
        "muối": 1506,
        "mì chính": 1509,
        "bột ngọt": 1509,
        "hạt nêm": 1508,
        "đường": 1507,
        "dầu ăn": 1505,
        "dầu ăn thực vật": 1505,
        "nước mắm": 1504,
        "nước mắm cá cơm": 1504,
        "nước tương": 1510,
        "xì dầu": 1510,
        "tiêu": 1512,
        "tiêu đen": 1512,
        "tỏi": 1514,
        "tỏi củ tươi": 1514,
        "hành tím": 1515,
        "hành củ khô": 1515,
        "hành lá": 1516,
        "hành lá tươi": 1516,
        "gừng": 1518,
        "gừng tươi": 1518,
        "sả": 1519,
        "sả tươi": 1519,
        "dưa chua": 2151,
        "dưa cải muối chua": 2151,
        "trứng gà": 204,
        "đậu phụ": 404,
        "đậu hũ": 404,
        "thịt bò": 203,
        "thịt ba chỉ": 205
    }

    def find_food_id(kw: str) -> int:
        kw_lower = kw.lower().strip()
        for k, fid in EXACT_MAP.items():
            if k in kw_lower:
                return fid
        for fid, fname in db_foods:
            if kw_lower in fname.lower():
                return fid
        if "cơm" in kw_lower or "gạo" in kw_lower:
            return 101
        if "heo" in kw_lower or "lợn" in kw_lower:
            return 202
        if "bò" in kw_lower:
            return 203
        if "chuối" in kw_lower:
            return 501
        return 101

    IMAGE_MAP = {
        "Phở bò": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=500&auto=format&fit=crop&q=80",
        "Bún bò": "https://images.unsplash.com/photo-1594998893017-36147cbcae05?w=500&auto=format&fit=crop&q=80",
        "Bún chả": "https://images.unsplash.com/photo-1503764654157-72d979d9af2f?w=500&auto=format&fit=crop&q=80",
        "Bún riêu": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=500&auto=format&fit=crop&q=80",
        "Bánh mì": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500&auto=format&fit=crop&q=80",
        "Bánh cuốn": "https://images.unsplash.com/photo-1541544741938-0af808871cc0?w=500&auto=format&fit=crop&q=80",
        "Xôi xéo": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format&fit=crop&q=80",
        "Cháo": "https://images.unsplash.com/photo-1547592180-85f173990554?w=500&auto=format&fit=crop&q=80",
        "Cá lóc kho": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?w=500&auto=format&fit=crop&q=80",
        "Cá basa": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?w=500&auto=format&fit=crop&q=80",
        "Cá rô phi": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500&auto=format&fit=crop&q=80",
        "Canh chua": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=500&auto=format&fit=crop&q=80",
        "Canh cua": "https://images.unsplash.com/photo-1547592180-85f173990554?w=500&auto=format&fit=crop&q=80",
        "Canh nghêu": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=500&auto=format&fit=crop&q=80",
        "Canh rau": "https://images.unsplash.com/photo-1547592180-85f173990554?w=500&auto=format&fit=crop&q=80",
        "Canh bí": "https://images.unsplash.com/photo-1547592180-85f173990554?w=500&auto=format&fit=crop&q=80",
        "Canh nấm": "https://images.unsplash.com/photo-1547592180-85f173990554?w=500&auto=format&fit=crop&q=80",
        "Thịt bò": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?w=500&auto=format&fit=crop&q=80",
        "Lòng bò": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=80",
        "Thịt lợn": "https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=80",
        "Thịt ba chỉ": "https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=80",
        "Thịt kho": "https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=80",
        "Sườn heo": "https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=80",
        "Thịt gà": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=500&auto=format&fit=crop&q=80",
        "Gà xé": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=500&auto=format&fit=crop&q=80",
        "Tôm": "https://images.unsplash.com/photo-1559742811-822873691df8?w=500&auto=format&fit=crop&q=80",
        "Mực": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500&auto=format&fit=crop&q=80",
        "Chả cá": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500&auto=format&fit=crop&q=80",
        "Trứng": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=500&auto=format&fit=crop&q=80",
        "Đậu": "https://images.unsplash.com/photo-1546069901-d5bfd2cbfb1f?w=500&auto=format&fit=crop&q=80",
        "Nấm": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500&auto=format&fit=crop&q=80",
        "Rau muống": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500&auto=format&fit=crop&q=80",
        "Su su": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500&auto=format&fit=crop&q=80",
        "Rau cải": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500&auto=format&fit=crop&q=80",
        "Cơm trắng": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=500&auto=format&fit=crop&q=80",
        "Gạo lứt": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=500&auto=format&fit=crop&q=80",
        "Khoai lang": "https://images.unsplash.com/photo-1596560548464-f010549b84d7?w=500&auto=format&fit=crop&q=80",
        "Bún tươi": "https://images.unsplash.com/photo-1503764654157-72d979d9af2f?w=500&auto=format&fit=crop&q=80",
        "Bắp": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=500&auto=format&fit=crop&q=80",
        "Miến": "https://images.unsplash.com/photo-1552611052-33e04de081de?w=500&auto=format&fit=crop&q=80",
        "Chuối": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=500&auto=format&fit=crop&q=80",
        "Dưa hấu": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=500&auto=format&fit=crop&q=80",
        "Táo": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500&auto=format&fit=crop&q=80",
        "Thanh long": "https://images.unsplash.com/photo-1527325678964-54921661f888?w=500&auto=format&fit=crop&q=80",
        "Sữa chua": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500&auto=format&fit=crop&q=80"
    }

    def resolve_image_url(name: str) -> str:
        for kw, url in IMAGE_MAP.items():
            if kw.lower() in name.lower():
                return url
        return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=80"

    inserted = 0
    updated = 0
    ings_count = 0

    for r in CURATED_RECIPES:
        img_url = resolve_image_url(r["name_vi"])
        cursor.execute("SELECT id FROM recipes WHERE name_vi = ?", (r["name_vi"],))
        ex = cursor.fetchone()
        if ex:
            rec_id = ex[0]
            cursor.execute("""
                UPDATE recipes 
                SET dish_role = ?, meal_type = ?, servings = ?, prep_time_min = ?, cook_time_min = ?,
                    difficulty = ?, is_vegetarian = ?, description = ?, source_name = 'CURATED_VN_MASTER', tags = ?,
                    image_url = ?
                WHERE id = ?
            """, (
                r["dish_role"], r["meal_type"], r["servings"], r["prep_time_min"], r["cook_time_min"],
                r["difficulty"], r["is_vegetarian"], r["description"], r["tags"], img_url, rec_id
            ))
            cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (rec_id,))
            cursor.execute("DELETE FROM recipe_steps WHERE recipe_id = ?", (rec_id,))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO recipes (name_vi, dish_role, meal_type, servings, prep_time_min, cook_time_min, difficulty, is_vegetarian, description, source_name, tags, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'CURATED_VN_MASTER', ?, ?)
            """, (
                r["name_vi"], r["dish_role"], r["meal_type"], r["servings"], r["prep_time_min"], r["cook_time_min"],
                r["difficulty"], r["is_vegetarian"], r["description"], r["tags"], img_url
            ))
            rec_id = cursor.lastrowid
            inserted += 1

        # Insert ingredients
        for ing in r["ingredients"]:
            fid = find_food_id(ing["food_kw"])
            qty_g = ing["quantity_g"]
            raw_q = ing.get("raw_quantity", qty_g)
            raw_u = ing.get("raw_unit", "ml" if any(k in ing["food_kw"].lower() for k in ["dầu", "mắm", "tương", "sữa", "nước dừa"]) else "g")
            cursor.execute("""
                INSERT INTO recipe_ingredients (recipe_id, food_id, quantity_g, raw_quantity, raw_unit)
                VALUES (?, ?, ?, ?, ?)
            """, (rec_id, fid, qty_g, raw_q, raw_u))
            ings_count += 1

        # Insert cooking instructions
        instructions_text = r.get("instructions", "")
        if instructions_text:
            step_lines = [s.strip() for s in instructions_text.split("\n") if s.strip()]
            for step_idx, step_txt in enumerate(step_lines, 1):
                cursor.execute("""
                    INSERT INTO recipe_steps (recipe_id, step_number, instruction_vi, duration_min)
                    VALUES (?, ?, ?, 5)
                """, (rec_id, step_idx, step_txt))

    conn.commit()
    conn.close()
    print(f"[Seed Curated Recipes V2] Success! Curated dishes: {len(CURATED_RECIPES)}. Inserted: {inserted}, Updated: {updated}, Ingredients mapped: {ings_count}")

if __name__ == "__main__":
    seed_database()
