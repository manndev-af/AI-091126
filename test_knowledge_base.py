
import json
import unittest
import tempfile

from pathlib import Path
from unittest.mock import patch

from chatbot import knowledge_base


class TestKnowledgeBase(unittest.TestCase):

    def setUp(self):
        # Membuat folder sementara untuk pengujian
        self.temp_dir = tempfile.TemporaryDirectory()

        self.file_path = (
            Path(self.temp_dir.name) / "knowledge_base.json"
        )

        # Mengganti lokasi file JSON dengan file sementara
        self.patcher = patch.object(
            knowledge_base,
            "KNOWLEDGE_BASE_PATH",
            self.file_path
        )

        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def write_data(self, data):
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file)

    # Menguji pertanyaan yang ditemukan
    def test_find_answer(self):

        self.write_data([
            {
                "id": "test-ai",
                "questions": ["apa itu ai?"],
                "answer": "AI adalah kecerdasan buatan."
            }
        ])

        result = knowledge_base.find_answer("apa itu ai?")

        self.assertEqual(
            result,
            "AI adalah kecerdasan buatan."
        )

    # Menguji huruf besar dan spasi
    def test_question_normalization(self):

        self.write_data([
            {
                "id": "test-ai",
                "questions": ["apa itu ai?"],
                "answer": "AI adalah kecerdasan buatan."
            }
        ])

        result = knowledge_base.find_answer("  APA ITU AI?  ")

        self.assertEqual(
            result,
            "AI adalah kecerdasan buatan."
        )

    # Menguji pertanyaan yang tidak ditemukan
    def test_answer_not_found(self):

        self.write_data([
            {
                "id": "test-ai",
                "questions": ["apa itu ai?"],
                "answer": "AI adalah kecerdasan buatan."
            }
        ])

        result = knowledge_base.find_answer(
            "apa itu database?"
        )

        self.assertIsNone(result)

    # Menguji pertanyaan kosong
    def test_empty_question(self):

        result = knowledge_base.find_answer("   ")

        self.assertIsNone(result)

    # Menguji file JSON yang rusak
    def test_invalid_json(self):

        self.file_path.write_text(
            "{ data tidak valid",
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            knowledge_base.find_answer("apa itu ai?")

    # Menguji format data yang salah
    def test_invalid_data_format(self):

        self.write_data({
            "id": "test-ai"
        })

        with self.assertRaises(ValueError):
            knowledge_base.find_answer("apa itu ai?")

    # Menguji pertanyaan duplikat
    def test_duplicate_question(self):

        self.write_data([
            {
                "id": "test-1",
                "questions": ["apa itu ai?"],
                "answer": "Jawaban pertama."
            },
            {
                "id": "test-2",
                "questions": [" APA ITU AI? "],
                "answer": "Jawaban kedua."
            }
        ])

        with self.assertRaises(ValueError):
            knowledge_base.find_answer("apa itu ai?")

    # Menguji file JSON yang tidak ditemukan
    def test_file_not_found(self):

        with self.assertRaises(OSError):
            knowledge_base.find_answer("apa itu ai?")


if __name__ == "__main__":
    unittest.main()
