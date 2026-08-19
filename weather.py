"""
Pleximus AI Agent — Weather Lookup Tool
========================================
A reliable, lightweight weather lookup tool that fetches live weather
information from the Open-Meteo API for supported cities.

This tool requires no API key and provides structured output suitable
for Python callers and Gemini LLM function calling.
"""

from typing import Any, Dict, Optional
import requests

# Open-Meteo Free Weather API Endpoint
API_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 10

# Predefined city-to-coordinate registry
CITIES: Dict[str, Dict[str, Any]] = {
    "mumbai": {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    "ratnagiri": {"name": "Ratnagiri", "latitude": 16.9902, "longitude": 73.3120},
    "pune": {"name": "Pune", "latitude": 18.5204, "longitude": 73.8567},
    "delhi": {"name": "Delhi", "latitude": 28.6139, "longitude": 77.2090},
    "bangalore": {"name": "Bangalore", "latitude": 12.9716, "longitude": 77.5946},
    "bengaluru": {"name": "Bangalore", "latitude": 12.9716, "longitude": 77.5946},
    "hyderabad": {"name": "Hyderabad", "latitude": 17.3850, "longitude": 78.4867},
    "chennai": {"name": "Chennai", "latitude": 13.0827, "longitude": 80.2707},
    "kolkata": {"name": "Kolkata", "latitude": 22.5726, "longitude": 88.3639},
    "ahmedabad": {"name": "Ahmedabad", "latitude": 23.0225, "longitude": 72.5714},
    "jaipur": {"name": "Jaipur", "latitude": 26.9124, "longitude": 75.7873},
    "london": {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    "new york": {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    "tokyo": {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    "paris": {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    "singapore": {"name": "Singapore", "latitude": 1.3521, "longitude": 103.8198},
    "sydney": {"name": "Sydney", "latitude": -33.8688, "longitude": 151.2093},
}

# WMO Weather interpretation codes (WW)
WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    62: "Moderate rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_condition(code: Optional[int]) -> str:
    """Translate WMO weather code into human-readable condition."""
    if code is None:
        return "Unknown weather condition"
    return WEATHER_CODES.get(code, "Unknown weather condition")


def normalize_city_name(city: str) -> str:
    """Normalize input city string by trimming whitespace and converting to lowercase."""
    if not isinstance(city, str):
        return ""
    return city.strip().lower()


def weather_lookup(city: str) -> Dict[str, Any]:
    """
    Retrieve current weather information for a supported city.

    Args:
        city: City name as string (case-insensitive, whitespace-tolerant).

    Returns:
        Structured weather dictionary with either:
        Success:
            {
                "success": True,
                "city": "Mumbai",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "temperature": 28.5,
                "wind_speed": 12.3,
                "weather_code": 2,
                "weather_condition": "Partly cloudy"
            }
        Error:
            {
                "success": False,
                "city": "Atlantis",
                "error": "City is not currently supported."
            }
    """
    # 1. Validate and normalize city input
    if not isinstance(city, str) or not city.strip():
        return {
            "success": False,
            "city": str(city) if city is not None else "",
            "error": "Please provide a valid city name.",
        }

    raw_city = city.strip()
    normalized = normalize_city_name(raw_city)

    # 2. Check if city is in local registry
    if normalized not in CITIES:
        return {
            "success": False,
            "city": raw_city,
            "error": "City is not currently supported.",
        }

    city_info = CITIES[normalized]
    lat = city_info["latitude"]
    lon = city_info["longitude"]
    canonical_name = city_info["name"]

    # 3. Call Open-Meteo API
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "city": canonical_name,
            "error": "Weather service request timed out.",
        }
    except requests.exceptions.RequestException:
        return {
            "success": False,
            "city": canonical_name,
            "error": "Weather service is currently unavailable.",
        }
    except ValueError:
        # JSON decode error
        return {
            "success": False,
            "city": canonical_name,
            "error": "Unable to parse weather data from service.",
        }
    except Exception as e:
        return {
            "success": False,
            "city": canonical_name,
            "error": f"An unexpected error occurred: {str(e)}",
        }

    # 4. Parse current weather data
    current = data.get("current_weather")
    if not current or not isinstance(current, dict):
        return {
            "success": False,
            "city": canonical_name,
            "error": "Weather data missing from API response.",
        }

    temperature = current.get("temperature")
    wind_speed = current.get("windspeed")
    weather_code = current.get("weathercode")

    if temperature is None or wind_speed is None:
        return {
            "success": False,
            "city": canonical_name,
            "error": "Incomplete weather measurements returned by service.",
        }

    condition = get_weather_condition(weather_code)

    return {
        "success": True,
        "city": canonical_name,
        "latitude": lat,
        "longitude": lon,
        "temperature": temperature,
        "wind_speed": wind_speed,
        "weather_code": weather_code,
        "weather_condition": condition,
    }
