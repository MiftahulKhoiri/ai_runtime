from flask import Flask, request, jsonify
import time
from flask import render_template_string

from core.bootstrap import bootstrap
from core.model_loader import load_model
from core.chatbot import ChatBot
from core.logger import get_logger

log = get_logger("AI_SERVER")

# ===============================
# BOOTSTRAP SEKALI SAJA
# ===============================
bootstrap()

tokenizer, model = load_model()
bot = ChatBot(tokenizer, model)

app = Flask(__name__)


# ===============================
# ROUTES
# ===============================

@app.route("/health", methods=["GET"])
def health():
    """
    Cek apakah server hidup
    """
    return jsonify({
        "status": "ok",
        "service": "ai_runtime",
    })


@app.route("/chat", methods=["POST"])
def chat():
    """
    Input:
    {
        "text": "apa itu AI"
    }
    """
    start = time.time()

    if not request.is_json:
        return jsonify({"error": "Request harus JSON"}), 400

    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Field 'text' kosong"}), 400

    try:
        reply = bot.reply(text)
    except Exception as e:
        log.error(f"Error inference: {e}")
        return jsonify({"error": "Gagal memproses input"}), 500

    latency = round(time.time() - start, 3)

    return jsonify({
        "reply": reply,
        "latency": latency
    })


@app.route("/reset", methods=["POST"])
def reset():
    """
    Reset memori percakapan
    """
    bot.reset()
    return jsonify({"status": "memory reset"})


# ===============================
# OPTIONAL: INFO MODEL
# ===============================
@app.route("/info", methods=["GET"])
def info():
    return jsonify({
        "model": model.__class__.__name__,
        "device": str(next(model.parameters()).device),
    })

@app.route("/", methods=["GET"])
def index():
    return render_template_string(index.html)

