-- Tabla optimizada para Once Noticias Sistema 2.0
-- Incluye todas las nuevas métricas y funcionalidades

CREATE TABLE content_generation_log_optimized (
    -- Identificadores y tiempo
    id NUMBER AUTOINCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    -- Datos de entrada del usuario
    user_prompt TEXT NOT NULL,
    sources_prompt TEXT,
    user_feedback TEXT,

    -- Contenido generado
    generated_content TEXT NOT NULL,

    -- Configuración de generación
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    text_type VARCHAR(50) NOT NULL,
    selected_length VARCHAR(20) DEFAULT 'auto',

    -- Métricas básicas
    word_count INTEGER,

    -- Métricas de calidad principales
    overall_quality_score FLOAT,
    publication_ready BOOLEAN DEFAULT FALSE,
    style_compliance_score FLOAT,

    -- Nuevas métricas del sistema optimizado
    improvement_applied BOOLEAN DEFAULT FALSE,
    system_version VARCHAR(20) DEFAULT '2.0_optimized',
    sensitive_topics_detected BOOLEAN DEFAULT FALSE,

    -- Métricas de rendimiento
    generation_time_seconds FLOAT,
    tokens_used INTEGER,

    -- Scores detallados de calidad (mantener compatibilidad)
    precision_factual_score FLOAT,
    calidad_periodistica_score FLOAT,
    relevancia_audiencia_score FLOAT,
    completitud_informativa_score FLOAT,
    identidad_editorial_score FLOAT,

    -- Índices para consultas optimizadas
    INDEX idx_timestamp (timestamp),
    INDEX idx_category_type (category, text_type),
    INDEX idx_quality_score (overall_quality_score),
    INDEX idx_publication_ready (publication_ready),
    INDEX idx_system_version (system_version)
);

-- Vista para análisis de rendimiento del sistema optimizado
CREATE OR REPLACE VIEW system_performance_analysis AS
SELECT
    system_version,
    DATE(timestamp) as generation_date,

    -- Métricas de volumen
    COUNT(*) as total_generations,
    COUNT(CASE WHEN improvement_applied THEN 1 END) as improvements_applied,

    -- Métricas de calidad
    AVG(overall_quality_score) as avg_quality_score,
    AVG(CASE WHEN publication_ready THEN 100 ELSE 0 END) as publication_ready_rate,
    AVG(style_compliance_score) as avg_style_compliance,

    -- Métricas de eficiencia
    AVG(generation_time_seconds) as avg_generation_time,
    AVG(tokens_used) as avg_tokens_used,
    AVG(word_count) as avg_word_count,

    -- Métricas de feedback
    COUNT(CASE WHEN user_feedback IS NOT NULL AND user_feedback != '' THEN 1 END) as feedback_provided,
    COUNT(CASE WHEN sensitive_topics_detected THEN 1 END) as sensitive_topics_handled,

    -- Distribución por tipo de contenido
    COUNT(CASE WHEN text_type = 'Nota Periodística' THEN 1 END) as notas_count,
    COUNT(CASE WHEN text_type = 'Artículo' THEN 1 END) as articulos_count,
    COUNT(CASE WHEN text_type = 'Guión de TV' THEN 1 END) as guiones_count,
    COUNT(CASE WHEN text_type = 'Crónica' THEN 1 END) as cronicas_count

FROM content_generation_log_optimized
GROUP BY system_version, DATE(timestamp)
ORDER BY generation_date DESC;

-- Vista para análisis de tendencias semanales
CREATE OR REPLACE VIEW weekly_trends_analysis AS
SELECT
    DATE_TRUNC('week', timestamp) as week_start,
    system_version,

    -- Tendencias de calidad
    AVG(overall_quality_score) as avg_quality,
    STDDEV(overall_quality_score) as quality_stddev,

    -- Tendencias de eficiencia
    AVG(generation_time_seconds) as avg_time,
    AVG(tokens_used) as avg_tokens,

    -- Tendencias de uso
    COUNT(*) as total_requests,
    AVG(CASE WHEN publication_ready THEN 100 ELSE 0 END) as ready_rate,
    AVG(CASE WHEN improvement_applied THEN 100 ELSE 0 END) as improvement_rate,
    AVG(CASE WHEN user_feedback IS NOT NULL AND user_feedback != '' THEN 100 ELSE 0 END) as feedback_rate,

    -- Comparación con semana anterior
    LAG(AVG(overall_quality_score)) OVER (PARTITION BY system_version ORDER BY DATE_TRUNC('week', timestamp)) as prev_week_quality,
    LAG(COUNT(*)) OVER (PARTITION BY system_version ORDER BY DATE_TRUNC('week', timestamp)) as prev_week_requests

