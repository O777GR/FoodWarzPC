"""Вкладка 'Статистика' — графики и аналитика."""
import streamlit as st
from database.repository import get_weekly_stats, get_monthly_stats
from services.ai_service import analyze_weekly_stats
from config import DEFAULT_CALORIE_GOAL, DEFAULT_PROTEIN_GOAL, DEFAULT_FAT_GOAL, DEFAULT_CARBS_GOAL


def render_stats_tab() -> None:
    """Отрисовка вкладки 'Статистика'."""
    st.subheader("📊 Статистика питания")
    
    # Выбор периода
    period = st.selectbox("Период:", ["Неделя", "Месяц"], key="stats_period")
    
    # Получаем данные из БД
    data = get_weekly_stats() if period == "Неделя" else get_monthly_stats()
    
    if not data:
        st.info("📭 Пока недостаточно данных для статистики")
        return
    
    # График калорий за период
    st.write("**🔥 Калории по дням**")
    chart_data = {
        "День": [d["date"] for d in data],
        "Ккал": [d["calories"] for d in data],
        "Цель": [DEFAULT_CALORIE_GOAL] * len(data)
    }
    st.bar_chart(chart_data, x="День", y=["Ккал", "Цель"])
    
    # Средняя статистика
    avg_calories = sum(d["calories"] for d in data) / len(data)
    avg_protein = sum(d["protein"] for d in data) / len(data)
    avg_fat = sum(d["fat"] for d in data) / len(data)
    avg_carbs = sum(d["carbs"] for d in data) / len(data)
    
    st.divider()
    st.write("**📈 Среднее за период:**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ккал", f"{avg_calories:.0f}")
    c2.metric("Белки", f"{avg_protein:.1f} г")
    c3.metric("Жиры", f"{avg_fat:.1f} г")
    c4.metric("Углеводы", f"{avg_carbs:.1f} г")
    
    # AI-анализ (только для недели)
    if period == "Неделя" and len(data) >= 3:
        st.divider()
        st.subheader("🧠 AI-анализ недели")
        st.caption("Локальная модель проанализирует твоё питание и даст рекомендации")
        
        if st.button("🔍 Провести анализ", type="primary"):
            with st.spinner("ИИ анализирует твою статистику..."):
                analysis = analyze_weekly_stats(
                    data,
                    DEFAULT_CALORIE_GOAL,
                    DEFAULT_PROTEIN_GOAL,
                    DEFAULT_FAT_GOAL,
                    DEFAULT_CARBS_GOAL
                )
            
            if analysis:
                # Сохраняем в session_state для отображения
                st.session_state.weekly_analysis = analysis
                st.rerun()
        
        # Показываем результат анализа
        if "weekly_analysis" in st.session_state:
            analysis = st.session_state.weekly_analysis
            
            # Резюме
            if "summary" in analysis:
                st.info(f"📝 **Резюме:** {analysis['summary']}")
            
            # Сильные стороны
            if "strengths" in analysis:
                st.write("**✅ Сильные стороны:**")
                for strength in analysis["strengths"]:
                    st.write(f"- {strength}")
            
            # Слабые стороны
            if "weaknesses" in analysis:
                st.write("**⚠️ Слабые стороны:**")
                for weakness in analysis["weaknesses"]:
                    st.write(f"- {weakness}")
            
            # Рекомендации
            if "recommendations" in analysis:
                st.write("** Рекомендации:**")
                for rec in analysis["recommendations"]:
                    level = rec.get("level", "Внимание")
                    text = rec.get("text", "")
                    
                    if level == "Критично":
                        st.error(f" **{level}:** {text}")
                    elif level == "Отлично":
                        st.success(f"🟢 **{level}:** {text}")
                    else:
                        st.warning(f"🟡 **{level}:** {text}")