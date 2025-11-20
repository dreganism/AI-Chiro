from __future__ import annotations

import os
from datetime import datetime

from groq import Groq

from backend.utils.formatters import truncate_text

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")


def _client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def build_prompt(raw_text: str) -> str:
    trimmed = truncate_text(raw_text, 15_000)
    return (
        "You are an expert medical-legal reporter. Generate a professional,\n"
        "structured medical report from this raw OCR text. Use clear sections\n"
        "(Patient Info, History, Examination, Diagnosis, Plan) and keep it concise.\n\n"
        f"Raw text (captured {datetime.utcnow().isoformat()} UTC):\n{trimmed}"
    )


def generate_summary(raw_text: str) -> str:
    client = _client()
    if client is None:
        return "AI summary unavailable: GROQ_API_KEY not configured."

    try:
        prompt = build_prompt(raw_text)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=DEFAULT_MODEL,
            temperature=0.3,
            max_tokens=2000,
        )
        return chat_completion.choices[0].message.content
    except Exception as exc:  # pragma: no cover - network call best-effort
        return f"AI summary failed: {exc}"
