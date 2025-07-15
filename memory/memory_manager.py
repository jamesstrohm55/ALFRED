import json
from pathlib import Path

MEMORY_FILE = Path("memory_store.json")

def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def remember(key, value):
    memory = load_memory()
    memory[key.lower()] = value
    save_memory(memory)

def recall(key):
    memory = load_memory()
    return memory.get(key.lower(), None)

def forget(key):
    memory = load_memory()
    if key.lower() in memory:
        del memory[key.lower()]
        save_memory(memory)
        return True
    return False

def list_memory():
    memory = load_memory()
    return memory
