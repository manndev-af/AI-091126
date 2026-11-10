# Chatbot Python: Knowledge Base + Fallback LLM

Workspace proyek chatbot sederhana untuk tim 5 orang. Chatbot mencari jawaban di knowledge base lokal terlebih dahulu. Jika tidak ditemukan, pertanyaan diteruskan ke LLM melalui API.

**Status:** web dan backend sudah terhubung ke knowledge base serta fallback LLM. Jalankan aplikasi melalui `main.py`; langkah lengkap tersedia pada bagian Cara menjalankan.

## Ruang lingkup

- Pengguna mengobrol melalui halaman web memakai HTML, CSS, dan JavaScript biasa.
- Backend Python menyajikan halaman web dan endpoint `POST /api/chat` dari origin yang sama.
- Knowledge base disimpan dalam JSON; isinya FAQ akademik UNP. Topik bisa diganti sesuai kebutuhan.
- Pencarian awal memakai normalisasi huruf kecil, penghapusan spasi di awal/akhir, dan pencocokan pertanyaan secara persis terhadap `questions`.
- LLM dipanggil hanya jika pencarian lokal tidak menghasilkan jawaban.
- Backend memakai standard library Python; klien LLM memakai `openai` dan konfigurasi `.env` dibaca oleh `python-dotenv`. Server awal untuk demo lokal di `127.0.0.1:8000`; deployment publik memerlukan server produksi dan pembatasan akses API.
- Riwayat percakapan cukup disimpan di tampilan selama halaman terbuka. Setiap request berisi satu pertanyaan, tanpa memori percakapan di LLM.

## Struktur folder

```text
chatbot-pemula/
├── main.py                 # Titik masuk server web
├── chatbot/
│   ├── __init__.py
│   ├── knowledge_base.py   # Membaca, memvalidasi, dan mencari FAQ
│   ├── llm.py              # Klien API LLM dan penanganan error
│   └── service.py          # Memilih jawaban lokal atau fallback LLM
├── backend/
│   ├── __init__.py
│   └── server.py           # HTTP server, file web, dan POST /api/chat
├── data/
│   └── knowledge_base.json # FAQ dan variasi pertanyaan
├── tests/
│   └── .gitkeep            # Tempat pengujian tim
├── web/
│   ├── index.html         # Struktur halaman chat
│   ├── style.css          # Tampilan responsif dan fokus keyboard
│   └── app.js             # Kirim pesan dan tampilkan respons API
├── .env                    # Konfigurasi lokal, tidak masuk Git
├── .env.example            # Contoh konfigurasi tanpa rahasia
├── .gitignore
└── README.md
```

## Alur jawaban

1. Pengguna memasukkan pertanyaan pada halaman web.
2. JavaScript mengirim JSON ke `POST /api/chat`; backend memvalidasi input lalu memanggil `service.answer()`.
3. Service mencari pertanyaan di knowledge base.
4. Jika ditemukan, service mengembalikan jawaban dengan sumber `knowledge_base` tanpa memanggil API.
5. Jika tidak ditemukan, service memanggil LLM dengan RAG: `knowledge_base.retrieve_context()` memilih maksimal tiga FAQ dari JSON berdasarkan kemiripan kata pada pertanyaan dan jawaban. LLM mengutamakan FAQ relevan dan mencantumkan ID FAQ yang digunakan. Pertanyaan umum di luar konteks boleh dijawab memakai pengetahuan LLM, termasuk ketika konteks kosong. Detail akademik khusus kampus, prodi, atau kelas tetap harus berdasarkan knowledge base; jika belum tersedia, LLM diarahkan menyatakan keterbatasan tersebut. Sumber respons tetap `llm`. Pencarian ini belum memakai embedding sehingga sinonim tanpa kata yang sama bisa tidak ditemukan.
6. Backend mengembalikan JSON; web menampilkan jawaban dan sumbernya. Jika API gagal, web menampilkan pesan gagal yang jelas dan mengaktifkan kembali tombol kirim. Jangan menampilkan jawaban palsu atau API key.

