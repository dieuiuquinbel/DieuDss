# -*- coding: utf-8 -*-
"""
Tests for NutriDSS Meal Plans & Saved Plans Flow
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_single_meal_generator(client):
    res = client.post("/api/meal-plans/single-meal", json={
        "meal_type": "LUNCH",
        "budget_vnd": 35000,
        "health_goal": "BALANCED",
        "structure_mode": "STANDARD"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["meal_type"] == "LUNCH"
    assert "options" in data
    assert len(data["options"]) == 3
    for opt in data["options"]:
        assert "meal" in opt
        assert opt["meal"]["estimated_cost_vnd"] > 0
        assert opt["meal"]["calories"] > 0

from backend.core.security import create_access_token

def test_saved_meal_plan_crud_flow(client):
    token = create_access_token({"sub": "2", "username": "demouser", "role": "USER"})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Save plan
    save_payload = {
        "plan_name": "Thực đơn test tự động",
        "plan_type": "DAILY",
        "health_goal": "LOSE_WEIGHT",
        "budget_vnd": 70000,
        "target_calories": 1750,
        "total_cost_vnd": 65000,
        "total_calories": 1720,
        "items": [
            {"recipe_id": 1001, "day_of_week": "Hôm nay", "meal_type": "BREAKFAST", "cost_vnd": 20000, "calories": 400},
            {"recipe_id": 1002, "day_of_week": "Hôm nay", "meal_type": "LUNCH", "cost_vnd": 45000, "calories": 800}
        ]
    }
    res_save = client.post("/api/meal-plans/save", json=save_payload, headers=headers)
    assert res_save.status_code == 200
    plan_id = res_save.json()["plan_id"]
    assert plan_id > 0

    # 2. List plans
    res_list = client.get("/api/meal-plans", headers=headers)
    assert res_list.status_code == 200
    plans = res_list.json()
    assert any(p["id"] == plan_id for p in plans)

    # 3. Get plan detail
    res_detail = client.get(f"/api/meal-plans/{plan_id}", headers=headers)
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["plan_name"] == "Thực đơn test tự động"
    assert len(detail["items"]) == 2
    assert "recipe_detail" in detail["items"][0]

    # 4. Apply plan
    res_apply = client.post(f"/api/meal-plans/{plan_id}/apply", headers=headers)
    assert res_apply.status_code == 200
    assert "áp dụng" in res_apply.json()["message"].lower()

    # 5. Delete plan
    res_del = client.delete(f"/api/meal-plans/{plan_id}", headers=headers)
    assert res_del.status_code == 200
