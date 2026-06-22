"""Утилиты для парсинга данных."""
import re
import json


def safe_parse_json(raw_text: str) -> dict | list[dict]:
    """
    Безопасный парсинг JSON с поддержкой нескольких объектов.
    
    Args:
        raw_text: Сырой текст от ИИ
        
    Returns:
        dict | list[dict]: Один объект или список объектов
        
    Raises:
        ValueError: Если JSON невалиден
    """
    # Сохраняем для отладки
    print(f"🔍 RAW RESPONSE: {raw_text}")
    
    # 1. Ищем JSON внутри markdown-блоков
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
    if match:
        clean_text = match.group(1)
    else:
        clean_text = raw_text.strip()
    
    # 2. Пытаемся распарсить как один JSON
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass
    
    # 3. Если не получилось — ищем несколько JSON-объектов
    json_objects = []
    # Ищем все блоки {...}
    pattern = r'\{[^{}]*\}'
    matches = re.findall(pattern, clean_text, re.DOTALL)
    
    for match in matches:
        try:
            obj = json.loads(match)
            json_objects.append(obj)
        except json.JSONDecodeError:
            continue
    
    if json_objects:
        return json_objects
    
    # 4. Если ничего не нашли — ошибка
    raise ValueError(
        f"Не удалось найти валидный JSON в ответе модели.\n"
        f"Полный ответ: {raw_text[:500]}..."
    )