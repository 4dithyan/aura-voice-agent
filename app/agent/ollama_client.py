import requests
import json
import base64
from pathlib import Path
from app.config import settings


def check_ollama() -> list[str]:
    """Checks if Ollama is running and returns a list of available models."""
    try:
        response = requests.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=3)
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model["name"] for model in models]
    except (requests.RequestException, ValueError):
        return []


def get_default_model() -> str:
    """Gets the configured fast model, or auto-detects a Qwen model."""
    if settings.FAST_MODEL:
        return settings.FAST_MODEL
    if settings.OLLAMA_MODEL:
        return settings.OLLAMA_MODEL

    models = check_ollama()
    qwen_models = [m for m in models if "qwen" in m.lower() and "vl" not in m.lower()]
    if qwen_models:
        return qwen_models[0]
    if models:
        return models[0]

    raise RuntimeError("Local AI engine is unavailable. Please start Ollama.")


def verify_models() -> dict:
    """Verifies that both required models are available in Ollama."""
    available = check_ollama()
    fast_ok = any(settings.FAST_MODEL.split(":")[0] in m for m in available)
    vision_ok = any(settings.VISION_MODEL.split(":")[0] in m for m in available)
    return {
        "fast_model": settings.FAST_MODEL,
        "fast_available": fast_ok,
        "vision_model": settings.VISION_MODEL,
        "vision_available": vision_ok,
        "all_models": available,
    }


def generate_text(
    prompt: str,
    system: str = "",
    model: str = None,
    max_tokens: int = 400,
) -> str:
    """Generates text from a specified Ollama model (defaults to fast model)."""
    if model is None:
        model = get_default_model()

    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"num_predict": max_tokens},
    }

    try:
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as e:
        print(f"[Ollama] Error: {e}")
        return ""


def generate_with_image(
    prompt: str,
    image_path: str,
    system: str = "",
    max_tokens: int = 500,
) -> str:
    """Sends a screenshot to the vision model (qwen3-vl:4b) for analysis."""
    img = Path(image_path)
    if not img.exists():
        return ""

    with open(img, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": settings.VISION_MODEL,
        "prompt": prompt,
        "system": system,
        "images": [b64_image],
        "stream": False,
        "options": {"num_predict": max_tokens},
    }

    try:
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as e:
        print(f"[Vision] Error: {e}")
        return ""
