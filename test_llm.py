import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from chatbot import knowledge_base, llm


class TestRAG(unittest.TestCase):
    def test_retrieves_relevant_faqs(self):
        results = knowledge_base.retrieve_context("Tolong jelaskan siapa dosen pengampu AI sekarang")
        self.assertEqual(results[0]["id"], "dosen-ai")
        self.assertLessEqual(len(results), 3)
        self.assertEqual(knowledge_base.retrieve_context("harga bitcoin"), [])
        self.assertEqual(knowledge_base.retrieve_context("apa itu"), [])

    def test_retrieval_ranks_and_limits(self):
        data = [{"id": str(i), "questions": ["dosen ai"], "answer": "Andi"} for i in range(5)]
        data.insert(0, {"id": "other", "questions": ["jadwal kuliah"], "answer": "Selasa"})
        with patch("chatbot.knowledge_base.load_knowledge_base", return_value=data):
            results = knowledge_base.retrieve_context("dosen ai")
        self.assertEqual([item["id"] for item in results], ["0", "1", "2"])

    def test_prompt_uses_retrieved_json(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=" Jawaban dari FAQ. "))],
        )
        with patch.object(llm, "client", client):
            self.assertEqual(llm.ask_llm("Siapakah dosen pengampu AI?"), "Jawaban dari FAQ.")
            kwargs = client.chat.completions.create.call_args.kwargs
            messages = kwargs["messages"]
            self.assertEqual(messages[0]["role"], "system")
            self.assertIn("Utamakan fakta relevan", messages[0]["content"])
            payload = json.loads(messages[1]["content"])
            self.assertEqual(payload["question"], "Siapakah dosen pengampu AI?")
            self.assertEqual(payload["knowledge_base"][0]["id"], "dosen-ai")
            self.assertIn("Andi Pratama", payload["knowledge_base"][0]["answer"])
            client.chat.completions.create.return_value.choices[0].message.content = "Fotosintesis mengubah energi cahaya."
            self.assertEqual(llm.ask_llm("Jelaskan fotosintesis"), "Fotosintesis mengubah energi cahaya.")
            empty = json.loads(client.chat.completions.create.call_args.kwargs["messages"][1]["content"])
            self.assertEqual(empty["knowledge_base"], [])
            policy = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
            self.assertIn("boleh menggunakan pengetahuan umum meskipun knowledge_base kosong", policy)
            self.assertIn("jangan mengarang atau menebak", policy)

    def test_bad_knowledge_base_skips_provider(self):
        with patch.object(llm, "client", Mock()) as client:
            for error in (ValueError("rusak"), OSError("hilang")):
                with patch("chatbot.knowledge_base.load_knowledge_base", side_effect=error):
                    with self.subTest(error=error), self.assertRaises(type(error)):
                        llm.ask_llm("dosen ai")
            client.chat.completions.create.assert_not_called()

    def test_invalid_input_and_missing_config(self):
        with patch.object(llm, "client", None):
            for question in (None, " ", "x" * 2001, "dosen ai"):
                with self.subTest(question=question), self.assertRaises(ValueError):
                    llm.ask_llm(question)

    def test_provider_failure_has_safe_error(self):
        client = Mock()
        client.chat.completions.create.side_effect = RuntimeError("secret provider details")
        with patch.object(llm, "client", client):
            with self.assertRaisesRegex(RuntimeError, "layanan AI sedang tidak tersedia") as error:
                llm.ask_llm("dosen ai")
        self.assertNotIn("secret", str(error.exception))


if __name__ == "__main__":
    unittest.main()
