"""Jalankan: python -m unittest test_server -v."""

import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from backend.server import ChatHandler
from chatbot.knowledge_base import load_knowledge_base


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ChatHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request(method, path, body, headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def post(self, data):
        return self.request("POST", "/api/chat", json.dumps(data),
                            {"Content-Type": "application/json"})

    def test_real_knowledge_base(self):
        item = load_knowledge_base()[0]
        status, _, body = self.post({"question": "  " + item["questions"][0].upper() + "  "})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"answer": item["answer"], "source": "knowledge_base"})

    def test_unknown_question(self):
        with patch("chatbot.service.ask_llm", return_value="Jawaban LLM.") as llm:
            status, _, body = self.post({"question": "__pertanyaan_tidak_tersedia__"})
        llm.assert_called_once_with("__pertanyaan_tidak_tersedia__")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"answer": "Jawaban LLM.", "source": "llm"})

    def test_invalid_requests(self):
        with patch("backend.server.answer") as lookup:
            for data in ([], {}, {"question": None}, {"question": 12},
                         {"question": "  "}, {"question": "x" * 2001}):
                with self.subTest(data=data):
                    self.assertEqual(self.post(data)[0], 400)
            for body in (b"{", b"\xff"):
                self.assertEqual(self.request("POST", "/api/chat", body,
                                 {"Content-Type": "application/json"})[0], 400)
            self.assertEqual(self.request("POST", "/api/chat", "{}")[0], 415)
            self.assertEqual(self.request("POST", "/api/chat", b"x" * 16385,
                             {"Content-Type": "application/json"})[0], 413)
            lookup.assert_not_called()

    def test_knowledge_base_error(self):
        for error in (ValueError("secret detail"), OSError("secret path")):
            with patch("chatbot.service.find_answer", side_effect=error):
                status, _, body = self.post({"question": "apa itu unp?"})
                self.assertEqual(status, 500)
                self.assertNotIn(b"secret", body)

    def test_llm_error(self):
        with patch("chatbot.service.find_answer", return_value=None):
            with patch("chatbot.service.ask_llm", side_effect=RuntimeError("secret")):
                status, _, body = self.post({"question": "pertanyaan lainnya"})
        self.assertEqual(status, 502)
        self.assertNotIn(b"secret", body)

    def test_static_routes_and_methods(self):
        for path in ("/", "/style.css", "/app.js"):
            self.assertEqual(self.request("GET", path)[0], 200)
        self.assertIn(b'src="app.js"', self.request("GET", "/")[2])
        self.assertEqual(self.request("HEAD", "/")[2], b"")
        for path in ("/.env", "/data/knowledge_base.json", "/../main.py"):
            self.assertEqual(self.request("GET", path)[0], 404)
        status, headers, _ = self.request("GET", "/api/chat")
        self.assertEqual((status, headers["Allow"]), (405, "POST"))
        self.assertEqual(self.request("POST", "/")[0], 405)
        self.assertEqual(self.request("PUT", "/api/chat")[0], 405)


if __name__ == "__main__":
    unittest.main()
