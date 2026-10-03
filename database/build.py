"""
NutriDSS - Single Database Build Pipeline (database/build.py)
Replaces ad-hoc, manual, multi-step scripts with a deterministic, reproducible pipeline:
DROP/RECREATE DEV DB -> Apply Schema -> Food Master -> Curated Recipes -> Market Prices -> Validate Contract
"""

import os
import sys
import argparse
import sqlite3

# Ensure project root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.seed import seed_database as seed_base
from database.seed_curated_recipes import seed_database as seed_curated
from database.seed_real_store_prices import seed_prices
from database.validate_database import validate_database

DB_PATH = os.path.join(os.path.dirname(__file__), "nutridss.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def build_database(clean: bool = False):
    print("=" * 60)
    print("🚀 NUTRIDSS DATABASE BUILD PIPELINE V3")
    print("=" * 60)

    if clean and os.path.exists(DB_PATH):
        print(f"[1/5] Removing existing database for clean build: {DB_PATH}")
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"[WARN] Could not remove existing DB ({e}), will apply migrations/DDL inplace.")

    print(f"[2/5] Applying DDL Schema from: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("   -> Schema initialized successfully.")

    print("[3/5] Seeding core foods, 30 nutrients, WHO guidelines, taxonomy...")
    seed_base()

    print("[4/5] Seeding curated Vietnamese recipes (63 dishes with strict roles & ingredients)...")
    seed_curated()

    print("[5/5] Seeding real supermarket store prices & price summary...")
    seed_prices()

    print("=" * 60)
    print("🔍 VALIDATING DATABASE CONTRACT...")
    print("=" * 60)
    is_valid = validate_database(DB_PATH)
    if not is_valid:
        raise RuntimeError("Database validation failed! Schema contract is breached.")

    print("\n✅ NUTRIDSS DATABASE IS 100% READY AND VERIFIED!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NutriDSS Single Database Builder")
    parser.add_argument("--clean", action="store_true", help="Remove existing database and rebuild from scratch")
    args = parser.parse_args()
    build_database(clean=args.clean)
