"""
Unit Tests for Pleximus AI Agent Currency Converter Tool
=========================================================
Automated test suite verifying Frankfurter API conversion, amount validation,
currency code normalization, error handling, and mock simulations.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests

from currency import currency_converter, normalize_currency_code


class TestCurrencyConverterValidConversions(unittest.TestCase):
    """Test valid currency conversions with mocked and live API responses."""

    @patch("currency.requests.get")
    def test_mocked_usd_to_inr(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 100.0,
            "base": "USD",
            "date": "2026-08-18",
            "rates": {"INR": 8800.0}
        }
        mock_get.return_value = mock_response

        res = currency_converter(100, "USD", "INR")
        self.assertTrue(res["success"])
        self.assertEqual(res["amount"], 100.0)
        self.assertEqual(res["from_currency"], "USD")
        self.assertEqual(res["to_currency"], "INR")
        self.assertEqual(res["converted_amount"], 8800.0)
        self.assertEqual(res["rate"], 88.0)

    @patch("currency.requests.get")
    def test_case_and_whitespace_insensitivity(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "amount": 10.0,
            "base": "EUR",
            "rates": {"USD": 10.8}
        }
        mock_get.return_value = mock_response

        res = currency_converter(" 10 ", " eur ", "  usd ")
        self.assertTrue(res["success"])
        self.assertEqual(res["from_currency"], "EUR")
        self.assertEqual(res["to_currency"], "USD")
        self.assertEqual(res["converted_amount"], 10.8)

    def test_same_currency_conversion(self):
        # Should return amount without needing network request
        res = currency_converter(50, "USD", "USD")
        self.assertTrue(res["success"])
        self.assertEqual(res["converted_amount"], 50.0)
        self.assertEqual(res["rate"], 1.0)


class TestCurrencyConverterValidationAndErrors(unittest.TestCase):
    """Test invalid currency codes and amount validation."""

    def test_negative_amount(self):
        res = currency_converter(-100, "USD", "INR")
        self.assertFalse(res["success"])
        self.assertIn("error", res)
        self.assertIn("positive number", res["error"])

    def test_invalid_non_numeric_amount(self):
        res = currency_converter("abc", "USD", "INR")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_invalid_currency_code_format(self):
        res1 = currency_converter(100, "US", "INR")
        self.assertFalse(res1["success"])
        self.assertIn("error", res1)

        res2 = currency_converter(100, "USD", "123")
        self.assertFalse(res2["success"])
        self.assertIn("error", res2)

    @patch("currency.requests.get")
    def test_unsupported_currency_code_api_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        res = currency_converter(100, "XYZ", "INR")
        self.assertFalse(res["success"])
        self.assertIn("unsupported", res["error"])


class TestCurrencyConverterNetworkFailures(unittest.TestCase):
    """Test network timeouts and API errors."""

    @patch("currency.requests.get")
    def test_connection_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        res = currency_converter(100, "USD", "INR")
        self.assertFalse(res["success"])
        self.assertIn("timed out", res["error"])

    @patch("currency.requests.get")
    def test_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Network disconnected")
        res = currency_converter(100, "USD", "INR")
        self.assertFalse(res["success"])
        self.assertIn("unavailable", res["error"])


class TestCurrencyLiveIntegration(unittest.TestCase):
    """Test live Frankfurter API query if internet is accessible."""

    def test_live_usd_to_inr(self):
        res = currency_converter(100, "USD", "INR")
        if res["success"]:
            self.assertEqual(res["from_currency"], "USD")
            self.assertEqual(res["to_currency"], "INR")
            self.assertGreater(res["converted_amount"], 0)
            self.assertGreater(res["rate"], 0)
        else:
            self.assertIn("error", res)


if __name__ == "__main__":
    unittest.main()
