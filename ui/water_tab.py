"""Вкладка 'Вода' — трекер потребления воды."""
import streamlit as st
from database.repository import save_water, get_todays_water, get_todays_water_total, delete_water
from config import DEFAULT_WATER_GOAL_ML, DEFAULT_WATER_PORTION_ML


def render_water_tab() -> None:
    """Отрисовка вкладки 'Вода'."""
    st.subheader("💧 Трекер воды")
    
    # Настройки
    with st.sidebar:
        st.write("**⚙️ Настройки воды**")
        water_goal = st.number_input("Цель (мл/день)", value=DEFAULT_WATER_GOAL_ML, step=100, key="water_goal_input")
        portion_size = st.number_input("Размер порции (мл)", value=DEFAULT_WATER_PORTION_ML, step=50, key="water_portion_input")
    
    # Получаем данные за сегодня
    water_records = get_todays_water()
    total_water = get_todays_water_total()
    
    # Прогресс
    progress = min(total_water / water_goal, 1.0)
    
    st.write(f"**Прогресс:** {total_water:.0f} мл / {water_goal} мл ({progress*100:.0f}%)")
    st.progress(progress)
    
    if total_water >= water_goal:
        st.success("🎉 Цель по воде достигнута!")
    
    st.divider()
    
    # Быстрое добавление
    st.write("**⚡ Быстрое добавление:**")
    col1, col2, col3, col4 = st.columns(4)
    
    if col1.button(f"🥛 {portion_size} мл", use_container_width=True, key="btn_water_1"):
        save_water(portion_size)
        st.rerun()
    
    if col2.button(f"🥤 {portion_size*2} мл", use_container_width=True, key="btn_water_2"):
        save_water(portion_size * 2)
        st.rerun()
    
    if col3.button(f"🍶 500 мл", use_container_width=True, key="btn_water_3"):
        save_water(500)
        st.rerun()
    
    if col4.button(f"🫙 1000 мл", use_container_width=True, key="btn_water_4"):
        save_water(1000)
        st.rerun()
    
    # Ручной ввод
    st.divider()
    st.write("**✏️ Ручной ввод:**")
    custom_amount = st.number_input("Количество (мл)", min_value=1, value=250, step=50, key="water_custom_amount")
    
    if st.button("➕ Добавить", use_container_width=True, type="primary", key="btn_add_water"):
        save_water(custom_amount)
        st.success(f"✅ Добавлено {custom_amount} мл")
        st.rerun()
    
    # История за сегодня
    st.divider()
    st.write("**📋 История за сегодня:**")
    
    if not water_records:
        st.info("Пока нет записей")
    else:
        for record in water_records:
            col_time, col_amount, col_action = st.columns([2, 2, 1])
            col_time.write(f"🕐 {record['time']}")
            col_amount.write(f"{record['amount_ml']:.0f} мл")
            
            if col_action.button("🗑️", key=f"del_water_{record['id']}"):
                delete_water(record['id'])
                st.rerun()