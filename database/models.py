"""Модели данных для приложения."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Meal(BaseModel):
    """Модель приёма пищи."""
    name: str = Field(..., description="Название блюда")
    calories: float = Field(..., ge=0, description="Калории в ккал")
    protein: float = Field(..., ge=0, description="Белки в граммах")
    fat: float = Field(..., ge=0, description="Жиры в граммах")
    carbs: float = Field(..., ge=0, description="Углеводы в граммах")
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"), description="Время приёма пищи")
    meal_type: str = Field(default="Другое", description="Тип приёма пищи: Завтрак, Обед, Ужин, 1-й перекус, 2-й перекус, Другое")
    amount: str = Field(default="", description="Количество (например: 200г, 300мл, 1 тарелка)")
    is_favorite: bool = Field(default=False, description="Добавлено в избранное")
    id: Optional[int] = Field(default=None, description="ID записи в БД")

    class Config:
        """Конфигурация Pydantic."""
        json_schema_extra = {
            "example": {
                "name": "Борщ украинский",
                "calories": 158,
                "protein": 12,
                "fat": 5,
                "carbs": 18,
                "date": "2026-06-22",
                "time": "13:30",
                "meal_type": "Обед",
                "amount": "300мл",
                "is_favorite": True
            }
        }