"""
NutriDSS - Application Configuration & Settings
"""

import os
from typing import List
from pydantic import BaseModel

def load_dotenv(filepath: str = ".env"):
    """Lightweight .env file parser to populate os.environ without external dependencies."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip()
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

load_dotenv()

class Settings(BaseModel):
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///database/nutridss.db")
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "models/best_recipe_ranker.joblib")
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "nutridss_insecure_default_secret_replace_in_production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:5500"
        ).split(",") if origin.strip()
    ]
    
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    USDA_FDC_API_KEY: str = os.getenv("USDA_FDC_API_KEY", "")

settings = Settings()
