import unittest
from unittest.mock import patch

from chatbot.service import answer


class TestService(unittest.TestCase):
    def test_local_answer_skips_llm(self):
        with patch("chatbot.service.find_answer", return_value="Jawaban lokal.") as lookup:
            with patch("chatbot.service.ask_llm") as llm:
                self.assertEqual(answer("  pertanyaan  "), {
                    "answer": "Jawaban lokal.", "source": "knowledge_base",
                })
        lookup.assert_called_once_with("pertanyaan")
        llm.assert_not_called()

    def test_invalid_input_skips_lookup(self):
        with patch("chatbot.service.find_answer") as lookup:
            for question in (None, 42, "", "  ", "x" * 2001):
                with self.subTest(question=question), self.assertRaises(ValueError):
                    answer(question)
        lookup.assert_not_called()

    def test_local_error_skips_llm(self):
        with patch("chatbot.service.find_answer", side_effect=ValueError("data rusak")):
            with patch("chatbot.service.ask_llm") as llm:
                with self.assertRaises(ValueError):
                    answer("pertanyaan")
        llm.assert_not_called()

    def test_invalid_llm_answer(self):
        with patch("chatbot.service.find_answer", return_value=None):
            for result in (None, "  ", 42):
                with patch("chatbot.service.ask_llm", return_value=result):
                    with self.subTest(result=result), self.assertRaises(RuntimeError):
                        answer("pertanyaan")


if __name__ == "__main__":
    unittest.main()
