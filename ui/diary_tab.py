"""Вкладка дневника питания."""
import streamlit as st
from database.repository import get_todays_meals, delete_meal
from database.models import Meal
from config import DEFAULT_CALORIE_GOAL, DEFAULT_PROTEIN_GOAL, DEFAULT_FAT_GOAL, DEFAULT_CARBS_GOAL


def render_diary_tab() -> None:
    """Отрисовка вкладки дневника питания."""
    st.subheader("📅 Дневник питания")
    
    meals = get_todays_meals()
    
    if not meals:
        st.info("🍽️ Пока ничего не съедено. Перейди во вкладку 'Опиши приём пищи'.")
        return
    
    # Сводка за день
    total_cals = sum(m.calories for m in meals)
    total_p = sum(m.protein for m in meals)
    total_f = sum(m.fat for m in meals)
    total_c = sum(m.carbs for m in meals)
    
    st.write("**Итого за сегодня:**")
    c1, c2, c3, c4 = st.columns(4)
    
    # Прогресс-бары для целей
    cal_progress = min(total_cals / DEFAULT_CALORIE_GOAL, 1.0)
    p_progress = min(total_p / DEFAULT_PROTEIN_GOAL, 1.0)
    f_progress = min(total_f / DEFAULT_FAT_GOAL, 1.0)
    c_progress = min(total_c / DEFAULT_CARBS_GOAL, 1.0)
    
    c1.metric("🔥 Калории", f"{total_cals:.0f} / {DEFAULT_CALORIE_GOAL}", 
              delta=f"{cal_progress*100:.0f}%")
    c1.progress(cal_progress)
    
    c2.metric("💪 Белки", f"{total_p:.1f} г / {DEFAULT_PROTEIN_GOAL} г",
              delta=f"{p_progress*100:.0f}%")
    c2.progress(p_progress)
    
    c3.metric("🥑 Жиры", f"{total_f:.1f} г / {DEFAULT_FAT_GOAL} г",
              delta=f"{f_progress*100:.0f}%")
    c3.progress(f_progress)
    
    c4.metric(" Углеводы", f"{total_c:.1f} г / {DEFAULT_CARBS_GOAL} г",
              delta=f"{c_progress*100:.0f}%")
    c4.progress(c_progress)
    
    st.divider()
    
    # Список приёмов пищи
    st.write("**Приёмы пищи:**")
    for meal in meals:
        with st.container(border=True):
            col_name, col_kcal, col_bjy, col_actions = st.columns([3, 1, 4, 1])
            
            col_name.write(f"**{meal.name}**")
            col_kcal.write(f"🔥 {meal.calories:.0f} ккал")
            
            # Прогресс-бары БЖУ для каждого блюда
            max_val = max(meal.protein, meal.fat, meal.carbs, 1)
            col_bjy.progress(meal.protein / max_val, text=f"Б: {meal.protein:.1f}г")
            col_bjy.progress(meal.fat / max_val, text=f"Ж: {meal.fat:.1f}г")
            col_bjy.progress(meal.carbs / max_val, text=f"У: {meal.carbs:.1f}г")
            
            # Кнопка удаления
            if col_actions.button("️", key=f"delete_{meal.id}"):
                delete_meal(meal.id)
                st.rerun()