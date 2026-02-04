from server.app import app
from core.bootstrap import bootstrap
import subprocess
from pathlib import Path
import socket
import signal
import sys

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
    bootstrap()

    ip = get_local_ip()
    print("=" * 48)
    print(" # SERVER AI SUDAH AKTIF #")
    print(" Bisa diakses melalui")
    print(f" : http://{ip}:5000")
    print("=" * 48)

    # 🚀 Jalankan Gunicorn
    proc = subprocess.Popen([
        str(GUNICORN),
        "app:app",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--timeout", "120"
    ])

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
