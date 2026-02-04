from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "training"


def load_model(device="cpu"):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

    model.to(device)
    model.eval()
    return tokenizer, model