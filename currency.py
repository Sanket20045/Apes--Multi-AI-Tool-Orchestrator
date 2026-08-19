"""
Pleximus AI Agent — Currency Converter Tool (Extension Tool)
=============================================================
A live currency conversion tool using the open Frankfurter API.

Supports major international currencies (USD, INR, EUR, GBP, JPY, CAD, AUD, etc.)
with zero API key required.
"""

from typing import Any, Dict, Union
import requests

API_URL = "https://api.frankfurter.dev/v1/latest"
REQUEST_TIMEOUT_SECONDS = 10


def normalize_currency_code(code: str) -> str:
    """Normalize currency code (strip spaces and uppercase)."""
    if not isinstance(code, str):
        return ""
    return code.strip().upper()


def currency_converter(
    amount: Union[int, float, str],
    from_currency: str,
    to_currency: str
) -> Dict[str, Any]:
    """
    Convert an amount from one currency to another using live exchange rates.

    Args:
        amount: Numeric amount to convert (e.g., 100, 25.50).
        from_currency: Source 3-letter currency code (e.g., 'USD', 'EUR').
        to_currency: Target 3-letter currency code (e.g., 'INR', 'GBP').

    Returns:
        Structured dictionary response:
        Success:
            {
                "success": True,
                "amount": 100.0,
                "from_currency": "USD",
                "to_currency": "INR",
                "converted_amount": 8800.0,
                "rate": 88.0
            }
        Error:
            {
                "success": False,
                "amount": float,
                "from_currency": str,
                "to_currency": str,
                "error": str
            }
    """
    # 1. Validate and convert amount
    try:
        if isinstance(amount, (int, float)):
            numeric_amount = float(amount)
        elif isinstance(amount, str) and amount.strip():
            numeric_amount = float(amount.strip())
        else:
            raise ValueError("Amount must be a numeric value.")

        if numeric_amount < 0:
            return {
                "success": False,
                "amount": numeric_amount,
                "from_currency": str(from_currency),
                "to_currency": str(to_currency),
                "error": "Amount must be a positive number.",
            }
    except (ValueError, TypeError):
        return {
            "success": False,
            "amount": amount,
            "from_currency": str(from_currency),
            "to_currency": str(to_currency),
            "error": f"Invalid amount '{amount}'. Please provide a valid numeric value.",
        }

    # 2. Normalize and validate currency codes
    src = normalize_currency_code(from_currency)
    dst = normalize_currency_code(to_currency)

    if not src or len(src) != 3 or not src.isalpha():
        return {
            "success": False,
            "amount": numeric_amount,
            "from_currency": str(from_currency),
            "to_currency": str(to_currency),
            "error": f"Invalid source currency code '{from_currency}'. Must be a 3-letter code like USD, EUR, INR.",
        }

    if not dst or len(dst) != 3 or not dst.isalpha():
        return {
            "success": False,
            "amount": numeric_amount,
            "from_currency": src,
            "to_currency": str(to_currency),
            "error": f"Invalid target currency code '{to_currency}'. Must be a 3-letter code like USD, EUR, INR.",
        }

    # 3. Handle identical source and target currencies directly
    if src == dst:
        return {
            "success": True,
            "amount": numeric_amount,
            "from_currency": src,
            "to_currency": dst,
            "converted_amount": numeric_amount,
            "rate": 1.0,
        }

    # 4. Call Frankfurter API
    params = {
        "amount": numeric_amount,
        "from": src,
        "to": dst,
    }

    try:
        response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)

        if response.status_code in (400, 404, 422):
            return {
                "success": False,
                "amount": numeric_amount,
                "from_currency": src,
                "to_currency": dst,
                "error": f"Currency code unsupported or exchange rate unavailable between '{src}' and '{dst}'.",
            }

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "amount": numeric_amount,
            "from_currency": src,
            "to_currency": dst,
            "error": "Currency exchange service request timed out.",
        }
    except requests.exceptions.RequestException:
        return {
            "success": False,
            "amount": numeric_amount,
            "from_currency": src,
            "to_currency": dst,
            "error": "Currency exchange service is currently unavailable.",
        }
    except ValueError:
        return {
            "success": False,
            "amount": numeric_amount,
            "from_currency": src,
            "to_currency": dst,
            "error": "Unable to parse currency data from service.",
        }
    except Exception as e:
        return {
            "success": False,
            "amount": numeric_amount,
            "from_currency": src,
            "to_currency": dst,
            "error": f"An unexpected error occurred: {str(e)}",
        }

    # 5. Extract converted rate and amount
    rates = data.get("rates", {})
    if dst not in rates:
        return {
            "success": False,
            "amount": numeric_amount,
            "from_currency": src,
            "to_currency": dst,
            "error": f"Target currency '{dst}' not found in exchange rate response.",
        }

    converted_amount = rates[dst]
    rate = converted_amount / numeric_amount if numeric_amount != 0 else 0.0

    return {
        "success": True,
        "amount": numeric_amount,
        "from_currency": src,
        "to_currency": dst,
        "converted_amount": round(converted_amount, 2),
        "rate": round(rate, 4),
    }
