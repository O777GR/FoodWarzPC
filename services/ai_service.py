"""Сервис для работы с локальной моделью (Ollama / llama.cpp)."""
import streamlit as st
from openai import OpenAI
from pydantic import ValidationError
from database.models import Meal
from utils.parsers import safe_parse_json
from config import LOCAL_BASE_URL, LOCAL_MODEL
from datetime import datetime


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

1. Если пользователь описал ОДНО блюдо (включая составные блюда) — верни ОДИН JSON-объект.

2. Если пользователь описал НЕСКОЛЬКО ОТДЕЛЬНЫХ блюд или ПРИЁМОВ ПИЩИ — верни МАССИВ JSON-объектов.

3. Верни ТОЛЬКО JSON. Никакого текста до или после. Никаких markdown-блоков.

4. Формат для одного блюда:
{"name": "Название", "calories": 150, "protein": 10, "fat": 5, "carbs": 20, "amount": "200г", "meal_type": "Обед"}

5. Формат для нескольких блюд: [{"name": "Блюдо1", ...}, {"name": "Блюдо2", ...}]

6. Если порция не указана в тексте, оставь amount пустым "".

7. Все числовые значения должны быть числами (int/float), не строками.

8. ОПРЕДЕЛЕНИЕ ТИПА ПРИЁМА ПИЩИ (meal_type):
   - Если указано время: 6:00-10:00 = "Завтрак", 11:00-15:00 = "Обед", 16:00-18:00 = "1-й перекус", 18:00-20:00 = "2-й перекус", 20:00-23:00 = "Ужин"
   - Если указано словами: "завтрак" = "Завтрак", "обед" = "Обед", "ужин" = "Ужин", "перекус" = "1-й перекус" или "2-й перекус"
   - Если не указано: определи по контексту или оставь "Другое"

9. ИЗВЛЕЧЕНИЕ КОЛИЧЕСТВА (amount):
   - "200 грамм" → "200г"
   - "300 мл" → "300мл"
   - "тарелка" → "1 тарелка"
   - "2 яйца" → "2 шт"
   - "кусочек хлеба" → "1 кусочек"
   - Если не указано количество → ""

10. СОСТАВНЫЕ БЛЮДА (ОДНО блюдо с несколькими ингредиентами, которые готовятся ВМЕСТЕ):
    - "Гречка с говядиной и курицей" = ОДНО блюдо (всё тушится вместе)
    - "Борщ с говядиной" = ОДНО блюдо
    - Возвращай ОДИН JSON-объект

11. НЕСКОЛЬКО ОТДЕЛЬНЫХ ПРИЁМОВ ПИЩИ (едят в разное время):
    - "Завтрак: сырники, Обед: суп" = ДВА блюда (массив из 2 объектов)
    - Возвращай МАССИВ JSON-объектов

ПРИМЕРЫ:

✅ ПРАВИЛЬНО:
Пользователь: "Завтрак в 8:00: 200г овсянки с молоком"
Правильно: {"name": "Овсянка с молоком", "calories": 250, "protein": 8, "fat": 5, "carbs": 45, "amount": "200г", "meal_type": "Завтрак"}

✅ ПРАВИЛЬНО:
Пользователь: "Обед: 300мл борща и 100г хлеба"
Правильно: [
  {"name": "Борщ", "calories": 150, "protein": 10, "fat": 5, "carbs": 15, "amount": "300мл", "meal_type": "Обед"},
  {"name": "Хлеб", "calories": 250, "protein": 8, "fat": 3, "carbs": 45, "amount": "100г", "meal_type": "Обед"}
]

✅ ПРАВИЛЬНО:
Пользователь: "Вечером выпил 250мл кефира"
Правильно: {"name": "Кефир", "calories": 140, "protein": 8, "fat": 8, "carbs": 10, "amount": "250мл", "meal_type": "2-й перекус"}

