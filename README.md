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