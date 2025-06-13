#!/usr/bin/env python3
"""
Dashboard simple para visualizar las vistas analíticas de Snowflake
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from src.utils.database_connection import get_database_connection

def get_user_satisfaction_data():
    """Obtiene datos de satisfacción del usuario"""
    conn = get_database_connection()
    if not conn:
        print("❌ No se pudo conectar a Snowflake")
        return None

    try:
        query = """
        SELECT
            analysis_date,
            category,
            text_type,
            avg_rating,
            total_ratings,
            satisfaction_rate,
            excellent_rate,
            avg_quality_high_rating,
            high_rating_with_web_search,
            high_rating_without_web_search
        FROM user_satisfaction_analysis
        ORDER BY analysis_date DESC
        LIMIT 100
        """

        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error obteniendo datos de satisfacción: {e}")
        return None

def get_system_performance_data():
    """Obtiene datos de rendimiento del sistema"""
    conn = get_database_connection()
    if not conn:
        return None

    try:
        query = """
        SELECT
            generation_date,
            total_generations,
            avg_quality_score,
            avg_user_rating,
            satisfaction_rate,
            avg_generation_time,
            avg_tokens_used,
            web_search_usage_rate,
            avg_sources_per_content
        FROM system_performance_analysis
        WHERE system_version = '2.0_optimized'
        ORDER BY generation_date DESC
        LIMIT 30
        """

        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error obteniendo datos de rendimiento: {e}")
        return None

def get_weekly_trends_data():
    """Obtiene datos de tendencias semanales"""
    conn = get_database_connection()
    if not conn:
        return None

    try:
        query = """
        SELECT
            week_start,
            avg_quality,
            avg_user_rating,
            web_search_usage_rate,
            avg_sources_used,
            total_requests,
            ready_rate,
            improvement_rate
        FROM weekly_trends_analysis
        WHERE system_version = '2.0_optimized'
        ORDER BY week_start DESC
        LIMIT 12
        """

        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error obteniendo tendencias semanales: {e}")
        return None

def create_satisfaction_visualizations(df_satisfaction):
    """Crea visualizaciones de satisfacción del usuario"""
    if df_satisfaction is None or df_satisfaction.empty:
        print("No hay datos de satisfacción para visualizar")
        return

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('📊 Análisis de Satisfacción del Usuario', fontsize=16, fontweight='bold')

    # 1. Rating promedio por categoría
    if 'category' in df_satisfaction.columns and 'avg_rating' in df_satisfaction.columns:
        avg_by_category = df_satisfaction.groupby('category')['avg_rating'].mean().sort_values(ascending=False)
        avg_by_category.plot(kind='bar', ax=axes[0,0], color='skyblue', edgecolor='black')
        axes[0,0].set_title('⭐ Rating Promedio por Categoría')
        axes[0,0].set_ylabel('Rating (1-5)')
        axes[0,0].tick_params(axis='x', rotation=45)
        axes[0,0].grid(True, alpha=0.3)

    # 2. Tasa de satisfacción por tipo de texto
    if 'text_type' in df_satisfaction.columns and 'satisfaction_rate' in df_satisfaction.columns:
        avg_by_type = df_satisfaction.groupby('text_type')['satisfaction_rate'].mean().sort_values(ascending=False)
        avg_by_type.plot(kind='bar', ax=axes[0,1], color='lightgreen', edgecolor='black')
        axes[0,1].set_title('😊 Tasa de Satisfacción por Tipo de Texto')
        axes[0,1].set_ylabel('% Satisfacción (Rating ≥ 4)')
        axes[0,1].tick_params(axis='x', rotation=45)
        axes[0,1].grid(True, alpha=0.3)

    # 3. Web Search vs Satisfacción
    if all(col in df_satisfaction.columns for col in ['high_rating_with_web_search', 'high_rating_without_web_search']):
        web_search_data = df_satisfaction[['high_rating_with_web_search', 'high_rating_without_web_search']].sum()
        web_search_data.plot(kind='pie', ax=axes[1,0], autopct='%1.1f%%', startangle=90)
        axes[1,0].set_title('🌐 Alta Satisfacción: Con vs Sin Web Search')
        axes[1,0].set_ylabel('')

    # 4. Evolución temporal de ratings
    if 'analysis_date' in df_satisfaction.columns and 'avg_rating' in df_satisfaction.columns:
        df_satisfaction['analysis_date'] = pd.to_datetime(df_satisfaction['analysis_date'])
        daily_ratings = df_satisfaction.groupby('analysis_date')['avg_rating'].mean().sort_index()
        daily_ratings.plot(ax=axes[1,1], color='orange', marker='o', linewidth=2)
        axes[1,1].set_title('📈 Evolución del Rating Promedio')
        axes[1,1].set_ylabel('Rating Promedio')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig('satisfaction_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_performance_visualizations(df_performance):
    """Crea visualizaciones de rendimiento del sistema"""
    if df_performance is None or df_performance.empty:
        print("No hay datos de rendimiento para visualizar")
        return

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('⚡ Análisis de Rendimiento del Sistema', fontsize=16, fontweight='bold')

    # 1. Correlación Calidad vs Rating del Usuario
    if all(col in df_performance.columns for col in ['avg_quality_score', 'avg_user_rating']):
        axes[0,0].scatter(df_performance['avg_quality_score'], df_performance['avg_user_rating'],
                         color='purple', alpha=0.7, s=60)
        axes[0,0].set_xlabel('Calidad Automática (Score)')
        axes[0,0].set_ylabel('Rating Usuario')
        axes[0,0].set_title('🎯 Correlación: Calidad Automática vs Rating Usuario')
        axes[0,0].grid(True, alpha=0.3)

    # 2. Evolución de tokens usados
    if all(col in df_performance.columns for col in ['generation_date', 'avg_tokens_used']):
        df_performance['generation_date'] = pd.to_datetime(df_performance['generation_date'])
        df_sorted = df_performance.sort_values('generation_date')
        axes[0,1].plot(df_sorted['generation_date'], df_sorted['avg_tokens_used'],
                      color='red', marker='s', linewidth=2)
        axes[0,1].set_title('🪙 Evolución del Uso de Tokens')
        axes[0,1].set_ylabel('Tokens Promedio')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].tick_params(axis='x', rotation=45)

    # 3. Web Search Usage Rate
    if 'web_search_usage_rate' in df_performance.columns:
        avg_web_usage = df_performance['web_search_usage_rate'].mean()
        axes[1,0].bar(['Web Search Usage'], [avg_web_usage], color='teal', edgecolor='black')
        axes[1,0].set_title('🌐 Tasa de Uso de Web Search')
        axes[1,0].set_ylabel('% de Generaciones')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].set_ylim(0, 100)

    # 4. Tiempo de generación vs Satisfacción
    if all(col in df_performance.columns for col in ['avg_generation_time', 'satisfaction_rate']):
        axes[1,1].scatter(df_performance['avg_generation_time'], df_performance['satisfaction_rate'],
                         color='green', alpha=0.7, s=60)
        axes[1,1].set_xlabel('Tiempo Generación (segundos)')
        axes[1,1].set_ylabel('Tasa Satisfacción (%)')
        axes[1,1].set_title('⏱️ Tiempo vs Satisfacción')
        axes[1,1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_trends_visualizations(df_trends):
    """Crea visualizaciones de tendencias semanales"""
    if df_trends is None or df_trends.empty:
        print("No hay datos de tendencias para visualizar")
        return

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('📈 Tendencias Semanales del Sistema', fontsize=16, fontweight='bold')

    df_trends['week_start'] = pd.to_datetime(df_trends['week_start'])
    df_trends = df_trends.sort_values('week_start')

    # 1. Tendencia de calidad y rating
    if all(col in df_trends.columns for col in ['avg_quality', 'avg_user_rating']):
        ax1 = axes[0,0]
        ax1.plot(df_trends['week_start'], df_trends['avg_quality'],
                color='blue', marker='o', label='Calidad Automática', linewidth=2)
        ax2 = ax1.twinx()
        ax2.plot(df_trends['week_start'], df_trends['avg_user_rating'],
                color='red', marker='s', label='Rating Usuario', linewidth=2)
        ax1.set_ylabel('Calidad Automática', color='blue')
        ax2.set_ylabel('Rating Usuario', color='red')
        ax1.set_title('📊 Calidad vs Rating por Semana')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)

    # 2. Volumen de requests
    if 'total_requests' in df_trends.columns:
        axes[0,1].bar(df_trends['week_start'], df_trends['total_requests'],
                     color='orange', alpha=0.7, edgecolor='black')
        axes[0,1].set_title('📝 Volumen Semanal de Requests')
        axes[0,1].set_ylabel('Número de Requests')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].tick_params(axis='x', rotation=45)

    # 3. Web Search Trends
    if 'web_search_usage_rate' in df_trends.columns:
        axes[1,0].plot(df_trends['week_start'], df_trends['web_search_usage_rate'],
                      color='teal', marker='D', linewidth=2)
        axes[1,0].set_title('🌐 Tendencia Uso de Web Search')
        axes[1,0].set_ylabel('% Uso Web Search')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].tick_params(axis='x', rotation=45)

    # 4. Tasas de mejora
    if all(col in df_trends.columns for col in ['ready_rate', 'improvement_rate']):
        width = pd.Timedelta(days=1.5)
        axes[1,1].bar(df_trends['week_start'] - width/2, df_trends['ready_rate'],
                     width=width, label='Ready Rate', alpha=0.7, color='green')
        axes[1,1].bar(df_trends['week_start'] + width/2, df_trends['improvement_rate'],
                     width=width, label='Improvement Rate', alpha=0.7, color='purple')
        axes[1,1].set_title('✅ Tasas de Calidad y Mejora')
        axes[1,1].set_ylabel('Porcentaje (%)')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig('trends_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_summary_stats(df_satisfaction, df_performance, df_trends):
    """Imprime estadísticas resumen"""
    print("\n" + "="*60)
    print("📊 RESUMEN EJECUTIVO DE MÉTRICAS")
    print("="*60)

    if df_satisfaction is not None and not df_satisfaction.empty:
        avg_rating = df_satisfaction['avg_rating'].mean()
        avg_satisfaction = df_satisfaction['satisfaction_rate'].mean()
        print(f"⭐ Rating Promedio Global: {avg_rating:.2f}/5")
        print(f"😊 Tasa de Satisfacción: {avg_satisfaction:.1f}%")

    if df_performance is not None and not df_performance.empty:
        avg_tokens = df_performance['avg_tokens_used'].mean()
        avg_time = df_performance['avg_generation_time'].mean()
        web_usage = df_performance['web_search_usage_rate'].mean()
        print(f"🪙 Tokens Promedio: {avg_tokens:.0f}")
        print(f"⏱️ Tiempo Promedio: {avg_time:.2f}s")
        print(f"🌐 Uso Web Search: {web_usage:.1f}%")

    if df_trends is not None and not df_trends.empty:
        total_requests = df_trends['total_requests'].sum()
        avg_sources = df_trends['avg_sources_used'].mean()
        print(f"📝 Total Requests: {total_requests}")
        print(f"📚 Fuentes Promedio: {avg_sources:.1f}")

    print("="*60)

def main():
    """Función principal del dashboard"""
    print("🚀 Cargando Dashboard de Analytics de Once Noticias...")
    print("📊 Conectando a Snowflake...")

    # Obtener datos
    df_satisfaction = get_user_satisfaction_data()
    df_performance = get_system_performance_data()
    df_trends = get_weekly_trends_data()

    # Verificar si tenemos datos
    if all(df is None or df.empty for df in [df_satisfaction, df_performance, df_trends]):
        print("❌ No se encontraron datos para visualizar.")
        print("💡 Asegúrate de que:")
        print("   1. Snowflake esté conectado correctamente")
        print("   2. Haya datos en la tabla content_generation_log_optimized")
        print("   3. Las vistas analíticas estén creadas")
        return

    # Configurar matplotlib
    plt.style.use('default')
    sns.set_palette("husl")

    # Crear visualizaciones
    print("📈 Generando visualizaciones...")

    if df_satisfaction is not None and not df_satisfaction.empty:
        create_satisfaction_visualizations(df_satisfaction)
        print("✅ Gráficos de satisfacción guardados como 'satisfaction_analysis.png'")

    if df_performance is not None and not df_performance.empty:
        create_performance_visualizations(df_performance)
        print("✅ Gráficos de rendimiento guardados como 'performance_analysis.png'")

    if df_trends is not None and not df_trends.empty:
        create_trends_visualizations(df_trends)
        print("✅ Gráficos de tendencias guardados como 'trends_analysis.png'")

    # Imprimir resumen
    print_summary_stats(df_satisfaction, df_performance, df_trends)

    print("\n🎉 Dashboard completado!")
    print("📁 Las imágenes se han guardado en el directorio actual")

if __name__ == "__main__":
    main()