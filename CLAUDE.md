# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Once Noticias Sistema Editorial - AI-powered content generation system for Mexican news organization. Streamlit web app using OpenAI GPT-4 for journalistic content generation with editorial standards compliance.

## Key Commands

### Development
```bash
# Run the application locally
streamlit run src/interfaces/streamlit_app.py

# Alternative entry point for deployment
python app.py

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run tests
pytest tests/test_prompt_system.py -v

# Run deployment validation
python deploy.py
```

### Configuration Setup
```bash
# Copy secrets template
cp config/.streamlit/secrets.toml.example config/.streamlit/secrets.toml
# Then edit with your OpenAI API key (required) and Snowflake credentials (optional)
```

## Architecture Overview

### Core Systems
- **OptimizedOnceNoticiasPromptSystem** (`src/core/prompt_system.py`): Main content generation engine with token optimization, web search, and security filters
- **OnceNoticiasQualityAssurance** (`src/core/quality_assurance.py`): Automated quality scoring with 5 weighted criteria
- **Editorial Pipeline** (`src/core/editorial_pipeline.py`): Background processing workflow with FastAPI

### Main Entry Point
`src/interfaces/streamlit_app.py` - Primary Streamlit interface handling user interactions, content generation, and feedback collection

### Database Architecture
- **Primary**: Snowflake cloud database with `content_generation_log_optimized` table
- **Fallback**: Local JSON storage in `data/metrics/` when Snowflake unavailable
- Schema defined in `database/snowflake_schema.sql`

## Critical Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: Essential for content generation
- `SNOWFLAKE_*`: Optional for cloud metrics (falls back to local storage)

### Configuration Files
- `config/settings.py`: Central configuration class with all system parameters
- `.env`: Environment variables (API keys)
- `config/.streamlit/secrets.toml`: Streamlit secrets management

## Content Generation Categories & Types

### Content Types
- Nota Periodística (News Article)
- Artículo (Article)  
- Guion TV (TV Script)
- Crónica (Chronicle)
- Copy Redes Sociales (Social Media Copy)

### Categories
Commerce, Economy, Energy, Government, International, Politics, Justice, Society, Transport, Sports, Entertainment

Each category has specialized prompts and subcategories defined in `config/settings.py`.

## Key Development Patterns

### Error Handling
- Always implement fallback for Snowflake to local storage
- Handle OpenAI API failures gracefully with user feedback
- Validate content against ethical guidelines before display

### State Management
- Use Streamlit session state for maintaining user context
- Track iterations with unique IDs for multi-user safety
- Store ratings and feedback with proper user identification

### Security Considerations
- Prompt injection protection in `OptimizedOnceNoticiasPromptSystem`
- Sensitive content detection before generation
- API keys stored in secrets, never in code

## Testing Strategy
- Unit tests for prompt system in `tests/test_prompt_system.py`
- Deployment validation script in `deploy.py`
- Manual testing through Streamlit interface for UI components

## Deployment
- **Streamlit Cloud**: Use GitHub integration, configure secrets in dashboard
- **Docker**: Build with `Dockerfile`, expose port 8501
- **Heroku**: Use `Procfile` and `runtime.txt`, set config vars
- **Local**: Direct streamlit run command with local secrets file