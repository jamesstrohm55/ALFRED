import json
from pathlib import Path
from services.embeddings_manager import store_memory_vector, search_memory

MEMORY_FILE = Path("data/memory.json")

if not MEMORY_FILE.exists():
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps({}))

def load_memory():
    with open(MEMORY_FILE, "r") as file:
        return json.load(file)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)

def remember(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

    # Also store in vector database
    store_memory_vector(f"{key} is {value}", metadata={"key": key})
    return True

def recall(key):
    memory = load_memory()
    return memory.get(key)

def forget(key):
    memory = load_memory()
    if key in memory:
        del memory[key]
        save_memory(memory)
        return True
    return False

def list_memory():
    return load_memory()

def semantic_search_memory(query, n_results=3):
    results = search_memory(query, n_results)
    matches = results.get("documents", [[]])[0]
    return matches if matches else None
