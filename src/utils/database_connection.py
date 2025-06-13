import snowflake.connector
import streamlit as st
from typing import Optional
import os
import logging
from config.settings import config

# Configurar logging básico
logging.basicConfig(level=logging.WARNING)  # Solo logs importantes
logger = logging.getLogger(__name__)

def get_database_connection() -> Optional[snowflake.connector.SnowflakeConnection]:
    """
    Establece conexión con Snowflake usando configuración desde secrets o .env

    Returns:
        SnowflakeConnection o None si no se puede conectar
    """
    try:
        connection_params = {}

        # Intentar obtener credenciales de Streamlit secrets primero
        try:
            if hasattr(st, 'secrets'):
                required_keys = ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD']
                available_keys = [key for key in required_keys if key in st.secrets]

                if len(available_keys) == len(required_keys):
                    connection_params = {
                        'account': st.secrets.get('SNOWFLAKE_ACCOUNT'),
                        'user': st.secrets.get('SNOWFLAKE_USER'),
                        'password': st.secrets.get('SNOWFLAKE_PASSWORD'),
                        'warehouse': st.secrets.get('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                        'database': st.secrets.get('SNOWFLAKE_DATABASE', 'ONCE_NOTICIAS'),
                        'schema': st.secrets.get('SNOWFLAKE_SCHEMA', 'PUBLIC')
                    }
                else:
                    raise Exception("Missing Snowflake secrets")
            else:
                raise Exception("Streamlit secrets not available")

        except Exception:
            # Fallback a variables de entorno
            env_params = {
                'account': os.getenv('SNOWFLAKE_ACCOUNT'),
                'user': os.getenv('SNOWFLAKE_USER'),
                'password': os.getenv('SNOWFLAKE_PASSWORD'),
                'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                'database': os.getenv('SNOWFLAKE_DATABASE', 'ONCE_NOTICIAS'),
                'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
            }
            connection_params = env_params

        # Verificar parámetros requeridos
        required_params = ['account', 'user', 'password']
        missing_params = [param for param in required_params if not connection_params.get(param)]

        if missing_params:
            logger.error(f"Parámetros de Snowflake faltantes: {', '.join(missing_params)}")
            return None

        # Conectar con timeout
        conn_params_with_timeout = {
            **connection_params,
            'login_timeout': 30,
            'network_timeout': 30
        }

        conn = snowflake.connector.connect(**conn_params_with_timeout)

        # Configurar base de datos y schema
        cursor = conn.cursor()

        database_name = connection_params['database']
        schema_name = connection_params['schema']

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.execute(f"USE DATABASE {database_name}")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        cursor.execute(f"USE SCHEMA {schema_name}")

        # ✅ SIMPLIFIED: Only ensure basic table exists, detailed schema is in .sql file
        # This is a minimal table creation for basic functionality
        # For full schema with views and indexes, run database/snowflake_schema.sql
        create_basic_table_query = """
        CREATE TABLE IF NOT EXISTS content_generation_log_optimized (
            id NUMBER AUTOINCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            openai_call_id VARCHAR(100),
            user_prompt TEXT NOT NULL,
            sources_prompt TEXT,
            user_feedback TEXT,
            user_rating INTEGER,
            generated_content TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            subcategory VARCHAR(50),
            text_type VARCHAR(50) NOT NULL,
            selected_length VARCHAR(20) DEFAULT 'auto',
            word_count INTEGER,
            overall_quality_score FLOAT,
            publication_ready BOOLEAN DEFAULT FALSE,
            style_compliance_score FLOAT,
            improvement_applied BOOLEAN DEFAULT FALSE,
            system_version VARCHAR(20) DEFAULT '2.0_optimized',
            sensitive_topics_detected BOOLEAN DEFAULT FALSE,
            generation_time_seconds FLOAT,
            tokens_used INTEGER,
            web_search_used BOOLEAN DEFAULT FALSE,
            web_search_sources_count INTEGER DEFAULT 0,
            citations_data TEXT,
            precision_factual_score FLOAT,
            calidad_periodistica_score FLOAT,
            relevancia_audiencia_score FLOAT,
            completitud_informativa_score FLOAT,
            identidad_editorial_score FLOAT
        )
        """

        cursor.execute(create_basic_table_query)
        cursor.close()

        return conn

    except Exception as e:
        logger.error(f"Error al conectar con Snowflake: {str(e)}")
        return None

def initialize_full_schema():
    """
    Ejecuta el schema completo desde el archivo .sql
    Incluye vistas analíticas, índices y comentarios
    """
    try:
        # Leer el archivo SQL
        schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'snowflake_schema.sql')

        if not os.path.exists(schema_path):
            logger.warning(f"Schema file not found: {schema_path}")
            return False

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Ejecutar el schema completo
        conn = get_database_connection()
        if not conn:
            return False

        cursor = conn.cursor()

        # ✅ IMPROVED: Better SQL parsing
        # Remove comments and split properly
        lines = schema_sql.split('\n')
        cleaned_lines = []

        for line in lines:
            # Remove comments but keep the line structure
            line = line.strip()
            if line and not line.startswith('--'):
                cleaned_lines.append(line)

        # Join back and split by semicolon for statements
        cleaned_sql = ' '.join(cleaned_lines)
        statements = [stmt.strip() for stmt in cleaned_sql.split(';') if stmt.strip()]

        executed_count = 0
        for statement in statements:
            if statement and len(statement) > 10:  # Skip very short statements
                try:
                    cursor.execute(statement)
                    executed_count += 1
                    logger.info(f"✅ Executed statement {executed_count}")
                except Exception as e:
                    # Log but continue with other statements
                    logger.warning(f"⚠️ Error executing statement {executed_count}: {e}")
                    logger.debug(f"Statement was: {statement[:100]}...")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✅ Schema setup completed - {executed_count} statements executed")
        return True

    except Exception as e:
        logger.error(f"Error inicializando schema completo: {e}")
        return False

