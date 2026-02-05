let typingEl = null;

// ===============================
// UI UTIL
// ===============================
function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = "message " + sender;
    msg.innerText = text;

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

// ===============================
// CHAT
// ===============================
async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    showTyping();

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await res.json();
        hideTyping();

        if (!res.ok || data.error) {
            addMessage(data.error || "Terjadi kesalahan.", "ai");
            return;
        }

        addMessage(data.reply, "ai");

    } catch (e) {
        hideTyping();
        addMessage("Gagal terhubung ke server.", "ai");
    }
}

// ===============================
// UX: ENTER TO SEND
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});