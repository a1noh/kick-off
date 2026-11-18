"""Check that the Gemini key in the project's .env works, without ever printing the key.

Runs from the kit, in the project folder: .venv/bin/python <kit>/templates/check_llm.py
"""

import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def main() -> str:
    """Send one tiny JSON request to Gemini and return an OK line; exit with a fix-it message on failure."""
    load_dotenv(Path.cwd() / ".env")
    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest").strip()
    if not key:
        sys.exit("FAIL: GEMINI_API_KEY is empty. Paste it into .env and save.")
    body = {
        "contents": [{"parts": [{"text": 'Return JSON {"ok": true}'}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    start = time.time()
    response = requests.post(URL.format(model=model), headers={"x-goog-api-key": key}, json=body, timeout=60)
    if response.ok:
        return f"OK: {model} answered in {time.time() - start:.1f}s"
    is_json = response.headers.get("content-type", "").startswith("application/json")
    message = (response.json().get("error", {}).get("message", "") if is_json else response.text)[:200]
    sys.exit(
        f"FAIL {response.status_code} on {model}: {message}\n"
        "Tip: 404 = model retired -> set GEMINI_MODEL=gemini-flash-lite-latest; 503/429 = busy, retry."
    )


if __name__ == "__main__":
    print(main())