def test_connection() -> bool:
    """
    Prueba la conexión a Snowflake

    Returns:
        bool: True si la conexión es exitosa
    """
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_USER()")
            result = cursor.fetchone()

            print(f"✅ Conexión exitosa - Database: {result[0]}, Schema: {result[1]}, User: {result[2]}")

            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error en prueba de conexión: {str(e)}")
            return False
    else:
        return False

def save_content_metrics(content_data: dict) -> Optional[int]:
    """
    Guarda métricas de contenido nuevo en Snowflake

    Args:
        content_data: Diccionario con los datos del contenido

    Returns:
        int: ID del registro insertado, o None si falló
    """
    conn = get_database_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO content_generation_log_optimized (
            user_prompt, sources_prompt, user_feedback, user_rating, openai_call_id,
            generated_content, category, subcategory, text_type, selected_length,
            word_count, overall_quality_score, publication_ready, style_compliance_score,
            improvement_applied, system_version, sensitive_topics_detected,
            generation_time_seconds, tokens_used, web_search_used, web_search_sources_count,
            citations_data, precision_factual_score, calidad_periodistica_score,
            relevancia_audiencia_score, completitud_informativa_score, identidad_editorial_score
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        values = (
            content_data.get('user_prompt', ''),
            content_data.get('sources_prompt', ''),
            content_data.get('user_feedback', ''),
            content_data.get('user_rating', None),
            content_data.get('openai_call_id', ''),
            content_data.get('generated_content', ''),
            content_data.get('category', ''),
            content_data.get('subcategory', ''),
            content_data.get('text_type', ''),
            content_data.get('selected_length', 'auto'),
            content_data.get('word_count', 0),
            content_data.get('overall_quality_score', 0.0),
            content_data.get('publication_ready', False),
            content_data.get('style_compliance_score', 0.0),
            content_data.get('improvement_applied', False),
            content_data.get('system_version', '2.0_optimized'),
            content_data.get('sensitive_topics_detected', False),
            content_data.get('generation_time_seconds', 0.0),
            content_data.get('tokens_used', 0),
            content_data.get('web_search_used', False),
            content_data.get('web_search_sources_count', 0),
            content_data.get('citations_data', ''),
            content_data.get('precision_factual_score', 0.0),
            content_data.get('calidad_periodistica_score', 0.0),
            content_data.get('relevancia_audiencia_score', 0.0),
            content_data.get('completitud_informativa_score', 0.0),
            content_data.get('identidad_editorial_score', 0.0)
        )

        cursor.execute(insert_query, values)

        # ✅ FIXED: Snowflake approach to get the inserted ID
        # Use a simpler approach - get the current max ID after insert
        cursor.execute("SELECT MAX(id) FROM content_generation_log_optimized")
        result = cursor.fetchone()
        record_id = result[0] if result else None

        conn.commit()
        cursor.close()
        conn.close()

        if record_id:
            logger.info(f"✅ Registro guardado con ID: {record_id}")

        return record_id

    except Exception as e:
        logger.error(f"Error al guardar en Snowflake: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return None

def update_content_rating(record_id: int, user_rating: int, user_feedback: str = None) -> bool:
    """
    Actualiza solo el rating y feedback de un registro existente

    Args:
        record_id: ID del registro a actualizar
        user_rating: Nuevo rating del usuario (1-5)
        user_feedback: Feedback adicional del usuario (opcional)

    Returns:
        bool: True si se actualizó correctamente
    """
    conn = get_database_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        if user_feedback:
            update_query = """
            UPDATE content_generation_log_optimized
            SET user_rating = %s, user_feedback = %s
            WHERE id = %s
            """
            cursor.execute(update_query, (user_rating, user_feedback, record_id))
        else:
            update_query = """
            UPDATE content_generation_log_optimized
            SET user_rating = %s
            WHERE id = %s
            """
            cursor.execute(update_query, (user_rating, record_id))

        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if rows_affected > 0:
            logger.info(f"✅ Rating actualizado para registro ID: {record_id} -> {user_rating} estrellas")
            return True
        else:
            logger.warning(f"⚠️ No se encontró registro con ID: {record_id}")
            return False

    except Exception as e:
        logger.error(f"Error al actualizar rating en Snowflake: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False

def get_latest_content_id() -> Optional[int]:
    """
    Obtiene el ID del contenido más reciente generado

    Returns:
        int: ID del último registro, o None si falló
    """
    conn = get_database_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM content_generation_log_optimized")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result[0] if result and result[0] else None

    except Exception as e:
        logger.error(f"Error obteniendo último ID: {str(e)}")
        return None

def update_content_rating_by_openai_id(openai_call_id: str, user_rating: int, user_feedback: str = None) -> bool:
    """
    Actualiza solo el rating y feedback de un registro existente usando OpenAI call ID
    ✅ MULTI-USER SAFE: Uses OpenAI call ID instead of record ID

    Args:
        openai_call_id: OpenAI call ID único del contenido
        user_rating: Nuevo rating del usuario (1-5)
        user_feedback: Feedback adicional del usuario (opcional)

    Returns:
        bool: True si se actualizó correctamente
    """
    conn = get_database_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        if user_feedback:
            update_query = """
            UPDATE content_generation_log_optimized
            SET user_rating = %s, user_feedback = %s
            WHERE openai_call_id = %s
            """
            cursor.execute(update_query, (user_rating, user_feedback, openai_call_id))
        else:
            update_query = """
            UPDATE content_generation_log_optimized
            SET user_rating = %s
            WHERE openai_call_id = %s
            """
            cursor.execute(update_query, (user_rating, openai_call_id))

        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if rows_affected > 0:
            logger.info(f"✅ Rating actualizado para OpenAI call ID: {openai_call_id} -> {user_rating} estrellas")
            return True
        else:
            logger.warning(f"⚠️ No se encontró contenido con OpenAI call ID: {openai_call_id}")
            return False

    except Exception as e:
        logger.error(f"Error al actualizar rating por OpenAI call ID en Snowflake: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False
