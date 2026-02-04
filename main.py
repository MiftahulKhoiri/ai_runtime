import subprocess
from pathlib import Path
import socket
import signal
import sys

from core.bootstrap import bootstrap

# ===============================
# PATH
# ===============================
BASE_DIR = Path(__file__).resolve().parent
GUNICORN = BASE_DIR / "venv" / "bin" / "gunicorn"


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


def run():
    # ===============================
    # 1. BOOTSTRAP (venv, deps, model)
    # ===============================
    bootstrap()

    ip = get_local_ip()
    print("=" * 48)
    print(" 🚀 SERVER AI SUDAH AKTIF")
    print(" Bisa diakses melalui:")
    print(f" http://{ip}:5000")
    print("=" * 48)

    # ===============================
    # 2. JALANKAN GUNICORN
    # ===============================
    proc = subprocess.Popen(
        [
            str(GUNICORN),
            "server.app:app",   # 🔥 PATH YANG BENAR
            "--bind", "0.0.0.0:5000",
            "--workers", "1",   # Raspberry Pi → 1 worker
            "--timeout", "120",
            "--log-level", "info",
        ],
        cwd=str(BASE_DIR),
    )

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Menghentikan server AI...")
        proc.send_signal(signal.SIGINT)
        proc.wait()
        print("✅ Server berhasil dihentikan dengan aman.")
        sys.exit(0)


if __name__ == "__main__":
    run()