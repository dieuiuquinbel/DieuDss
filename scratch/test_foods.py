import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/nutridss.db')
c = conn.cursor()

keywords = ["mướp", "mồng tơi", "cua", "bắp cải", "khổ qua", "dưa hấu", "táo", "thanh long", "cần tây", "nấm hương", "khoai tây", "cà rốt", "sườn", "chả", "thịt", "cá", "đậu", "tôm"]

for kw in keywords:
    c.execute("SELECT f.id, f.canonical_name_vi, fps.estimated_price_per_100g FROM foods f LEFT JOIN food_price_summary fps ON f.id = fps.food_id WHERE f.canonical_name_vi LIKE ?", (f"%{kw}%",))
    rows = c.fetchall()
    print(f"=== Keyword: {kw} (found {len(rows)}) ===")
    for r in rows[:3]:
        print(f"   id={r[0]}: {r[1]} -> {r[2]}đ/100g")

conn.close()
