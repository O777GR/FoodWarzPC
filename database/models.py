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


class SleepRecord(BaseModel):
    """Модель записи о сне."""
    id: Optional[int] = None
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    bedtime: str = Field(default="", description="Время отбоя (HH:MM)")
    wake_time: str = Field(default="", description="Время подъёма (HH:MM)")
    fall_asleep_time: int = Field(default=0, ge=0, description="Время засыпания в минутах")
    awakenings: int = Field(default=0, ge=0, description="Количество ночных пробуждений")
    wellbeing_score: int = Field(default=5, ge=1, le=10, description="Самочувствие утром (1-10)")
    pre_sleep_activities: str = Field(default="", description="Активности перед сном")


class ExerciseRecord(BaseModel):
    """Модель записи о тренировке."""
    id: Optional[int] = None
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    exercise_type: str = Field(default="Кардио", description="Тип тренировки")
    exercises: str = Field(default="", description="Список упражнений (текст)")
    duration_min: int = Field(default=0, ge=0, description="Длительность в минутах")
    wellbeing_score: int = Field(default=5, ge=1, le=10, description="Самочувствие (1-10)")
    notes: str = Field(default="", description="Заметки")