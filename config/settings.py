# Once Noticias - Configuración Central
# Configuraciones del sistema editorial optimizado

import os
from typing import Dict, Any

class OnceNoticiasConfig:
    """Configuración central para el sistema Once Noticias"""

    # Versión del sistema
    SYSTEM_VERSION = "2.0.0"

    # Configuración OpenAI
    OPENAI_MODEL = "gpt-4.1"
    OPENAI_TEMPERATURE = 0.1
    OPENAI_MAX_TOKENS = 2000
    OPENAI_TOP_P = 0.9

    # Configuración de calidad
    MIN_QUALITY_SCORE = 70
    PUBLICATION_READY_THRESHOLD = 85

    # Configuración de seguridad
    MAX_PROMPT_LENGTH = 2000
    SECURITY_FILTERS_ENABLED = True

    # Configuración de métricas
    METRICS_RETENTION_DAYS = 90
    ENABLE_WEEKLY_ANALYSIS = False

    # ✅ ACTUALIZADO: Configuración de almacenamiento
    ENABLE_DATABASE_STORAGE = True  # Snowflake opcional
    LOCAL_STORAGE_ENABLED = True    # ✅ HABILITADO como fallback
    LOCAL_STORAGE_PATH = "data/metrics/"  # Carpeta para métricas locales

    # Configuración de datos externos (para versiones futuras)
    DATA_INJECTION_ENABLED = False
    WEB_SEARCH_ENABLED = True  # ✅ HABILITADO para web search

    # Configuración de base de datos (solo si está habilitada)
    DATABASE_TABLE = "content_generation_log_optimized"
    DATABASE_FALLBACK_TABLE = "content_generation_log"

    # Configuración de Streamlit
    STREAMLIT_CONFIG = {
        "page_title": "Once Noticias - Sistema Editorial Optimizado",
        "page_icon": "📰",
        "layout": "wide"
    }

    # Configuración de categorías
    CATEGORIES = [
        "Comercio", "Economía", "Energía", "Gobierno",
        "Internacional", "Política", "Justicia", "Sociedad", "Transporte",
        "Deportes", "Espectáculos"
    ]

    SUBCATEGORIES = [
        "Agricultura", "Finanzas", "Empleo", "Medio Ambiente",
        "Infraestructura", "Seguridad", "Comercio Internacional",
        "Salud", "Inversión Extranjera", "Mercados",
        "Electoral", "Ninguna"
    ]

    TEXT_TYPES = [
        "Nota Periodística", "Artículo", "Guión de TV", "Crónica",
        "Copy Redes Sociales"
    ]

    LENGTH_OPTIONS = {
        "Auto (Optimizada Once Noticias)": "auto",
        "Corta (100-300 palabras)": "corta",
        "Media (301-500 palabras)": "media",
        "Larga (501-800 palabras)": "larga",
        "Muy larga (801+ palabras)": "muy_larga"
    }

    # Configuración de Supers para TV
    SUPER_TYPES = {
        "CG:1L (1 línea - máx. 55 caracteres)": "CG_1L",
        "CG:2L (2 líneas - máx. 55 caracteres c/u)": "CG_2L",
        "CG:3L (3 líneas - Estados/Internacional)": "CG_3L",
        "ALERTA ONCE 1L": "ALERTA_1L",
        "ALERTA ONCE 2L": "ALERTA_2L",
        "CONDUCTOR (Nombre y Twitter)": "CONDUCTOR",
        "FALLA DE ORIGEN (máx. 15 caracteres)": "FALLA_ORIGEN",
        "SCROLL (Cintillo - máx. 633 caracteres)": "SCROLL"
    }

    # Límites de caracteres por tipo de super
    SUPER_CHAR_LIMITS = {
        "CG_1L": 55,
        "CG_2L": 55,  # por línea
        "CG_3L": 55,  # por línea
        "ALERTA_1L": 55,
        "ALERTA_2L": 55,  # por línea
        "CONDUCTOR": 50,  # por línea
        "FALLA_ORIGEN": 15,
        "SCROLL": 633
    }

    # Número de propuestas de supers a generar
    SUPER_GENERATION_COUNT = 3

    @classmethod
    def get_api_key(cls, key_name: str) -> str:
        """Obtiene API keys de forma segura desde Streamlit secrets o variables de entorno"""
        try:
            # Intentar obtener de Streamlit secrets primero
            import streamlit as st
            if hasattr(st, 'secrets') and key_name in st.secrets:
                return st.secrets[key_name]
        except:
            pass

        # Fallback a variables de entorno
        return os.getenv(key_name, "")

    @classmethod
    def is_database_available(cls) -> bool:
        """Verifica si la base de datos está disponible y configurada"""
        if not cls.ENABLE_DATABASE_STORAGE:
            return False

        # Verificar configuración de Snowflake
        required_vars = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
        return all(cls.get_api_key(var) for var in required_vars)

    @classmethod
    def get_storage_mode(cls) -> str:
        """Devuelve el modo de almacenamiento actual"""
        if cls.is_database_available():
            return "database"
        elif cls.LOCAL_STORAGE_ENABLED:
            return "local"
        else:
            return "none"

    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Valida la configuración del sistema"""
        issues = []
        warnings = []

        # Verificar API keys críticas
        if not cls.get_api_key("OPENAI_API_KEY"):
            issues.append("OPENAI_API_KEY no configurada - REQUERIDA para funcionar")

        # Verificar configuración de base de datos (solo advertencia si está habilitada)
        if cls.ENABLE_DATABASE_STORAGE:
            required_db_vars = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
            missing_vars = [var for var in required_db_vars if not cls.get_api_key(var)]
            if missing_vars:
                warnings.append(f"Snowflake habilitado pero faltan: {', '.join(missing_vars)}")
                warnings.append("Se usará almacenamiento local en su lugar")

        storage_mode = cls.get_storage_mode()
        if storage_mode == "none":
            warnings.append("No hay almacenamiento configurado - métricas se perderán")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "system_version": cls.SYSTEM_VERSION,
            "storage_mode": storage_mode
        }

# Instancia global de configuración
config = OnceNoticiasConfig()