"""
server/app.py
Flask app ai_runtime (production-ready)

Catatan:
- Tidak ada bootstrap di import time
- Model di-load lazy & reloadable
- Aman untuk Gunicorn
"""

import time
from flask import Flask, request, jsonify
from core.logger import get_logger
from core.model_loader import load_model
from core.model_downloader import download_latest_model
from core.chatbot import ChatBot

log = get_logger("AI_SERVER")

app = Flask(__name__)

# ===============================
# RUNTIME STATE (GLOBAL TERKONTROL)
# ===============================
_tokenizer = None
_model = None
_device = None
_bot: ChatBot | None = None


def get_bot() -> ChatBot:
    """
    Lazy load chatbot (aman untuk Gunicorn)
    """
    global _tokenizer, _model, _device, _bot

    if _bot is None:
        log.info("Memuat model & chatbot runtime")
        _tokenizer, _model, _device = load_model()
        _bot = ChatBot(_tokenizer, _model, device=_device)

    return _bot


# ===============================
# ROUTES
# ===============================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "ai_runtime",
    })


@app.route("/chat", methods=["POST"])
def chat():
    start = time.time()

    if not request.is_json:
        return jsonify({"error": "Request harus JSON"}), 400

    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Field 'text' kosong"}), 400

    try:
        bot = get_bot()
        reply = bot.reply(text)
    except Exception as e:
        log.exception("Error inference")
        return jsonify({"error": "Gagal memproses input"}), 500

    latency = round(time.time() - start, 3)

    return jsonify({
        "reply": reply,
        "latency": latency,
    })


@app.route("/reset", methods=["POST"])
def reset():
    bot = get_bot()
    bot.reset()
    return jsonify({"status": "memory reset"})


@app.route("/info", methods=["GET"])
def info():
    bot = get_bot()
    model = bot.model

    return jsonify({
        "model_class": model.__class__.__name__,
        "device": str(next(model.parameters()).device),
    })


@app.route("/reload", methods=["POST"])
def reload_model():
    """
    Paksa cek & reload model terbaru dari ai_factory
    """
    global _bot

    updated = download_latest_model()
    if updated:
        load_model(force_reload=True)
        _bot = None  # force recreate chatbot
        return jsonify({"status": "model updated & reloaded"})

    return jsonify({"status": "model already up-to-date"})


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "AI Runtime Server",
        "endpoints": [
            "/health",
            "/chat",
            "/reset",
            "/info",
            "/reload",
        ],
    })