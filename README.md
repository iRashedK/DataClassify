# Data Classify MVP

This project provides a minimal backend and frontend for classifying columns in Excel files according to the Saudi NDMO and PDPL policies.

## Features
* Upload `.xlsx` files via FastAPI
* Sample the first five values from each column
* Classify each column using OpenRouter (GPT‑4) with a Saudi‑specific prompt
* Streamlit dashboard showing per‑column classifications and overall counts
* Dockerized services with `docker-compose`

## Quick Start

1. Copy `.env.sample` to `.env` and provide your OpenRouter API key.
2. Build and run using docker-compose:

```bash
docker-compose up --build
```

Backend will be available at <http://localhost:8000> and Streamlit UI at <http://localhost:8501>.

## Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Then run Streamlit separately:

```bash
streamlit run frontend/streamlit_app.py
```
