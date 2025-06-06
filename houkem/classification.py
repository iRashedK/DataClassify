import os
import re
from typing import List, Dict, Any

try:
    import openai  # optional, used if OPENROUTER_API_KEY is provided
except ImportError:  # if package not installed
    openai = None


PATTERNS = [
    ("Top Secret", re.compile(r"(passport|national id|nid|ssn|iqama)", re.I)),
    ("Confidential", re.compile(r"(email|e-mail|phone|address|credit|bank|health)", re.I)),
    ("Internal", re.compile(r"(name|department|title)", re.I)),
]


class ColumnClassification:
    def __init__(self, column: str, label: str, reason: str, source_name: str, source_type: str) -> None:
        self.column = column
        self.label = label
        self.reason = reason
        self.source_name = source_name
        self.source_type = source_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "column": self.column,
            "label": self.label,
            "reason": self.reason,
            "source_name": self.source_name,
            "source_type": self.source_type,
        }


def heuristic_classify(column_name: str, samples: List[str]) -> ColumnClassification:
    text = " ".join(str(s) for s in samples)
    for label, pattern in PATTERNS:
        if pattern.search(text):
            reason = f"Matched pattern '{pattern.pattern}'"
            return ColumnClassification(column_name, label, reason, column_name, "uploaded file")
    return ColumnClassification(column_name, "Public", "No sensitive patterns detected", column_name, "uploaded file")


def ai_classify(column_name: str, samples: List[str]) -> ColumnClassification:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or openai is None:
        return heuristic_classify(column_name, samples)

    openai.api_key = api_key
    openai.base_url = "https://openrouter.ai/api/v1"

    prompt = (
        "You are a data classification assistant. "
        "Classify the following column according to NDMO, Saudi PDPL, and global data standards. "
        "Return one of: Public, Internal, Confidential, Top Secret. "
        "Provide reasoning in one sentence."
    )
    user_content = f"Column: {column_name}\nSamples: {samples}"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_content},
    ]

    try:
        resp = openai.ChatCompletion.create(
            model="qwen:Qwen1.5-72B-chat",
            messages=messages,
            temperature=0.2,
        )
        content = resp["choices"][0]["message"]["content"].strip()
        # expecting label: reasoning
        parts = content.split(":", 1)
        if len(parts) == 2:
            label, reason = parts[0].strip(), parts[1].strip()
        else:
            label, reason = content, ""
        if label not in {"Public", "Internal", "Confidential", "Top Secret"}:
            label = "Public"
        return ColumnClassification(column_name, label, reason, column_name, "uploaded file")
    except Exception as exc:
        return ColumnClassification(column_name, "Public", f"AI error: {exc}", column_name, "uploaded file")


def classify_column(column_name: str, samples: List[str]) -> ColumnClassification:
    return ai_classify(column_name, samples)
