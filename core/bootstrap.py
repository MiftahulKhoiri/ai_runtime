"""
bootstrap.py
Bootstrap resmi ai_runtime (production-ready)

Tugas:
- Pastikan virtualenv
- Install dependency
- Self update (opsional)
- Sinkronisasi model dari ai_factory
"""

import os
import sys
import subprocess
from pathlib import Path

from core.logger import get_logger
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
    log.warning("Restart aplikasi di dalam virtualenv...")
    os.execv(str(python_bin), [str(python_bin)] + sys.argv)


# ===============================
# REQUIREMENTS
# ===============================
def install_requirements():
    log.info("Memastikan dependency terinstall")

    pip_bin = VENV_DIR / "bin" / "pip"
    subprocess.check_call(
        [
            str(pip_bin),
            "install",
            "--upgrade",
            "-r",
            str(REQ_FILE),
        ]
    )

    log.info("Dependency siap")


# ===============================
# MODEL VALIDATION
# ===============================
def validate_model() -> bool:
    """
    Validasi minimum model HuggingFace
    """
    if not MODEL_DIR.exists():
        return False

    required_files = [
        "config.json",
        "pytorch_model.bin",
    ]

    for f in required_files:
        if not (MODEL_DIR / f).exists():
            log.error(f"File model hilang: {f}")
            return False

    return True


# ===============================
# BOOTSTRAP UTAMA
# ===============================
def bootstrap():
    log.info("=== BOOTSTRAP AI_RUNTIME DIMULAI ===")

    # 1️⃣ Pastikan virtualenv
    if not VENV_DIR.exists():
        create_venv()
        restart_in_venv()

    if not in_virtualenv():
        restart_in_venv()

    # 2️⃣ Dependency
    install_requirements()

    # 3️⃣ Self update (opsional)
    updater = SelfUpdater(repo_dir=str(BASE_DIR))
    if updater.update_if_needed():
        log.warning("Source code ter-update, restart runtime...")
        restart_in_venv()

    # 4️⃣ Model sync
    if not validate_model():
        log.warning("Model belum ada / tidak valid, sinkronisasi dengan ai_factory")
        updated = download_latest_model()
        if not updated:
            log.error("Model gagal disinkronisasi")
            raise RuntimeError("Runtime tidak memiliki model valid")
    else:
        log.info("Model valid, siap inference")

    log.info("=== BOOTSTRAP AI_RUNTIME SELESAI ===")