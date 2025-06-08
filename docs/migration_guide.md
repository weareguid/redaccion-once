# 🔄 Guía de Migración - Once Noticias Sistema Optimizado 2.0

## 📋 Resumen de Cambios

El proyecto ha sido completamente reorganizado para mejorar la mantenibilidad, escalabilidad y claridad del código.

### ✅ Cambios Principales

1. **Estructura Modular**: Código organizado en paquetes lógicos
2. **Separación de Responsabilidades**: Core, interfaces, configuración separados
3. **Archivos Legacy**: Sistemas anteriores preservados en `legacy/`
4. **Configuración Centralizada**: Settings unificados en `config/`
5. **Testing Preparado**: Estructura para tests unitarios
6. **Documentación Mejorada**: Docs centralizadas en `docs/`

## 🗂️ Mapeo de Archivos

### Archivos Principales (Movidos)
```
ANTES                           →  DESPUÉS
optimized_prompt_system.py      →  src/core/prompt_system.py
quality_assurance_system.py     →  src/core/quality_assurance.py
automated_editorial_pipeline.py →  src/core/editorial_pipeline.py
app_optimized.py                →  src/interfaces/streamlit_app.py
snowflake_optimized_table.sql   →  database/snowflake_schema.sql
README_SISTEMA_OPTIMIZADO.md    →  docs/README.md
```

### Archivos Legacy (Preservados)
```
enhanced_prompt_system.py       →  legacy/enhanced_prompt_system.py
app.py                         →  legacy/app.py
research_system.py             →  legacy/research_system.py
integration_plan.md            →  legacy/integration_plan.md
app_integration_guide.py       →  legacy/app_integration_guide.py
optimized_integration_guide.py →  legacy/optimized_integration_guide.py
```

### Archivos Nuevos
```
src/__init__.py                 →  Paquete principal
src/core/__init__.py           →  Imports de sistemas core
src/interfaces/__init__.py     →  Interfaces de usuario
src/utils/__init__.py          →  Utilidades futuras
config/settings.py             →  Configuración centralizada
config/.streamlit/secrets.toml.example → Ejemplo de configuración
setup.py                       →  Instalación como paquete
tests/                         →  Estructura para testing
```

## 🚀 Cómo Usar la Nueva Estructura

### 1. Ejecutar la Aplicación
```bash
# Método recomendado (desde raíz)
streamlit run src/interfaces/streamlit_app.py

# Método alternativo
cd src/interfaces
streamlit run streamlit_app.py
```

### 2. Importar Sistemas en Código
```python
# ANTES (ya no funciona)
from optimized_prompt_system import OptimizedOnceNoticiasPromptSystem
from quality_assurance_system import OnceNoticiasQualityAssurance

# DESPUÉS (nueva estructura)
from src.core.prompt_system import OptimizedOnceNoticiasPromptSystem
from src.core.quality_assurance import OnceNoticiasQualityAssurance
from src.core.editorial_pipeline import AutomatedEditorialPipeline

# O usando el paquete core
from src.core import (
    OptimizedOnceNoticiasPromptSystem,
    OnceNoticiasQualityAssurance,
    AutomatedEditorialPipeline
)
```

### 3. Configuración
```bash
# Copiar archivo de configuración
cp config/.streamlit/secrets.toml.example config/.streamlit/secrets.toml

# Editar con tus API keys
nano config/.streamlit/secrets.toml
```

### 4. Instalación como Paquete (Opcional)
```bash
# Instalar en modo desarrollo
pip install -e .

# Esto permite importar desde cualquier lugar
from src.core import OptimizedOnceNoticiasPromptSystem
```

## 🔧 Configuración Actualizada

### Archivo de Secrets
El archivo de configuración ahora está en:
```
config/.streamlit/secrets.toml
```

### Settings Centralizados
Configuraciones del sistema en:
```python
from config.settings import config

# Usar configuraciones
model = config.OPENAI_MODEL
temperature = config.OPENAI_TEMPERATURE
```

## 📊 Base de Datos

### Schema Actualizado
El schema de Snowflake está ahora en:
```
database/snowflake_schema.sql
```

### Tablas Optimizadas
- `content_generation_log_optimized`: Tabla principal con nuevas métricas
- `content_generation_log`: Tabla de fallback para compatibilidad

## 🧪 Testing

### Estructura Preparada
```
tests/
├── __init__.py
├── test_prompt_system.py      # Tests del sistema de prompts
├── test_quality_assurance.py  # Tests de calidad (por crear)
└── test_pipeline.py           # Tests del pipeline (por crear)
```

### Ejecutar Tests
```bash
# Instalar dependencias de desarrollo
pip install pytest pytest-asyncio

# Ejecutar tests
pytest tests/ -v
```

## 📚 Documentación

### Nueva Estructura
```
docs/
├── README.md              # Documentación técnica principal
├── migration_guide.md     # Esta guía
├── deployment.md          # Guía de despliegue (por crear)
└── api_reference.md       # Referencia API (por crear)
```

## 🔄 Migración de Código Existente

### Si tienes código que usa el sistema anterior:

1. **Actualizar Imports**:
   ```python
   # Cambiar esto:
   from optimized_prompt_system import OptimizedOnceNoticiasPromptSystem

   # Por esto:
   from src.core.prompt_system import OptimizedOnceNoticiasPromptSystem
   ```

2. **Actualizar Rutas de Archivos**:
   ```python
   # Cambiar esto:
   with open("snowflake_optimized_table.sql") as f:

   # Por esto:
   with open("database/snowflake_schema.sql") as f:
   ```

3. **Usar Configuración Centralizada**:
   ```python
   # Cambiar esto:
   OPENAI_MODEL = "gpt-4o"

   # Por esto:
   from config.settings import config
   model = config.OPENAI_MODEL
   ```

## 🚨 Problemas Comunes

### Error de Import
```
ModuleNotFoundError: No module named 'optimized_prompt_system'
```
**Solución**: Actualizar imports a la nueva estructura.

### Error de Archivo No Encontrado
```
FileNotFoundError: [Errno 2] No such file or directory: 'app_optimized.py'
```
**Solución**: Usar `src/interfaces/streamlit_app.py`

### Error de Configuración
```
KeyError: 'OPENAI_API_KEY'
```
**Solución**: Copiar y configurar `config/.streamlit/secrets.toml`

## 📞 Soporte

Si tienes problemas con la migración:

1. **Revisar esta guía** completa
2. **Verificar la estructura** con `tree` o `ls -la`
3. **Comprobar imports** en tu código
4. **Validar configuración** de secrets
5. **Consultar documentación** en `docs/README.md`

## ✅ Checklist de Migración

- [ ] Estructura de carpetas creada correctamente
- [ ] Archivos movidos a nuevas ubicaciones
- [ ] Imports actualizados en código personalizado
- [ ] Configuración copiada y editada
- [ ] Aplicación ejecutándose correctamente
- [ ] Tests básicos funcionando
- [ ] Documentación revisada

---

**Once Noticias AI Team** - Migración completada exitosamente 🎉