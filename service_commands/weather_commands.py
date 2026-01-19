"""
Weather command handler for A.L.F.R.E.D - processes weather-related queries.
"""
from __future__ import annotations

from typing import Optional, Union

from services.weather_service import get_weather, get_location_from_ip


def handle_weather_command(user_input: str) -> Optional[str]:
    """
    Handle weather-related commands.

    Args:
        user_input: The user's command text

    Returns:
        Weather response string or None if not a weather command
    """
    user_input = user_input.lower()
    keywords: list[str] = [
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
        parts: list[str] = user_input.split("in")
        location: Union[str, tuple[str, str], None]

        if len(parts) > 1:
            location = parts[1].strip()
        else:
            location = get_location_from_ip()
            if not location:
                return "Could not determine your location. Please specify a city."

        return get_weather(location)

    return None