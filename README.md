# Houkem

Houkem is a simple AI‑powered data classification demo. Upload an Excel file and the system will attempt to classify each column according to Saudi PDPL, NDMO and global standards. The classification uses OpenRouter/Qwen when an API key is provided (via `OPENROUTER_API_KEY` environment variable); otherwise a basic heuristic is applied.

## Features

* Upload `.xlsx` files
* Extract sample rows from each column
* AI or heuristic classification into **Public**, **Internal**, **Confidential**, or **Top Secret**
* Multilingual interface (English and Arabic)
* Minimal Docker setup

## Running locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENROUTER_API_KEY=your_key_here  # optional
python -m houkem.app
```

Then open <http://localhost:5000>.

## Docker

```bash
docker build -t houkem .
docker run -p 5000:5000 -e OPENROUTER_API_KEY=your_key_here houkem
```
