"""Вкладка 'Продукты' — база избранных блюд."""
import streamlit as st
from database.repository import get_favorites, delete_meal
import sqlite3
from config import DB_PATH


def render_products_tab() -> None:
    """Отрисовка вкладки 'Продукты'."""
    st.subheader("🍽️ База избранных блюд")
    st.caption("Здесь хранятся твои часто используемые блюда для быстрого добавления")
    
    favorites = get_favorites()
    
    if not favorites:
        st.info("⭐ Пока нет избранных блюд. Добавляй блюда с галочкой 'В избранное'")
        return
    
    # Поиск по базе
    search = st.text_input("🔍 Поиск блюд:", placeholder="Например: борщ")
    
    if search:
        favorites = [f for f in favorites if search.lower() in f.name.lower()]
    
    st.write(f"Найдено блюд: **{len(favorites)}**")
    st.divider()
    
    # Отображение в виде карточек
    cols = st.columns(3)
    for idx, meal in enumerate(favorites):
        with cols[idx % 3]:
            with st.container(border=True):
                st.write(f"**{meal.name}**")
                st.caption(f"🔥 {meal.calories:.0f} ккал")
                
                c1, c2 = st.columns(2)
                c1.metric("Б", f"{meal.protein:.0f}г")
                c2.metric("Ж", f"{meal.fat:.0f}г")
                
                c3, c4 = st.columns(2)
                c3.metric("У", f"{meal.carbs:.0f}г")
                
                # Кнопка быстрого добавления (сегодня)
                if st.button("➕ Добавить сегодня", key=f"add_{meal.id}", use_container_width=True):
                    from database.repository import save_meal
                    from database.models import Meal
                    save_meal(meal)
                    st.success(f"✅ {meal.name} добавлен!")
                    st.rerun()
                
                # Кнопка удаления из избранного
                if st.button("🗑️ Удалить", key=f"del_{meal.id}", use_container_width=True):
                    delete_meal(meal.id)
                    st.success("Удалено!")
                    st.rerun()