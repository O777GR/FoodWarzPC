"""Главное приложение FoodWarz PC."""
import sys
import os

# Добавляем корневую директорию в путь для корректных импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from ui.today_tab import render_today_tab
from ui.stats_tab import render_stats_tab
from ui.products_tab import render_products_tab
from ui.water_tab import render_water_tab
from ui.vitamins_tab import render_vitamins_tab
from ui.sleep_tab import render_sleep_tab
from ui.exercise_tab import render_exercise_tab
from database.repository import init_db


def main() -> None:
    """Главная функция приложения."""
    st.set_page_config(
        page_title="FoodWarz PC",
        page_icon="🍲",
        layout="wide"
    )
    
    # Инициализация базы данных
    init_db()
    
    st.title("🍲 FoodWarz PC")
    st.caption("Твой персональный трекер питания с локальным ИИ")
    
    # Основные вкладки
    tab_today, tab_water, tab_vitamins, tab_sleep, tab_exercise, tab_stats, tab_products = st.tabs([
        "📅 Сегодня",
        " Вода",
        "💊 Витамины",
        "🌙 Сон",
        "️ Упражнения",
        "📊 Статистика",
        "🍽️ Продукты"
    ])

    with tab_today:
        render_today_tab()

    with tab_water:
        render_water_tab()

    with tab_vitamins:
        render_vitamins_tab()

    with tab_sleep:
        render_sleep_tab()

    with tab_exercise:
        render_exercise_tab()

    with tab_stats:
        render_stats_tab()

    with tab_products:
        render_products_tab()


if __name__ == "__main__":
    main()