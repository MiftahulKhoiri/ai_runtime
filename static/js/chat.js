let lastQuestion = "";
let typingEl = null;

function addMessage(text, sender, meta = null) {
    const chatBox = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = "message " + sender;
    msg.innerText = text;

    // ===== CONFIDENCE BADGE =====
    if (meta && meta.confidence) {
        const badge = document.createElement("span");
        badge.className = "confidence " + meta.confidence;
        badge.innerText = meta.confidence.toUpperCase();
        msg.appendChild(badge);
    }

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msg;
}

function showTyping() {
    typingEl = addMessage("AI sedang mengetik...", "ai");
    typingEl.classList.add("typing");
}

function hideTyping() {
    if (typingEl) {
        typingEl.remove();
        typingEl = null;
    }
}

function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    lastQuestion = text;
    addMessage(text, "user");
    input.value = "";

    showTyping();

    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text })
    })
    .then(res => res.json())
    .then(data => {
        hideTyping();

        const aiMsg = addMessage(
            data.answer,
            "ai",
            { confidence: data.confidence }
        );

        // ===== TAMPILKAN AJARI AI HANYA JIKA BOLEH =====
        if (data.can_learn === true) {
            const learnBox = document.createElement("div");
            learnBox.className = "learn-box";

            const btn = document.createElement("button");
            btn.innerText = "Ajari AI";
            btn.onclick = () => teachAI(learnBox);

            learnBox.appendChild(btn);
            aiMsg.appendChild(learnBox);
        }
    })
    .catch(() => {
        hideTyping();
        addMessage("Terjadi kesalahan server.", "ai");
    });
}

function teachAI(container) {
    container.innerHTML = "";

    const textarea = document.createElement("textarea");
    textarea.placeholder = "Masukkan jawaban yang benar...";
    textarea.rows = 1;
    textarea.style.width = "100%";
    textarea.style.resize = "none";

    textarea.addEventListener("input", () => {
        textarea.style.height = "auto";
        textarea.style.height = textarea.scrollHeight + "px";
    });

    const btn = document.createElement("button");
    btn.innerText = "Simpan";

    btn.onclick = () => {
        const answer = textarea.value.trim();
        if (!answer) return;

        fetch("/learn", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: lastQuestion.toLowerCase(),
                answer: answer
            })
        })
        .then(res => res.json())
        .then(() => {
            addMessage("Terima kasih, saya sudah belajar 👍", "ai");
            container.remove();
        });
    };

    container.appendChild(textarea);
    container.appendChild(btn);
    textarea.focus();
}