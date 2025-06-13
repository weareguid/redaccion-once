-- Once Noticias Enhanced Snowflake Schema
-- Sistema optimizado 2.0 con métricas de Web Search y análisis de usuario

-- ===== TABLA PRINCIPAL DE LOGS =====
CREATE OR REPLACE TABLE content_generation_log_optimized (
    -- Identificadores y tiempo
    id NUMBER AUTOINCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    openai_call_id VARCHAR(100), -- ✅ Added OpenAI call tracking

    -- Datos de entrada del usuario
    user_prompt TEXT NOT NULL,
    sources_prompt TEXT,
    user_feedback TEXT,
    user_rating INTEGER, -- 1-5 stars

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

    -- Métricas de Web Search
    web_search_used BOOLEAN DEFAULT FALSE,
    web_search_sources_count INTEGER DEFAULT 0,
    citations_data TEXT, -- JSON con citaciones

    -- Scores detallados de calidad
    precision_factual_score FLOAT,
    calidad_periodistica_score FLOAT,
    relevancia_audiencia_score FLOAT,
    completitud_informativa_score FLOAT,
    identidad_editorial_score FLOAT
);

-- ===== VISTA ANALÍTICA: SATISFACCIÓN DEL USUARIO =====
CREATE OR REPLACE VIEW user_satisfaction_analysis AS
SELECT
    DATE(timestamp) as analysis_date,
    category,
    text_type,

    -- Métricas de rating
    ROUND(AVG(user_rating), 2) as avg_rating,
    COUNT(CASE WHEN user_rating IS NOT NULL THEN 1 END) as total_ratings,

    -- Tasa de satisfacción (rating >= 4)
    ROUND(
        COUNT(CASE WHEN user_rating >= 4 THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN user_rating IS NOT NULL THEN 1 END), 0),
        1
    ) as satisfaction_rate,

    -- Tasa de excelencia (rating = 5)
    ROUND(
        COUNT(CASE WHEN user_rating = 5 THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN user_rating IS NOT NULL THEN 1 END), 0),
        1
    ) as excellent_rate,

    -- Correlación con calidad automática
    ROUND(AVG(CASE WHEN user_rating >= 4 THEN overall_quality_score END), 2) as avg_quality_high_rating,

    -- Web Search effectiveness
    COUNT(CASE WHEN user_rating >= 4 AND web_search_used = TRUE THEN 1 END) as high_rating_with_web_search,
    COUNT(CASE WHEN user_rating >= 4 AND web_search_used = FALSE THEN 1 END) as high_rating_without_web_search

FROM content_generation_log_optimized
WHERE timestamp >= DATEADD(day, -30, CURRENT_DATE()) -- Últimos 30 días
    AND system_version = '2.0_optimized'
GROUP BY DATE(timestamp), category, text_type
ORDER BY analysis_date DESC, avg_rating DESC;

-- ===== VISTA ANALÍTICA: RENDIMIENTO DEL SISTEMA =====
CREATE OR REPLACE VIEW system_performance_analysis AS
SELECT
    DATE(timestamp) as generation_date,
    COUNT(*) as total_generations,

    -- Métricas de calidad
    ROUND(AVG(overall_quality_score), 2) as avg_quality_score,
    ROUND(AVG(user_rating), 2) as avg_user_rating,

    -- Tasa de satisfacción
    ROUND(
        COUNT(CASE WHEN user_rating >= 4 THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN user_rating IS NOT NULL THEN 1 END), 0),
        1
    ) as satisfaction_rate,

    -- Métricas de rendimiento
    ROUND(AVG(generation_time_seconds), 2) as avg_generation_time,
    ROUND(AVG(tokens_used), 0) as avg_tokens_used,

    -- Web Search metrics
    ROUND(AVG(CASE WHEN web_search_used THEN 1.0 ELSE 0.0 END) * 100, 1) as web_search_usage_rate,
    ROUND(AVG(web_search_sources_count), 1) as avg_sources_per_content,

    -- System version
    system_version

FROM content_generation_log_optimized
WHERE timestamp >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY DATE(timestamp), system_version
ORDER BY generation_date DESC;

