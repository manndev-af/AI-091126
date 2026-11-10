"""Pilih jawaban knowledge base, lalu fallback ke LLM."""

from chatbot.knowledge_base import find_answer
from chatbot.llm import ask_llm


def answer(question: str) -> dict[str, str]:
    if not isinstance(question, str) or not question.strip() or len(question) > 2000:
        raise ValueError("Pertanyaan harus berupa teks 1 sampai 2.000 karakter.")

    question = question.strip()
    local_answer = find_answer(question)
    if local_answer is not None:
        return {"answer": local_answer, "source": "knowledge_base"}

    llm_answer = ask_llm(question)
    if not isinstance(llm_answer, str) or not llm_answer.strip():
        raise RuntimeError("LLM mengembalikan jawaban kosong atau tidak valid.")
    return {"answer": llm_answer.strip(), "source": "llm"}