## Kontrak HTTP

Halaman dibuka melalui `http://127.0.0.1:8000/` setelah server dijalankan. Backend hanya menyajikan `/`, `/style.css`, dan `/app.js` dari folder `web/`; file `.env`, kode Python, dan folder `data/` tidak boleh dapat diakses melalui HTTP. Gunakan daftar rute statis yang diizinkan, jangan menyajikan seluruh workspace.

Request `POST /api/chat`, dengan `Content-Type: application/json`:

```json
{"question": "apa itu python?"}
```

Respons sukses `200`, dengan `Content-Type: application/json`:

```json
{"answer": "Python adalah bahasa pemrograman tingkat tinggi ...", "source": "knowledge_base"}
```

`source` bernilai `knowledge_base` atau `llm`. Respons gagal memakai bentuk `{"error": "Pesan yang aman untuk pengguna"}`:

| Status | Kondisi |
| --- | --- |
| `400` | JSON rusak, body bukan objek, atau `question` bukan string, kosong, atau lebih dari 2.000 karakter. |
| `404` | Rute tidak dikenal. |
| `405` | Metode HTTP tidak didukung untuk rute tersebut; sertakan header `Allow`. |
| `413` | Body request melebihi 16 KiB; periksa batas sebelum membaca body. |
| `415` | Content-Type request bukan `application/json`. |
| `500` | Knowledge base rusak/hilang atau konfigurasi server tidak valid. |
| `502` | API LLM gagal, timeout, atau respons provider tidak valid. |

API key hanya dibaca backend. JavaScript memanggil URL relatif `/api/chat`; browser tidak memanggil provider LLM langsung. Tampilkan teks pengguna dan jawaban memakai `textContent`, bukan `innerHTML`.

## Format knowledge base

`data/knowledge_base.json` berisi daftar objek:

```json
[
  {
    "id": "python-definition",
    "questions": ["apa itu python?", "apa itu python"],
    "answer": "Python adalah bahasa pemrograman tingkat tinggi untuk berbagai kebutuhan."
  }
]
```

Aturan data: `id` unik dan tidak kosong; `questions` berupa daftar string tidak kosong; `answer` berupa string tidak kosong. Hindari pertanyaan yang sama setelah normalisasi pada dua entri berbeda. File rusak atau format tidak valid harus dilaporkan sebagai error konfigurasi, bukan dianggap sebagai pertanyaan yang tidak ditemukan.

## Kontrak antarmodul

Kontrak fungsi yang digunakan oleh aplikasi:

| Modul | Fungsi | Hasil dan perilaku |
| --- | --- | --- |
| `knowledge_base.py` | `find_answer(question: str) -> str \| None` | Membaca `data/knowledge_base.json` relatif terhadap lokasi proyek; mengembalikan jawaban atau `None` jika tidak cocok. Data tidak valid menghasilkan `ValueError`; kegagalan membaca file menghasilkan `OSError`. |
| `llm.py` | `ask_llm(question: str) -> str` | Membaca konfigurasi environment, memanggil API dengan timeout, dan mengembalikan teks jawaban tidak kosong. Konfigurasi tidak valid menghasilkan `ValueError`; kegagalan API menghasilkan `RuntimeError` dengan pesan aman. |
| `service.py` | `answer(question: str) -> dict[str, str]` | Menolak pertanyaan kosong atau lebih dari 2.000 karakter dengan `ValueError`; mengembalikan `{"answer": "...", "source": "knowledge_base"}` atau `{"answer": "...", "source": "llm"}`. Error modul diteruskan ke backend. |
| `backend/server.py` | `run() -> None` | Menjalankan server lokal, menyajikan file web yang diizinkan, memvalidasi request sebelum memanggil service, dan memetakan error ke respons HTTP sesuai kontrak. |
| `main.py` | `main() -> None` | Memanggil `backend.server.run()` dan menangani Ctrl+C untuk menghentikan server. |
| `web/app.js` | Form chat dan request HTTP | Mengirim `question`, membaca respons sukses/gagal, menampilkan sumber, mengatur indikator menunggu, serta menangani jaringan gagal. |