-- ===== VISTA ANALÍTICA: TENDENCIAS SEMANALES =====
CREATE OR REPLACE VIEW weekly_trends_analysis AS
SELECT
    DATE_TRUNC('week', timestamp) as week_start,

    -- Métricas de calidad
    ROUND(AVG(overall_quality_score), 2) as avg_quality,
    ROUND(AVG(user_rating), 2) as avg_user_rating,

    -- Web Search trends
    ROUND(AVG(CASE WHEN web_search_used THEN 1.0 ELSE 0.0 END) * 100, 1) as web_search_usage_rate,
    ROUND(AVG(web_search_sources_count), 1) as avg_sources_used,

    -- Volume metrics
    COUNT(*) as total_requests,

    -- Success rates
    ROUND(AVG(CASE WHEN publication_ready THEN 1.0 ELSE 0.0 END) * 100, 1) as ready_rate,
    ROUND(AVG(CASE WHEN improvement_applied THEN 1.0 ELSE 0.0 END) * 100, 1) as improvement_rate,

    -- Satisfaction trends
    ROUND(
        COUNT(CASE WHEN user_rating >= 4 THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN user_rating IS NOT NULL THEN 1 END), 0),
        1
    ) as satisfaction_trend,

    system_version

FROM content_generation_log_optimized
WHERE timestamp >= DATEADD(week, -12, CURRENT_DATE()) -- Últimas 12 semanas
GROUP BY DATE_TRUNC('week', timestamp), system_version
ORDER BY week_start DESC;

-- ===== VISTA ANALÍTICA: TEMAS SENSIBLES =====
CREATE OR REPLACE VIEW sensitive_topics_analysis AS
SELECT
    DATE(timestamp) as analysis_date,
    category,

    -- Detección de temas sensibles
    COUNT(*) as total_content,
    COUNT(CASE WHEN sensitive_topics_detected THEN 1 END) as sensitive_detected,
    ROUND(
        COUNT(CASE WHEN sensitive_topics_detected THEN 1 END) * 100.0 / COUNT(*),
        1
    ) as sensitive_rate,

    -- Calidad en temas sensibles
    ROUND(AVG(CASE WHEN sensitive_topics_detected THEN overall_quality_score END), 2) as avg_quality_sensitive,
    ROUND(AVG(CASE WHEN NOT sensitive_topics_detected THEN overall_quality_score END), 2) as avg_quality_regular,

    -- Rating de usuario en temas sensibles
    ROUND(AVG(CASE WHEN sensitive_topics_detected THEN user_rating END), 2) as avg_rating_sensitive,
    ROUND(AVG(CASE WHEN NOT sensitive_topics_detected THEN user_rating END), 2) as avg_rating_regular

FROM content_generation_log_optimized
WHERE timestamp >= DATEADD(day, -30, CURRENT_DATE())
    AND system_version = '2.0_optimized'
GROUP BY DATE(timestamp), category
ORDER BY analysis_date DESC, sensitive_rate DESC;

-- ===== ÍNDICES PARA PERFORMANCE =====
CREATE INDEX IF NOT EXISTS idx_timestamp ON content_generation_log_optimized (timestamp);
CREATE INDEX IF NOT EXISTS idx_category ON content_generation_log_optimized (category);
CREATE INDEX IF NOT EXISTS idx_user_rating ON content_generation_log_optimized (user_rating);
CREATE INDEX IF NOT EXISTS idx_web_search ON content_generation_log_optimized (web_search_used);
CREATE INDEX IF NOT EXISTS idx_system_version ON content_generation_log_optimized (system_version);
CREATE INDEX IF NOT EXISTS idx_openai_call_id ON content_generation_log_optimized (openai_call_id);

-- ===== COMENTARIOS DEL SCHEMA =====
COMMENT ON TABLE content_generation_log_optimized IS 'Log principal de generación de contenido Once Noticias - Sistema 2.0 optimizado con Web Search y análisis de usuario';
COMMENT ON COLUMN content_generation_log_optimized.user_rating IS 'Rating del usuario de 1-5 estrellas para el contenido generado';
COMMENT ON COLUMN content_generation_log_optimized.web_search_used IS 'Indica si se utilizó búsqueda web para generar el contenido';
COMMENT ON COLUMN content_generation_log_optimized.citations_data IS 'Datos JSON de las citaciones obtenidas via web search';
COMMENT ON COLUMN content_generation_log_optimized.openai_call_id IS 'ID único de la llamada a OpenAI API para tracking';