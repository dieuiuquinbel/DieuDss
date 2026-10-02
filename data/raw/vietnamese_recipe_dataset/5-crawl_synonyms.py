"""
Generate synonyms cho nguyên liệu sử dụng Qwen model
"""
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm

# ===== LOAD MODEL =====
print("Loading Qwen model...")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-3B-Instruct",
    device_map="auto",
    torch_dtype=torch.float16
)
print("Model loaded.\n")

def generate_synonyms(ingredient_name):
    """Generate synonyms for an ingredient using improved prompt"""
    messages = [
        {
            "role": "system", 
            "content": "Bạn là trợ lý AI chuyên về ẩm thực Việt Nam. Nhiệm vụ của bạn là liệt kê các tên gọi khác của nguyên liệu."
        },
        {
            "role": "user",
            "content": f"""Cho nguyên liệu "{ingredient_name}", hãy liệt kê các cách gọi KHÁC (không bao gồm chính từ "{ingredient_name}").
# ĐỊNH NGHĨA: Tên gọi khác là những cách gọi khác nhau của {ingredient_name}. Tên gọi khác có thể bao gồm: từ địa phương (ví dụ ngô = bắp, bột ngọt = mì chính, ba chỉ = ba rọi), tên gọi thuần việt của một từ tiếng Anh (baking soda = muối nở hoặc bột nở), tên gọi thương mại,... 
VÍ DỤ ĐÚNG:
- bắp → ngô, bắp ngô
- thịt heo → thịt lợn, lợn
- thịt ba rọi -> thịt ba chỉ, ba chỉ
- muối → (để trống nếu không có từ đồng nghĩa)
Yêu cầu:
- CHỈ trả lời danh sách các tên gọi khác, cách nhau bởi dấu phẩy
- KHÔNG output lời giải thích hay bất kỳ văn bản nào khác. Không thêm các icons, emojis. 
- KHÔNG thêm tên gọi của các nguyên liệu khác
- KHÔNG bịa đặt tên gọi. Các từ được output phải là từ có nghĩa được sử dụng trong tiếng Việt
- Nếu KHÔNG có tên gọi khác phù hợp, không trả về gì cả
- Nếu input là tiếng Anh, có thể output bản dịch tiếng Việt (ví dụ all purpose cream = kem đa dụng)
Trả lời (chỉ danh sách từ, hoặc để trống):"""
        }
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=50,
        temperature=0.2, 
        top_p=0.85,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    
    generated_ids = [
        output_ids[len(input_ids):] 
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

    if not response or response in ['-', '—', '–', '(rỗng)', 'rỗng']:
        return []
    
    synonyms = [s.strip() for s in response.split(',') if s.strip()]
    synonyms = [s for s in synonyms if s.lower() != ingredient_name.lower()]
    
    return synonyms[:3]
    
def main():
    # Đọc danh sách nguyên liệu
    with open('data/unique_ingredients.json', 'r', encoding='utf-8') as f:
        ingredients = json.load(f)
    
    print(f"Generating synonyms for {len(ingredients)} ingredients...\n")
    
    results = []
    
    for ingredient in tqdm(ingredients, desc="Processing"):
        try:
            synonyms = get_synonyms(ingredient)
            
            results.append({
                'ingredient': ingredient,
                'synonyms': synonyms
            })
            
        except Exception as e:
            tqdm.write(f"Error [{ingredient}]: {e}")
            results.append({
                'ingredient': ingredient,
                'synonyms': ["", "", ""]
            })
    
    # Lưu kết quả
    with open('data/ingredients_synonyms_qwen.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nCompleted: {len(results)} ingredients")
    print("Saved to: data/ingredients_synonyms_qwen.json")

if __name__ == "__main__":
    main()