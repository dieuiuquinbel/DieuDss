import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/nutridss.db')
c = conn.cursor()

c.execute("""
    SELECT r.id, r.name_vi, r.dish_role,
           SUM(ROUND(fps.estimated_price_per_100g * ri.quantity_g / 100.0, 0)) as cost,
           SUM(ROUND(f.calories_kcal_100g * ri.quantity_g / 100.0, 1)) as cal,
           SUM(ROUND(f.protein_g_100g * ri.quantity_g / 100.0, 1)) as prot
    FROM recipes r
    JOIN recipe_ingredients ri ON r.id = ri.recipe_id
    JOIN foods f ON ri.food_id = f.id
    LEFT JOIN food_price_summary fps ON f.id = fps.food_id
    WHERE r.source_name = 'CURATED_VN_MASTER'
    GROUP BY r.id
    ORDER BY r.dish_role, cost ASC
""")

rows = c.fetchall()
print(f"Total curated recipes with verified pricing: {len(rows)}")
for r in rows:
    print(f"[{r[2]:12s}] {r[1]:45s} -> {r[3]:,.0f}đ | {r[4]} Kcal | {r[5]}g P")

conn.close()
