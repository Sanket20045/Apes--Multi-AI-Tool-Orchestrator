"""
Pleximus AI Agent — Weather CLI Interface
==========================================
Command-line testing interface for the Weather Lookup Tool.

Usage:
    Interactive mode:
        python main_weather.py

    Direct lookup mode:
        python main_weather.py Mumbai
        python main_weather.py "New York"
"""

import sys

# Ensure UTF-8 output on Windows consoles if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from weather import weather_lookup


BANNER = """=================================
      Pleximus Weather Tool
================================="""


def display_weather(city_query: str) -> None:
    """Lookup weather for a given city and display formatted result."""
    response = weather_lookup(city_query)

    if response["success"]:
        print(f"\nWeather in {response['city']}\n")
        print(f"Temperature: {response['temperature']}°C")
        print(f"Wind Speed: {response['wind_speed']} km/h")
        print(f"Condition: {response['weather_condition']}")
    else:
        print(f"\nError: {response['error']}")


def interactive_mode() -> None:
    """Run an interactive REPL loop allowing multiple city lookups."""
    print(BANNER)
    print("\nEnter a city or type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break

        display_weather(user_input)
        print()  # Spacer between queries


def main() -> None:
    """Main CLI entry point."""
    if len(sys.argv) > 1:
        # Direct CLI argument mode
        city_input = " ".join(sys.argv[1:])
        display_weather(city_input)
    else:
        # Interactive REPL mode
        interactive_mode()


if __name__ == "__main__":
    main()
