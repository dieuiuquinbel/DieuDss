import json
from unidecode import unidecode

# Load files
with open('ingredient_knowledge_base.json', 'r', encoding='utf-8') as f:
    ingredients = json.load(f)

with open('data/recipes_detail.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

# Tạo mapping dictionary: name_vi -> {id, category, name_en}
ingredient_map = {}
for ing in ingredients:
    name = ing['name_vi'].lower().strip()
    ingredient_map[name] = {
        'id': ing['id'],
        'category': ing.get('category', ''),
        'name_en': ing.get('name_en', '')
    }

# Normalize Vietnamese text
def normalize(text):
    return unidecode(text).lower()

# Process recipes
dishes = []
seen_dishes = set()  # Track các món đã thêm

for idx, recipe in enumerate(recipes, start=1):
    dish_name = recipe['dish_name'].lower().strip()
    
    # Skip nếu món này đã có
    if dish_name in seen_dishes:
        continue
    
    seen_dishes.add(dish_name)
    
    dish = {
        "id": f"dish{str(len(dishes) + 1).zfill(4)}",
        "name_vi": recipe['dish_name'],
        "name_normalized": normalize(recipe['dish_name']),
        "category": normalize(recipe.get('category', '')),
        "ingredients": [],
        "type": "dish"
    }
    
    # Tính threshold cho 30% đầu
    total_ingredients = len(recipe['ingredients'])
    critical_threshold = int(total_ingredients * 0.3)
    normal_threshold = int(total_ingredients * 0.7)
    
    for ing_idx, ing in enumerate(recipe['ingredients']):
        ing_name = ing['name'].lower().strip()
        ingredient_data = ingredient_map.get(ing_name, None)
        
        # Xác định importance: 30% đầu là critical, còn lại là normal
        importance = 3 if ing_idx < critical_threshold else 2 if ing_idx < normal_threshold else 1
        
        dish['ingredients'].append({
            "ingredient_id": ingredient_data['id'],
            "name_vi": ing['name'],
            "name_en": ingredient_data['name_en'],
            "quantity": ing.get('quantity', 0),
            "unit": ing.get('unit', ''),
            "category": ingredient_data['category'],
            "importance": importance,
            "name_normalized": normalize(ing['name'])
        })
    
    dishes.append(dish)

# Save output
with open('dish_knowledge_base.json', 'w', encoding='utf-8') as f:
    json.dump(dishes, f, ensure_ascii=False, indent=2)

print(f"✅ Đã tạo {len(dishes)} món ăn trong dish_knowledge_base.json")
