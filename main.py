"""
Pleximus AI Agent — Multi-Tool AI CLI Interface
================================================
Main interactive entry point for the Pleximus AI Agent.
Accepts natural language user input, displays tool selection,
and prints the final response.

Usage:
    Interactive mode:
        python main.py

    Direct query mode:
        python main.py "What is 25 * 17?"
        python main.py "What's the weather in Mumbai?"
"""

import sys

# Ensure UTF-8 output on Windows consoles if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from orchestrator import PleximusOrchestrator

BANNER = """============================================
              APES AI AGENT
============================================

I can help with:

🧮 Calculations
🌦️ Weather lookup
📝 Text operations
💱 Currency conversion

Type 'exit' to quit."""


def create_tool_listener():
    """Create a callback function to display selected tools in real time."""
    selected = []

    def on_tool_selected(tool_name: str, arguments: dict):
        selected.append((tool_name, arguments))
        print(f"\n[Tool selected: {tool_name}]")

    return on_tool_selected


def run_single_query(orchestrator: PleximusOrchestrator, query: str) -> None:
    """Execute a single query and display output."""
    listener = create_tool_listener()
    response = orchestrator.process_query(query, on_tool_selected=listener)
    print(f"\nAgent: {response}\n")


def interactive_session(orchestrator: PleximusOrchestrator) -> None:
    """Run continuous interactive chat session."""
    print(BANNER)
    if orchestrator.is_gemini_available():
        print("\n✨ Connected to Gemini LLM (Native Function Calling Active)\n")
    else:
        print("\n💡 Running in Local Mode. (Set GEMINI_API_KEY in .env for live Gemini LLM)\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not user_input:
            print("\nAgent: Please enter a request.\n")
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("\nGoodbye!")
            break

        listener = create_tool_listener()
        response = orchestrator.process_query(user_input, on_tool_selected=listener)
        print(f"\nAgent: {response}\n")


def main() -> None:
    """Main CLI entry point."""
    orchestrator = PleximusOrchestrator()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        run_single_query(orchestrator, query)
    else:
        interactive_session(orchestrator)


if __name__ == "__main__":
    main()