## Pembagian tugas 5 orang

Ganti label anggota dengan nama tim. Setiap anggota menyertakan pengujian untuk modul miliknya; anggota 5 memimpin pengujian integrasi.

| Anggota | Fokus | File utama | Kriteria selesai |
| --- | --- | --- | --- |
| 1 | Data dan pencarian knowledge base | `data/knowledge_base.json`, `chatbot/knowledge_base.py`, `tests/test_knowledge_base.py` | Minimal 15 FAQ terverifikasi, variasi pertanyaan, validasi data, pencocokan normalisasi, dan hasil `None` ketika tidak ditemukan. |
| 2 | Integrasi LLM | `chatbot/llm.py`, `tests/test_llm.py`, `.env.example` | Sepakati provider dan format API; kirim pertanyaan, baca respons, gunakan timeout, tangani key kosong, HTTP error, jaringan gagal, serta respons tidak valid. Pengujian memakai mock tanpa biaya API. |
| 3 | Backend dan alur chatbot | `main.py`, `backend/`, `chatbot/service.py`, `tests/test_service.py`, `tests/test_server.py` | Jalankan server, sajikan web, implementasikan kontrak HTTP, hubungkan knowledge base dan LLM, serta pastikan fallback hanya saat hasil lokal `None`. |
| 4 | Antarmuka web | `web/index.html`, `web/style.css`, `web/app.js` | Form chat berlabel, riwayat pesan, sumber jawaban, indikator menunggu, tombol kirim, dan pesan error. Responsif, bisa diakses dengan keyboard, dan teks dirender aman. |
| 5 | Integrasi, pengujian, dokumentasi | `tests/test_integration.py`, `README.md`, `.gitignore` | Satukan modul, jalankan skenario penerimaan, dokumentasikan konfigurasi provider dan cara menjalankan versi akhir. |

Urutan kerja:

1. Semua anggota menyepakati kontrak fungsi dan provider API. Anggota 2 mendokumentasikan bentuk URL, request, dan response provider terpilih.
2. Anggota 1, 2, dan 4 mengerjakan modul masing-masing. Anggota 3 dapat memakai mock sampai modul tersedia; anggota 5 menyiapkan skenario integrasi.
3. Gabungkan data dan klien API, lalu service dan backend, lalu web. Setiap perubahan melewati review minimal satu anggota lain.
4. Anggota 5 menjalankan pengujian integrasi; pemilik modul memperbaiki kegagalan di modulnya.

Branch yang disarankan: `feat/knowledge-base`, `feat/llm`, `feat/backend`, `feat/web`, dan `test/integration`. Hindari perubahan file anggota lain tanpa koordinasi.

## Cara menjalankan

Gunakan Python 3.10 atau lebih baru. Jalankan perintah berikut melalui PowerShell dari folder proyek yang berisi `main.py` dan `requirement.txt`.

1. Buat virtual environment dan instal dependensi:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirement.txt
   ```

   Dependensi proyek: `openai` dan `python-dotenv`. Perintah memakai Python virtual environment langsung sehingga tidak perlu aktivasi.

2. Buat konfigurasi lokal jika `.env` belum ada:

   ```powershell
   if (-not (Test-Path .env)) { Copy-Item .env.example .env }
   ```

   Edit file `.env` dan ganti nilai contoh berikut dengan konfigurasi provider:

   ```dotenv
   API_AI_BASE_URL=https://alamat-provider.example/v1
   API_AI_KEY=isi-api-key-lokal
   API_AI_MODEL=isi-model-provider
   ```

   URL di atas hanya placeholder. Gunakan base URL, API key, dan nama model dari provider yang mendukung API Chat Completions kompatibel OpenAI. `API_AI_BASE_URL` adalah base URL, bukan URL lengkap `/chat/completions`.

   `chatbot/llm.py` membaca `.env` otomatis. Environment variable yang sudah disetel pada terminal memiliki prioritas atas nilai `.env`. Jangan commit file `.env` atau membagikan API key.

   Untuk mencoba knowledge base tanpa API LLM, kosongkan ketiga nilai konfigurasi tersebut. Pertanyaan lokal tetap dijawab; pertanyaan yang tidak ditemukan menampilkan error konfigurasi LLM.

3. Jalankan server:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

   Terminal menampilkan alamat `http://127.0.0.1:8000/`. Biarkan terminal tetap terbuka selama memakai chatbot.

