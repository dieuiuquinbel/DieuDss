# -*- coding: utf-8 -*-
import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.food_vision_service import FoodVisionService

client = TestClient(app)

def test_food_vision_service():
    service = FoodVisionService()
    assert len(service.labels) == 103
    
    # Create a small dummy RGB image
    img = Image.new("RGB", (224, 224), color=(255, 120, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()
    
    res = service.predict(img_bytes)
    assert res["status"] == "success"
    assert "predicted_label" in res
    assert "confidence" in res
    assert len(res["top_3"]) == 3

def test_vision_api_endpoints():
    # 1. Get classes
    res_classes = client.get("/api/vision/classes")
    assert res_classes.status_code == 200
    classes = res_classes.json()
    assert len(classes) == 103

    # 2. Predict image endpoint
    img = Image.new("RGB", (100, 100), color=(100, 200, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    files = {"file": ("test_dish.png", buf, "image/png")}
    res_predict = client.post("/api/vision/predict-food", files=files)
    assert res_predict.status_code == 200
    data = res_predict.json()
    assert "vision_result" in data
    assert data["vision_result"]["status"] == "success"
    assert "predicted_label" in data["vision_result"]
