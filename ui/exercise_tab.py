"""Вкладка 'Упражнения' — трекер тренировок."""
import streamlit as st
from database.repository import save_exercise_record, get_todays_exercises, delete_exercise
from database.models import ExerciseRecord


def render_exercise_tab() -> None:
    """Отрисовка вкладки 'Упражнения'."""
    st.subheader("🏋️ Трекер упражнений")
    
    # Форма добавления тренировки
    with st.form(key="exercise_form", clear_on_submit=True):
        st.write("**Добавить тренировку:**")
        
        col1, col2 = st.columns(2)
        exercise_type = col1.selectbox("Тип тренировки", ["Кардио", "Силовая", "Растяжка", "Йога", "Другое"])
        duration_min = col2.number_input("Время (мин)", min_value=0, value=15, step=5)
        
        st.write("**Упражнения:**")
        exercises_text = st.text_area(
            "Список упражнений (каждое с новой строки)",
            placeholder="Шаги в стороны с подъёмом рук: 2 подхода × 60 сек\nПодъёмы коленей с хлопком: 3 подхода × 20 сек",
            height=150
        )
        
        wellbeing = st.slider("Самочувствие после тренировки (1-10)", 1, 10, value=7)
        notes = st.text_area("Заметки", placeholder="Немного устал, но нормально")
        
        submitted = st.form_submit_button("💾 Сохранить тренировку", type="primary", use_container_width=True)
        
        if submitted:
            if exercises_text:
                record = ExerciseRecord(
                    exercise_type=exercise_type,
                    exercises=exercises_text,
                    duration_min=int(duration_min),
                    wellbeing_score=int(wellbeing),
                    notes=notes
                )
                save_exercise_record(record)
                st.success("✅ Тренировка сохранена!")
                st.rerun()
            else:
                st.warning("⚠️ Добавь хотя бы одно упражнение")
    
    st.divider()
    
    # Тренировки за сегодня
    st.write("### 📋 Тренировки за сегодня")
    today_exercises = get_todays_exercises()
    
    if not today_exercises:
        st.info("Сегодня ещё не было тренировок")
    else:
        for record in today_exercises:
            with st.container(border=True):
                col_type, col_time, col_score, col_action = st.columns([2, 2, 2, 1])
                
                col_type.write(f"**{record.exercise_type}**")
                col_time.write(f"⏱️ {record.duration_min} мин")
                col_score.write(f"😊 {record.wellbeing_score}/10")
                
                if col_action.button("🗑️", key=f"del_ex_{record.id}"):
                    delete_exercise(record.id)
                    st.rerun()
                
                st.write("**Упражнения:**")
                st.text(record.exercises)
                
                if record.notes:
                    st.caption(f"📝 {record.notes}")
                
                # Экспорт в TXT
                txt_content = format_exercise_to_txt(record)
                st.download_button(
                    label=" Скачать TXT",
                    data=txt_content,
                    file_name=f"exercise_{record.date}_{record.id}.txt",
                    mime="text/plain",
                    key=f"download_{record.id}"
                )


def format_exercise_to_txt(record: ExerciseRecord) -> str:
    """Форматирование тренировки в TXT."""
    txt = f"Дата: {record.date}\n"
    txt += f"Тип: {record.exercise_type}\n"
    txt += f"Упражнения:\n{record.exercises}\n"
    txt += f"Время: {record.duration_min} мин\n"
    txt += f"Самочувствие: {record.wellbeing_score}/10\n"
    if record.notes:
        txt += f"Заметки: {record.notes}\n"
    return txt