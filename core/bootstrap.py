import os
import sys
import subprocess
from pathlib import Path

from core.logger import get_logger
from core.model_downloader import download_latest_model
from core.update import SelfUpdater

log = get_logger("AI_RUNTIME_BOOTSTRAP")

# ===============================
# PATH
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
VENV_DIR = BASE_DIR / "venv"
REQ_FILE = BASE_DIR / "requirements.txt"

MODEL_DIR = BASE_DIR / "model" / "current"

# ===============================
# VIRTUAL ENV
# ===============================
def in_virtualenv() -> bool:
    return sys.prefix != sys.base_prefix


def create_venv():
    log.warning("Virtualenv belum ada, membuat venv...")
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    log.info("Virtualenv berhasil dibuat")


def restart_in_venv():
    python_bin = VENV_DIR / "bin" / "python"
    log.warning("Restarting aplikasi di dalam virtualenv...")
    os.execv(str(python_bin), [str(python_bin)] + sys.argv)


# ===============================
# REQUIREMENTS
# ===============================
def install_requirements():
    log.info("Memastikan dependency terinstall...")

    pip_bin = VENV_DIR / "bin" / "pip"
    subprocess.check_call([
        str(pip_bin),
        "install",
        "--upgrade",
        "-r",
        str(REQ_FILE),
    ])

    log.info("Dependency siap")


# ===============================
# MODEL VALIDATION
# ===============================
def validate_model() -> bool:
    if not MODEL_DIR.exists():
        return False

    required = [
        "config.json",
        "pytorch_model.bin",
        "tokenizer.json"
    ]

    for f in required:
        if not (MODEL_DIR / f).exists():
            log.error(f"File model hilang: {f}")
            return False

    return True


# ===============================
# BOOTSTRAP UTAMA
# ===============================
def bootstrap():
    # ===============================
    # 1. Pastikan venv
    # ===============================
    if not VENV_DIR.exists():
        create_venv()
        restart_in_venv()

    if not in_virtualenv():
        restart_in_venv()

    # ===============================
    # 2. Dependency
    # ===============================
    install_requirements()

    # ===============================
    # 3. Auto update (OPSIONAL)
    # ===============================
    updater = SelfUpdater(repo_dir=str(BASE_DIR))
    if updater.update_if_needed():
        log.warning("Restart setelah update...")
         restart_in_venv()

    # ===============================
    # 4. MODEL (PAKAI DOWNLOADER)
    # ===============================
    if not validate_model():
        log.warning("Model belum ada / tidak valid, sinkronisasi dengan ai_factory...")
        download_latest_model()
    else:
        log.info("Model valid, siap inference")