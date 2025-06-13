# 📰 Once Noticias - Sistema Editorial Optimizado

Sistema de inteligencia artificial para la generación de contenido periodístico de Once Noticias, con manejo de temas sensibles, feedback del usuario, y sistema de calificación interactivo.

## 🚀 Características Principales

- **Sistema de Prompts Optimizado**: Generación eficiente de contenido editorial
- **Evaluación de Calidad Automatizada**: Métricas específicas Once Noticias
- **Pipeline Editorial Completo**: Generación → Evaluación → Mejora
- **Manejo de Temas Sensibles**: Detección automática y guías éticas
- **Sistema de Rating Interactivo**: Calificación con estrellas clickeables (1-5)
- **Feedback del Usuario**: Mejoras basadas en retroalimentación
- **Búsqueda Web Inteligente**: Información actualizada cuando es necesaria
- **Métricas en Tiempo Real**: Análisis de rendimiento y tendencias
- **Multi-usuario Seguro**: Sistema de tracking individual por usuario

## 📁 Estructura del Proyecto

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
│       └── database_connection.py    # Conexión a base de datos
├── 📁 database/                      # Scripts y configuración de BD
│   └── snowflake_schema.sql          # Esquema de base de datos
├── 📁 config/                        # Configuraciones
│   ├── .streamlit/
│   │   ├── secrets.toml.template     # Plantilla de configuración
│   │   └── config.toml               # Configuración de Streamlit
│   └── settings.py                   # Configuración centralizada
├── 📁 docs/                          # Documentación completa
├── 📁 data/                          # Datos y métricas
│   └── metrics/                      # Almacenamiento local de métricas
├── requirements.txt                   # Dependencias principales
├── requirements_deploy.txt            # Dependencias para despliegue
├── Dockerfile                        # Configuración Docker
├── Procfile                          # Configuración Heroku
└── DEPLOYMENT.md                     # Guía de despliegue
```

## ⚡ Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/once-noticias-app.git
cd once-noticias-app
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar secrets
```bash
# Copiar archivo de plantilla
cp config/.streamlit/secrets.toml.template config/.streamlit/secrets.toml

