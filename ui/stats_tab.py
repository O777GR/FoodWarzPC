"""Вкладка 'Статистика' — графики и аналитика."""
import streamlit as st
import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH, DEFAULT_CALORIE_GOAL


def render_stats_tab() -> None:
    """Отрисовка вкладки 'Статистика'."""
    st.subheader("📊 Статистика питания")
    
    # Выбор периода
    period = st.selectbox(
        "Период:",
        ["Неделя", "Месяц"],
        key="stats_period"
    )
    
    # Получаем данные из БД
    data = get_weekly_stats() if period == "Неделя" else get_monthly_stats()
    
    if not data:
        st.info("📭 Пока недостаточно данных для статистики")
        return
    
    # График калорий за период
    st.write("**🔥 Калории по дням**")
    chart_data = {
        "День": [d["date"] for d in data],
        "Ккал": [d["calories"] for d in data],
        "Цель": [DEFAULT_CALORIE_GOAL] * len(data)
    }
    st.bar_chart(chart_data, x="День", y=["Ккал", "Цель"])
    
    # Средняя статистика
    avg_calories = sum(d["calories"] for d in data) / len(data)
    avg_protein = sum(d["protein"] for d in data) / len(data)
    avg_fat = sum(d["fat"] for d in data) / len(data)
    avg_carbs = sum(d["carbs"] for d in data) / len(data)
    
    st.divider()
    st.write("**📈 Среднее за период:**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ккал", f"{avg_calories:.0f}")
    c2.metric("Белки", f"{avg_protein:.1f} г")
    c3.metric("Жиры", f"{avg_fat:.1f} г")
    c4.metric("Углеводы", f"{avg_carbs:.1f} г")


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