# 🧠 ai_runtime

ai_runtime adalah runtime server AI untuk menjalankan chatbot berbasis Transformer.
Repo ini hanya digunakan untuk inference (menjawab) dan TIDAK melakukan training atau pengolahan data.

Model AI diunduh otomatis dari repo ai_factory, diverifikasi, lalu digunakan oleh server.

## 🎯 Fungsi Utama

- Menjalankan server AI (Flask + Gunicorn)
- Download model terbaru dari ai_factory
- Verifikasi model (struktur & hash)
- Load model untuk inference
- Menyediakan API chatbot
- Menolak start server jika model tidak valid

## 🧩 Arsitektur

ai_factory (training & export)
        ↓
   model.zip + manifest
        ↓
ai_runtime (download & inference)

## 📁 Struktur Folder

ai_runtime/
├── core/
│   ├── bootstrap.py
│   ├── model_downloader.py
│   ├── model_loader.py
│   └── chatbot.py
│
├── server/
│   └── app.py
│
├── model/
│   ├── current/
│   ├── cache/
│   └── rollback/
│
├── requirements.txt
├── main.py
└── README.md

## 📦 Folder model/

Saat pertama clone repo:

model/
├── current/.gitkeep
├── cache/.gitkeep
└── rollback/.gitkeep

File model TIDAK di-commit ke Git.
Model akan diisi otomatis saat runtime dijalankan.

## 🚫 .gitignore

model/current/*
model/cache/*
model/rollback/*

## ⚙️ Cara Menjalankan

git clone https://github.com/USERNAME/ai_runtime.git
cd ai_runtime
python main.py

Langkah ini akan:
- Membuat virtualenv otomatis
- Menginstall dependency
- Download & verifikasi model
- Menjalankan server AI

## 🌐 API Endpoint

POST /chat
Request:
{
  "text": "Apa itu Artificial Intelligence?"
}

Response:
{
  "reply": "Artificial Intelligence adalah..."
}

POST /reset
Response:
{
  "status": "reset"
}

GET /health
Response:
{
  "status": "ok",
  "model_loaded": true
}

## 🛡️ Keamanan

Server TIDAK akan start jika:
- Model belum ada
- Download gagal
- Struktur model tidak valid
- Tokenizer atau model gagal load


## 🧠 Filosofi Desain

- Factory vs Runtime separation
- Immutable model artifact
- Fail-fast startup
- Siap production & deployment ringan

## 📌 Repo Terkait

- ai_factory → training & export model
- ai_runtime → inference & API server

