import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Ollama settings
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "")

# Model roles
FAST_MODEL = os.getenv("FAST_MODEL", "qwen2.5:1.5b")
VISION_MODEL = os.getenv("VISION_MODEL", "qwen3-vl:4b")

# Voice settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
TTS_ENABLED = os.getenv("TTS_ENABLED", "true").lower() == "true"
PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", str(MODELS_DIR / "piper" / "en_US-lessac-medium.onnx"))

WAKE_WORD_ENABLED = os.getenv("WAKE_WORD_ENABLED", "false").lower() == "true"
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis").lower()

# Safety settings
LOG_COMMANDS = os.getenv("LOG_COMMANDS", "true").lower() == "true"
CONFIRM_DANGEROUS_ACTIONS = os.getenv("CONFIRM_DANGEROUS_ACTIONS", "true").lower() == "true"
CONFIRM_PURCHASES = os.getenv("CONFIRM_PURCHASES", "true").lower() == "true"

# Vision settings
VISION_ENABLED = os.getenv("VISION_ENABLED", "true").lower() == "true"
VISION_ON_FAILURE = os.getenv("VISION_ON_FAILURE", "true").lower() == "true"
VISION_MIN_CONFIDENCE = float(os.getenv("VISION_MIN_CONFIDENCE", "0.80"))

# Browser settings
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

# Task / agent settings
MAX_ACTION_RETRIES = int(os.getenv("MAX_ACTION_RETRIES", "2"))
MAX_TASK_STEPS = int(os.getenv("MAX_TASK_STEPS", "30"))
MAX_CONTEXT_ITEMS = int(os.getenv("MAX_CONTEXT_ITEMS", "8"))
MAX_SCREENSHOT_CACHE = int(os.getenv("MAX_SCREENSHOT_CACHE", "5"))
MAX_ACTION_HISTORY = int(os.getenv("MAX_ACTION_HISTORY", "20"))

# Low resource mode — minimises screenshots, context, and parallel calls
LOW_RESOURCE_MODE = os.getenv("LOW_RESOURCE_MODE", "true").lower() == "true"
