# Once Noticias - Nueva Estructura del Proyecto

## 📁 Estructura Propuesta

```
once-noticias-ai/
├── 📁 src/                           # Código fuente principal
│   ├── 📁 core/                      # Sistemas centrales
│   │   ├── prompt_system.py          # Sistema de prompts optimizado
│   │   ├── quality_assurance.py      # Sistema de evaluación de calidad
│   │   └── editorial_pipeline.py     # Pipeline automatizado
│   ├── 📁 interfaces/                # Interfaces de usuario
│   │   └── streamlit_app.py          # Aplicación Streamlit principal
│   └── 📁 utils/                     # Utilidades y helpers
│       └── __init__.py
├── 📁 database/                      # Scripts y configuración de BD
│   ├── snowflake_schema.sql          # Esquema de base de datos
│   └── migrations/                   # Migraciones futuras
├── 📁 docs/                          # Documentación completa
│   ├── README.md                     # Documentación principal
│   ├── deployment.md                 # Guía de despliegue
│   └── api_reference.md              # Referencia de API
├── 📁 tests/                         # Tests unitarios e integración
│   ├── test_prompt_system.py
│   ├── test_quality_assurance.py
│   └── test_pipeline.py
├── 📁 config/                        # Configuraciones
│   ├── .streamlit/
│   │   └── secrets.toml.example
│   └── settings.py
├── 📁 legacy/                        # Archivos antiguos (backup)
│   ├── enhanced_prompt_system.py     # Sistema anterior
│   ├── app.py                        # App anterior
│   ├── research_system.py            # Sistema de investigación
│   └── integration_plan.md           # Plan de integración anterior
├── 📁 data/                          # Datos y entrenamiento
│   ├── training/
│   │   ├── training_data.jsonl
│   │   └── training_data.json
│   └── processed/
├── requirements.txt                   # Dependencias principales
├── setup.py                         # Setup del paquete
├── .gitignore                        # Git ignore
└── README.md                         # README principal
```

## 🗂️ Archivos a Reorganizar

### ✅ Mantener y Mover:
- `optimized_prompt_system.py` → `src/core/prompt_system.py`
- `quality_assurance_system.py` → `src/core/quality_assurance.py`
- `automated_editorial_pipeline.py` → `src/core/editorial_pipeline.py`
- `app_optimized.py` → `src/interfaces/streamlit_app.py`
- `snowflake_optimized_table.sql` → `database/snowflake_schema.sql`
- `README_SISTEMA_OPTIMIZADO.md` → `docs/README.md`

### 📦 Mover a Legacy:
- `enhanced_prompt_system.py` → `legacy/enhanced_prompt_system.py`
- `app.py` → `legacy/app.py`
- `research_system.py` → `legacy/research_system.py`
- `integration_plan.md` → `legacy/integration_plan.md`
- `app_integration_guide.py` → `legacy/app_integration_guide.py`
- `optimized_integration_guide.py` → `legacy/optimized_integration_guide.py`

### 🗑️ Considerar Eliminar:
- `optimizacion_impact_analysis.md` (información incluida en nueva documentación)
- Scripts de training antiguos si no se usan
- Archivos de test temporales

### 📁 Organizar por Funcionalidad:
- Mantener `data/` con datos de entrenamiento
- Mantener `requirements.txt` en raíz
- Crear `tests/` para testing futuro
- Crear `config/` para configuraciones