"""Вкладка 'Сон' — трекер и анализ сна."""
import streamlit as st
from database.repository import save_sleep_record, get_todays_sleep_record, get_weekly_sleep_records
from database.models import SleepRecord
from services.ai_service import analyze_weekly_sleep


def render_sleep_tab() -> None:
    """Отрисовка вкладки 'Сон'."""
    st.subheader("🌙 Трекер сна")
    
    today_record = get_todays_sleep_record()
    
    # Форма ввода
    with st.form(key="sleep_form", clear_on_submit=False):
        st.write("**Заполнить данные за сегодня:**")
        col1, col2 = st.columns(2)
        
        bedtime = col1.text_input("Время отбоя (HH:MM)", value=today_record.bedtime if today_record else "23:00")
        wake_time = col2.text_input("Время подъёма (HH:MM)", value=today_record.wake_time if today_record else "07:00")
        
        col3, col4 = st.columns(2)
        fall_asleep = col3.number_input("Время засыпания (мин)", min_value=0, value=today_record.fall_asleep_time if today_record else 15)
        awakenings = col4.number_input("Ночные пробуждения", min_value=0, value=today_record.awakenings if today_record else 0)
        
        wellbeing = st.slider("Самочувствие утром (1-10)", 1, 10, value=today_record.wellbeing_score if today_record else 7)
        activities = st.text_area("Что делали перед сном (экраны, еда, кофеин)", value=today_record.pre_sleep_activities if today_record else "")
        
        submitted = st.form_submit_button("💾 Сохранить запись", type="primary", use_container_width=True)
        
        if submitted:
            record = SleepRecord(
                bedtime=bedtime, wake_time=wake_time,
                fall_asleep_time=int(fall_asleep), awakenings=int(awakenings),
                wellbeing_score=int(wellbeing), pre_sleep_activities=activities
            )
            save_sleep_record(record)
            st.success("✅ Запись о сне сохранена!")
            st.rerun()

    st.divider()
    
    # Анализ недели
    st.write("### 🧠 AI-анализ недели")
    weekly_data = get_weekly_sleep_records()
    
    if len(weekly_data) < 3:
        st.info(f"Для анализа нужно минимум 3 дня. Сейчас записей: {len(weekly_data)}")
    else:
        if st.button("🔍 Анализировать неделю", type="primary", key="btn_analyze_sleep"):
            with st.spinner("Сомнолог анализирует твой сон..."):
                analysis = analyze_weekly_sleep(weekly_data)
            
            if analysis:
                st.session_state.sleep_analysis = analysis
                st.rerun()
        
        if "sleep_analysis" in st.session_state:
            analysis = st.session_state.sleep_analysis
            
            score = analysis.get("sleep_quality_score", 0)
            st.metric("Оценка качества сна", f"{score}/10")
            st.info(f"📝 **Резюме:** {analysis.get('summary', '')}")
            
            if issues := analysis.get("issues"):
                st.write("**⚠️ Выявленные проблемы:**")
                for issue in issues:
                    st.write(f"- {issue}")
                    
            if recs := analysis.get("recommendations"):
                st.write("**💡 Рекомендации:**")
                for rec in recs:
                    level = rec.get("level", "Внимание")
                    text = rec.get("text", "")
                    if level == "Критично": st.error(f"🔴 **{level}:** {text}")
                    elif level == "Отлично": st.success(f"🟢 **{level}:** {text}")
                    else: st.warning(f"🟡 **{level}:** {text}")