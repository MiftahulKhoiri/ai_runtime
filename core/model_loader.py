"""
model_loader.py
Loader model runtime (production-ready)

Fitur:
- Load dari model/current
- Logging jelas
- CPU-safe
- Siap reload model
"""

from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from core.logger import get_logger

log = get_logger("MODEL_LOADER")

# ===============================
# PATH
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "current"

# Cache global (runtime)
_TOKENIZER = None
_MODEL = None
_DEVICE = None


def load_model(force_reload: bool = False, device: str | None = None):
    """
    Load tokenizer & model dari model/current

    force_reload=True → paksa reload model (misal setelah update)
    """
    global _TOKENIZER, _MODEL, _DEVICE

    # Tentukan device
    if device:
        _DEVICE = device
    elif not _DEVICE:
        _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # Jika sudah load dan tidak force reload
    if _MODEL is not None and not force_reload:
        return _TOKENIZER, _MODEL, _DEVICE

    log.info("Memuat model runtime")

    if not MODEL_PATH.exists():
        raise RuntimeError("Folder model/current tidak ditemukan")

    # Guard isi folder
    if not any(MODEL_PATH.iterdir()):
        raise RuntimeError("Folder model/current kosong")

    # Load tokenizer & model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float32,
    )

    model.to(_DEVICE)
    model.eval()

    _TOKENIZER = tokenizer
    _MODEL = model

    log.info(f"Model berhasil dimuat di device: {_DEVICE}")

    return _TOKENIZER, _MODEL, _DEVICE


def unload_model():
    """
    Lepaskan model dari memory (opsional, advanced)
    """
    global _TOKENIZER, _MODEL

    if _MODEL is not None:
        del _MODEL
        del _TOKENIZER
        _MODEL = None
        _TOKENIZER = None
        torch.cuda.empty_cache()

        log.info("Model berhasil di-unload dari memory")