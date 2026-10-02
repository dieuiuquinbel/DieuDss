-- NutriDSS Database Schema V2 (SQLite & MySQL Compatible)
-- Architecture: Comprehensive Relational Nutrition DSS Data Backbone

-- 1. Food Groups Taxonomy
CREATE TABLE IF NOT EXISTS food_groups (
    id INTEGER PRIMARY KEY,
    name_vi TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE
);

-- 2. Master Foods (with Food State & Edible Fraction)
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY,
    canonical_name_vi TEXT NOT NULL,
    food_group_id INTEGER,
    food_state TEXT DEFAULT 'RAW', -- RAW, COOKED, BOILED, GRILLED, STEAMED, FRIED
    edible_fraction REAL DEFAULT 1.0,
    default_unit TEXT DEFAULT 'g',
    source_quality TEXT DEFAULT 'CANONICAL',
    is_active INTEGER DEFAULT 1,
    -- Fast access denormalized macros (synced with food_nutrients)
    calories_kcal_100g REAL DEFAULT 0,
    protein_g_100g REAL DEFAULT 0,
    carb_g_100g REAL DEFAULT 0,
    fat_g_100g REAL DEFAULT 0,
    fiber_g_100g REAL DEFAULT 0,
    sugar_g_100g REAL DEFAULT 0,
    sodium_mg_100g REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_group_id) REFERENCES food_groups(id)
);

-- 3. Nutrients Master (30+ Criteria from WHO & National Nutrition Guidelines)
CREATE TABLE IF NOT EXISTS nutrients (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name_en TEXT NOT NULL,
    name_vi TEXT NOT NULL,
    unit TEXT NOT NULL, -- kcal, g, mg, mcg
    category TEXT NOT NULL, -- MACRO, SUGAR_LIPID, MINERAL, VITAMIN, FATTY_ACID
    daily_recommended REAL,
    who_upper_limit REAL
);

-- 4. Relational Food Nutrients (EAV / Relational Matrix with Provenance)
CREATE TABLE IF NOT EXISTS food_nutrients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER NOT NULL,
    nutrient_id INTEGER NOT NULL,
    value REAL NOT NULL,
    basis TEXT DEFAULT 'per_100g_edible', -- per_100g_edible, per_serving
    source_id INTEGER,
    confidence REAL DEFAULT 1.0,
    UNIQUE (food_id, nutrient_id),
    FOREIGN KEY (food_id) REFERENCES foods(id),
    FOREIGN KEY (nutrient_id) REFERENCES nutrients(id)
);

-- 5. Food Aliases & Synonyms (Vietnamese Localization & Normalization)
CREATE TABLE IF NOT EXISTS food_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER NOT NULL,
    raw_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    language TEXT DEFAULT 'vi',
    source TEXT,
    confidence REAL DEFAULT 1.0,
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

-- 6. Unit Conversions (e.g., 1 quả trứng = 55g, 1 muỗng = 15ml)
CREATE TABLE IF NOT EXISTS unit_conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER,
    from_unit TEXT NOT NULL,
    to_unit TEXT NOT NULL,
    conversion_value REAL NOT NULL,
    conversion_source TEXT,
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

-- 7. Data Provenance & Sources
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY,
    organization TEXT NOT NULL,
    dataset TEXT NOT NULL,
    version TEXT,
    source_url TEXT,
    license TEXT,
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Stores & Retailers
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT DEFAULT 'VIETNAM',
    source_url TEXT
);

-- 9. Food Price Observations
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
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

-- 10. Food Price Summary & Statistics
CREATE TABLE IF NOT EXISTS food_price_summary (
    food_id INTEGER PRIMARY KEY,
    price_min REAL,
    price_median REAL,
    price_max REAL,
    estimated_price_per_100g REAL,
    sample_count INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

-- 11. Allergens Taxonomy
CREATE TABLE IF NOT EXISTS allergens (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name_vi TEXT NOT NULL,
    description TEXT
);

-- 12. Food-Allergen Mapping
CREATE TABLE IF NOT EXISTS food_allergens (
    food_id INTEGER NOT NULL,
    allergen_id INTEGER NOT NULL,
    PRIMARY KEY (food_id, allergen_id),
    FOREIGN KEY (food_id) REFERENCES foods(id),
    FOREIGN KEY (allergen_id) REFERENCES allergens(id)
);

-- 13. Recipes
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    name_vi TEXT NOT NULL,
    meal_type TEXT NOT NULL, -- BREAKFAST, LUNCH, DINNER, SNACK
    servings INTEGER DEFAULT 1,
    prep_time_min INTEGER DEFAULT 10,
    cook_time_min INTEGER DEFAULT 15,
    difficulty TEXT DEFAULT 'EASY',
    description TEXT,
    source_name TEXT,
    tags TEXT,
    image_url TEXT
);

