"""
Unit Tests for Pleximus AI Agent Orchestrator
==============================================
Automated test suite verifying tool registration, dispatch execution,
Gemini tool declaration schemas, and orchestrator query routing.
"""

import unittest
from unittest.mock import patch, MagicMock

from orchestrator import (
    execute_tool,
    get_gemini_tool_declarations,
    PleximusOrchestrator,
    TOOLS_REGISTRY,
)


class TestOrchestratorToolDispatch(unittest.TestCase):
    """Test execute_tool dispatcher across all 4 tools."""

    def test_calculator_dispatch(self):
        res = execute_tool("calculator", {"expression": "25 * 4"})
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 100)

    @patch("weather.requests.get")
    def test_weather_dispatch(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_weather": {
                "temperature": 28.0,
                "windspeed": 10.0,
                "weathercode": 0
            }
        }
        mock_get.return_value = mock_response

        res = execute_tool("weather_lookup", {"city": "Mumbai"})
        self.assertTrue(res["success"])
        self.assertEqual(res["city"], "Mumbai")

    def test_text_utility_dispatch(self):
        res = execute_tool("text_utility", {"operation": "reverse", "text": "Hackathon"})
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], "nohtakcaH")

    @patch("currency.requests.get")
    def test_currency_dispatch(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 100.0,
            "rates": {"INR": 8800.0}
        }
        mock_get.return_value = mock_response

        res = execute_tool("currency_converter", {"amount": 100, "from_currency": "USD", "to_currency": "INR"})
        self.assertTrue(res["success"])
        self.assertEqual(res["converted_amount"], 8800.0)

    def test_unknown_tool_dispatch(self):
        res = execute_tool("nonexistent_tool", {})
        self.assertFalse(res["success"])
        self.assertIn("not recognized", res["error"])


class TestOrchestratorDeclarations(unittest.TestCase):
    """Test Gemini tool declarations structure."""

    def test_tool_declarations(self):
        tools = get_gemini_tool_declarations()
        self.assertEqual(len(tools), 1)
        tool = tools[0]
        self.assertTrue(hasattr(tool, "function_declarations"))
        func_names = [f.name for f in tool.function_declarations]
        self.assertIn("calculator", func_names)
        self.assertIn("weather_lookup", func_names)
        self.assertIn("text_utility", func_names)
        self.assertIn("currency_converter", func_names)


class TestOrchestratorQueryProcessing(unittest.TestCase):
    """Test query processing and fallback routing."""

    def setUp(self):
        # Create orchestrator without API key for fallback testing
        self.orchestrator = PleximusOrchestrator(api_key="")

    def test_empty_query(self):
        res = self.orchestrator.process_query("")
        self.assertEqual(res, "Please enter a request.")

    def test_fallback_calculation_routing(self):
        selected_tools = []
        def on_tool(name, args):
            selected_tools.append((name, args))

        res = self.orchestrator.process_query("What is 50 * 20?", on_tool_selected=on_tool)
        self.assertIn("1000", res)
        self.assertEqual(len(selected_tools), 1)
        self.assertEqual(selected_tools[0][0], "calculator")

    def test_fallback_reverse_routing(self):
        selected_tools = []
        def on_tool(name, args):
            selected_tools.append((name, args))

        res = self.orchestrator.process_query("Reverse the word Hackathon", on_tool_selected=on_tool)
        self.assertIn("nohtakcaH", res)
        self.assertEqual(len(selected_tools), 1)
        self.assertEqual(selected_tools[0][0], "text_utility")

    @patch("currency.requests.get")
    def test_fallback_currency_routing(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 100.0,
            "rates": {"INR": 8800.0}
        }
        mock_get.return_value = mock_response

        selected_tools = []
        def on_tool(name, args):
            selected_tools.append((name, args))

        res = self.orchestrator.process_query("Convert 100 USD to INR", on_tool_selected=on_tool)
        self.assertIn("8800", res)
        self.assertEqual(selected_tools[0][0], "currency_converter")


if __name__ == "__main__":
    unittest.main()
