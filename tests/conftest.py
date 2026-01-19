"""
Pytest configuration and shared fixtures for A.L.F.R.E.D tests.
"""
from __future__ import annotations

import pytest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def reset_memory_cache():
    """Reset memory cache before each test."""
    try:
        from memory.memory_manager import clear_cache
        clear_cache()
    except ImportError:
        pass
    yield


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    from unittest.mock import MagicMock, patch

    with patch('core.brain.client') as mock_client:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_weather_api():
    """Mock weather API responses."""
    from unittest.mock import MagicMock, patch

    with patch('services.weather_service.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "weather": [{"description": "clear sky"}],
            "main": {"temp": 20, "feels_like": 19, "humidity": 50}
        }
        mock_get.return_value = mock_response
        yield mock_get
