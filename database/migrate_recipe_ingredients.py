import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutridss.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(recipe_ingredients)")
existing_cols = [row[1] for row in cursor.fetchall()]

if "raw_quantity" not in existing_cols:
    cursor.execute("ALTER TABLE recipe_ingredients ADD COLUMN raw_quantity REAL")
    print("Added raw_quantity column")

if "raw_unit" not in existing_cols:
    cursor.execute("ALTER TABLE recipe_ingredients ADD COLUMN raw_unit TEXT DEFAULT 'g'")
    print("Added raw_unit column")

# Also ensure default values if empty
cursor.execute("UPDATE recipe_ingredients SET raw_quantity = quantity_g WHERE raw_quantity IS NULL")
cursor.execute("UPDATE recipe_ingredients SET raw_unit = 'g' WHERE raw_unit IS NULL")

conn.commit()
conn.close()
print("recipe_ingredients schema check complete!")
