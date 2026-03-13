import subprocess
from core.voice import speak
from core.listener import listen
from core.brain import get_response
from memory.database import check_connection
from utils.logger import get_logger

logger = get_logger(__name__)

def boot_sequence():
    try:
        subprocess.run(["./boot.exe"], check=True)
    except Exception as e:
        speak("Boot sequence failed. Please check the system.")
        raise e

def main():
    # Verify Supabase connection on boot
    try:
        if check_connection():
            logger.info("Supabase connection ready")
        else:
            logger.warning("Supabase connection failed — memory features may be unavailable")
    except Exception as e:
        logger.error(f"Supabase initialization failed: {e}")

    boot_sequence()
    speak("Boot sequence successful. Initializing systems. How may I assist you today?")

    while True:
        command = listen()
        if not command:
            continue

        if "sleep" in command.lower():
            speak("Powering down. Goodbye, sir.")
            break

        response = get_response(command)
        speak(response)

if __name__ == "__main__":
    main()
