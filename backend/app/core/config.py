from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def get_settings() -> dict:
    return {
        "recipe_api_key": os.getenv("RECIPE_API_KEY", ""),
        "recipe_api_base_url": os.getenv("RECIPE_API_BASE_URL", "https://api.qqsuu.cn/api/dm-caipu"),
        "model_api_key": os.getenv("MODEL_API_KEY", ""),
        "model_api_base_url": os.getenv("MODEL_API_BASE_URL", "https://api.deepseek.com"),
        "app_env": os.getenv("APP_ENV", "development"),
    }
