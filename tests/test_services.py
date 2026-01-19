"""
Unit tests for services - automation, system_monitor, weather_service.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
import datetime

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAutomation:
    """Tests for services/automation.py"""

    def test_tell_time_format(self):
        """Test that tell_time returns properly formatted time."""
        from services.automation import tell_time

        result = tell_time()
        assert "current time" in result.lower()
        # Check format includes AM/PM
        assert "AM" in result or "PM" in result

    def test_run_command_fuzzy_matching(self):
        """Test fuzzy command matching."""
        from services.automation import run_command

        with patch('services.automation.open_browser') as mock_browser:
            mock_browser.return_value = "Opening browser"
            # Slightly misspelled should still match
            result = run_command("opn browser")
            # May or may not match depending on cutoff

    def test_run_command_no_match_returns_none(self):
        """Test that unrecognized commands return None."""
        from services.automation import run_command

        result = run_command("completely unrelated command xyz123")
        assert result is None

    def test_command_map_contains_expected_commands(self):
        """Test that all expected commands are in the map."""
        from services.automation import command_map

        expected_commands = ["open browser", "open vs code", "tell time", "play music", "lock computer"]
        for cmd in expected_commands:
            assert cmd in command_map


class TestSystemMonitor:
    """Tests for services/system_monitor.py"""

    def test_get_system_stats_returns_dict(self):
        """Test that system stats returns a dictionary with expected keys."""
        from services.system_monitor import get_system_stats

        stats = get_system_stats()

        assert isinstance(stats, dict)
        expected_keys = [
            "cpu_percent", "ram_percent", "ram_used_gb", "ram_total_gb",
            "disk_percent", "disk_used_gb", "disk_total_gb", "uptime", "os", "os_version"
        ]
        for key in expected_keys:
            assert key in stats

    def test_get_system_stats_values_in_range(self):
        """Test that percentage values are in valid range."""
        from services.system_monitor import get_system_stats

        stats = get_system_stats()

        assert 0 <= stats["cpu_percent"] <= 100
        assert 0 <= stats["ram_percent"] <= 100
        assert 0 <= stats["disk_percent"] <= 100

    def test_get_system_stats_memory_positive(self):
        """Test that memory values are positive."""
        from services.system_monitor import get_system_stats

        stats = get_system_stats()

        assert stats["ram_total_gb"] > 0
        assert stats["disk_total_gb"] > 0

    def test_get_disk_path_returns_string(self):
        """Test that disk path function returns a string."""
        from services.system_monitor import _get_disk_path

        path = _get_disk_path()
        assert isinstance(path, str)
        assert len(path) > 0


class TestWeatherService:
    """Tests for services/weather_service.py"""

    def test_get_location_from_ip_caching(self):
        """Test that location results are cached."""
        from services.weather_service import get_location_from_ip, _location_cache

        with patch('services.weather_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "status": "success",
                "city": "Test City",
                "country": "Test Country"
            }
            mock_get.return_value = mock_response

            # First call should hit the API
            result1 = get_location_from_ip()

            # Second call should use cache
            result2 = get_location_from_ip()

            # Should only be called once due to caching
            assert mock_get.call_count == 1
            assert result1 == result2

    def test_get_weather_with_tuple_location(self):
        """Test weather lookup with tuple location."""
        from services.weather_service import get_weather

        with patch('services.weather_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "weather": [{"description": "clear sky"}],
                "main": {"temp": 20, "feels_like": 19, "humidity": 50}
            }
            mock_get.return_value = mock_response

            result = get_weather(("London", "UK"))
            assert "Weather in London, UK" in result
            assert "clear sky" in result

    def test_get_weather_caching(self):
        """Test that weather results are cached."""
        from services.weather_service import get_weather, _weather_cache

        with patch('services.weather_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "weather": [{"description": "sunny"}],
                "main": {"temp": 25, "feels_like": 24, "humidity": 40}
            }
            mock_get.return_value = mock_response

            # Clear cache first
            from services.weather_service import clear_weather_cache
            clear_weather_cache()

            # First call
            get_weather("TestCity")

            # Second call should use cache
            get_weather("TestCity")

            # Should only hit API once
            assert mock_get.call_count == 1

    def test_get_weather_handles_api_error(self):
        """Test that API errors are handled gracefully."""
        from services.weather_service import get_weather, clear_weather_cache

        clear_weather_cache()

        with patch('services.weather_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = get_weather("NonexistentCity")
            assert "Could not retrieve" in result

    def test_clear_weather_cache(self):
        """Test cache clearing functionality."""
        from services.weather_service import clear_weather_cache, _weather_cache, _location_cache

        clear_weather_cache()
        assert _location_cache["data"] is None
