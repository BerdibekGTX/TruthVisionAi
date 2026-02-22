import base64
import json
import os
import re

import requests


GROK_API_URL = os.getenv("XAI_API_URL", "https://api.x.ai/v1/chat/completions")
GROK_MODEL = os.getenv("XAI_MODEL", "grok-4")


def _extract_json(content: str) -> dict:
    if not content:
        raise ValueError("Empty Grok response.")

    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if not match:
        raise ValueError("Could not parse JSON from Grok response.")
    return json.loads(match.group(0))


def _normalize_probability(value):
    value = float(value)
    if value > 1:
        value = value / 100.0
    return max(0.0, min(1.0, value))


def analyze_image_with_grok(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("XAI_API_KEY is not configured.")

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime_type};base64,{b64_image}"

    system_prompt = (
        "You are an AI image authenticity classifier. "
        "Return ONLY strict JSON with fields: "
        "is_ai (boolean), ai_probability (number 0..1), real_probability (number 0..1), reason (string)."
    )
    user_prompt = (
        "Classify whether this image is AI-generated or real. "
        "Respond with JSON only."
    )

    payload = {
        "model": GROK_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            },
        ],
    }

    response = requests.post(
        GROK_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    parsed = _extract_json(content)
    ai_probability = _normalize_probability(parsed.get("ai_probability", 0.5))
    real_probability = _normalize_probability(parsed.get("real_probability", 1 - ai_probability))

    # If returned probabilities are inconsistent, re-normalize.
    total = ai_probability + real_probability
    if total <= 0:
        ai_probability = 0.5
        real_probability = 0.5
    elif abs(total - 1.0) > 1e-6:
        ai_probability = ai_probability / total
        real_probability = real_probability / total

    is_ai = bool(parsed.get("is_ai", ai_probability >= real_probability))

    return {
        "provider": "grok",
        "is_ai": is_ai,
        "ai_probability": ai_probability,
        "real_probability": real_probability,
        "confidence": max(ai_probability, real_probability),
        "label": "AI Generated" if is_ai else "Real Image",
        "reason": str(parsed.get("reason", "")),
    }
