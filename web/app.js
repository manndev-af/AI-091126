// Tugas anggota 4: form chat, fetch POST /api/chat, dan render teks dengan textContent.
/* =====================================================================
   BAGIAN 1 — JAWABAN SEMENTARA (DUMMY)
   Hanya supaya UI bisa dicoba. Nanti fungsi ambilJawaban() diganti
   untuk memanggil backend tim (TF-IDF + LLM).

   Format jawaban yang dipakai UI:
   { jawaban: string, sumber: "knowledge_base" | "llm" | "tidak_ditemukan", skor: number }
   ===================================================================== */

const FAQ_DUMMY = [
  { kunci: "jadwal pengisian krs",
    jawaban: "Pengisian KRS semester genap dibuka tanggal 5–16 Januari 2027 melalui portal akademik. Jangan lupa konsultasi dengan dosen PA sebelum KRS disetujui." },
  { kunci: "dosen ai kecerdasan buatan",
    jawaban: "Mata kuliah Kecerdasan Buatan (AI) untuk angkatan 2025 diampu oleh Dr. Andi Pratama, M.Kom." },
  { kunci: "jadwal ai kecerdasan buatan",
    jawaban: "Kecerdasan Buatan: Selasa 10.00–12.30 di Ruang 3.2." },
  { kunci: "jadwal jaringan komputer jarkom",
    jawaban: "Jaringan Komputer kelas A: Senin 08.00–10.30 di Lab Jaringan.\nKelas B: Rabu 13.00–15.30 di Lab Jaringan." },
  { kunci: "dosen jaringan komputer jarkom",
    jawaban: "Jaringan Komputer diampu oleh Bapak Rizky Hidayat, M.Kom." },
  { kunci: "sks sistem operasi so",
    jawaban: "Sistem Operasi berbobot 3 SKS (2 SKS teori + 1 SKS praktikum)." },
  { kunci: "dosen sistem operasi so",
    jawaban: "Sistem Operasi diampu oleh Ibu Sari Wulandari, M.T." },
];

const STOPWORDS = new Set(["apa", "yang", "di", "ke", "dan", "untuk", "mata", "kuliah", "berapa",
  "kapan", "siapa", "dong", "ya", "itu", "ini", "adalah", "saya", "aku"]);

function token(teks) {
  return new Set((teks.toLowerCase().match(/[a-z0-9]+/g) || []).filter(k => !STOPWORDS.has(k)));
}

async function ambilJawaban(pertanyaan) {
  // Simulasi jeda server
  await new Promise(r => setTimeout(r, 600));

  const q = token(pertanyaan);
  let terbaik = null, skorTerbaik = 0;

  for (const item of FAQ_DUMMY) {
    const t = token(item.kunci);
    const irisan = [...q].filter(k => t.has(k)).length;
    const gabungan = new Set([...q, ...t]).size;
    const skor = gabungan ? irisan / gabungan : 0;
    if (skor > skorTerbaik) { terbaik = item; skorTerbaik = skor; }
  }

  if (terbaik && skorTerbaik >= 0.3) {
    return { jawaban: terbaik.jawaban, sumber: "knowledge_base", skor: +skorTerbaik.toFixed(3) };
  }
  return {
    jawaban: "Maaf, informasi tersebut belum tersedia di data layanan akademik. Silakan hubungi bagian akademik prodi untuk info lebih lanjut.",
    sumber: "tidak_ditemukan",
    skor: +skorTerbaik.toFixed(3),
  };

  /* NANTI, kalau backend tim sudah jadi, isi fungsi ini cukup diganti jadi:

  const res = await fetch("ALAMAT_BACKEND/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pesan: pertanyaan }),
  });
  if (!res.ok) throw new Error("Server error");
  return await res.json();
  */
}


/* =====================================================================
   BAGIAN 2 — LOGIKA TAMPILAN (tidak perlu diubah)
   ===================================================================== */

const chat = document.getElementById("chat");
const form = document.getElementById("form");
const input = document.getElementById("input");
const btnSend = document.getElementById("btn-send");
const btnReset = document.getElementById("btn-reset");
const welcomeHTML = document.getElementById("welcome").outerHTML;

const LABEL_SUMBER = {
  knowledge_base: "Knowledge Base",
  llm: "LLM",
  tidak_ditemukan: "Tidak ditemukan",
};

function jam() {
  return new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
}

function scrollBawah() {
  chat.scrollTop = chat.scrollHeight;
}

function tambahPesan(teks, peran, info = {}) {
  document.getElementById("welcome")?.remove();

  const msg = document.createElement("div");
  msg.className = `msg ${peran}` + (info.error ? " error" : "");

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = teks; // textContent supaya aman dari XSS
  msg.appendChild(bubble);

  const meta = document.createElement("div");
  meta.className = "meta";
  if (peran === "bot" && info.sumber) {
    const badge = document.createElement("span");
    badge.className = `badge ${info.sumber}`;
    badge.textContent = LABEL_SUMBER[info.sumber] || info.sumber;
    meta.appendChild(badge);
    if (info.sumber === "knowledge_base" && info.skor !== undefined) {
      const skor = document.createElement("span");
      skor.textContent = `skor ${info.skor}`;
      meta.appendChild(skor);
    }
  }
  const waktu = document.createElement("span");
  waktu.textContent = jam();
  meta.appendChild(waktu);
  msg.appendChild(meta);

  chat.appendChild(msg);
  scrollBawah();
}

function tampilkanMengetik() {
  const el = document.createElement("div");
  el.className = "msg bot typing";
  el.id = "typing";
  el.innerHTML = '<div class="bubble"><span></span><span></span><span></span></div>';
  chat.appendChild(el);
  scrollBawah();
}

async function kirim(teks) {
  teks = teks.trim();
  if (!teks) return;

  tambahPesan(teks, "user");
  input.value = "";
  aturTinggi();
  btnSend.disabled = true;
  tampilkanMengetik();

  try {
    const data = await ambilJawaban(teks);
    document.getElementById("typing")?.remove();
    tambahPesan(data.jawaban, "bot", { sumber: data.sumber, skor: data.skor });
  } catch (err) {
    document.getElementById("typing")?.remove();
    tambahPesan("Tidak dapat terhubung ke server. Coba lagi nanti.", "bot", { error: true });
  } finally {
    btnSend.disabled = false;
    input.focus();
  }
}

function aturTinggi() {
  input.style.height = "auto";
  input.style.height = input.scrollHeight + "px";
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  kirim(input.value);
});

// Enter = kirim, Shift+Enter = baris baru
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!btnSend.disabled) kirim(input.value);
  }
});
input.addEventListener("input", aturTinggi);

// Tombol pertanyaan cepat
chat.addEventListener("click", (e) => {
  if (e.target.classList.contains("chip")) kirim(e.target.textContent);
});

btnReset.addEventListener("click", () => {
  chat.innerHTML = welcomeHTML;
  input.focus();
});