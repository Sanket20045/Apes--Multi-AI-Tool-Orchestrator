"""
Unit Tests for Pleximus AI Agent Weather Lookup Tool
=====================================================
Automated test suite verifying location resolution, Open-Meteo API handling,
mocked API failures, weather code translations, and edge cases.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests

from weather import weather_lookup, get_weather_condition, normalize_city_name, CITIES


class TestWeatherLookupValidCities(unittest.TestCase):
    """Test valid city lookups with mocked API responses."""

    @patch("weather.requests.get")
    def test_valid_city_mumbai(self, mock_get):
        # Mock successful Open-Meteo response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "latitude": 19.076,
            "longitude": 72.8777,
            "current_weather": {
                "temperature": 28.5,
                "windspeed": 12.3,
                "weathercode": 2,
            }
        }
        mock_get.return_value = mock_response

        res = weather_lookup("Mumbai")
        self.assertTrue(res["success"])
        self.assertEqual(res["city"], "Mumbai")
        self.assertEqual(res["latitude"], 19.0760)
        self.assertEqual(res["longitude"], 72.8777)
        self.assertEqual(res["temperature"], 28.5)
        self.assertEqual(res["wind_speed"], 12.3)
        self.assertEqual(res["weather_code"], 2)
        self.assertEqual(res["weather_condition"], "Partly cloudy")

    @patch("weather.requests.get")
    def test_case_insensitivity(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_weather": {
                "temperature": 24.0,
                "windspeed": 8.0,
                "weathercode": 0,
            }
        }
        mock_get.return_value = mock_response

        for city_variant in ["Mumbai", "mumbai", "MUMBAI", "MuMbAi"]:
            res = weather_lookup(city_variant)
            self.assertTrue(res["success"], f"Failed for variant: {city_variant}")
            self.assertEqual(res["city"], "Mumbai")

    @patch("weather.requests.get")
    def test_whitespace_handling(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_weather": {
                "temperature": 26.0,
                "windspeed": 10.0,
                "weathercode": 1,
            }
        }
        mock_get.return_value = mock_response

        res = weather_lookup("   Mumbai   \n\t")
        self.assertTrue(res["success"])
        self.assertEqual(res["city"], "Mumbai")

    @patch("weather.requests.get")
    def test_other_predefined_cities(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_weather": {
                "temperature": 22.0,
                "windspeed": 5.5,
                "weathercode": 3,
            }
        }
        mock_get.return_value = mock_response

        for city in ["pune", "ratnagiri", "delhi", "bangalore", "london", "tokyo"]:
            res = weather_lookup(city)
            self.assertTrue(res["success"], f"Failed for predefined city: {city}")
            self.assertIn(city, CITIES)


class TestWeatherLookupUnsupportedCity(unittest.TestCase):
    """Test unsupported and invalid city inputs."""

    def test_unsupported_city_atlantis(self):
        res = weather_lookup("Atlantis")
        self.assertFalse(res["success"])
        self.assertEqual(res["city"], "Atlantis")
        self.assertEqual(res["error"], "City is not currently supported.")

    def test_empty_string(self):
        res = weather_lookup("")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_whitespace_only(self):
        res = weather_lookup("     ")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_non_string_input(self):
        res = weather_lookup(12345)  # type: ignore
        self.assertFalse(res["success"])
        self.assertIn("error", res)


class TestWeatherLookupAPIFailures(unittest.TestCase):
    """Test API network failures and timeouts using mocking."""

    @patch("weather.requests.get")
    def test_api_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        res = weather_lookup("Mumbai")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Weather service is currently unavailable.")

    @patch("weather.requests.get")
    def test_api_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        res = weather_lookup("Mumbai")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Weather service request timed out.")

    @patch("weather.requests.get")
    def test_api_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        res = weather_lookup("Mumbai")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Weather service is currently unavailable.")


class TestWeatherLookupInvalidResponses(unittest.TestCase):
    """Test malformed and incomplete API responses."""

    @patch("weather.requests.get")
    def test_invalid_json_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        res = weather_lookup("Mumbai")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Unable to parse weather data from service.")

    @patch("weather.requests.get")
    def test_missing_current_weather_field(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"latitude": 19.076}
        mock_get.return_value = mock_response

        res = weather_lookup("Mumbai")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Weather data missing from API response.")

    @patch("weather.requests.get")
    def test_missing_temperature_field(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_weather": {
                "windspeed": 10.0,
                "weathercode": 1
            }
        }
        mock_get.return_value = mock_response

        res = weather_lookup("Mumbai")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Incomplete weather measurements returned by service.")


class TestWeatherCodeTranslation(unittest.TestCase):
    """Test WMO weather code translation helper."""

    def test_known_codes(self):
        self.assertEqual(get_weather_condition(0), "Clear sky")
        self.assertEqual(get_weather_condition(1), "Mainly clear")
        self.assertEqual(get_weather_condition(2), "Partly cloudy")
        self.assertEqual(get_weather_condition(3), "Overcast")
        self.assertEqual(get_weather_condition(45), "Fog")
        self.assertEqual(get_weather_condition(61), "Slight rain")
        self.assertEqual(get_weather_condition(95), "Thunderstorm")

    def test_unknown_code(self):
        self.assertEqual(get_weather_condition(999), "Unknown weather condition")
        self.assertEqual(get_weather_condition(None), "Unknown weather condition")


class TestWeatherLiveIntegration(unittest.TestCase):
    """Test live Open-Meteo API query (if internet is reachable)."""

    def test_live_mumbai_weather(self):
        res = weather_lookup("Mumbai")
        if res["success"]:
            self.assertEqual(res["city"], "Mumbai")
            self.assertIsInstance(res["temperature"], (int, float))
            self.assertIsInstance(res["wind_speed"], (int, float))
            self.assertIsInstance(res["weather_condition"], str)
        else:
            # If offline, ensure it failed gracefully with a clean error
            self.assertIn("error", res)


if __name__ == "__main__":
    unittest.main()
