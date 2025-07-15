from services.weather_service import get_weather
from services.weather_service import get_location_from_ip

def handle_weather_command(user_input):
    user_input = user_input.lower()
    keywords = [
        "weather",
        "how's the weather",
        "what's the weather",
        "current weather",
        "weather update",
        "weather report",
        "forecast",
        "temperature",
    ]

    if any(keyword in user_input for keyword in keywords):
        parts = user_input.split("in")
        if len(parts) > 1:
            location = parts[1].strip()
        else:
            location = get_location_from_ip()
            if not location:
                return "Could not determine your location. Please specify a city."

        return get_weather(location)
    
    return None