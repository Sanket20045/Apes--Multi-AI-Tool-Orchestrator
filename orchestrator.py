"""
Pleximus AI Agent — Multi-Tool AI Orchestrator
===============================================
Connects Google Gemini LLM with 4 specialized local tools:
1. calculator (Safe AST mathematical evaluator)
2. weather_lookup (Live Open-Meteo weather)
3. text_utility (Local word count, character count, reverse, etc.)
4. currency_converter (Live Frankfurter currency exchange)

Uses native Gemini Function Calling for intelligent tool selection and multi-tool orchestration.
"""

import os
import re
from typing import Any, Callable, Dict, List, Optional
from dotenv import load_dotenv

from calculator import calculator
from weather import weather_lookup
from text_utils import text_utility
from currency import currency_converter

# Load environment variables from .env
load_dotenv()

# System instruction defining agent personality and tool usage guidelines
SYSTEM_INSTRUCTION = """You are Apes AI, a helpful, precise, and polite multi-tool AI agent developed for the AI Hackathon.

You have access to 4 specialized tools:
1. calculator: Use for all mathematical calculations, arithmetic (+, -, *, /, %, **), functions (sqrt, sin, cos, tan, log, etc.), and constants (pi, e).
2. weather_lookup: Use for looking up current live weather data (temperature, wind speed, conditions) for supported cities (e.g. Mumbai, Pune, Ratnagiri, Delhi, Bangalore, London, Tokyo, etc.).
3. text_utility: Use for text operations including word counting, character counting, reversing text, case transformation (uppercase/lowercase), and sentence counting.
4. currency_converter: Use for converting currency amounts between international currencies (USD, INR, EUR, GBP, JPY, CAD, AUD, etc.) using live exchange rates.

Guidelines:
- ALWAYS use tools whenever a user request requires calculation, weather, text manipulation, or currency conversion. Do NOT guess or perform manual math/weather estimations.
- Never invent or hallucinate tool results; use the exact data returned by the tools.
- When a tool returns an error (e.g. unsupported city, division by zero, invalid currency), explain the issue clearly and politely.
- If a user's prompt requires MULTIPLE tools (e.g. "Calculate 25 * 4 and tell me the weather in Mumbai"), call all necessary tools.
- Deliver your final answer in clean, readable natural language.
"""

