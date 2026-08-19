"""
Pleximus AI Agent — Word / Text Utility Tool
=============================================
A local text manipulation tool providing word counting, character counting,
reversing, case transformation, and sentence counting.

No external API is required. All operations execute locally.
"""

import re
from typing import Any, Dict, Union


def text_utility(operation: str, text: str) -> Dict[str, Any]:
    """
    Perform a text operation on the provided input text.

    Args:
        operation: The operation to perform ('word_count', 'character_count',
                   'reverse', 'uppercase', 'lowercase', 'sentence_count').
        text: The input text to process.

    Returns:
        Structured response dictionary:
        Success:
            {
                "success": True,
                "operation": str,
                "text": str,
                "result": Union[int, str]
            }
        Error:
            {
                "success": False,
                "operation": str,
                "error": str
            }
    """
    # 1. Validate inputs
    if not isinstance(operation, str) or not operation.strip():
        return {
            "success": False,
            "operation": str(operation) if operation is not None else "",
            "error": "Operation name must be a non-empty string.",
        }

    if not isinstance(text, str):
        return {
            "success": False,
            "operation": operation.strip(),
            "error": "Text must be a string.",
        }

    op = operation.strip().lower().replace("-", "_").replace(" ", "_")

    # 2. Execute requested operation
    try:
        if op in ("word_count", "count_words", "words"):
            # Split text by whitespace to count words
            words = text.strip().split()
            count = len(words) if text.strip() else 0
            return {
                "success": True,
                "operation": "word_count",
                "text": text,
                "result": count,
            }

        elif op in ("character_count", "char_count", "length", "chars"):
            # Total character count
            count = len(text)
            return {
                "success": True,
                "operation": "character_count",
                "text": text,
                "result": count,
            }

        elif op in ("reverse", "reverse_text", "reversed"):
            # Reverse string
            reversed_text = text[::-1]
            return {
                "success": True,
                "operation": "reverse",
                "text": text,
                "result": reversed_text,
            }

        elif op in ("uppercase", "upper", "to_upper"):
            return {
                "success": True,
                "operation": "uppercase",
                "text": text,
                "result": text.upper(),
            }

        elif op in ("lowercase", "lower", "to_lower"):
            return {
                "success": True,
                "operation": "lowercase",
                "text": text,
                "result": text.lower(),
            }

        elif op in ("sentence_count", "sentences", "count_sentences"):
            if not text.strip():
                count = 0
            else:
                # Count sentences ending with punctuation or whole text
                sentences = re.split(r"[.!?]+", text.strip())
                count = len([s for s in sentences if s.strip()])
            return {
                "success": True,
                "operation": "sentence_count",
                "text": text,
                "result": count,
            }

        else:
            return {
                "success": False,
                "operation": operation,
                "error": f"Unsupported operation '{operation}'. Supported operations: word_count, character_count, reverse, uppercase, lowercase, sentence_count.",
            }

    except Exception as e:
        return {
            "success": False,
            "operation": operation,
            "error": f"Error performing text operation: {str(e)}",
        }
