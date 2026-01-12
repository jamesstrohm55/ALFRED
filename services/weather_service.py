import requests
from config import WEATHER_API_KEY
from utils.logger import get_logger

logger = get_logger(__name__)

API_KEY = WEATHER_API_KEY

def get_location_from_ip():
    """Get user's location from IP address for weather lookups."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        if data["status"] == "success":
            return data["city"], data["country"]
    except requests.RequestException as e:
        logger.warning(f"Could not determine location from IP: {e}")
    except (KeyError, ValueError) as e:
        logger.warning(f"Invalid location response: {e}")
    return None

def get_weather(location):
    if isinstance(location, tuple):
        location = f"{location[0]}, {location[1]}"

    url = ( 
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={location}&appid={API_KEY}&units=metric"
    )
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"Could not retrieve weather data for {location}."
    
    data = response.json()
    weather_desc = data['weather'][0]['description']
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    humidity = data['main']['humidity']

    return (
        f"Weather in {location}: {weather_desc}. "
        f"Temperature: {temp}°C (feels like {feels_like}°C). "
        f"Humidity: {humidity}%."
    )