"""Вкладка 'Сегодня' — дневник питания и чат с ИИ."""
import streamlit as st
from services.ai_service import analyze_meal, generate_recipe_recommendations
from database.repository import (
    save_meal, get_todays_meals, delete_meal, update_meal, toggle_favorite,
    save_water, get_todays_water_total, get_todays_water, delete_water,
    get_todays_vitamins, toggle_vitamin
)
from database.models import Meal
from config import (
    DEFAULT_CALORIE_GOAL, DEFAULT_PROTEIN_GOAL, DEFAULT_FAT_GOAL, DEFAULT_CARBS_GOAL,
    DEFAULT_WATER_GOAL_ML, DEFAULT_WATER_PORTION_ML
)


def render_today_tab() -> None:
    """Отрисовка вкладки 'Сегодня'."""
    
    # Инициализация состояния для редактирования
    if "editing_meal_id" not in st.session_state:
        st.session_state.editing_meal_id = None
    
    # Три колонки: дневник, чат, трекеры
    col_diary, col_chat, col_trackers = st.columns([2, 1, 1])
    
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
            
            c1.metric("🔥 Калории", f"{total_cals:.0f} / {DEFAULT_CALORIE_GOAL}", delta=f"{cal_progress*100:.0f}%")
            c1.progress(cal_progress)
            c2.metric("💪 Белки", f"{total_p:.1f} г / {DEFAULT_PROTEIN_GOAL} г", delta=f"{p_progress*100:.0f}%")
            c2.progress(p_progress)
            c3.metric(" Жиры", f"{total_f:.1f} г / {DEFAULT_FAT_GOAL} г", delta=f"{f_progress*100:.0f}%")
            c3.progress(f_progress)
            c4.metric("🍞 Углеводы", f"{total_c:.1f} г / {DEFAULT_CARBS_GOAL} г", delta=f"{c_progress*100:.0f}%")
            c4.progress(c_progress)
            
            st.divider()
            
            # Виджет "Что съесть?"
            remaining_calories = DEFAULT_CALORIE_GOAL - total_cals
            
            if remaining_calories > 50:
                with st.expander(f" Что съесть? Осталось {remaining_calories:.0f} ккал", expanded=False):
                    st.caption(f"Текущий баланс: Б:{total_p:.0f}г, Ж:{total_f:.0f}г, У:{total_c:.0f}г")
                    
                    if st.button("🔍 Подобрать перекус", use_container_width=True, type="primary", key="btn_generate_recipe"):
                        with st.spinner("ИИ подбирает рецепты..."):
                            recommendations = generate_recipe_recommendations(
                                remaining_calories,
                                total_p,
                                total_f,
                                total_c
                            )
                        
                        if recommendations:
                            st.session_state.recipe_recommendations = recommendations
                            st.rerun()
                    
                    # Показываем рекомендации
                    if "recipe_recommendations" in st.session_state:
                        st.write("**💡 Рекомендации от ИИ:**")
                        
                        for idx, recipe in enumerate(st.session_state.recipe_recommendations):
                            with st.container(border=True):
                                st.write(f"**{recipe.get('name', 'Без названия')}**")
                                
                                if 'description' in recipe:
                                    st.caption(recipe['description'])
                                
                                # Ингредиенты
                                if 'ingredients' in recipe:
                                    st.write(f"**🥕 Ингредиенты:** {', '.join(recipe['ingredients'])}")
                                
                                # Время приготовления
                                if 'prep_time' in recipe:
                                    st.write(f"⏱️ **Время:** {recipe['prep_time']}")
                                
                                # КБЖУ
                                col1, col2, col3, col4 = st.columns(4)
                                col1.metric("🔥 Ккал", f"{recipe.get('calories', 0):.0f}")
                                col2.metric("💪 Б", f"{recipe.get('protein', 0):.0f}г")
                                col3.metric(" Ж", f"{recipe.get('fat', 0):.0f}г")
                                col4.metric("🍞 У", f"{recipe.get('carbs', 0):.0f}г")
                                
                                # Кнопка добавления
                                if st.button(f"✅ Добавить в дневник", key=f"add_recipe_{idx}", use_container_width=True):
                                    # Создаём Meal из рецепта
                                    meal = Meal(
                                        name=recipe.get('name', 'Без названия'),
                                        calories=recipe.get('calories', 0),
                                        protein=recipe.get('protein', 0),
                                        fat=recipe.get('fat', 0),
                                        carbs=recipe.get('carbs', 0),
                                        amount="1 порция",
                                        meal_type="1-й перекус" if remaining_calories < 500 else "Другое"
                                    )
                                    save_meal(meal)
                                    st.success(f"✅ {recipe.get('name', 'Блюдо')} добавлен!")
                                    
                                    # Очищаем рекомендации
                                    if 'recipe_recommendations' in st.session_state:
                                        del st.session_state.recipe_recommendations
                                    st.rerun()
            else:
                st.info(" Цель по калориям достигнута! Отличная работа!")
            
            st.divider()
            
            # Группировка по типу приёма пищи
            meal_types = ["Завтрак", "Обед", "Ужин", "1-й перекус", "2-й перекус", "Другое"]
            
            for meal_type in meal_types:
                type_meals = [m for m in meals if m.meal_type == meal_type]
                
                if type_meals:
                    # Иконка для типа приёма пищи
                    icons = {
                        "Завтрак": "🌅",
                        "Обед": "☀️",
                        "Ужин": "🌙",
                        "1-й перекус": "🍎",
                        "2-й перекус": "🍪",
                        "Другое": "🍽️"
                    }
                    icon = icons.get(meal_type, "🍽️")
                    
                    st.write(f"### {icon} {meal_type}")
                    
                    for meal in type_meals:
                        with st.container(border=True):
                            # Верхняя строка: Время, Название, Ккал
                            col_time, col_name, col_kcal, col_actions = st.columns([1, 3, 1, 2])
                            
                            # Время
                            if meal.time:
                                col_time.write(f"🕐 **{meal.time}**")
                            else:
                                col_time.write("")
                            
                            # Название и количество
                            name_text = f"**{meal.name}**"
                            if meal.amount:
                                name_text += f"\n_{meal.amount}_"
                            if meal.is_favorite:
                                name_text += " ⭐"
                            col_name.write(name_text)
                            
                            # Калории
                            col_kcal.write(f"🔥 {meal.calories:.0f} ккал")
                            
                            # Кнопки действий
                            btn_star = col_actions.button("⭐" if meal.is_favorite else "☆", key=f"fav_{meal.id}", help="В избранное")
                            btn_edit = col_actions.button("️", key=f"edit_{meal.id}", help="Редактировать КБЖУ")
                            btn_del = col_actions.button("🗑️", key=f"del_{meal.id}", help="Удалить")
                            
                            if btn_star:
                                toggle_favorite(meal.id)
                                st.rerun()
                            if btn_del:
                                delete_meal(meal.id)
                                st.rerun()
                            
                            if btn_edit:
                                st.session_state.editing_meal_id = meal.id
                            
                            if st.session_state.editing_meal_id == meal.id:
                                with st.expander("✏️ Корректировка КБЖУ", expanded=True):
                                    with st.form(key=f"edit_form_{meal.id}"):
                                        edit_cals = st.number_input("Калории", value=meal.calories, step=10.0)
                                        edit_p = st.number_input("Белки (г)", value=meal.protein, step=1.0)
                                        edit_f = st.number_input("Жиры (г)", value=meal.fat, step=1.0)
                                        edit_c = st.number_input("Углеводы (г)", value=meal.carbs, step=1.0)
                                        edit_amount = st.text_input("Количество", value=meal.amount)
                                        
                                        form_col1, form_col2 = st.columns(2)
                                        submitted = form_col1.form_submit_button("💾 Сохранить", type="primary")
                                        cancelled = form_col2.form_submit_button("❌ Отмена")
                                        
                                        if submitted:
                                            update_meal(meal.id, edit_cals, edit_p, edit_f, edit_c, edit_amount)
                                            st.session_state.editing_meal_id = None
                                            st.rerun()
                                        if cancelled:
                                            st.session_state.editing_meal_id = None
                                            st.rerun()
                            
                            if st.session_state.editing_meal_id != meal.id:
                                col_bjy = st.container()
                                max_val = max(meal.protein, meal.fat, meal.carbs, 1)
                                col_bjy.progress(meal.protein / max_val, text=f"Б: {meal.protein:.1f}г")
                                col_bjy.progress(meal.fat / max_val, text=f"Ж: {meal.fat:.1f}г")
                                col_bjy.progress(meal.carbs / max_val, text=f"У: {meal.carbs:.1f}г")
                    
                    st.divider()

    with col_chat:
        st.subheader("💬 ИИ-ассистент")
        render_chat_widget()
    
    with col_trackers:
        # Виджет воды
        st.subheader("💧 Вода")
        total_water = get_todays_water_total()
        water_progress = min(total_water / DEFAULT_WATER_GOAL_ML, 1.0)
        st.write(f"{total_water:.0f} / {DEFAULT_WATER_GOAL_ML} мл")
        st.progress(water_progress)
        
        if st.button(f"+{DEFAULT_WATER_PORTION_ML} мл", use_container_width=True, key="btn_add_water_widget"):
            save_water(DEFAULT_WATER_PORTION_ML)
            st.rerun()
        
        st.divider()
        
        # Виджет витаминов
        st.subheader("💊 Витамины")
        vitamins = get_todays_vitamins()
        
        if vitamins:
            taken = sum(1 for v in vitamins if v['taken'])
            st.write(f"{taken}/{len(vitamins)} принято")
            st.progress(taken / len(vitamins))
            
            for vitamin in vitamins[:3]:  # Показываем только первые 3
                status = "✅" if vitamin['taken'] else "⏳"
                st.write(f"{status} {vitamin['name']}")
                
                if st.button("✓", key=f"vit_{vitamin['id']}", use_container_width=True):
                    toggle_vitamin(vitamin['id'])
                    st.rerun()
        else:
            st.info("Нет витаминов на сегодня")


def render_chat_widget() -> None:
    """Виджет чата для быстрого добавления еды."""
    st.caption("Опиши что съел — ИИ посчитает калории")
    
    user_input = st.text_area(
        "Что съел?",
        placeholder="Например: Завтрак в 8:00: 200г овсянки с молоком",
        height=80,
        key="chat_input"
    )
    
    add_to_fav = st.checkbox("Сразу в избранное", key="chat_fav")
    
    if st.button("🚀 Добавить", use_container_width=True, type="primary", key="btn_add_meal"):
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
            st.warning("⚠️ Введи описание!")