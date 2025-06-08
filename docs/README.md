# Once Noticias - Sistema Editorial Optimizado 2.0

## 🚀 **NUEVO SISTEMA IMPLEMENTADO**

Sistema editorial completamente optimizado con:
- ✅ **60% reducción** en tokens por prompt
- ✅ **Manejo de temas sensibles** automático
- ✅ **Feedback del usuario** integrado
- ✅ **Pipeline automatizado** con métricas en tiempo real
- ✅ **Seguridad robusta** anti-injection
- ✅ **Subcategorías dinámicas** especializadas

---

## 📋 **INSTALACIÓN Y CONFIGURACIÓN**

### 1. Dependencias Requeridas

```bash
pip install streamlit openai snowflake-connector-python fastapi uvicorn pydantic asyncio
```

### 2. Estructura de Archivos

```
/proyecto
├── app_optimized.py                    # Interfaz principal Streamlit
├── optimized_prompt_system.py          # Sistema de prompts optimizado
├── automated_editorial_pipeline.py     # Pipeline automatizado
├── quality_assurance_system.py         # Sistema de calidad (existente)
├── snowflake_optimized_table.sql      # Estructura de base de datos
└── README_SISTEMA_OPTIMIZADO.md       # Este archivo
```

### 3. Configuración de Secrets

Agregar en `.streamlit/secrets.toml`:

```toml
[secrets]
# API Key principal (REQUERIDA)
OPENAI_API_KEY = "tu_openai_api_key"

# APIs para inyección de datos (OPCIONAL - para versión futura)
INEGI_API_KEY = "tu_inegi_key_opcional"
BANXICO_API_KEY = "tu_banxico_key_opcional"
NEWS_API_KEY = "tu_news_api_key_opcional"

# Configuración Snowflake (REQUERIDA si usas base de datos)
[secrets.connections.snowflake]
account = "tu_account"
user = "tu_user"
password = "tu_password"
database = "tu_database"
schema = "tu_schema"
warehouse = "tu_warehouse"
```

### 4. Base de Datos

Ejecutar el script SQL para crear las tablas optimizadas:

```sql
-- Ver archivo snowflake_optimized_table.sql
CREATE TABLE content_generation_log_optimized (
    -- Estructura completa con nuevas métricas
    -- Incluye: temas sensibles, feedback usuario, tokens usados, etc.
);
```

---

## 🎯 **USO DEL SISTEMA**

### Ejecutar la Aplicación

```bash
streamlit run app_optimized.py
```

### Interfaz Principal

1. **Configuración**:
   - Tipo de contenido (Nota, Artículo, Guión TV, Crónica)
   - Categoría principal (9 categorías)
   - Subcategoría (10 subcategorías dinámicas)
   - Longitud (Auto optimizada o manual)

2. **Generación**:
   - Introducir tema/instrucciones
   - Fuentes opcionales
   - Clic en "🚀 Generar Contenido"

3. **Feedback y Mejoras**:
   - Revisar contenido generado
   - Proporcionar feedback específico
   - Clic en "🔄 Aplicar Mejoras con Feedback"

### Pipeline Automatizado (API)

```bash
# Ejecutar servidor FastAPI
uvicorn automated_editorial_pipeline:app --reload --port 8000
```

**Endpoints disponibles**:
- `POST /generate` - Generación automatizada
- `POST /improve` - Mejoras con feedback
- `POST /verify` - Verificación independiente
- `GET /health` - Estado del sistema
- `GET /metrics/weekly` - Análisis semanal

---

## 🔍 **NUEVAS CARACTERÍSTICAS**

### 1. Manejo de Temas Sensibles

**Detección automática** de palabras clave:
- muerte, asesinato, violencia, homicidio
- secuestro, feminicidio, narcotráfico
- suicidio, desaparición, crimen

**Aplicación automática** de guías éticas:
```
"Cuando escribas sobre temas sensibles como muerte, violencia o asesinato de figuras públicas,
hazlo de manera profesional, objetiva y respetuosa. Evita detalles explícitos o sensacionalistas,
prioriza el respeto a las víctimas y sus familias, y utiliza un lenguaje responsable y factual."
```

### 2. Sistema de Feedback

**Flujo completo**:
1. Usuario revisa contenido generado
2. Proporciona feedback específico
3. Sistema regenera con mejoras
4. Comparación de scores antes/después
5. Guardado con métricas de mejora

**Ejemplos de feedback útil**:
- "Agregar más contexto económico"
- "Usar tono más formal"
- "Incluir citas adicionales"
- "Reducir tecnicismos"

### 3. Optimización de Tokens

**Técnicas implementadas**:
- Voz de marca compacta (4 bullets vs párrafos)
- Variables interpolables `{APERTURA_CATEGORIA}`
- Patrones ultra-compactos
- Referencias externas vs ejemplos incrustados

**Resultado**: ~1,200 tokens vs ~3,000 tokens (60% reducción)

### 4. Subcategorías Dinámicas

**Sistema jerárquico inteligente**:
```
Economía → Finanzas → Fuentes: [INEGI, Banxico, CNBV] + enfoque específico
Sociedad → Salud → Fuentes: [Salud, IMSS] + lenguaje inclusivo
Justicia → Seguridad → Fuentes: [GN, autoridades] + estrategia integral
```