# Editar con tus API keys
# OPENAI_API_KEY es REQUERIDA
```

### 4. Ejecutar la aplicación
```bash
streamlit run src/interfaces/streamlit_app.py
```

## 🔧 Configuración

### API Keys Requeridas
- **OpenAI API Key**: Para generación de contenido (REQUERIDA)

### Configuración Opcional
- **Snowflake**: Para almacenamiento de métricas en la nube
- **SERPER API**: Para búsqueda web avanzada

### Configuración de Búsqueda Web
- **🤖 Auto (recomendado)**: Usa búsqueda web cuando es necesaria
- **🌐 Siempre activada**: Búsqueda web en cada generación
- **📚 Solo conocimiento base**: Sin búsqueda web

## ⭐ Sistema de Rating Interactivo

### Características del Rating
- **Estrellas Clickeables**: Sistema intuitivo de 1-5 estrellas
- **Sin Rating Inicial**: Los usuarios deben calificar explícitamente
- **Actualización en Tiempo Real**: Cambios se guardan inmediatamente
- **Multi-usuario Seguro**: Cada usuario solo afecta su propio contenido
- **Tracking Individual**: Cada contenido tiene un ID único

### Cómo Funciona
1. Genera contenido editorial
2. Haz clic en las estrellas para calificar (1-5)
3. El rating se guarda automáticamente en la base de datos
4. Puedes cambiar tu calificación en cualquier momento

## 📊 Métricas y Análisis

### Métricas Disponibles
- Tiempo de generación
- Score de calidad automatizado
- Rating del usuario (1-5 estrellas)
- Tasa de publicación lista
- Uso de búsqueda web
- Número de fuentes consultadas
- Historial de mejoras aplicadas

### Dashboard en Tiempo Real
- Estado de conexión a base de datos
- Métricas del sistema en sidebar
- Análisis de tendencias
- Tracking de satisfacción del usuario

## 🎯 Tipos de Contenido Soportados

1. **Nota Periodística**: Pirámide invertida, objetivo, institucional
2. **Artículo**: Desarrollo extenso, bloques temáticos, pedagógico
3. **Guión de TV**: Fragmentos cortos, lectura oral, conversacional
4. **Crónica**: Narrativo, inmersivo, literario

## 🏷️ Categorías y Subcategorías

### Categorías Principales
- Comercio, Economía, Energía, Gobierno
- Internacional, Política, Justicia, Sociedad, Transporte

### Subcategorías Dinámicas
- Agricultura, Finanzas, Empleo, Medio Ambiente
- Infraestructura, Seguridad, Comercio Internacional
- Salud, Inversión Extranjera, Mercados

## 🔒 Seguridad y Temas Sensibles

### Filtros de Seguridad
- Detección automática de contenido sensible
- Filtros anti-manipulación de prompts
- Validación de entrada de usuario

### Manejo de Temas Sensibles
- Detección de violencia/muerte/crimen
- Aplicación automática de guías éticas
- Lenguaje responsable y respetuoso

## 🚀 Uso del Sistema

### Interfaz Web (Streamlit)
1. **Configurar**: Seleccionar tipo de contenido y categoría
2. **Describir**: Especificar el tema a cubrir
3. **Fuentes**: Agregar referencias opcionales
4. **Generar**: Crear contenido con IA
5. **Calificar**: Usar sistema de estrellas (1-5)
6. **Mejorar**: Aplicar feedback para refinamiento
7. **Descargar**: Exportar en Word o PDF

### Funciones Avanzadas
- **Ctrl+Enter**: Atajos de teclado para generación rápida
- **Historial de Iteraciones**: Navegar entre versiones
- **Búsqueda Web Automática**: Información actualizada
- **Citaciones Automáticas**: Referencias incluidas

## 🔄 Pipeline Editorial

### Flujo Automatizado
1. **Generación**: Prompt optimizado → OpenAI GPT-4
2. **Búsqueda Web**: Información actualizada (si es necesaria)
3. **Evaluación**: Criterios de calidad Once Noticias
4. **Presentación**: Contenido con citaciones
5. **Rating**: Calificación del usuario
6. **Mejora**: Feedback → Regeneración (opcional)
7. **Almacenamiento**: Métricas → Base de datos

### Criterios de Calidad
1. **Precisión Factual** (25%)
2. **Calidad Periodística** (25%)
3. **Relevancia Audiencia** (20%)
4. **Completitud Informativa** (15%)
5. **Identidad Editorial** (15%)

## 🌐 Despliegue

### Opciones de Despliegue
- **Streamlit Cloud**: Despliegue gratuito y fácil
- **Docker**: Contenedorización completa
- **Heroku**: Plataforma como servicio
- **Local**: Desarrollo y testing

### Archivos de Despliegue Incluidos
- `Dockerfile`: Para contenedorización
- `Procfile`: Para Heroku
- `requirements_deploy.txt`: Dependencias optimizadas
- `.streamlit/config.toml`: Configuración de producción
- `DEPLOYMENT.md`: Guía completa de despliegue

## 📈 Base de Datos y Analytics

### Almacenamiento
- **Snowflake**: Base de datos principal en la nube
- **Local**: Fallback automático si Snowflake no está disponible
- **Vistas Analíticas**: Análisis de satisfacción y rendimiento

### Métricas Tracked
- Contenido generado con metadatos completos
- Ratings de usuario con timestamps
- Uso de búsqueda web y fuentes
- Tiempo de generación y tokens utilizados
- Feedback aplicado y mejoras realizadas

## 🛠️ Desarrollo

### Estructura de Código
- **Modular**: Sistemas independientes y reutilizables
- **Testeable**: Preparado para testing unitario
- **Escalable**: Arquitectura para crecimiento futuro
- **Mantenible**: Código limpio y documentado

### Comandos de Desarrollo
```bash
# Instalar en modo desarrollo
pip install -e .

# Verificar despliegue
python deploy.py

# Ejecutar aplicación
streamlit run src/interfaces/streamlit_app.py
```

## 📚 Documentación

- **Guía de Despliegue**: `DEPLOYMENT.md`
- **Documentación Técnica**: `docs/README.md`
- **Configuración**: `config/.streamlit/secrets.toml.template`
- **Base de Datos**: `database/snowflake_schema.sql`

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

- **Issues**: GitHub Issues
- **Documentación**: `DEPLOYMENT.md` y `docs/`
- **Configuración**: Revisar archivos de configuración

---

**Once Noticias AI** - Sistema Editorial con IA y Rating Interactivo
