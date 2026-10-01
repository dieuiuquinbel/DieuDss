-- NutriDSS Database Schema (SQLite / MySQL Compatible)

CREATE TABLE IF NOT EXISTS food_groups (
    id INTEGER PRIMARY KEY,
    name_vi TEXT NOT NULL,
    code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY,
    canonical_name_vi TEXT NOT NULL,
    food_group_id INTEGER,
    default_unit TEXT DEFAULT 'g',
    calories_kcal_100g REAL DEFAULT 0,
    protein_g_100g REAL DEFAULT 0,
    carb_g_100g REAL DEFAULT 0,
    fat_g_100g REAL DEFAULT 0,
    fiber_g_100g REAL DEFAULT 0,
    sugar_g_100g REAL DEFAULT 0,
    sodium_mg_100g REAL DEFAULT 0,
    FOREIGN KEY (food_group_id) REFERENCES food_groups(id)
);

CREATE TABLE IF NOT EXISTS food_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER NOT NULL,
    store_name TEXT NOT NULL,
    store_product_name TEXT NOT NULL,
    price_vnd REAL NOT NULL,
    quantity_g REAL NOT NULL,
    normalized_price_per_100g REAL NOT NULL,
    normalized_price_per_kg REAL NOT NULL,
    region TEXT,
    promotion_flag INTEGER DEFAULT 0,
    source_url TEXT,
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

CREATE TABLE IF NOT EXISTS food_price_summary (
    food_id INTEGER PRIMARY KEY,
    price_min REAL,
    price_median REAL,
    price_max REAL,
    estimated_price_per_100g REAL,
    sample_count INTEGER,
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

CREATE TABLE IF NOT EXISTS allergens (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL,
    name_vi TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS food_allergens (
    food_id INTEGER NOT NULL,
    allergen_id INTEGER NOT NULL,
    PRIMARY KEY (food_id, allergen_id),
    FOREIGN KEY (food_id) REFERENCES foods(id),
    FOREIGN KEY (allergen_id) REFERENCES allergens(id)
);

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    name_vi TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    servings INTEGER DEFAULT 1,
    prep_time_min INTEGER DEFAULT 10,
    cook_time_min INTEGER DEFAULT 15,
    difficulty TEXT,
    description TEXT,
    source_name TEXT,
    tags TEXT
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity_g REAL NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL,
    health_goal TEXT NOT NULL,
    daily_budget_vnd REAL NOT NULL,
    activity_level TEXT DEFAULT 'MODERATE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
