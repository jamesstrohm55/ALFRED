"""
Weather service for A.L.F.R.E.D - provides weather data with caching and IP-based location.
"""
from __future__ import annotations

import time
from typing import Any, Optional, Union

import requests
from config import WEATHER_API_KEY
from utils.logger import get_logger

logger = get_logger(__name__)

API_KEY: Optional[str] = WEATHER_API_KEY

# Cache configuration
_LOCATION_CACHE_TTL: int = 300  # 5 minutes
_WEATHER_CACHE_TTL: int = 180  # 3 minutes
_REQUEST_TIMEOUT: int = 10  # seconds

# Cache storage
_location_cache: dict[str, Any] = {"data": None, "timestamp": 0}
_weather_cache: dict[str, dict[str, Any]] = {}


def get_location_from_ip() -> Optional[tuple[str, str]]:
    """
    Get user's location from IP address for weather lookups.

    Returns cached location if available and not expired.
    """
    current_time: float = time.time()

    # Check cache
    if (_location_cache["data"] is not None and
            current_time - _location_cache["timestamp"] < _LOCATION_CACHE_TTL):
        logger.debug("Using cached location data")
        return _location_cache["data"]

    try:
        response = requests.get("http://ip-api.com/json/", timeout=_REQUEST_TIMEOUT)
        data: dict[str, Any] = response.json()
        if data["status"] == "success":
            location: tuple[str, str] = (data["city"], data["country"])
            # Update cache
            _location_cache["data"] = location
            _location_cache["timestamp"] = current_time
            return location
    except requests.RequestException as e:
        logger.warning(f"Could not determine location from IP: {e}")
    except (KeyError, ValueError) as e:
        logger.warning(f"Invalid location response: {e}")
    return None


def get_weather(location: Union[str, tuple[str, str]]) -> str:
    """
    Get weather data for the specified location.

    Uses caching to reduce API calls for repeated requests.
    """
    if isinstance(location, tuple):
        location = f"{location[0]}, {location[1]}"

    current_time: float = time.time()
    cache_key: str = location.lower()

    # Check cache
    if cache_key in _weather_cache:
        cached = _weather_cache[cache_key]
        if current_time - cached["timestamp"] < _WEATHER_CACHE_TTL:
            logger.debug(f"Using cached weather data for {location}")
            return cached["response"]

    url: str = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={location}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=_REQUEST_TIMEOUT)
    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {e}")
        return f"Could not retrieve weather data for {location}."

    if response.status_code != 200:
        return f"Could not retrieve weather data for {location}."

    data: dict[str, Any] = response.json()
    weather_desc: str = data['weather'][0]['description']
    temp: float = data['main']['temp']
    feels_like: float = data['main']['feels_like']
    humidity: int = data['main']['humidity']

    result: str = (
        f"Weather in {location}: {weather_desc}. "
        f"Temperature: {temp}°C (feels like {feels_like}°C). "
        f"Humidity: {humidity}%."
    )

    # Update cache
    _weather_cache[cache_key] = {"response": result, "timestamp": current_time}

    return result


def clear_weather_cache() -> None:
    """Clear all cached weather data."""
    global _weather_cache, _location_cache
    _weather_cache = {}
    _location_cache = {"data": None, "timestamp": 0}
    logger.info("Weather cache cleared")