"""Конфигурация приложения."""
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "food_diary.db"

# Локальная модель (llama.cpp server)
# Имя модели должно совпадать с тем, что выдает сервер (обычно имя файла без .gguf)
LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL", "http://localhost:8080/v1")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "qwen2.5-7b-instruct-q4_K_S")

# Цели по умолчанию
DEFAULT_CALORIE_GOAL = 2200
DEFAULT_PROTEIN_GOAL = 160
DEFAULT_FAT_GOAL = 70
DEFAULT_CARBS_GOAL = 220