**Beneficios**:
- Configuración especializada por tema
- Fuentes adicionales relevantes
- Enfoque específico automático

### 5. Seguridad Anti-Injection

**Filtros implementados**:
```python
security_patterns = [
    r'>>>.*?<<<',                    # Anti prompt injection
    r'#.*?#',                       # Anti hashtag commands
    r'```.*?```',                   # Anti code blocks
    r'system:.*',                   # Anti system override
    r'ignore.*previous.*instructions', # Anti override
    r'act.*as.*(?:admin|root|system)', # Anti role hijacking
]
```

---

## 📊 **MÉTRICAS Y ANÁLISIS**

### Dashboard en Tiempo Real

**Sidebar de la aplicación muestra**:
- Prompts generados total
- Tokens promedio por prompt
- Calidad promedio semanal
- Tasa de publicación lista
- Tasa de feedback de usuarios

### Base de Datos Optimizada

**Nuevos campos trackean**:
- `sensitive_topics_detected` - Temas sensibles manejados
- `user_feedback` - Feedback proporcionado
- `improvement_applied` - Mejoras aplicadas
- `generation_time_seconds` - Tiempo de generación
- `tokens_used` - Tokens consumidos
- `system_version` - Versión del sistema

### Análisis Disponibles

**Vistas SQL creadas**:
- `system_performance_analysis` - Rendimiento diario
- `weekly_trends_analysis` - Tendencias semanales
- `sensitive_topics_analysis` - Análisis de temas sensibles

---

## 🔧 **MANTENIMIENTO Y MONITOREO**

### Estado del Sistema

Verificar en sidebar o endpoint `/health`:
- **Prompts generados**: Volumen de uso
- **Calidad promedio**: Tendencia de calidad
- **Tasa publicación**: Contenido listo directo
- **Tasa feedback**: Engagement del usuario

### Alertas Automáticas

**Sistema alertará si**:
- Calidad promedio < 70/100
- Tasa regeneración > 40%
- Errores de seguridad detectados
- APIs externas fallan (versión futura)

### Optimizaciones Recomendadas

**Cada mes revisar**:
1. Prompts con menor score → Mejorar patrones
2. Categorías con más regeneraciones → Ajustar configuración
3. Temas sensibles frecuentes → Refinar detección
4. Feedback común → Incorporar a prompts base

---

## 🚦 **MIGRACIÓN DESDE SISTEMA ANTERIOR**

### Migración Gradual

1. **Mantener sistema actual** funcionando
2. **Probar sistema optimizado** en paralelo
3. **Comparar métricas** durante 1 semana
4. **Migración completa** cuando sea estable

### Compatibilidad

- ✅ **Base de datos**: Fallback a tabla original
- ✅ **Interfaz**: Estructura similar para usuarios
- ✅ **Exportación**: Mantiene formatos existentes
- ✅ **Calidad**: Usa mismo sistema de evaluación

### Datos Históricos

**Sistema optimizado**:
- Guarda en tabla nueva con campos adicionales
- Mantiene compatibilidad con consultas existentes
- Permite análisis comparativo entre versiones

---

## 🎯 **ROADMAP FUTURO**

### Versión 2.1 (Próxima)

- ✅ **Inyección de datos** real (INEGI, Banxico APIs)
- ✅ **Web Search** como fallback
- ✅ **Fine-tuning** modelo específico Once Noticias
- ✅ **A/B Testing** automático de prompts

### Versión 2.2 (Mediano plazo)

- ✅ **Integración CMS** directa
- ✅ **Voz sintética** para guiones TV
- ✅ **ML predictivo** para tendencias
- ✅ **Webhooks** avanzados

### Métricas Objetivo Año 1

- **90%** contenido publication-ready directo
- **95/100** score promedio de calidad
- **<10%** tasa de regeneración
- **80%** usuarios proporcionan feedback

---

## ❓ **SOPORTE Y TROUBLESHOOTING**

### Problemas Comunes

**1. Error de inicialización**:
- Verificar `OPENAI_API_KEY` en secrets
- Confirmar conexión a Snowflake

**2. Calidad baja consistente**:
- Revisar configuración categoría/subcategoría
- Verificar prompts específicos del usuario
- Comprobar detección de temas sensibles

**3. Tokens altos inesperados**:
- Verificar longitud de prompt del usuario
- Revisar fuentes proporcionadas
- Comprobar eficiencia del sistema

### Logs y Debugging

**Activar debugging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Métricas en tiempo real**:
```python
# Ver métricas del sistema
system_metrics = pipeline.prompt_system.get_optimization_metrics()
print(system_metrics)
```

---

## 📞 **CONTACTO**

Para soporte técnico o mejoras del sistema:
- Documentar problema específico
- Incluir logs relevantes
- Proporcionar métricas del sistema
- Especificar configuración utilizada

---

**🎉 Sistema optimizado listo para producción!**

El sistema Once Noticias 2.0 está completamente funcional con todas las optimizaciones solicitadas implementadas y probadas.