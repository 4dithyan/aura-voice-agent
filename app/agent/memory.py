import json
import os
from app.config.settings import DATA_DIR

MEMORY_FILE = DATA_DIR / "memory.json"

def load_memory() -> dict:
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"aliases": {}, "preferences": {}, "context": {}}
    return {"aliases": {}, "preferences": {}, "context": {}}

def save_memory(data: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_alias(name: str) -> str:
    mem = load_memory()
    return mem.get("aliases", {}).get(name.lower())

def set_alias(name: str, path: str):
    mem = load_memory()
    if "aliases" not in mem:
        mem["aliases"] = {}
    mem["aliases"][name.lower()] = path
    save_memory(mem)

def get_context() -> dict:
    mem = load_memory()
    return mem.get("context", {})

def update_context(key: str, value: str):
    mem = load_memory()
    if "context" not in mem:
         mem["context"] = {}
    mem["context"][key] = value
    save_memory(mem)

def clear_context():
    mem = load_memory()
    mem["context"] = {}
    save_memory(mem)
