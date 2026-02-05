bootstrap()

"""
run_server.py
Entry point server ai_runtime (production-ready)

Tugas:
- Bootstrap runtime
- Menjalankan Gunicorn
- Handle shutdown dengan aman
"""

import subprocess
from pathlib import Path
import socket
import signal
import sys
import os

from core.bootstrap import bootstrap
from core.logger import get_logger

log = get_logger("AI_RUNTIME_SERVER")

# ===============================
# PATH
# ===============================
BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / "venv"
GUNICORN = VENV_DIR / "bin" / "gunicorn"


# ===============================
# UTIL
# ===============================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


# ===============================
# SERVER RUNNER
# ===============================
def run():
    log.info("=== MENJALANKAN AI RUNTIME SERVER ===")

    # 1️⃣ Bootstrap (venv, deps, model)
    bootstrap()

    if not GUNICORN.exists():
        log.error("Gunicorn tidak ditemukan di virtualenv")
        raise RuntimeError("Pastikan gunicorn terinstall di requirements.txt")

    ip = get_local_ip()
    log.info("🚀 SERVER AI SIAP")
    log.info(f"Akses: http://{ip}:5000")

    # 2️⃣ Jalankan Gunicorn
    cmd = [
        str(GUNICORN),
        "server.app:app",          # pastikan path benar
        "--bind", "0.0.0.0:5000",
        "--workers", "1",          # Raspberry Pi → 1 worker
        "--timeout", "120",
        "--log-level", "info",
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=str(BASE_DIR),
        env=os.environ.copy(),
    )

    # ===============================
    # SIGNAL HANDLER
    # ===============================
    def shutdown(signum, frame):
        log.warning(f"Menerima sinyal {signum}, menghentikan server...")
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            proc.wait()
        log.info("Server berhasil dihentikan dengan aman")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Tunggu Gunicorn
    proc.wait()


if __name__ == "__main__":
    run()