import speech_recognition as sr

def listen():
    recognizer = sr.Recognizer()
    try:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(audio)
                    print(f"You (via mic): {command}")
                    return command
                except sr.UnknownValueError:
                    print("Sorry, I didn’t catch that.")
                    return None
                except sr.WaitTimeoutError:
                    print("Listening timed out.")
                    return None
        except (OSError, AttributeError):
            # No mic found or access issue
            command = input("🎤 Microphone not found. Please type your command: ")
            print(f"You (typed): {command}")
            return command
    except sr.UnknownValueError:
        print("Sorry, I didn’t catch that.")
        return None