4. Buka [http://127.0.0.1:8000/](http://127.0.0.1:8000/) di browser. Halaman harus dibuka melalui server agar request `/api/chat` berfungsi.

   Coba pertanyaan `Apa itu UNP?` atau `Siapa dosen AI?`. Jawaban lokal menampilkan sumber `Knowledge Base`. Pertanyaan yang tidak cocok diteruskan ke LLM jika konfigurasi tersedia.

5. Tekan **Ctrl+C** di terminal untuk menghentikan server. Setelah mengubah `.env` atau kode Python, hentikan lalu jalankan kembali server.

## Menjalankan pengujian

Dari folder proyek, jalankan di terminal lain:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s . -p "test_*.py" -v
```

Tes tersedia pada `test_knowledge_base.py`, `test_service.py`, `test_server.py`, dan `test_llm.py`. Pengujian fallback LLM dan konteks RAG memakai mock sehingga tidak mengirim request ke provider. Pengujian API asli dilakukan melalui web dengan konfigurasi provider yang valid.

## Kendala umum

| Kendala | Langkah perbaikan |
| --- | --- |
| `python` tidak dikenali | Instal Python 3.10 atau lebih baru dan aktifkan opsi Add Python to PATH. Buka ulang terminal. |
| `ModuleNotFoundError` untuk `openai` atau `dotenv` | Instal ulang dengan `.\.venv\Scripts\python.exe -m pip install -r requirement.txt`, lalu jalankan server memakai Python yang sama. |
| Browser gagal terhubung | Pastikan server masih berjalan dan buka `http://127.0.0.1:8000/`. |
| Port 8000 sudah dipakai | Hentikan proses server lama sebelum menjalankan server baru. |
| Knowledge base atau konfigurasi LLM tidak valid | Pastikan `data/knowledge_base.json` tersedia dan formatnya valid; periksa tiga nilai konfigurasi LLM pada `.env`. |
| Layanan AI gagal merespons | Periksa koneksi internet, base URL provider, API key, nama model, serta kuota provider. |

## Skenario penerimaan

- Pertanyaan yang tersedia mengembalikan jawaban lokal dengan sumber `knowledge_base`; klien LLM tidak dipanggil.
- Variasi kapital dan spasi di awal/akhir tetap cocok.
- Pertanyaan di luar data memanggil LLM sekali dan mengembalikan sumber `llm`.
- Input kosong ditolak tanpa memanggil API.
- Data JSON rusak atau hilang menampilkan error lokal tanpa fallback ke API.
- Request JSON rusak, tipe input salah, pertanyaan terlalu panjang, dan body terlalu besar ditolak sesuai kontrak HTTP tanpa memanggil LLM.
- API key hilang, timeout, HTTP error, dan respons kosong menampilkan pesan aman; web tetap dapat mengirim pertanyaan berikutnya.
- Halaman chat menampilkan pesan pengguna, jawaban, sumber, serta status menunggu; tombol kirim aktif kembali setelah sukses maupun gagal.
- Teks seperti `<script>alert(1)</script>` tampil sebagai teks, tidak dieksekusi.
- `.env` dan file di luar daftar rute statis tidak dapat diambil lewat HTTP.
- Form dapat digunakan lewat keyboard, memiliki label input dan area status `aria-live`, serta tetap terbaca pada layar ponsel.
- Ctrl+C menghentikan server tanpa traceback.

Target awal selesai ketika seluruh skenario lolos, pengujian otomatis tersedia, dan README sudah memuat konfigurasi provider yang dipilih.
