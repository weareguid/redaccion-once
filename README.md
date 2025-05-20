<<<<<<< HEAD
# Generador de Contenido Periodístico

Una aplicación Streamlit que utiliza GPT-4 para generar contenido periodístico de alta calidad, con integración a Snowflake para almacenamiento y análisis de feedback.

## Características

- Generación de contenido periodístico en diferentes formatos
- Múltiples categorías y subcategorías
- Control de longitud y estilo del texto
- Exportación a Word y PDF
- Sistema de feedback y análisis
- Integración con Snowflake para almacenamiento y análisis

## Requisitos Previos

- Python 3.9 o superior
- Cuenta de Snowflake con acceso a ML features
- API key de OpenAI

## Configuración

1. Clona el repositorio:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Crea un entorno virtual e instala las dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configura las variables de entorno en `.streamlit/secrets.toml`:
```toml
[SNOWFLAKE]
user = "your-snowflake-user"
password = "your-snowflake-password"
account = "your-snowflake-account"
warehouse = "COMPUTE_WH"
database = "FEEDBACK_DB"
schema = "PUBLIC"

[OPENAI]
api_key = "your-openai-api-key"
```

4. Inicializa la base de datos Snowflake:
```bash
python setup_snowflake.py
```

## Despliegue en Streamlit Cloud

1. Crea una cuenta en [Streamlit Cloud](https://streamlit.io/cloud)

2. Conecta tu repositorio de GitHub

3. Configura las variables de entorno en la sección de Secrets:
   - Copia el contenido de tu archivo `.streamlit/secrets.toml`

4. Despliega la aplicación

## Uso Local

Para ejecutar la aplicación localmente:

```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## Estructura del Proyecto

```
.
├── app.py                 # Aplicación principal
├── setup_snowflake.py     # Script de configuración de Snowflake
├── requirements.txt       # Dependencias del proyecto
├── .streamlit/
│   └── secrets.toml      # Configuración de secretos
└── README.md             # Este archivo
```

## Contribuir

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

### About the Project:

This website is inspired by [Streamlit's](https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps) conversational app model

### Deployment

The website is deployed and hosted on Streamlit cloud, providing a fast and reliable browsing experience. Feel free to explore the live version at [https://app-chatgpt-clone.streamlit.app](https://app-chatgpt-clone.streamlit.app)


### Contact me:

<p align="center">

  <a href="https://www.linkedin.com/in/punyah-baghla-2b9ab3289/">
    <img src="https://www.vectorlogo.zone/logos/linkedin/linkedin-icon.svg" alt="Punyah's LinkedIn Profile" height="30" width="30">
  </a>


  <a href="https://twitter.com/iamrockstar211">
    <img src="https://cdn.svgporn.com/logos/twitter.svg" alt="Punyah's Twitter Profile" height="30" width="30">
  </a>
  
</p>
  

## License

This project is licensed under the MIT License. Feel free to use the code for personal or commercial purposes.
=======
# Editorial Voice Fine-tuning Project

This project fine-tunes GPT-3.5-turbo to replicate editorial voice across various domains (economics, finance, tourism, etc.).

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other configurations
```

## Project Structure

```
.
├── data_processing/     # Article processing and cleaning
├── model_training/      # Fine-tuning pipeline
├── api/                 # FastAPI endpoints
├── frontend/           # Human-in-the-loop interface
├── evaluation/         # Model evaluation tools
├── security/           # Security and privacy
└── monitoring/         # System monitoring
```

## Usage

1. Process articles:
```bash
python -m data_processing.process_articles --input_dir ./articles --output_dir ./processed
```

2. Fine-tune model:
```bash
python -m model_training.fine_tune --data_path ./processed/training.jsonl
```

3. Start API server:
```bash
uvicorn api.main:app --reload
```

4. Start frontend:
```bash
cd frontend
npm install
npm run dev
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Type checking: `mypy .`

## Security

- All API keys and sensitive data should be stored in `.env`
- Never commit `.env` to version control
- Use the provided security middleware for API endpoints

## Monitoring

- Access MLflow dashboard: `mlflow ui`
- View metrics: `http://localhost:8000/metrics`

## License

MIT License 
>>>>>>> f0d112154d2fd15efb5f864495819b65d9c6b028
