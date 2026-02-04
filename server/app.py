from flask import Flask, request, jsonify
from core.bootstrap import bootstrap
from core.model_loader import load_model
from core.chatbot import ChatBot

bootstrap()
tokenizer, model = load_model()
bot = ChatBot(tokenizer, model)

app = Flask(__name__)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    text = data.get("text", "")
    reply = bot.reply(text)
    return jsonify({"reply": reply})


@app.route("/reset", methods=["POST"])
def reset():
    bot.reset()
    return jsonify({"status": "reset"})

