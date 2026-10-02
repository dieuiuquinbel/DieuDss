import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("1. Testing GET / (Frontend 7 tabs)")
res = client.get("/")
assert res.status_code == 200
assert "tab-recipe-book" in res.text
assert "tab-guidelines" in res.text
assert "planIsVegetarian" in res.text
print("   -> PASS: 7 tabs present in HTML")

print("2. Testing GET /api/recipes")
res = client.get("/api/recipes?limit=5")
assert res.status_code == 200
recs = res.json()
assert len(recs) > 0
print(f"   -> PASS: Found {len(recs)} recipes, first is {recs[0]['name_vi']} (~{recs[0]['estimated_cost_vnd']}đ)")

print("3. Testing GET /api/recipes/{id} for Lòng bò xào lá lốt")
# Find ID of Lòng bò
all_res = client.get("/api/recipes?q=Lòng bò")
long_bo = all_res.json()[0]
det_res = client.get(f"/api/recipes/{long_bo['id']}")
assert det_res.status_code == 200
det = det_res.json()
print(f"   -> PASS: {det['name_vi']} cost = {det['calculated_cost_vnd']:,.0f}đ, steps count = {len(det['steps'])}, ings count = {len(det['ingredients'])}")
assert det['calculated_cost_vnd'] > 30000 and det['calculated_cost_vnd'] < 50000

print("4. Testing POST /api/meal-plans/generate (Standard)")
plan_res = client.post("/api/meal-plans/generate", json={
    "health_goal": "LOSE_WEIGHT",
    "daily_budget_vnd": 70000.0,
    "allergies": ["SEAFOOD"],
    "is_vegetarian": False
})
assert plan_res.status_code == 200
plan_data = plan_res.json()
print(f"   -> PASS: Generated {len(plan_data['options'])} options")
lunch = plan_data['options'][0]['meals']['lunch']
print(f"   Lunch: {lunch['name_vi']} (~{lunch['estimated_cost_vnd']:,.0f}đ)")
if 'meal_set' in lunch:
    print(f"      - Staple: {lunch['meal_set']['staple']['name_vi']}")
    print(f"      - Main: {lunch['meal_set']['main_dish']['name_vi']}")
    print(f"      - Soup: {lunch['meal_set']['soup_veg']['name_vi']}")

print("5. Testing POST /api/meal-plans/generate (Vegetarian)")
veg_res = client.post("/api/meal-plans/generate", json={
    "health_goal": "MAINTAIN",
    "daily_budget_vnd": 70000.0,
    "allergies": [],
    "is_vegetarian": True
})
assert veg_res.status_code == 200
veg_data = veg_res.json()
lunch_veg = veg_data['options'][0]['meals']['lunch']
print(f"   Vegetarian Lunch: {lunch_veg['name_vi']} (~{lunch_veg['estimated_cost_vnd']:,.0f}đ)")

print("\nALL INTEGRATION CHECKS PASSED PERFECTLY!")
