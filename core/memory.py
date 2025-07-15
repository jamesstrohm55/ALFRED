conversation_history = []

def add_to_memory(role, content):
    conversation_history.append({"role": role, "content": content})

def get_memory():
    return conversation_history[-10:] # Return the last 10 interactions for context
