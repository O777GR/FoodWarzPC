"""Вкладка 'Витамины' — трекер приёма витаминов."""
import streamlit as st
from database.repository import save_vitamin, get_todays_vitamins, toggle_vitamin, delete_vitamin
from config import DEFAULT_VITAMINS


def render_vitamins_tab() -> None:
    """Отрисовка вкладки 'Витамины'."""
    st.subheader("💊 Трекер витаминов")
    
    # Добавление нового витамина
    with st.expander("➕ Добавить витамин"):
        vitamin_name = st.text_input("Название", placeholder="Например: Витамин D")
        vitamin_dosage = st.text_input("Дозировка", placeholder="Например: 1000 МЕ")
        
        if st.button("💾 Сохранить", type="primary"):
            if vitamin_name:
                save_vitamin(vitamin_name, vitamin_dosage)
                st.success(f"✅ {vitamin_name} добавлен")
                st.rerun()
            else:
                st.warning("Введи название витамина")
    
    st.divider()
    
    # Быстрое добавление популярных витаминов
    st.write("**⚡ Быстрое добавление:**")
    cols = st.columns(4)
    for idx, vitamin in enumerate(DEFAULT_VITAMINS):
        if cols[idx % 4].button(vitamin, use_container_width=True):
            save_vitamin(vitamin)
            st.success(f"✅ {vitamin} добавлен")
            st.rerun()
    
    st.divider()
    
    # Список витаминов за сегодня
    st.write("**📋 Витамины на сегодня:**")
    
    vitamins = get_todays_vitamins()
    
    if not vitamins:
        st.info("Пока нет витаминов на сегодня")
    else:
        # Счётчики
        taken_count = sum(1 for v in vitamins if v['taken'])
        total_count = len(vitamins)
        
        st.write(f"Принято: **{taken_count}** из **{total_count}**")
        st.progress(taken_count / total_count if total_count > 0 else 0)
        
        st.divider()
        
        for vitamin in vitamins:
            with st.container(border=True):
                col_name, col_status, col_actions = st.columns([3, 2, 2])
                
                # Название и дозировка
                name_text = f"**{vitamin['name']}**"
                if vitamin['dosage']:
                    name_text += f" ({vitamin['dosage']})"
                col_name.write(name_text)
                
                # Статус
                status = "✅ Принят" if vitamin['taken'] else "⏳ Ожидает"
                col_status.write(status)
                
                # Кнопки
                if col_actions.button("✓" if not vitamin['taken'] else "↺", key=f"toggle_{vitamin['id']}"):
                    toggle_vitamin(vitamin['id'])
                    st.rerun()
                
                if col_actions.button("🗑️", key=f"del_vit_{vitamin['id']}"):
                    delete_vitamin(vitamin['id'])
                    st.rerun()