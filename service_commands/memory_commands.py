from memory.memory_manager import remember, recall, forget, list_memory, load_memory, save_memory

def initialize_memory():
    """Ensure memory file exists and is loaded."""
    load_memory()  # Load memory to ensure the file exists

def persist_memory():
    """Save the current memory state to the file."""
    save_memory()

def handle_memory_commands(text):
    lower = text.lower().strip()

    if lower.startswith("remember that"):
        _, fact = lower.split("remember that", 1)
        if " is " in fact:
            key, value = fact.split(" is ", 1)
            remember(key.strip(), value.strip())
            persist_memory()
            key_for_reply = key.strip().replace("my ", "your ")
            return f"I'll remember that {key_for_reply} is {value.strip()}."
        return "Please phrase it like: 'Remember that [key] is [value]'."

    if "what do you remember about" in lower or "what do you know about" in lower:
        key = lower.replace("what do you remember about", "").replace("what do you know about", "").strip()
        key_for_reply = key.replace("my ", "your ")
        value = recall(key)
        return f"{key_for_reply.capitalize()} is {value}." if value else f"I don't remember anything about {key_for_reply}."

    if lower.startswith("forget"):
        key = lower.replace("forget", "").strip()
        success = forget(key)
        if success:
            persist_memory()
            return f"I've forgotten everything about {key}."
        else:
            return f"I don't remember anything about {key} to forget."
    
    if "what do you remember" in lower or "list everything you remember" in lower:
        data = list_memory()
        return "I don't have anything stored yet." if not data else "Here is what I remember:\n" + "\n".join([f"{k}: {v}" for k, v in data.items()])
    
    return None
