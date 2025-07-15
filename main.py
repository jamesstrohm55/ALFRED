from core.voice import speak
from core.listener import listen
from core.brain import get_response
from services.automation import run_command

def main():
    speak("Initializing systems. How may I assist you today?")
    
    while True:
        command = listen()
        if not command:
            continue

        if "sleep" in command.lower():
            speak("Powering down. Goodbye, sir.")
            break
        
        system_response = run_command(command)
        if system_response:
            speak(system_response)
            continue
        
        response = get_response(command)
        speak(response)

if __name__ == "__main__":
    main()
