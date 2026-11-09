
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_AI_KEY")
BASE_URL = os.getenv("API_AI_BASE_URL")
MODEL = os.getenv("API_AI_MODEL")

print(BASE_URL, API_KEY, MODEL)

client = None

if API_KEY and BASE_URL and MODEL:
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )


def ask_llm(question: str) -> str:
    if client is None:
        return "Konfigurasi LLM belum lengkap."

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

        return response.choices[0].message.content or "AI tidak memberikan jawaban."

    except Exception as e:
        print(f"LLM Error: {e}")
        return "Maaf, layanan AI sedang tidak tersedia."
