import os
import json
import hashlib
import requests
import zipfile
from pathlib import Path

# ===============================
# CONFIG
# ===============================
REPO = "USERNAME/ai_factory"   # GANTI
API_BASE = f"https://api.github.com/repos/{REPO}"
MODEL_DIR = Path("model/current")
MANIFEST_LOCAL = Path("model/manifest.json")

MODEL_DIR.mkdir(parents=True, exist_ok=True)

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
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


# ===============================
# MAIN LOGIC
# ===============================
def download_latest_model():
    print("[INFO] Mengecek model terbaru di GitHub...")

    # --- Ambil release terbaru ---
    resp = requests.get(f"{API_BASE}/releases/latest")
    resp.raise_for_status()
    release = resp.json()

    assets = {a["name"]: a for a in release["assets"]}

    if "manifest.json" not in assets:
        raise RuntimeError("manifest.json tidak ditemukan di release")

    # --- Download manifest ---
    manifest_tmp = Path("model/manifest_tmp.json")
    download(assets["manifest.json"]["browser_download_url"], manifest_tmp)

    manifest_remote = json.loads(manifest_tmp.read_text(encoding="utf-8"))

    remote_hash = manifest_remote["hash"]
    zip_name = manifest_remote["filename"]

    # --- Bandingkan dengan manifest lokal ---
    if MANIFEST_LOCAL.exists():
        local_manifest = json.loads(MANIFEST_LOCAL.read_text(encoding="utf-8"))
        if local_manifest.get("hash") == remote_hash:
            print("[OK] Model sudah versi terbaru, tidak perlu download")
            return

    print("[INFO] Model baru terdeteksi, download dimulai...")

    if zip_name not in assets:
        raise RuntimeError(f"{zip_name} tidak ditemukan di release")

    zip_path = Path("model") / zip_name
    download(assets[zip_name]["browser_download_url"], zip_path)

    # --- Verifikasi hash ---
    zip_hash = sha256(zip_path)
    if zip_hash != remote_hash:
        zip_path.unlink(missing_ok=True)
        raise RuntimeError("Hash ZIP tidak cocok! Download dibatalkan")

    print("[OK] Hash valid, ekstrak model...")

    # --- Bersihkan model lama ---
    if MODEL_DIR.exists():
        for p in MODEL_DIR.iterdir():
            if p.is_file():
                p.unlink()
            else:
                import shutil
                shutil.rmtree(p)

    # --- Extract ---
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(MODEL_DIR)

    # --- Simpan manifest ---
    MANIFEST_LOCAL.write_text(
        json.dumps(manifest_remote, indent=2),
        encoding="utf-8"
    )

    zip_path.unlink(missing_ok=True)

    print("[SUCCESS] Model siap digunakan")
    print("Version :", manifest_remote["version"])
    print("Hash    :", remote_hash)