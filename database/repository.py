"""Репозиторий для работы с базой данных."""
import sqlite3
from datetime import datetime
from pathlib import Path
from database.models import Meal
from config import DB_PATH


def init_db() -> None:
    """Инициализация таблиц базы данных."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                fat REAL NOT NULL,
                carbs REAL NOT NULL,
                is_favorite BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()


def save_meal(meal: Meal) -> int:
    """
    Сохранение приёма пищи в базу данных.
    
    Args:
        meal: Объект Meal для сохранения
        
    Returns:
        int: ID созданной записи
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meals (date, name, calories, protein, fat, carbs, is_favorite)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (meal.date, meal.name, meal.calories, meal.protein, meal.fat, meal.carbs, meal.is_favorite))
        conn.commit()
        return cursor.lastrowid


def get_todays_meals() -> list[Meal]:
    """
    Получение всех приёмов пищи за сегодня.
    
    Returns:
        list[Meal]: Список объектов Meal
    """
    today = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, date, name, calories, protein, fat, carbs, is_favorite
            FROM meals
            WHERE date = ?
            ORDER BY id DESC
        ''', (today,))
        
        meals = []
        for row in cursor.fetchall():
            meal = Meal(
                id=row[0],
                date=row[1],
                name=row[2],
                calories=row[3],
                protein=row[4],
                fat=row[5],
                carbs=row[6],
                is_favorite=bool(row[7])
            )
            meals.append(meal)
        return meals


def get_favorites() -> list[Meal]:
    """
    Получение списка избранных блюд (с группировкой по названию).
    
    Returns:
        list[Meal]: Список уникальных избранных блюд
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Группируем по имени и берем последние значения КБЖУ
        cursor.execute('''
            SELECT name, calories, protein, fat, carbs
            FROM meals
            WHERE is_favorite = 1
            GROUP BY name
            ORDER BY MAX(id) DESC
        ''')
        
        favorites = []
        for row in cursor.fetchall():
            meal = Meal(
                name=row[0],
                calories=row[1],
                protein=row[2],
                fat=row[3],
                carbs=row[4]
            )
            favorites.append(meal)
        return favorites


def delete_meal(meal_id: int) -> None:
    """
    Удаление приёма пищи по ID.
    
    Args:
        meal_id: ID записи для удаления
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
        conn.commit()


def update_meal(meal_id: int, calories: float, protein: float, fat: float, carbs: float) -> None:
    """
    Обновление КБЖУ для существующего приёма пищи.
    
    Args:
        meal_id: ID записи для обновления
        calories: Новое значение калорий
        protein: Новое значение белков
        fat: Новое значение жиров
        carbs: Новое значение углеводов
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE meals 
            SET calories=?, protein=?, fat=?, carbs=? 
            WHERE id=?
        ''', (calories, protein, fat, carbs, meal_id))
        conn.commit()


def toggle_favorite(meal_id: int) -> None:
    """
    Переключение статуса 'Избранное' для приёма пищи.
    
    Args:
        meal_id: ID записи для переключения
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT is_favorite FROM meals WHERE id=?', (meal_id,))
        row = cursor.fetchone()
        if row:
            new_state = not bool(row[0])
            cursor.execute('UPDATE meals SET is_favorite=? WHERE id=?', (new_state, meal_id))
            conn.commit()