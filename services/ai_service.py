"""Сервис для работы с локальной моделью (Ollama / llama.cpp)."""
import os
import streamlit as st
from openai import OpenAI
from pydantic import ValidationError
from database.models import Meal
from utils.parsers import safe_parse_json
from config import LOCAL_BASE_URL, LOCAL_MODEL


@st.cache_resource
def get_local_client() -> OpenAI:
    """Получение кешированного клиента для локального OpenAI-совместимого API."""
    return OpenAI(
        base_url=LOCAL_BASE_URL,
        api_key="ollama"
    )


SYSTEM_PROMPT = """
Ты — строгий ИИ-нутрициолог. Твоя задача — парсить описание еды в JSON.

ПРАВИЛА:
1. Если пользователь описал ОДНО блюдо — верни ОДИН JSON-объект.
2. Если пользователь описал НЕСКОЛЬКО блюд — верни МАССИВ JSON-объектов.
3. Верни ТОЛЬКО JSON. Никакого текста до или после. Никаких markdown-блоков.
4. Формат для одного блюда: {"name": "Название", "calories": 150, "protein": 10, "fat": 5, "carbs": 20}
5. Формат для нескольких блюд: [{"name": "Блюдо1", ...}, {"name": "Блюдо2", ...}]
6. Если порция не указана, считай стандартную (200-250г для горячего, 100г для гарнира).
7. Все числовые значения должны быть числами (int/float), не строками.

ПРИМЕРЫ:
Одно блюдо: {"name": "Борщ", "calories": 158, "protein": 12, "fat": 5, "carbs": 18}
Несколько блюд: [{"name": "Чай", "calories": 50, "protein": 0, "fat": 0, "carbs": 12}, {"name": "Печенье", "calories": 200, "protein": 3, "fat": 8, "carbs": 30}]

НАЧНИ ОТВЕТ С { ИЛИ [
"""


def analyze_meal(description: str) -> Meal | list[Meal] | None:
    """Анализ описания еды через локальную модель."""
    try:
        client = get_local_client()
        
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": description}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        raw_json = response.choices[0].message.content
        data = safe_parse_json(raw_json)
        
        # Если вернулась список — создаем список Meal
        if isinstance(data, list):
            meals = []
            for item in data:
                try:
                    meal = Meal(**item)
                    meals.append(meal)
                except ValidationError as e:
                    st.warning(f"⚠️ Пропущено блюдо из-за ошибки валидации: {e}")
                    continue
            return meals if meals else None
        
        # Если вернулся один объект — создаем один Meal
        meal = Meal(**data)
        return meal
        
    except ValidationError as e:
        st.error(f"⚠️ Модель вернула некорректный JSON: {e}")
        st.info("💡 Попробуй описать еду подробнее (например, укажи вес в граммах).")
        return None
    except Exception as e:
        error_msg = str(e).lower()
        if "connection" in error_msg or "refused" in error_msg:
            st.error("🔌 Не удалось подключиться к локальному серверу!")
            st.info("Убедись, что Ollama или llama.cpp server запущен и порт в .env совпадает.")
        else:
            st.error(f"❌ Ошибка локальной модели: {e}")
        return None