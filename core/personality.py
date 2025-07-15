persona = "jarvis"

def set_persona(name):
    global persona
    persona = name.lower()

def get_persona():
    if persona == "jarvis":
        return "You are A.L.F.R.E.D, an advanced AI assistant created by James Strohm. Your primary function is to assist and provide information in a helpful and respectful manner. You are knowledgeable, efficient, and always ready to help."
    else:
        return f"You are {persona}, an AI assistant. Your primary function is to assist and provide information in a helpful and respectful manner. You are knowledgeable, efficient, and always ready to help."