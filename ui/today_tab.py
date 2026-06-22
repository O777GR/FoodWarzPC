"""Вкладка 'Сегодня' — дневник питания и чат с ИИ."""
import streamlit as st
from services.ai_service import analyze_meal
from database.repository import save_meal, get_todays_meals, delete_meal, update_meal, toggle_favorite
from database.models import Meal
from config import DEFAULT_CALORIE_GOAL, DEFAULT_PROTEIN_GOAL, DEFAULT_FAT_GOAL, DEFAULT_CARBS_GOAL


def render_today_tab() -> None:
    """Отрисовка вкладки 'Сегодня'."""
    
    # Инициализация состояния для редактирования
    if "editing_meal_id" not in st.session_state:
        st.session_state.editing_meal_id = None
    
    # Две колонки: слева дневник, справа чат
    col_diary, col_chat = st.columns([2, 1])
    
    with col_diary:
        st.subheader("📋 Дневник питания")
        
        meals = get_todays_meals()
        
        if not meals:
            st.info("🍽️ Пока ничего не съедено. Опиши приём пищи в чате справа →")
        else:
            # Сводка за день
            total_cals = sum(m.calories for m in meals)
            total_p = sum(m.protein for m in meals)
            total_f = sum(m.fat for m in meals)
            total_c = sum(m.carbs for m in meals)
            
            st.write("**Итого за сегодня:**")
            c1, c2, c3, c4 = st.columns(4)
            
            cal_progress = min(total_cals / DEFAULT_CALORIE_GOAL, 1.0)
            p_progress = min(total_p / DEFAULT_PROTEIN_GOAL, 1.0)
            f_progress = min(total_f / DEFAULT_FAT_GOAL, 1.0)
            c_progress = min(total_c / DEFAULT_CARBS_GOAL, 1.0)
            
            c1.metric("🔥 Ккал", f"{total_cals:.0f} / {DEFAULT_CALORIE_GOAL}", delta=f"{cal_progress*100:.0f}%")
            c1.progress(cal_progress)
            c2.metric("💪 Белки", f"{total_p:.1f} г / {DEFAULT_PROTEIN_GOAL} г", delta=f"{p_progress*100:.0f}%")
            c2.progress(p_progress)
            c3.metric("🥑 Жиры", f"{total_f:.1f} г / {DEFAULT_FAT_GOAL} г", delta=f"{f_progress*100:.0f}%")
            c3.progress(f_progress)
            c4.metric("🍞 Углеводы", f"{total_c:.1f} г / {DEFAULT_CARBS_GOAL} г", delta=f"{c_progress*100:.0f}%")
            c4.progress(c_progress)
            
            st.divider()
            
            # Список приёмов пищи
            for meal in meals:
                with st.container(border=True):
                    # Верхняя строка: Название, Ккал, Кнопки действий
                    col_name, col_kcal, col_actions = st.columns([3, 1, 2])
                    
                    col_name.write(f"**{meal.name}** {'⭐' if meal.is_favorite else ''}")
                    col_kcal.write(f"🔥 {meal.calories:.0f} ккал")
                    
                    # Кнопки действий
                    btn_star = col_actions.button("⭐" if meal.is_favorite else "☆", key=f"fav_{meal.id}", help="В избранное")
                    btn_edit = col_actions.button("✏️", key=f"edit_{meal.id}", help="Редактировать КБЖУ")
                    btn_del = col_actions.button("🗑️", key=f"del_{meal.id}", help="Удалить")
                    
                    # Логика кнопок
                    if btn_star:
                        toggle_favorite(meal.id)
                        st.rerun()
                    if btn_del:
                        delete_meal(meal.id)
                        st.rerun()
                    
                    # Раскрывающийся блок для редактирования
                    if btn_edit:
                        st.session_state.editing_meal_id = meal.id
                    
                    if st.session_state.editing_meal_id == meal.id:
                        with st.expander("✏️ Корректировка КБЖУ", expanded=True):
                            with st.form(key=f"edit_form_{meal.id}"):
                                edit_cals = st.number_input("Калории", value=meal.calories, step=10.0)
                                edit_p = st.number_input("Белки (г)", value=meal.protein, step=1.0)
                                edit_f = st.number_input("Жиры (г)", value=meal.fat, step=1.0)
                                edit_c = st.number_input("Углеводы (г)", value=meal.carbs, step=1.0)
                                
                                form_col1, form_col2 = st.columns(2)
                                submitted = form_col1.form_submit_button("💾 Сохранить", type="primary")
                                cancelled = form_col2.form_submit_button("❌ Отмена")
                                
                                if submitted:
                                    update_meal(meal.id, edit_cals, edit_p, edit_f, edit_c)
                                    st.session_state.editing_meal_id = None
                                    st.rerun()
                                if cancelled:
                                    st.session_state.editing_meal_id = None
                                    st.rerun()
                    
                    # Мини-прогресс бары БЖУ (если не в режиме редактирования)
                    if st.session_state.editing_meal_id != meal.id:
                        col_bjy = st.container()
                        max_val = max(meal.protein, meal.fat, meal.carbs, 1)
                        col_bjy.progress(meal.protein / max_val, text=f"Б: {meal.protein:.1f}г")
                        col_bjy.progress(meal.fat / max_val, text=f"Ж: {meal.fat:.1f}г")
                        col_bjy.progress(meal.carbs / max_val, text=f"У: {meal.carbs:.1f}г")

    with col_chat:
        st.subheader("💬 ИИ-ассистент")
        render_chat_widget()


def render_chat_widget() -> None:
    """Виджет чата для быстрого добавления еды."""
    st.caption("Опиши что съел — ИИ посчитает калории")
    
    user_input = st.text_area(
        "Что съел?",
        placeholder="Например: борщ с хлебом",
        height=80,
        key="chat_input"
    )
    
    add_to_fav = st.checkbox("Сразу в избранное", key="chat_fav")
    
    if st.button("🚀 Добавить", use_container_width=True, type="primary"):
        if user_input:
            with st.spinner("ИИ считает..."):
                result = analyze_meal(user_input)
            
            if result:
                if isinstance(result, list):
                    for meal in result:
                        meal.is_favorite = add_to_fav
                        save_meal(meal)
                    st.success(f"✅ Добавлено {len(result)} блюд")
                else:
                    result.is_favorite = add_to_fav
                    save_meal(result)
                    st.success(f"✅ Добавлено: {result.name}")
                st.rerun()
        else:
            st.warning("Введи описание!")