import json
from unidecode import unidecode
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm

# ===== LOAD MODELS =====
print("Loading classification model...")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    device_map="auto",
    torch_dtype=torch.float16
)
print("Models loaded.\n")

# ===== CATEGORIES =====
CATEGORIES = {
    'alcoholic_beverages': 'Đồ uống có cồn như rượu vang, bia, rượu mạnh, sake, whisky, vodka',
    'beverages': 'Đồ uống như nước ngọt, nước ép, trà, cà phê, nước khoáng, sinh tố',
    'cakes': 'Bánh ngọt như bánh kem, bánh bông lan, bánh quy, bánh su kem, bánh tart',
    'candies': 'Kẹo như kẹo dẻo, kẹo cứng, socola, kẹo mút, kẹo cao su',
    'cereals_grains': 'Ngũ cốc như yến mạch, cornflakes, muesli, ngũ cốc ăn sáng',
    'cold_cuts:_sausages_&_ham': 'Thịt nguội như xúc xích, giăm bông, salami, bacon, thịt hun khói',
    'dried_fruits': 'Trái cây sấy khô như nho khô, mơ khô, táo sấy, chuối sấy, việt quất khô',
    'fresh_fruits': 'Trái cây tươi như chuối, táo, cam, xoài, dứa, đu đủ, bưởi, nho, dâu tây',
    'fresh_meat': 'Thịt tươi như thịt gà, thịt heo, thịt bò, thịt vịt, sườn, ba chỉ',
    'fruit_jam': 'Mứt trái cây như mứt dâu, mứt cam, mứt việt quất, mứt đào, mứt táo',
    'grains_staples': 'Ngũ cốc và lương thực như gạo, bột mì, nui, miến, bún, phở, mì ống',
    'ice_cream_&_cheese': 'Kem và phô mai như kem que, kem hộp, phô mai lát, phô mai que, mascarpone',
    'instant_foods': 'Đồ ăn liền như mì gói, phở gói, cháo ăn liền, súp gói, cơm hộp',
    'milk': 'Sữa như sữa tươi, sữa đặc, sữa bột, sữa hạt, sữa đậu nành',
    'seafood_&_fish_balls': 'Hải sản và chả cá như tôm, cá, mực, nghêu, chả cá, viên cá, cua, ghẹ',
    'seasonings': 'Gia vị như muối, đường, nước mắm, tương, hạt nêm, tiêu, ớt, tỏi, gừng, dầu ăn',
    'snacks': 'Đồ ăn vặt như snack khoai tây, bánh quy mặn, popcorn, bánh tráng, hạt điều rang',
    'vegetables': 'Rau củ và rau thơm như cà chua, bí, củ cải, khoai, bắp, húng, ngò, rau mùi',
    'yogurt': 'Sữa chua như sữa chua uống, sữa chua ăn, sữa chua Hy Lạp, sữa chua có đường'
}

# ===== FUNCTIONS =====
def normalize_text(text):
    """Bỏ dấu tiếng Việt"""
    return unidecode(text).lower()

def translate_vi_to_en(text):
    """Dịch tiếng Việt sang tiếng Anh bằng Qwen"""
    try:
        prompt = f"""Translate the Vietnamese ingredient name to English. Only return the English name, nothing else.

        Examples:
        - Cà chua -> Tomato
        - Thịt heo -> Pork
        - Bắp cải -> Cabbage
        - Húng lủi -> Peppermint
        
        Translate: {text} ->"""

        messages = [{"role": "user", "content": prompt}]
        text_input = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([text_input], return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=30,
                temperature=0.1
            )
        
        response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
        return response.strip()
    
    except Exception as e:
        return ""

def classify_category(ingredient_name):
    """Phân loại nguyên liệu bằng Qwen model"""
    categories_text = '\n'.join([f"- {k}: {v}" for k, v in CATEGORIES.items()])
    
    messages = [
        {
            "role": "system",
            "content": "Bạn là chuyên gia phân loại nguyên liệu ẩm thực Việt Nam. Nhiệm vụ của bạn là phân loại nguyên liệu vào các nhóm đã định sẵn dựa trên loại và cách sử dụng."
        },
        {
            "role": "user",
            "content": f"""Phân loại nguyên liệu "{ingredient_name}" vào MỘT trong các nhóm sau:

            {categories_text}

            HƯỚNG DẪN:
            - Phân tích xem đây là loại nguyên liệu gì (rau thơm, rau củ, thịt, gia vị, v.v.)
            - Chỉ trả về mã nhóm (ví dụ: rau-thom, gia-vi, thit-ca)
            - KHÔNG thêm giải thích, dấu câu, hoặc bất kỳ văn bản nào khác
            - Nếu không chắc chắn, chọn nhóm phù hợp nhất dựa trên cách sử dụng phổ biến

            VÍ DỤ:
            - húng quế → vegetables
            - thịt heo → fresh-meat
            - muối → seasonings
            - cà chua → vegetables
            - gạo → grains-staples
            - sữa tươi → milk
            - nấm hương → dried-fruits
            - dầu ăn → cooking-oils

            Trả lời (chỉ mã nhóm):"""
        }
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs, 
        max_new_tokens=10,  # Chỉ cần mã nhóm ngắn
        temperature=0.1,    # Nhiệt độ thấp cho output nhất quán
        do_sample=True,    # Greedy decoding để chọn đáp án chắc chắn nhất
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)

    # Parse response
    response = response.strip().lower()
    for cat in CATEGORIES.keys():
        if cat in response:
            return cat
    

def build_kb():
    """Build knowledge base"""
    # Load data
    with open('/kaggle/input/vietnamese-food-recipe-dataset/unique_ingredients.json', 'r', encoding='utf-8') as f:
        ingredients = json.load(f)

    with open("/kaggle/input/vietnamese-food-recipe-dataset/ingredients_synonyms_qwen.json", 'r', encoding='utf-8') as f:
        synonyms_data = json.load(f)
        synonyms_map = {item['ingredient']: item['synonyms'] for item in synonyms_data}
    
    print(f"Processing {len(ingredients)} ingredients...\n")
    
    kb = []
    for idx, ingredient in enumerate(tqdm(ingredients, desc="Building KB"), 1):
        try:
            # Generate fields
            record = {
                "id": f"ingre{idx:05d}",
                "name_vi": ingredient,
                "name_normalized": normalize_text(ingredient),
                "name_en": translate_vi_to_en(ingredient),
                "category": classify_category(ingredient),
                "synonyms": synonyms_map.get(ingredient, []),
                "type": "ingredient"
            }
            
            kb.append(record)
            
            # Save every 20 items
            if idx % 20 == 0:
                with open('ingredient_knowledge_base.json', 'w', encoding='utf-8') as f:
                    json.dump(kb, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            tqdm.write(f"ERROR [{ingredient}]: {e}")
            continue
    
    # Final save
    with open('ingredient_knowledge_base.json', 'w', encoding='utf-8') as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    
    print(f"\nCompleted: {len(kb)} ingredients")
    print("Saved to: ingredient_knowledge_base.json")

build_kb()