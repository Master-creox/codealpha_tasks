"""Offline tests for codealpha_tasks (no network needed)."""
import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "Task2_Chatbot"))
sys.path.insert(0, os.path.join(ROOT, "Task1_Translator"))

from chatbot import find_answer, list_topics          # noqa: E402
from translator import translate_lines, translate_text  # noqa: E402


class FakeTranslator:
    def __init__(self, source, target):
        self.source, self.target = source, target

    def translate(self, text):
        return f"[{self.target}] {text}"


def fake_factory(source, target):
    return FakeTranslator(source, target)


class TestChatbot(unittest.TestCase):
    def test_exact_topics(self):
        for q, topic in [("what is phishing?", "phishing"),
                         ("Explain SQL injection", "sql injection"),
                         ("tell me about XSS", "xss"),
                         ("how do I make a strong password", "password"),
                         ("what is a vpn", "vpn")]:
            answer, matched = find_answer(q)
            self.assertEqual(matched, topic, q)
            self.assertGreater(len(answer), 40)

    def test_synonym_otp_maps_to_2fa(self):
        _answer, matched = find_answer("should I share my OTP with the bank?")
        self.assertEqual(matched, "2fa")

    def test_case_and_punctuation_ignored(self):
        _a, matched = find_answer("WHAT IS RANSOMWARE?!")
        self.assertEqual(matched, "ransomware")

    def test_unknown_question_gets_fallback(self):
        answer, matched = find_answer("what is the weather today")
        self.assertIsNone(matched)
        self.assertIn("don't know", answer)

    def test_topics_listed(self):
        self.assertIn("phishing", list_topics())


class TestTranslator(unittest.TestCase):
    def test_translate_text_uses_injected_translator(self):
        out = translate_text("hello", target="es", translator_factory=fake_factory)
        self.assertEqual(out, "[es] hello")

    def test_empty_text_raises(self):
        with self.assertRaises(ValueError):
            translate_text("   ", translator_factory=fake_factory)

    def test_translate_lines_preserves_blanks(self):
        out = translate_lines(["one", "", "two"], "hi", translator_factory=fake_factory)
        self.assertEqual(out, ["[hi] one", "", "[hi] two"])


if __name__ == "__main__":
    unittest.main()
