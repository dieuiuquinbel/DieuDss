import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/nutridss.db')
c = conn.cursor()

c.execute("SELECT id, canonical_name_vi, calories_kcal_100g, protein_g_100g FROM foods WHERE canonical_name_vi LIKE '%đậu%' OR canonical_name_vi LIKE '%khoai%' OR canonical_name_vi LIKE '%gà%'")
for r in c.fetchall()[:20]:
    print(r)
conn.close()
