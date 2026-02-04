from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ===============================
# PATH MODEL (AI_RUNTIME)
# ===============================
MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "current"


def load_model(device: str | None = None):
    """
    Load tokenizer & model dari model/current
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    if not MODEL_PATH.exists():
        raise RuntimeError("Model belum tersedia. Jalankan bootstrap terlebih dahulu.")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

    model.to(device)
    model.eval()

    return tokenizer, model