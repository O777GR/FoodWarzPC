"""Вкладка 'Статистика' — графики и аналитика."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['date_str'] = df['date'].dt.strftime('%d.%m')
        
        # График 1: Калории по дням с линией цели
        fig_calories = go.Figure()
        
        fig_calories.add_trace(go.Bar(
            x=df['date_str'],
            y=df['calories'],
            name='Калории',
            marker_color='#FF6B6B',
            text=df['calories'].apply(lambda x: f'{x:.0f}'),
            textposition='outside'
        ))
        
        fig_calories.add_trace(go.Scatter(
            x=df['date_str'],
            y=[DEFAULT_CALORIE_GOAL] * len(df),
            mode='lines',
            name=f'Цель ({DEFAULT_CALORIE_GOAL} ккал)',
            line=dict(color='#4ECDC4', width=3, dash='dash')
        ))
        
        fig_calories.update_layout(
            title='🔥 Калории по дням',
            xaxis_title='Дата',
            yaxis_title='Ккал',
            hovermode='x unified',
            height=400,
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_calories, use_container_width=True)
        
        # График 2: БЖУ по дням (stacked bar)
        fig_macros = go.Figure()
        
        fig_macros.add_trace(go.Bar(
            x=df['date_str'],
            y=df['protein'],
            name='Белки',
            marker_color='#4ECDC4'
        ))
        
        fig_macros.add_trace(go.Bar(
            x=df['date_str'],
            y=df['fat'],
            name='Жиры',
            marker_color='#FFE66D'
        ))
        
        fig_macros.add_trace(go.Bar(
            x=df['date_str'],
            y=df['carbs'],
            name='Углеводы',
            marker_color='#95E1D3'
        ))
        
        fig_macros.update_layout(
            title='💪 БЖУ по дням (граммы)',
            xaxis_title='Дата',
            yaxis_title='Граммы',
            barmode='stack',
            hovermode='x unified',
            height=400,
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_macros, use_container_width=True)
        
        # График 3: Круговая диаграмма среднего БЖУ
        avg_protein = df['protein'].mean()
        avg_fat = df['fat'].mean()
        avg_carbs = df['carbs'].mean()
        
        fig_pie = px.pie(
            values=[avg_protein, avg_fat, avg_carbs],
            names=['Белки', 'Жиры', 'Углеводы'],
            color_discrete_sequence=['#4ECDC4', '#FFE66D', '#95E1D3'],
            hole=0.4
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            title='🥧 Среднее соотношение БЖУ за период',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Средняя статистика
        avg_calories = df['calories'].mean()
        
        st.write("**📈 Среднее за период:**")
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
            
            if st.button("🔍 Провести анализ питания", key="analyze_nutrition"):
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
        df_water = pd.DataFrame(water_data)
        df_water['date'] = pd.to_datetime(df_water['date'])
        df_water['date_str'] = df_water['date'].dt.strftime('%d.%m')
        df_water['goal_met'] = df_water['total_ml'] >= DEFAULT_WATER_GOAL_ML
        
        # График воды
        fig_water = go.Figure()
        
        # Цвета столбцов в зависимости от достижения цели
        colors = ['#4ECDC4' if met else '#FF6B6B' for met in df_water['goal_met']]
        
        fig_water.add_trace(go.Bar(
            x=df_water['date_str'],
            y=df_water['total_ml'],
            name='Выпито',
            marker_color=colors,
            text=df_water['total_ml'].apply(lambda x: f'{x:.0f} мл'),
            textposition='outside'
        ))
        
        fig_water.add_trace(go.Scatter(
            x=df_water['date_str'],
            y=[DEFAULT_WATER_GOAL_ML] * len(df_water),
            mode='lines',
            name=f'Цель ({DEFAULT_WATER_GOAL_ML} мл)',
            line=dict(color='#4ECDC4', width=3, dash='dash')
        ))
        
        fig_water.update_layout(
            title='💧 Потребление воды по дням',
            xaxis_title='Дата',
            yaxis_title='Миллилитры',
            hovermode='x unified',
            height=400,
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_water, use_container_width=True)
        
        # Средняя статистика
        avg_water = df_water['total_ml'].mean()
        days_met_goal = df_water['goal_met'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 Среднее в день", f"{avg_water:.0f} мл")
        c2.metric("🎯 Дней с достигнутой целью", f"{days_met_goal}/{len(df_water)}")
        c3.metric("📈 Процент выполнения", f"{(days_met_goal/len(df_water)*100):.0f}%")
        
        if days_met_goal == len(df_water):
            st.success("🎉 Отлично! Цель по воде достигнута каждый день!")
        elif days_met_goal >= len(df_water) * 0.7:
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
        
        # Круговая диаграмма витаминов
        fig_vitamins = go.Figure(data=[go.Pie(
            labels=['Принято', 'Пропущено'],
            values=[taken, missed],
            hole=0.4,
            marker_colors=['#4ECDC4', '#FF6B6B'],
            textinfo='label+percent'
        )])
        
        fig_vitamins.update_layout(
            title='💊 Статистика приёма витаминов',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_vitamins, use_container_width=True)
        
        # Метрики
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
            st.info("👍 Хорошо! Большинство витаминов принято вовремя.")
        elif progress >= 0.5:
            st.warning("⚠️ Половина витаминов пропущена. Попробуй установить напоминания.")
        else:
            st.error("🔴 Критично! Больше половины витаминов пропущено.")
        
        # Рекомендации
        if missed > 0:
            st.write("**💡 Совет:** Попробуй принимать витамины в одно и то же время каждый день, например, сразу после завтрака.")