"""app/vision/analyzer.py — Vision analysis using qwen3-vl:4b via Ollama."""
import json
from typing import Dict, Any
from app.agent.ollama_client import generate_with_image
from app.config import settings

VISION_SYSTEM = (
    "You are a visual UI analysis assistant. Analyze the provided screenshot and return ONLY valid JSON. "
    "Do not include any explanation or markdown. Output JSON only."
)


def analyze_screenshot(screenshot_path: str, question: str) -> Dict[str, Any]:
    """
    Sends a screenshot to qwen3-vl:4b and returns a structured JSON response.
    Returns empty dict on failure.
    """
    if not settings.VISION_ENABLED:
        return {}

    prompt = (
        f"{question}\n\n"
        "Respond with JSON only. Example format:\n"
        '{"page_type": "search_results", "elements": [{"type": "button", "label": "Search", "confidence": 0.95}], "description": "..."}'
    )

    raw = generate_with_image(
        prompt=prompt,
        image_path=screenshot_path,
        system=VISION_SYSTEM,
        max_tokens=500,
    )

    return _parse_json_safe(raw)


def find_element_visually(screenshot_path: str, element_description: str) -> Dict[str, Any]:
    """
    Asks the vision model to locate a specific UI element.
    Returns element info with approximate region and confidence.
    Only used as DOM fallback.
    """
    prompt = (
        f"Find this UI element in the screenshot: '{element_description}'\n"
        "Return JSON with keys: element_type, label, confidence (0.0-1.0), "
        "approximate_region (x, y, width, height as fractions 0-1 of image size). "
        "If not found, return {\"found\": false}."
    )

    raw = generate_with_image(
        prompt=prompt,
        image_path=screenshot_path,
        system=VISION_SYSTEM,
        max_tokens=300,
    )

    result = _parse_json_safe(raw)

    # Confidence gate
    confidence = result.get("confidence", 0.0)
    if isinstance(confidence, (int, float)) and confidence < settings.VISION_MIN_CONFIDENCE:
        print(f"[Vision] Confidence {confidence:.2f} below threshold {settings.VISION_MIN_CONFIDENCE}.")
        result["below_threshold"] = True

    return result


def identify_page_type(screenshot_path: str) -> str:
    """Quick page classification using vision."""
    prompt = (
        "What type of page is shown in this screenshot? "
        "Return JSON: {\"page_type\": \"<type>\"} "
        "where type is one of: search_results, product, cart, checkout, login, captcha, general"
    )
    raw = generate_with_image(prompt=prompt, image_path=screenshot_path, max_tokens=100)
    result = _parse_json_safe(raw)
    return result.get("page_type", "general")


def _parse_json_safe(text: str) -> Dict[str, Any]:
    """Safely parses JSON from model output, stripping markdown if present."""
    if not text:
        return {}
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON object from somewhere in the text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except Exception:
                pass
    return {}
