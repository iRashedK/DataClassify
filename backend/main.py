import os
import json
import pandas as pd
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

PROMPT = (
    "You are a senior data classification officer working for the Saudi National Data Management Office (NDMO). "
    "Given a column name and a small sample of its values, your task is to classify the sensitivity and impact of this data based on both:\n"
    "- The Saudi NDMO Data Classification Policy\n"
    "- The Saudi Personal Data Protection Law (PDPL)\n\n"
    "Classify each column into only one of the following Impact Levels:\n"
    "- \ud83d\udd34 Top Secret: Highly sensitive data; unauthorized disclosure could threaten national security or cause severe damage to the Kingdom's strategic interests.\n"
    "- \ud83d\udd36 Confidential: Sensitive data; unauthorized disclosure could cause significant harm to the state or organizations.\n"
    "- \ud83d\dfe1 Restricted: Data requiring special protection; unauthorized disclosure does not pose a serious threat.\n"
    "- \ud83d\udd35 Public: Data that can be shared with the public without restrictions.\n\n"
    "Respond in the following JSON format only:\n"
    "{\n  \"column\": \"ColumnName\",\n  \"classification\": \"Public | Restricted | Confidential | Top Secret\",\n  \"justification\": \"Short explanation for classification based on Saudi regulations.\"\n}"
    "If in doubt, always choose the safer classification."
)

app = FastAPI(title="Data Classify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


PATTERNS = [
    ("Top Secret", r"(passport|national id|nid|ssn|iqama)",),
    ("Confidential", r"(email|e-mail|phone|mobile|address|credit|bank|health)",),
    ("Restricted", r"(name|department|title)",),
]


def heuristic_classify(column: str, samples):
    text = " ".join(samples)
    for label, pattern in PATTERNS:
        if re.search(pattern, text, re.I):
            return {
                "column": column,
                "classification": label,
                "justification": f"Matched pattern '{pattern}'"
            }
    return {"column": column, "classification": "Public", "justification": "No sensitive patterns detected"}


import re

def ai_classify(column: str, samples):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return heuristic_classify(column, samples)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    messages = [
        {"role": "system", "content": PROMPT},
        {
            "role": "user",
            "content": f"Column name: {column}\nSample values: {samples}"
        },
    ]
    payload = {
        "model": "gpt-4",  # use gpt-4 via OpenRouter
        "messages": messages,
        "temperature": 0.2,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as exc:
        return heuristic_classify(column, samples)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
    df = pd.read_excel(file.file)
    results = []
    for col in df.columns:
        samples = df[col].dropna().astype(str).tolist()[:5]
        classification = ai_classify(col, samples)
        results.append(classification)
    return {"results": results}


@app.get("/health")
def health():
    return {"status": "ok"}