FROM content_generation_log_optimized
GROUP BY DATE_TRUNC('week', timestamp), system_version
ORDER BY week_start DESC;

-- Vista para análisis de temas sensibles
CREATE OR REPLACE VIEW sensitive_topics_analysis AS
SELECT
    DATE(timestamp) as analysis_date,
    category,
    text_type,

    COUNT(*) as total_content,
    COUNT(CASE WHEN sensitive_topics_detected THEN 1 END) as sensitive_detected,
    ROUND(COUNT(CASE WHEN sensitive_topics_detected THEN 1 END) * 100.0 / COUNT(*), 2) as sensitive_percentage,

    -- Calidad promedio en contenido sensible vs normal
    AVG(CASE WHEN sensitive_topics_detected THEN overall_quality_score END) as avg_quality_sensitive,
    AVG(CASE WHEN NOT sensitive_topics_detected THEN overall_quality_score END) as avg_quality_normal,

    -- Tiempo de generación para contenido sensible
    AVG(CASE WHEN sensitive_topics_detected THEN generation_time_seconds END) as avg_time_sensitive,
    AVG(CASE WHEN NOT sensitive_topics_detected THEN generation_time_seconds END) as avg_time_normal

FROM content_generation_log_optimized
GROUP BY DATE(timestamp), category, text_type
HAVING COUNT(*) >= 5  -- Solo incluir días con suficiente volumen
ORDER BY analysis_date DESC, sensitive_percentage DESC;

-- Query de ejemplo para dashboard ejecutivo
SELECT
    'Sistema Optimizado 2.0' as sistema,
    COUNT(*) as total_generaciones,
    ROUND(AVG(overall_quality_score), 1) as calidad_promedio,
    ROUND(AVG(CASE WHEN publication_ready THEN 100 ELSE 0 END), 1) as tasa_publicacion,
    ROUND(AVG(generation_time_seconds), 2) as tiempo_promedio_segundos,
    ROUND(AVG(tokens_used), 0) as tokens_promedio,
    COUNT(CASE WHEN improvement_applied THEN 1 END) as mejoras_aplicadas,
    COUNT(CASE WHEN sensitive_topics_detected THEN 1 END) as temas_sensibles_manejados,
    ROUND(COUNT(CASE WHEN user_feedback IS NOT NULL AND user_feedback != '' THEN 1 END) * 100.0 / COUNT(*), 1) as tasa_feedback

FROM content_generation_log_optimized
WHERE timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP())
  AND system_version = '2.0_optimized';

-- Comentarios sobre mejoras implementadas:
/*
OPTIMIZACIONES IMPLEMENTADAS EN LA TABLA:

1. ✅ NUEVOS CAMPOS:
   - user_feedback: Para capturar feedback del usuario
   - improvement_applied: Rastrea si se aplicaron mejoras
   - system_version: Identifica versión del sistema
   - sensitive_topics_detected: Marca contenido sensible
   - generation_time_seconds: Métricas de rendimiento
   - tokens_used: Optimización de costos

2. ✅ ÍNDICES OPTIMIZADOS:
   - Por timestamp para análisis temporal
   - Por categoría y tipo para filtros rápidos
   - Por métricas de calidad para análisis

3. ✅ VISTAS ANALÍTICAS:
   - system_performance_analysis: Dashboard de rendimiento
   - weekly_trends_analysis: Tendencias semanales
   - sensitive_topics_analysis: Análisis de temas sensibles

4. ✅ COMPATIBILIDAD:
   - Mantiene campos existentes
   - Permite migración gradual
   - Fallback a tabla original
*/