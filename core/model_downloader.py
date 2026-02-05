"""
model_downloader.py
Downloader model runtime (sinkron dengan ai_factory)

Fitur:
- Ambil model dari GitHub Release
- Verifikasi hash (SHA256)
- Atomic update (aman jika gagal)
- Logging konsisten
"""

import json
import hashlib
import requests
import zipfile
import shutil
from pathlib import Path
from core.logger import get_logger

log = get_logger("MODEL_DOWNLOADER")

# ===============================
# PATH & CONFIG
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent

REPO = "MiftahulKhoiri/ai_factory"   # ⬅️ pastikan benar
API_BASE = f"https://api.github.com/repos/{REPO}"

MODEL_ROOT = BASE_DIR / "model"
MODEL_CURRENT = MODEL_ROOT / "current"
MODEL_TMP = MODEL_ROOT / "_tmp"
MANIFEST_LOCAL = MODEL_ROOT / "manifest.json"

MODEL_ROOT.mkdir(exist_ok=True)
MODEL_CURRENT.mkdir(parents=True, exist_ok=True)


# ===============================
# UTIL
# ===============================
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path):
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


# ===============================
# MAIN ENGINE
# ===============================
def download_latest_model():
    log.info("Mengecek model terbaru di GitHub Release")

    # 1️⃣ Ambil release terbaru
    resp = requests.get(
        f"{API_BASE}/releases/latest",
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )
    resp.raise_for_status()
    release = resp.json()

    assets = {a["name"]: a for a in release.get("assets", [])}

    if "manifest.json" not in assets:
        raise RuntimeError("manifest.json tidak ditemukan di GitHub Release")

    # 2️⃣ Download manifest
    manifest_tmp = MODEL_ROOT / "manifest_tmp.json"
    download(assets["manifest.json"]["browser_download_url"], manifest_tmp)

    manifest_remote = json.loads(manifest_tmp.read_text(encoding="utf-8"))
    remote_hash = manifest_remote["hash"]
    zip_name = manifest_remote["filename"]

    # 3️⃣ Bandingkan dengan manifest lokal
    if MANIFEST_LOCAL.exists():
        local_manifest = json.loads(MANIFEST_LOCAL.read_text(encoding="utf-8"))
        if local_manifest.get("hash") == remote_hash:
            log.info("Model sudah versi terbaru, tidak perlu update")
            manifest_tmp.unlink(missing_ok=True)
            return False

    log.info("Model baru terdeteksi, download dimulai")

    if zip_name not in assets:
        raise RuntimeError(f"{zip_name} tidak ditemukan di release")

    zip_path = MODEL_ROOT / zip_name
    download(assets[zip_name]["browser_download_url"], zip_path)

    # 4️⃣ Verifikasi hash ZIP
    zip_hash = sha256(zip_path)
    if zip_hash != remote_hash:
        zip_path.unlink(missing_ok=True)
        raise RuntimeError("Hash ZIP tidak cocok, update dibatalkan")

    log.info("Hash valid, ekstrak model")

    # 5️⃣ Extract ke folder sementara (ATOMIC)
    if MODEL_TMP.exists():
        shutil.rmtree(MODEL_TMP)
    MODEL_TMP.mkdir(parents=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(MODEL_TMP)

    # 6️⃣ Swap model (atomic replace)
    if MODEL_CURRENT.exists():
        shutil.rmtree(MODEL_CURRENT)
    MODEL_TMP.rename(MODEL_CURRENT)

    # 7️⃣ Simpan manifest
    MANIFEST_LOCAL.write_text(
        json.dumps(manifest_remote, indent=2),
        encoding="utf-8",
    )

    # 8️⃣ Cleanup
    zip_path.unlink(missing_ok=True)
    manifest_tmp.unlink(missing_ok=True)

    log.info("Model berhasil diperbarui")
    log.info(f"Version : {manifest_remote.get('version')}")
    log.info(f"Hash    : {remote_hash}")

    return True