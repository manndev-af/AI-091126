"""Tugas anggota 1: implementasikan find_answer(question); kontrak di README.md."""

import json
from pathlib import Path


# ==========================================
# KONFIGURASI LOKASI KNOWLEDGE BASE
# ==========================================

KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "knowledge_base.json"
)


# ==========================================
# NORMALISASI PERTANYAAN
# ==========================================

def normalize_question(question: str) -> str:
    """
    Mengubah pertanyaan menjadi huruf kecil
    dan menghapus spasi di awal serta akhir.
    """
    return question.lower().strip()


# ==========================================
# MEMBACA DAN MEMVALIDASI DATA JSON
# ==========================================

def load_knowledge_base() -> list[dict]:
    """
    Membaca data knowledge base dari file JSON.

    Raises:
        ValueError: Jika format atau isi JSON tidak valid.
        OSError: Jika file gagal dibaca atau tidak ditemukan.
    """

    with KNOWLEDGE_BASE_PATH.open("r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Format file knowledge_base.json tidak valid."
            ) from error

    # Memastikan data berbentuk list
    if not isinstance(data, list):
        raise ValueError("Knowledge base harus berbentuk list.")

    used_ids = set()
    used_questions = set()

    for index, item in enumerate(data):

        # Memastikan setiap item berbentuk dictionary
        if not isinstance(item, dict):
            raise ValueError(
                f"Data pada indeks {index} harus berbentuk objek."
            )

        item_id = item.get("id")
        questions = item.get("questions")
        answer = item.get("answer")

        # Validasi ID
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(
                f"ID pada indeks {index} tidak boleh kosong."
            )

        normalized_id = item_id.strip().lower()

        if normalized_id in used_ids:
            raise ValueError(
                f"ID knowledge base duplikat: {item_id}"
            )

        used_ids.add(normalized_id)

        # Validasi daftar pertanyaan
        if not isinstance(questions, list) or not questions:
            raise ValueError(
                f"Questions pada ID {item_id} harus berupa list "
                "yang tidak kosong."
            )

        for question in questions:

            if not isinstance(question, str) or not question.strip():
                raise ValueError(
                    f"Pertanyaan pada ID {item_id} tidak valid."
                )

            normalized = normalize_question(question)

            # Memeriksa pertanyaan duplikat
            if normalized in used_questions:
                raise ValueError(
                    f"Pertanyaan duplikat ditemukan: {question}"
                )

            used_questions.add(normalized)

        # Validasi jawaban
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError(
                f"Jawaban pada ID {item_id} tidak boleh kosong."
            )

    return data


# ==========================================
# FIND ANSWER
# ==========================================

def find_answer(question: str) -> str | None:
    """
    Mencari jawaban berdasarkan pertanyaan pengguna.

    Args:
        question (str): Pertanyaan dari pengguna.

    Returns:
        str: Jawaban jika pertanyaan ditemukan.
        None: Jika pertanyaan tidak ditemukan.
    """

    # Normalisasi pertanyaan pengguna
    normalized_question = normalize_question(question)

    # Jika pertanyaan kosong
    if not normalized_question:
        return None

    # Membaca knowledge base
    data = load_knowledge_base()

    # Mencocokkan pertanyaan
    for item in data:

        for stored_question in item["questions"]:

            normalized_stored = normalize_question(
                stored_question
            )

            if normalized_question == normalized_stored:
                return item["answer"]

    # Jika tidak ditemukan
    return None