# Tool execution registry mapping function name to Python callable
TOOLS_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {
    "calculator": calculator,
    "weather_lookup": weather_lookup,
    "text_utility": text_utility,
    "currency_converter": currency_converter,
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely execute a registered tool function with provided keyword arguments.

    Args:
        tool_name: Name of the tool in TOOLS_REGISTRY.
        arguments: Dictionary of arguments to pass to the tool function.

    Returns:
        Structured response dictionary from the tool.
    """
    if tool_name not in TOOLS_REGISTRY:
        return {
            "success": False,
            "error": f"Tool '{tool_name}' is not recognized.",
        }

    tool_func = TOOLS_REGISTRY[tool_name]
    try:
        return tool_func(**arguments)
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing tool '{tool_name}': {str(e)}",
        }


def get_gemini_tool_declarations() -> list:
    """Generate types.FunctionDeclaration objects for Google GenAI SDK."""
    try:
        from google.genai import types
    except ImportError:
        return []

    calculator_decl = types.FunctionDeclaration(
        name="calculator",
        description="Calculates the result of a mathematical expression (supports +, -, *, /, %, **, sqrt, sin, cos, tan, pi, e, etc.).",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "expression": types.Schema(
                    type="STRING",
                    description="The mathematical expression to evaluate, e.g. '25 * 17', 'sqrt(144)', '(10 + 20) * 2'."
                )
            },
            required=["expression"]
        )
    )

    weather_decl = types.FunctionDeclaration(
        name="weather_lookup",
        description="Retrieves current live weather information (temperature in Celsius, wind speed in km/h, and weather conditions) for a supported city.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "city": types.Schema(
                    type="STRING",
                    description="The name of the city, e.g. 'Mumbai', 'Pune', 'Ratnagiri', 'Delhi', 'London', 'Tokyo'."
                )
            },
            required=["city"]
        )
    )

    text_util_decl = types.FunctionDeclaration(
        name="text_utility",
        description="Performs text operations including word counting, character counting, reversing text, uppercase/lowercase, and sentence counting.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "operation": types.Schema(
                    type="STRING",
                    description="The operation to perform: 'word_count', 'character_count', 'reverse', 'uppercase', 'lowercase', 'sentence_count'."
                ),
                "text": types.Schema(
                    type="STRING",
                    description="The text string to process."
                )
            },
            required=["operation", "text"]
        )
    )

    currency_decl = types.FunctionDeclaration(
        name="currency_converter",
        description="Converts an amount from one currency to another using live exchange rates from the Frankfurter API.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "amount": types.Schema(
                    type="NUMBER",
                    description="The numeric amount of money to convert, e.g. 100 or 25.50."
                ),
                "from_currency": types.Schema(
                    type="STRING",
                    description="The 3-letter source currency code, e.g. 'USD', 'EUR', 'GBP', 'INR'."
                ),
                "to_currency": types.Schema(
                    type="STRING",
                    description="The 3-letter target currency code, e.g. 'INR', 'USD', 'EUR', 'GBP'."
                )
            },
            required=["amount", "from_currency", "to_currency"]
        )
    )

    return [
        types.Tool(
            function_declarations=[
                calculator_decl,
                weather_decl,
                text_util_decl,
                currency_decl
            ]
        )
    ]


class PleximusOrchestrator:
    """
    Main AI Orchestrator class managing Gemini conversation and tool execution.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.6-flash"):
        """
        Initialize the orchestrator with Gemini client.

        Args:
            api_key: Optional Gemini API key. If not provided, reads GEMINI_API_KEY from environment.
            model_name: Gemini model name (default: 'gemini-3.6-flash').
        """
        self.api_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY", "").strip()
        self.model_name = model_name
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Warning] Could not initialize Gemini Client: {e}")

    def is_gemini_available(self) -> bool:
        """Check if live Gemini client is configured and ready."""
        return self.client is not None and bool(self.api_key)

    def process_query(
        self,
        user_prompt: str,
        on_tool_selected: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> str:
        """
        Process a natural language user query through Gemini with tool orchestration.

        Args:
            user_prompt: The user's input string.
            on_tool_selected: Optional callback invoked when a tool is selected: callback(tool_name, arguments).

        Returns:
            The final natural-language response string.
        """
        if not user_prompt or not user_prompt.strip():
            return "Please enter a request."

        cleaned_prompt = user_prompt.strip()

        # If Gemini is configured, use native LLM function calling
        if self.is_gemini_available():
            return self._process_with_gemini(cleaned_prompt, on_tool_selected)

        # Fallback simulation mode for testing when no API key is set
        return self._process_fallback(cleaned_prompt, on_tool_selected)

    def _process_with_gemini(
        self,
        user_prompt: str,
        on_tool_selected: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> str:
        """Execute LLM function calling loop with Google GenAI SDK."""
        from google.genai import types

        tool_declarations = get_gemini_tool_declarations()
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tool_declarations,
            temperature=0.1,
        )

        try:
            # Turn 1: Send user prompt with available tools
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )

            # Check if Gemini decided to invoke one or more tools
            function_calls = getattr(response, "function_calls", None)
            if not function_calls and hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content and hasattr(candidate.content, "parts"):
                    function_calls = [
                        p.function_call for p in candidate.content.parts if hasattr(p, "function_call") and p.function_call
                    ]

            if not function_calls:
                # Direct natural language response without tool calling
                return response.text if hasattr(response, "text") and response.text else "I have processed your request."

            # Execute all requested tools and collect responses
            tool_response_parts = []
            for call in function_calls:
                tool_name = call.name
                arguments = dict(call.args) if hasattr(call, "args") and call.args else {}

                # Notify tool selection listener
                if on_tool_selected:
                    on_tool_selected(tool_name, arguments)

                # Execute Python tool
                tool_output = execute_tool(tool_name, arguments)

                # Build function response part
                tool_response_parts.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": tool_output}
                    )
                )

            # Turn 2: Send tool results back to Gemini for final answer generation
            conversation_contents = [
                types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)]),
                response.candidates[0].content,
                types.Content(role="user", parts=tool_response_parts)
            ]

            followup_response = self.client.models.generate_content(
                model=self.model_name,
                contents=conversation_contents,
                config=config,
            )

            return followup_response.text if hasattr(followup_response, "text") and followup_response.text else "Operation completed."

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                fallback_result = self._process_fallback(user_prompt, on_tool_selected)
                return f"{fallback_result}\n\n*(Note: Gemini free-tier rate limit reached; resolved seamlessly via local tool engine)*"
            # Fallback to local evaluation if network or API quota error occurs
            return f"Error communicating with Gemini: {err_str}"

    def _process_fallback(
        self,
        user_prompt: str,
        on_tool_selected: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> str:
        """
        Local fallback processor for offline testing when GEMINI_API_KEY is not configured.
        """
        prompt_lower = user_prompt.lower()
        results = []

        # 1. Check for currency conversion query
        currency_match = re.search(r"convert\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]{3})\s*(?:to|in)\s*([a-zA-Z]{3})", user_prompt, re.IGNORECASE)
        if currency_match:
            amt = float(currency_match.group(1))
            from_c = currency_match.group(2).upper()
            to_c = currency_match.group(3).upper()
            if on_tool_selected:
                on_tool_selected("currency_converter", {"amount": amt, "from_currency": from_c, "to_currency": to_c})
            res = currency_converter(amt, from_c, to_c)
            if res["success"]:
                results.append(f"{res['amount']} {res['from_currency']} is approximately {res['converted_amount']} {res['to_currency']} (rate: {res['rate']}).")
            else:
                results.append(f"Currency Error: {res['error']}")

        # 2. Check for weather query
        weather_match = re.search(r"weather\s+(?:in|for|at)?\s*([a-zA-Z\s]+)", user_prompt, re.IGNORECASE)
        if weather_match and not ("calculate" in prompt_lower and not "and" in prompt_lower):
            city = weather_match.group(1).strip().rstrip("?.!")
            if city:
                if on_tool_selected:
                    on_tool_selected("weather_lookup", {"city": city})
                res = weather_lookup(city)
                if res["success"]:
                    results.append(f"The current weather in {res['city']} is {res['temperature']}°C with {res['weather_condition'].lower()} and winds around {res['wind_speed']} km/h.")
                else:
                    results.append(f"Weather Error: {res['error']}")

        # 3. Check for text utility query
        if "reverse" in prompt_lower:
            match = re.search(r"reverse\s+(?:the\s+word\s+|text\s+)?[\"']?([^\"'\n]+)[\"']?", user_prompt, re.IGNORECASE)
            text_val = match.group(1).strip() if match else user_prompt.replace("reverse", "").strip()
            if on_tool_selected:
                on_tool_selected("text_utility", {"operation": "reverse", "text": text_val})
            res = text_utility("reverse", text_val)
            if res["success"]:
                results.append(f"Reversed text: {res['result']}")

        elif "word" in prompt_lower and ("count" in prompt_lower or "how many" in prompt_lower):
            match = re.search(r"[\"']([^\"']+)[\"']", user_prompt)
            text_val = match.group(1) if match else user_prompt
            if on_tool_selected:
                on_tool_selected("text_utility", {"operation": "word_count", "text": text_val})
            res = text_utility("word_count", text_val)
            if res["success"]:
                results.append(f"Word count: {res['result']}")

        # 4. Check for calculation query
        calc_match = re.search(r"(?:calculate|what is|compute)\s+([0-9\+\-\*\/\(\)\.\s\^%]+|sqrt\([0-9\.]+\)|sin\([0-9\.]+\)|cos\([0-9\.]+\))", user_prompt, re.IGNORECASE)
        if calc_match:
            expr = calc_match.group(1).strip().rstrip("?.!")
            if any(char.isdigit() for char in expr):
                if on_tool_selected:
                    on_tool_selected("calculator", {"expression": expr})
                res = calculator(expr)
                if res["success"]:
                    results.append(f"{res['expression']} = {res['result']}")
                else:
                    results.append(f"Calculation Error: {res['error']}")

        if results:
            return "\n\n".join(results)

        return (
            "I'm running in local test mode (GEMINI_API_KEY is not set in .env).\n"
            "Set your GEMINI_API_KEY in .env for full LLM orchestration, or try asking:\n"
            "• 'What is 25 * 17?'\n"
            "• 'What is the weather in Mumbai?'\n"
            "• 'Reverse the word Hackathon'\n"
            "• 'Convert 100 USD to INR'"
        )
