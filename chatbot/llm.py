
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_AI_KEY")
BASE_URL = os.getenv("API_AI_BASE_URL")
MODEL = os.getenv("API_AI_MODEL")


client = None

if API_KEY and BASE_URL and MODEL:
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )


def ask_llm(question: str) -> str:
    if client is None:
        raise ValueError("Konfigurasi LLM belum lengkap.")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            timeout=30
        )

        answer = response.choices[0].message.content
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("AI tidak memberikan jawaban.")
        return answer.strip()

    except Exception:
        raise RuntimeError("Maaf, layanan AI sedang tidak tersedia.") from None
