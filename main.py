"""Jalankan web chatbot lokal dengan python main.py."""

from backend.server import run


def main() -> None:
    try:
        run()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")


if __name__ == "__main__":
    main()
