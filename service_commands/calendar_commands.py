import datetime
import dateparser
from services.calendar_service import add_event # Assuming you have a function to capture voice input
from core.listener import listen
from core.voice import speak

def prompt(prompt_text):
    """Prompt the user via voice or fallback to text input"""
    try:
        print(f"A.L.F.R.E.D: {prompt_text}")
        return listen()  # Use your assistant's microphone input/text input method
    except:
        return input(f"{prompt_text}\n> ")

def handle_calendar_command(user_input):
    user_input = user_input.lower()

    if user_input.startswith("add meeting") or user_input.startswith("add event"):
        # 🔷 Ask user what to add
        speak("What is the title of the event?")
        title = input("Title: ")

        speak("When does it start?")
        date_input = input("Date and time: ")
        try:
            start_datetime = dateparser.parse(date_input)
            if not start_datetime:
                return "I couldn't understand the date and time."
        except:
            return "Sorry, I'm missing the 'dateparser' library. Please install it with: pip install dateparser"

        speak("How long is the event?")
        duration_input = input("Event duration: ")
        duration = parse_duration(duration_input)
        end_datetime = start_datetime + duration

        speak("Would you like to add a description?")
        description = input("Description: ")

        link = add_event(title, start_datetime, end_datetime, description)
        return f" {title} has been added to your calendar {start_datetime.strftime('%Y-%m-%d %I:%M %p')}.\n"

    return None

def parse_duration(text):
    text = text.lower()
    minutes = 0
    if "hour" in text:
        parts = text.split("hour")[0].strip()
        try:
            minutes += int(parts) * 60
        except:
            pass
    if "minute" in text:
        parts = text.split("minute")[0].strip().split()
        try:
            minutes += int(parts[-1])
        except:
            pass
    return datetime.timedelta(minutes=minutes or 30)  # Default to 30 mins if unclear
