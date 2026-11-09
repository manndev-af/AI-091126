async function ambilJawaban(pertanyaan) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: pertanyaan }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Server gagal memproses pertanyaan.");
  if (typeof data.answer !== "string" || typeof data.source !== "string") {
    throw new Error("Respons server tidak valid.");
  }
  return { jawaban: data.answer, sumber: data.source };
}

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
  if (!teks || btnSend.disabled) return;

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
    tambahPesan(err instanceof TypeError ? "Tidak dapat terhubung ke server. Jalankan python main.py dan buka http://127.0.0.1:8000/." : err.message, "bot", { error: true });
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