"""Вкладка чата с ИИ для анализа приёмов пищи."""
import streamlit as st
from services.ai_service import analyze_meal
from database.repository import save_meal, get_favorites
from database.models import Meal


def render_chat_tab() -> None:
    """Отрисовка вкладки чата с ИИ."""
    st.subheader("Что съел?")
    
    # Инициализация session_state для последних добавленных блюд
    if "last_added_meals" not in st.session_state:
        st.session_state.last_added_meals = []
    
    # Показываем последние добавленные блюда (если есть)
    if st.session_state.last_added_meals:
        meals = st.session_state.last_added_meals
        
        if len(meals) == 1:
            meal = meals[0]
            st.success(f"✅ Добавлено: **{meal.name}**")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🔥 Ккал", f"{meal.calories:.0f}")
            c2.metric("💪 Белки", f"{meal.protein:.1f} г")
            c3.metric("🥑 Жиры", f"{meal.fat:.1f} г")
            c4.metric("🍞 Углеводы", f"{meal.carbs:.1f} г")
        else:
            st.success(f"✅ Добавлено {len(meals)} блюд:")
            
            for meal in meals:
                with st.container(border=True):
                    st.write(f"**{meal.name}**")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("🔥 Ккал", f"{meal.calories:.0f}")
                    c2.metric("💪 Белки", f"{meal.protein:.1f} г")
                    c3.metric("🥑 Жиры", f"{meal.fat:.1f} г")
                    c4.metric("🍞 Углеводы", f"{meal.carbs:.1f} г")
        
        st.divider()
        # Очищаем после показа
        st.session_state.last_added_meals = []
    
    # Блок избранных блюд
    favorites = get_favorites()
    if favorites:
        st.write("⭐ **Избранные блюда** (нажми, чтобы быстро добавить):")
        cols = st.columns(3)
        for idx, fav in enumerate(favorites[:6]):
            if cols[idx % 3].button(fav.name, use_container_width=True):
                meal = Meal(
                    name=fav.name,
                    calories=fav.calories,
                    protein=fav.protein,
                    fat=fav.fat,
                    carbs=fav.carbs,
                    is_favorite=True
                )
                save_meal(meal)
                st.success(f"✅ Добавлено: {fav.name}")
                st.rerun()
        
        if len(favorites) > 6:
            st.caption(f"И ещё {len(favorites) - 6} блюд...")
    
    st.divider()
    
    user_input = st.text_area(
        "Опиши приём пищи",
        placeholder="Например: Съел тарелку борща с говядиной и кусок черного хлеба",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        add_to_fav = st.checkbox("В избранное")
    
    if st.button("🚀 Анализировать и добавить", use_container_width=True, type="primary"):
        if user_input:
            with st.spinner("Локальная модель считает калории..."):
                result = analyze_meal(user_input)
            
            if result:
                # Если вернулась список — сохраняем все блюда
                if isinstance(result, list):
                    for meal in result:
                        meal.is_favorite = add_to_fav
                        save_meal(meal)
                    st.session_state.last_added_meals = result
                else:
                    # Если вернулась один объект
                    result.is_favorite = add_to_fav
                    save_meal(result)
                    st.session_state.last_added_meals = [result]
                
                st.rerun()
        else:
            st.warning("⚠️ Введи описание приёма пищи!")