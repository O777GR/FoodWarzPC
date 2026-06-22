"""Репозиторий для работы с базой данных."""
import sqlite3
from datetime import datetime, timedelta
from database.models import Meal
from config import DB_PATH


def init_db() -> None:
    """Инициализация таблиц базы данных."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Таблица приёмов пищи
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
        
        # Таблица воды
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                amount_ml REAL NOT NULL
            )
        ''')
        
        # Таблица витаминов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vitamins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                dosage TEXT,
                taken BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()


# ==========================================
# МЕТОДЫ ДЛЯ ПРИЁМОВ ПИЩИ
# ==========================================

def save_meal(meal: Meal) -> int:
    """Сохранение приёма пищи в базу данных."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meals (date, name, calories, protein, fat, carbs, is_favorite)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (meal.date, meal.name, meal.calories, meal.protein, meal.fat, meal.carbs, meal.is_favorite))
        conn.commit()
        return cursor.lastrowid


def get_todays_meals() -> list[Meal]:
    """Получение всех приёмов пищи за сегодня."""
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
    """Получение списка избранных блюд (с группировкой по названию)."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
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
    """Удаление приёма пищи по ID."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
        conn.commit()


def update_meal(meal_id: int, calories: float, protein: float, fat: float, carbs: float) -> None:
    """Обновление КБЖУ для существующего приёма пищи."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE meals 
            SET calories=?, protein=?, fat=?, carbs=? 
            WHERE id=?
        ''', (calories, protein, fat, carbs, meal_id))
        conn.commit()


def toggle_favorite(meal_id: int) -> None:
    """Переключение статуса 'Избранное' для приёма пищи."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT is_favorite FROM meals WHERE id=?', (meal_id,))
        row = cursor.fetchone()
        if row:
            new_state = not bool(row[0])
            cursor.execute('UPDATE meals SET is_favorite=? WHERE id=?', (new_state, meal_id))
            conn.commit()


# ==========================================
# МЕТОДЫ ДЛЯ ВОДЫ
# ==========================================

def save_water(amount_ml: float) -> int:
    """Сохранение записи о выпитой воде."""
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO water (date, time, amount_ml)
            VALUES (?, ?, ?)
        ''', (today, time_now, amount_ml))
        conn.commit()
        return cursor.lastrowid


def get_todays_water() -> list[dict]:
    """Получение всех записей о воде за сегодня."""
    today = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, time, amount_ml
            FROM water
            WHERE date = ?
            ORDER BY time DESC
        ''', (today,))
        
        return [
            {"id": row[0], "time": row[1], "amount_ml": row[2]}
            for row in cursor.fetchall()
        ]


def get_todays_water_total() -> float:
    """Получение общего количества воды за сегодня."""
    today = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(amount_ml)
            FROM water
            WHERE date = ?
        ''', (today,))
        
        result = cursor.fetchone()
        return result[0] if result[0] else 0.0


def delete_water(water_id: int) -> None:
    """Удаление записи о воде."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM water WHERE id = ?', (water_id,))
        conn.commit()


# ==========================================
# МЕТОДЫ ДЛЯ ВИТАМИНОВ
# ==========================================

def save_vitamin(name: str, dosage: str = "") -> int:
    """Сохранение записи о приёме витамина."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vitamins (date, name, dosage, taken)
            VALUES (?, ?, ?, 0)
        ''', (today, name, dosage))
        conn.commit()
        return cursor.lastrowid


def get_todays_vitamins() -> list[dict]:
    """Получение всех витаминов за сегодня."""
    today = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, dosage, taken
            FROM vitamins
            WHERE date = ?
            ORDER BY id
        ''', (today,))
        
        return [
            {"id": row[0], "name": row[1], "dosage": row[2], "taken": bool(row[3])}
            for row in cursor.fetchall()
        ]


def toggle_vitamin(vitamin_id: int) -> None:
    """Переключение статуса приёма витамина."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT taken FROM vitamins WHERE id=?', (vitamin_id,))
        row = cursor.fetchone()
        if row:
            new_state = not bool(row[0])
            cursor.execute('UPDATE vitamins SET taken=? WHERE id=?', (new_state, vitamin_id))
            conn.commit()


def delete_vitamin(vitamin_id: int) -> None:
    """Удаление витамина."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vitamins WHERE id = ?', (vitamin_id,))
        conn.commit()


# ==========================================
# МЕТОДЫ ДЛЯ СТАТИСТИКИ
# ==========================================

def get_weekly_stats() -> list[dict]:
    """Получить статистику за последние 7 дней."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, 
                   SUM(calories) as total_calories,
                   SUM(protein) as total_protein,
                   SUM(fat) as total_fat,
                   SUM(carbs) as total_carbs
            FROM meals
            WHERE date >= date('now', '-7 days')
            GROUP BY date
            ORDER BY date
        ''')
        
        return [
            {
                "date": row[0],
                "calories": row[1] or 0,
                "protein": row[2] or 0,
                "fat": row[3] or 0,
                "carbs": row[4] or 0
            }
            for row in cursor.fetchall()
        ]


def get_monthly_stats() -> list[dict]:
    """Получить статистику за последние 30 дней."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, 
                   SUM(calories) as total_calories,
                   SUM(protein) as total_protein,
                   SUM(fat) as total_fat,
                   SUM(carbs) as total_carbs
            FROM meals
            WHERE date >= date('now', '-30 days')
            GROUP BY date
            ORDER BY date
        ''')
        
        return [
            {
                "date": row[0],
                "calories": row[1] or 0,
                "protein": row[2] or 0,
                "fat": row[3] or 0,
                "carbs": row[4] or 0
            }
            for row in cursor.fetchall()
        ]