-- 14. Recipe Ingredients
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity_g REAL NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

-- 15. Recipe Steps & Instructions
CREATE TABLE IF NOT EXISTS recipe_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    instruction_vi TEXT NOT NULL,
    duration_min INTEGER DEFAULT 5,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

-- 16. Guideline Sources (WHO, VN Ministry of Health, FAO)
CREATE TABLE IF NOT EXISTS guideline_sources (
    id INTEGER PRIMARY KEY,
    organization TEXT NOT NULL,
    title TEXT NOT NULL,
    version TEXT,
    source_url TEXT,
    published_at TEXT
);

-- 17. Guideline Rules (Hard & Soft Constraints)
CREATE TABLE IF NOT EXISTS guideline_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    rule_code TEXT NOT NULL UNIQUE,
    population TEXT DEFAULT 'GENERAL_ADULT',
    nutrient TEXT NOT NULL,
    min_value REAL,
    max_value REAL,
    unit TEXT NOT NULL,
    scope TEXT DEFAULT 'DAILY', -- DAILY, PER_MEAL
    description TEXT,
    FOREIGN KEY (source_id) REFERENCES guideline_sources(id)
);

-- 18. User Accounts & Security
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'USER', -- USER, ADMIN, DIETITIAN
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 19. User Profiles & Health Context
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    display_name TEXT NOT NULL,
    age INTEGER,
    gender TEXT, -- MALE, FEMALE
    height_cm REAL,
    weight_kg REAL,
    activity_level TEXT DEFAULT 'MODERATE',
    health_goal TEXT NOT NULL, -- LOSE_WEIGHT, GAIN_MUSCLE, MAINTAIN, KETO, LOW_CARB, HEALTHY
    daily_budget_vnd REAL NOT NULL,
    target_calories REAL,
    target_protein_g REAL,
    target_carb_g REAL,
    target_fat_g REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 20. User Preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    preference_type TEXT NOT NULL, -- LIKE, DISLIKE
    weight REAL DEFAULT 1.0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

-- 21. User Allergies
CREATE TABLE IF NOT EXISTS user_allergies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    allergen_id INTEGER NOT NULL,
    severity TEXT DEFAULT 'SEVERE',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (allergen_id) REFERENCES allergens(id)
);

-- 22. Meal Plans Persistence
CREATE TABLE IF NOT EXISTS meal_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    plan_type TEXT DEFAULT 'DAILY', -- DAILY, WEEKLY
    start_date TEXT,
    end_date TEXT,
    budget_vnd REAL NOT NULL,
    health_goal TEXT NOT NULL,
    target_calories REAL,
    total_cost_vnd REAL,
    total_calories REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 23. Meal Plan Items
CREATE TABLE IF NOT EXISTS meal_plan_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_plan_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    day_of_week TEXT DEFAULT 'TODAY', -- MONDAY, TUESDAY, ..., SUNDAY, TODAY
    meal_type TEXT NOT NULL, -- BREAKFAST, LUNCH, DINNER, SNACK
    portion_multiplier REAL DEFAULT 1.0,
    selected_by TEXT DEFAULT 'SYSTEM', -- SYSTEM, USER
    cost_vnd REAL,
    calories REAL,
    FOREIGN KEY (meal_plan_id) REFERENCES meal_plans(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

-- 24. Real User Interaction & Feedback Loop
CREATE TABLE IF NOT EXISTS user_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    recipe_id INTEGER,
    food_id INTEGER,
    event_type TEXT NOT NULL, -- VIEW, CLICK, ADD, KEEP, REPLACE, REMOVE, FAVORITE, DISLIKE, RATE
    rating REAL,
    session_id TEXT,
    metadata_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

-- 25. Model Versions Registry
CREATE TABLE IF NOT EXISTS model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    dataset_version TEXT,
    metric_json TEXT,
    artifact_path TEXT,
    is_active INTEGER DEFAULT 1,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 26. Security Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    ip_address TEXT,
    metadata_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 27. External API Sources Registry
CREATE TABLE IF NOT EXISTS api_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    base_url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    rate_limit_per_min INTEGER DEFAULT 30,
    last_success TIMESTAMP,
    last_failure TIMESTAMP
);
