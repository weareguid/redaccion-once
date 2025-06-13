# 🚀 Once Noticias - Guía de Despliegue

Esta guía te ayudará a desplegar la aplicación Once Noticias en diferentes plataformas.

## 📋 Requisitos Previos

1. **Cuenta de GitHub** con el repositorio del proyecto
2. **API Key de OpenAI** configurada
3. **Credenciales de Snowflake** (opcional, pero recomendado)
4. **Cuenta en plataforma de despliegue** (Streamlit Cloud, Heroku, etc.)

## 🌐 Opción 1: Streamlit Cloud (Recomendado)

### Paso 1: Preparar el Repositorio
```bash
# Asegúrate de que todos los archivos estén en GitHub
git add .
git commit -m "Preparar para despliegue"
git push origin main
```

### Paso 2: Configurar Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona tu repositorio `redaccion-once`
4. Configura:
   - **Main file path**: `src/interfaces/streamlit_app.py`
   - **Python version**: 3.9+

### Paso 3: Configurar Secrets
En Streamlit Cloud, ve a "Settings" > "Secrets" y agrega:

```toml
# OpenAI Configuration
OPENAI_API_KEY = "tu-api-key-aqui"

# Snowflake Configuration (opcional)
SNOWFLAKE_ACCOUNT = "tu-account"
SNOWFLAKE_USER = "tu-usuario"
SNOWFLAKE_PASSWORD = "tu-password"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "ONCE_NOTICIAS"
SNOWFLAKE_SCHEMA = "PUBLIC"

# Web Search Configuration
SERPER_API_KEY = "tu-serper-key"  # Si usas Serper para web search
```

### Paso 4: Desplegar
1. Haz clic en "Deploy"
2. Espera a que se complete la instalación
3. ¡Tu app estará disponible en una URL pública!

## 🐳 Opción 2: Docker + Cloud Provider

### Crear Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos
COPY requirements_deploy.txt .
COPY . .

# Instalar dependencias de Python
RUN pip3 install -r requirements_deploy.txt

# Exponer puerto
EXPOSE 8501

# Comando de inicio
CMD ["streamlit", "run", "src/interfaces/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Desplegar en Cloud Run (Google Cloud)
```bash
# Construir imagen
docker build -t once-noticias .

# Subir a Google Cloud
gcloud builds submit --tag gcr.io/tu-proyecto/once-noticias

# Desplegar
gcloud run deploy --image gcr.io/tu-proyecto/once-noticias --platform managed
```

## 🔧 Opción 3: Heroku

### Crear archivos necesarios

**Procfile:**
```
web: streamlit run src/interfaces/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**
```
python-3.9.18
```

### Comandos de despliegue
```bash
# Instalar Heroku CLI y hacer login
heroku login

# Crear app
heroku create tu-app-once-noticias

# Configurar variables de entorno
heroku config:set OPENAI_API_KEY=tu-api-key
heroku config:set SNOWFLAKE_ACCOUNT=tu-account
# ... otras variables

# Desplegar
git push heroku main
```

## ⚙️ Configuración de Variables de Entorno

### Variables Requeridas
- `OPENAI_API_KEY`: Tu API key de OpenAI

### Variables Opcionales
- `SNOWFLAKE_ACCOUNT`: Cuenta de Snowflake
- `SNOWFLAKE_USER`: Usuario de Snowflake
- `SNOWFLAKE_PASSWORD`: Contraseña de Snowflake
- `SNOWFLAKE_WAREHOUSE`: Warehouse (default: COMPUTE_WH)
- `SNOWFLAKE_DATABASE`: Base de datos (default: ONCE_NOTICIAS)
- `SNOWFLAKE_SCHEMA`: Schema (default: PUBLIC)
- `SERPER_API_KEY`: Para búsqueda web avanzada

## 🔍 Verificación Post-Despliegue

### Checklist de Funcionalidades
- [ ] ✅ Aplicación carga correctamente
- [ ] ✅ Generación de contenido funciona
- [ ] ✅ Sistema de rating con estrellas funciona
- [ ] ✅ Búsqueda web funciona (si está configurada)
- [ ] ✅ Base de datos se conecta (si Snowflake está configurado)
- [ ] ✅ Descarga de documentos funciona
- [ ] ✅ Mejora iterativa funciona

### URLs de Prueba
Una vez desplegado, prueba estas funcionalidades:
1. Generar contenido básico
2. Usar el sistema de rating
3. Aplicar mejoras iterativas
4. Descargar documentos

## 🚨 Solución de Problemas

### Error: "Module not found"
- Verifica que `requirements_deploy.txt` tenga todas las dependencias
- Asegúrate de que la estructura de carpetas sea correcta

### Error: "OpenAI API Key not found"
- Verifica que la variable `OPENAI_API_KEY` esté configurada
- Revisa que no haya espacios extra en la clave

### Error: "Snowflake connection failed"
- Verifica las credenciales de Snowflake
- La app funcionará con almacenamiento local si Snowflake falla

### Performance Issues
- Considera usar un plan de pago en la plataforma de despliegue
- Optimiza el código para reducir tiempo de carga

## 📊 Monitoreo

### Métricas a Monitorear
- Tiempo de respuesta de la aplicación
- Uso de memoria y CPU
- Errores de API (OpenAI, Snowflake)
- Satisfacción del usuario (ratings)

### Logs Importantes
- Errores de conexión a base de datos
- Fallos en generación de contenido
- Problemas de autenticación

## 🔄 Actualizaciones

Para actualizar la aplicación desplegada:

1. **Streamlit Cloud**: Push a GitHub, auto-redeploy
2. **Heroku**: `git push heroku main`
3. **Docker**: Rebuild y redeploy imagen

## 📞 Soporte

Si encuentras problemas durante el despliegue:
1. Revisa los logs de la plataforma
2. Verifica las variables de entorno
3. Consulta la documentación específica de tu plataforma

---

¡Tu aplicación Once Noticias estará lista para generar contenido editorial de alta calidad! 🎉