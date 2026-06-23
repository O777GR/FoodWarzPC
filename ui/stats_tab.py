"""Вкладка 'Статистика' — графики и аналитика."""
import streamlit as st
from database.repository import (
    get_weekly_stats, get_monthly_stats,
    get_weekly_water_stats, get_monthly_water_stats,
    get_weekly_vitamins_stats, get_monthly_vitamins_stats
)
from services.ai_service import analyze_weekly_stats
from config import (
    DEFAULT_CALORIE_GOAL, DEFAULT_PROTEIN_GOAL, DEFAULT_FAT_GOAL, DEFAULT_CARBS_GOAL,
    DEFAULT_WATER_GOAL_ML
)


def render_stats_tab() -> None:
    """Отрисовка вкладки 'Статистика'."""
    st.subheader("📊 Статистика питания")
    
    # Выбор периода
    period = st.selectbox("Период:", ["Неделя", "Месяц"], key="stats_period")
    
    # ==========================================
    # СЕКЦИЯ 1: ПИТАНИЕ (КБЖУ)
    # ==========================================
    st.write("### 🍽️ Питание")
    
    data = get_weekly_stats() if period == "Неделя" else get_monthly_stats()
    
    if not data:
        st.info("📭 Пока недостаточно данных по питанию")
    else:
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
        
        st.write("** Среднее за период:**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ккал", f"{avg_calories:.0f}")
        c2.metric("Белки", f"{avg_protein:.1f} г")
        c3.metric("Жиры", f"{avg_fat:.1f} г")
        c4.metric("Углеводы", f"{avg_carbs:.1f} г")
        
        # AI-анализ (только для недели)
        if period == "Неделя" and len(data) >= 3:
            st.divider()
            st.write("**🧠 AI-анализ питания**")
            st.caption("Локальная модель проанализирует твоё питание и даст рекомендации")
            
            if st.button(" Провести анализ питания", key="analyze_nutrition"):
                with st.spinner("ИИ анализирует твою статистику..."):
                    analysis = analyze_weekly_stats(
                        data,
                        DEFAULT_CALORIE_GOAL,
                        DEFAULT_PROTEIN_GOAL,
                        DEFAULT_FAT_GOAL,
                        DEFAULT_CARBS_GOAL
                    )
                
                if analysis:
                    st.session_state.weekly_analysis = analysis
                    st.rerun()
            
            # Показываем результат анализа
            if "weekly_analysis" in st.session_state:
                analysis = st.session_state.weekly_analysis
                
                if "summary" in analysis:
                    st.info(f"📝 **Резюме:** {analysis['summary']}")
                
                if "strengths" in analysis:
                    st.write("**✅ Сильные стороны:**")
                    for strength in analysis["strengths"]:
                        st.write(f"- {strength}")
                
                if "weaknesses" in analysis:
                    st.write("**⚠️ Слабые стороны:**")
                    for weakness in analysis["weaknesses"]:
                        st.write(f"- {weakness}")
                
                if "recommendations" in analysis:
                    st.write("**💡 Рекомендации:**")
                    for rec in analysis["recommendations"]:
                        level = rec.get("level", "Внимание")
                        text = rec.get("text", "")
                        
                        if level == "Критично":
                            st.error(f"🔴 **{level}:** {text}")
                        elif level == "Отлично":
                            st.success(f"🟢 **{level}:** {text}")
                        else:
                            st.warning(f"🟡 **{level}:** {text}")
    
    # ==========================================
    # СЕКЦИЯ 2: ВОДА
    # ==========================================
    st.divider()
    st.write("### 💧 Вода")
    
    water_data = get_weekly_water_stats() if period == "Неделя" else get_monthly_water_stats()
    
    if not water_data:
        st.info("📭 Пока нет данных по воде")
    else:
        # График воды
        st.write("**📊 Потребление воды по дням**")
        water_chart = {
            "День": [d["date"] for d in water_data],
            "мл": [d["total_ml"] for d in water_data],
            "Цель": [DEFAULT_WATER_GOAL_ML] * len(water_data)
        }
        st.bar_chart(water_chart, x="День", y=["мл", "Цель"])
        
        # Средняя статистика
        avg_water = sum(d["total_ml"] for d in water_data) / len(water_data)
        days_met_goal = sum(1 for d in water_data if d["total_ml"] >= DEFAULT_WATER_GOAL_ML)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 Среднее в день", f"{avg_water:.0f} мл")
        c2.metric("🎯 Дней с достигнутой целью", f"{days_met_goal}/{len(water_data)}")
        c3.metric("📈 Процент выполнения", f"{(days_met_goal/len(water_data)*100):.0f}%")
        
        if days_met_goal == len(water_data):
            st.success("🎉 Отлично! Цель по воде достигнута каждый день!")
        elif days_met_goal >= len(water_data) * 0.7:
            st.info("💪 Хороший результат! Большинство дней цель достигнута.")
        else:
            st.warning("⚠️ Нужно пить больше воды. Попробуй установить напоминания.")
    
    # ==========================================
    # СЕКЦИЯ 3: ВИТАМИНЫ
    # ==========================================
    st.divider()
    st.write("### 💊 Витамины")
    
    vitamins_stats = get_weekly_vitamins_stats() if period == "Неделя" else get_monthly_vitamins_stats()
    
    if vitamins_stats["total"] == 0:
        st.info("📭 Пока нет данных по витаминам")
    else:
        taken = vitamins_stats["taken"]
        total = vitamins_stats["total"]
        missed = vitamins_stats["missed"]
        
        # Визуализация
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Принято", f"{taken}")
        col2.metric("⏳ Пропущено", f"{missed}")
        col3.metric("📊 Всего запланировано", f"{total}")
        
        # Прогресс-бар
        progress = taken / total if total > 0 else 0
        st.progress(progress)
        st.write(f"**Процент выполнения:** {progress*100:.1f}%")
        
        # Оценка
        if progress >= 0.9:
            st.success("🎉 Превосходно! Ты принимаешь витамины очень дисциплинированно!")
        elif progress >= 0.7:
            st.info(" Хорошо! Большинство витаминов принято вовремя.")
        elif progress >= 0.5:
            st.warning("⚠️ Половина витаминов пропущена. Попробуй установить напоминания.")
        else:
            st.error("🔴 Критично! Больше половины витаминов пропущено.")
        
        # Рекомендации
        if missed > 0:
            st.write("**💡 Совет:** Попробуй принимать витамины в одно и то же время каждый день, например, сразу после завтрака.")