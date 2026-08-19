"""
Unit Tests for Pleximus AI Agent Text Utility Tool
===================================================
Automated test suite verifying word counting, character counting,
string reversing, case transformation, sentence counting, and error handling.
"""

import unittest
from text_utils import text_utility


class TestTextUtilityWordCount(unittest.TestCase):
    """Test word_count operation."""

    def test_word_count_standard(self):
        res = text_utility("word_count", "Artificial intelligence is amazing")
        self.assertTrue(res["success"])
        self.assertEqual(res["operation"], "word_count")
        self.assertEqual(res["result"], 4)

        res5 = text_utility("word_count", "Artificial intelligence is truly amazing")
        self.assertTrue(res5["success"])
        self.assertEqual(res5["result"], 5)

    def test_word_count_multiple_spaces(self):
        res = text_utility("word_count", "  Hello    world   from   AI  ")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 4)

    def test_word_count_empty(self):
        res = text_utility("word_count", "")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 0)


class TestTextUtilityCharacterCount(unittest.TestCase):
    """Test character_count operation."""

    def test_character_count_standard(self):
        res = text_utility("character_count", "Hello")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 5)

    def test_character_count_with_spaces(self):
        res = text_utility("character_count", "Hello World")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 11)


class TestTextUtilityReverse(unittest.TestCase):
    """Test reverse operation."""

    def test_reverse_word(self):
        res = text_utility("reverse", "Hackathon")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], "nohtakcaH")

    def test_reverse_phrase(self):
        res = text_utility("reverse", "Pleximus AI")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], "IA sumixelP")


class TestTextUtilityCaseTransformations(unittest.TestCase):
    """Test uppercase and lowercase transformations."""

    def test_uppercase(self):
        res = text_utility("uppercase", "hackathon 2026")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], "HACKATHON 2026")

    def test_lowercase(self):
        res = text_utility("lowercase", "PLEXIMUS AGENT")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], "pleximus agent")


class TestTextUtilitySentenceCount(unittest.TestCase):
    """Test sentence_count operation."""

    def test_sentence_count(self):
        text = "Hello world! This is AI agent. How are you?"
        res = text_utility("sentence_count", text)
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 3)


class TestTextUtilityErrorHandling(unittest.TestCase):
    """Test invalid operations and malformed inputs."""

    def test_unsupported_operation(self):
        res = text_utility("invalid_op", "some text")
        self.assertFalse(res["success"])
        self.assertIn("error", res)
        self.assertIn("Unsupported operation", res["error"])

    def test_non_string_text(self):
        res = text_utility("word_count", 12345)  # type: ignore
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_empty_operation(self):
        res = text_utility("", "some text")
        self.assertFalse(res["success"])
        self.assertIn("error", res)


if __name__ == "__main__":
    unittest.main()