НАЧНИ ОТВЕТ С { ИЛИ [
"""


def analyze_meal(description: str) -> Meal | list[Meal] | None:
    """Анализ описания еды через локальную модель."""
    try:
        client = get_local_client()
        
        # Добавляем текущее время в запрос для контекста
        current_time = datetime.now().strftime("%H:%M")
        enhanced_description = f"[Текущее время: {current_time}]\n{description}"
        
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": enhanced_description}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        raw_json = response.choices[0].message.content
        data = safe_parse_json(raw_json)
        
        if isinstance(data, list):
            meals = []
            for item in data:
                try:
                    # Добавляем время если не указано
                    if "time" not in item:
                        item["time"] = datetime.now().strftime("%H:%M")
                    meal = Meal(**item)
                    meals.append(meal)
                except ValidationError as e:
                    st.warning(f"⚠️ Пропущено блюдо из-за ошибки валидации: {e}")
                    continue
            return meals if meals else None
        
        # Если вернулся один объект
        if "time" not in data:
            data["time"] = datetime.now().strftime("%H:%M")
        meal = Meal(**data)
        return meal
        
    except ValidationError as e:
        st.error(f"️ Модель вернула некорректный JSON: {e}")
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


WEEKLY_ANALYSIS_PROMPT = """
Ты — профессиональный нутрициолог. Проанализируй статистику питания пользователя за неделю и дай краткие, конкретные рекомендации.

Данные за неделю:
{stats_data}

Цели пользователя:
- Калории: {cal_goal} ккал/день
- Белки: {protein_goal} г/день
- Жиры: {fat_goal} г/день
- Углеводы: {carbs_goal} г/день

Проанализируй:
1. Среднее потребление КБЖУ vs цели
2. Дни с перебором/недобором калорий
3. Баланс макронутриентов
4. Конкретные рекомендации (что улучшить)

Верни ТОЛЬКО JSON в формате:
{{
  "summary": "Краткое резюме (1-2 предложения)",
  "strengths": ["Сильная сторона 1", "Сильная сторона 2"],
  "weaknesses": ["Слабая сторона 1", "Слабая сторона 2"],
  "recommendations": [
    {{"level": "Внимание", "text": "Рекомендация 1"}},
    {{"level": "Критично", "text": "Рекомендация 2"}}
  ]
}}

Уровень может быть: "Внимание", "Критично", "Отлично"
"""


def analyze_weekly_stats(stats_data: list[dict], cal_goal: int, protein_goal: int, fat_goal: int, carbs_goal: int) -> dict | None:
    """Анализ недельной статистики через ИИ."""
    try:
        client = get_local_client()
        
        # Формируем текст статистики
        stats_text = "\n".join([
            f"{d['date']}: {d['calories']:.0f} ккал, Б:{d['protein']:.0f}г, Ж:{d['fat']:.0f}г, У:{d['carbs']:.0f}г"
            for d in stats_data
        ])
        
        prompt = WEEKLY_ANALYSIS_PROMPT.format(
            stats_data=stats_text,
            cal_goal=cal_goal,
            protein_goal=protein_goal,
            fat_goal=fat_goal,
            carbs_goal=carbs_goal
        )
        
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        raw_json = response.choices[0].message.content
        data = safe_parse_json(raw_json)
        
        return data
        
    except Exception as e:
        st.error(f"❌ Ошибка анализа статистики: {e}")
        return None


RECIPE_GENERATION_PROMPT = """
Ты — шеф-повар и нутрициолог. Пользователю нужно подобрать перекус/блюдо под оставшиеся калории.

ОСТАТОК КАЛОРИЙ: {remaining_calories} ккал
ТЕКУЩИЙ БАЛАНС БЖУ ЗА ДЕНЬ: Белки: {protein}г, Жиры: {fat}г, Углеводы: {carbs}г

ЗАДАЧА:
Предложи 3 варианта перекуса или небольшого блюда, которые:
1. Вписываются в оставшиеся калории (±20 ккал)
2. Помогают сбалансировать БЖУ (если не хватает белка — предложи белковые варианты)
3. Простые в приготовлении (5-15 минут)
4. Используют доступные продукты

Верни ТОЛЬКО JSON в формате:
{{
  "recommendations": [
    {{
      "name": "Название блюда",
      "description": "Краткое описание (что входит, как готовить)",
      "calories": 250,
      "protein": 15,
      "fat": 10,
      "carbs": 25,
      "ingredients": ["Ингредиент 1", "Ингредиент 2"],
      "prep_time": "10 минут"
    }},
    {{
      "name": "Второе блюдо",
      "description": "...",
      "calories": 280,
      "protein": 12,
      "fat": 8,
      "carbs": 35,
      "ingredients": ["Ингредиент 1", "Ингредиент 2"],
      "prep_time": "5 минут"
    }},
    {{
      "name": "Третье блюдо",
      "description": "...",
      "calories": 300,
      "protein": 18,
      "fat": 12,
      "carbs": 28,
      "ingredients": ["Ингредиент 1", "Ингредиент 2"],
      "prep_time": "15 минут"
    }}
  ]
}}

ВАЖНО:
- Калории каждого блюда должны быть близки к {remaining_calories} ккал
- Все числовые значения — числа, не строки
- Ингредиенты — реальные, доступные продукты
- Описание — краткое, 1-2 предложения
"""

SLEEP_ANALYSIS_PROMPT = """
Ты — сомнолог и эксперт по гигиене сна. Проанализируй данные о сне пользователя за неделю.

Данные за неделю:
{sleep_data}

Проанализируй:
1. Среднее время засыпания и количество пробуждений.
2. Корреляцию между активностями перед сном и качеством сна (самочувствие).
3. Режим (насколько стабильно время отбоя/подъёма).

Верни ТОЛЬКО JSON в формате:
{{
  "summary": "Краткое резюме (1-2 предложения)",
  "sleep_quality_score": 7,
  "issues": ["Нестабильное время отбоя", "Позднее засыпание в выходные"],
  "recommendations": [
    {{"level": "Внимание", "text": "Рекомендация 1"}},
    {{"level": "Критично", "text": "Рекомендация 2"}}
  ]
}}
Уровень может быть: "Внимание", "Критично", "Отлично".
"""

def analyze_weekly_sleep(weekly_data: list[dict]) -> dict | None:
    """Анализ недельной статистики сна через ИИ."""
    try:
        client = get_local_client()
        
        stats_text = "\n".join([
            f"{d['date']}: Отбой {d['bedtime']}, Подъём {d['wake_time']}, "
            f"Засыпание {d['fall_asleep_time']} мин, Пробуждения {d['awakenings']}, "
            f"Самочувствие {d['wellbeing_score']}/10"
            for d in weekly_data
        ])
        
        prompt = SLEEP_ANALYSIS_PROMPT.format(sleep_data=stats_text)
        
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return safe_parse_json(response.choices[0].message.content)
    except Exception as e:
        st.error(f"❌ Ошибка анализа сна: {e}")
        return None

def generate_recipe_recommendations(remaining_calories: float, current_protein: float, current_fat: float, current_carbs: float) -> list[dict] | None:
    """Генерация рекомендаций по рецептам на основе оставшихся калорий."""
    try:
        client = get_local_client()
        
        prompt = RECIPE_GENERATION_PROMPT.format(
            remaining_calories=remaining_calories,
            protein=current_protein,
            fat=current_fat,
            carbs=current_carbs
        )
        
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Чуть больше креативности для рецептов
            response_format={"type": "json_object"}
        )
        
        raw_json = response.choices[0].message.content
        data = safe_parse_json(raw_json)
        
        if "recommendations" in data:
            return data["recommendations"]
        else:
            st.error("ИИ не вернул рекомендации в правильном формате")
            return None
        
    except Exception as e:
        st.error(f"❌ Ошибка генерации рецептов: {e}")
        return None