"""
chatbot.py
Runtime chatbot engine (production-ready)

Fitur:
- Prompt konsisten dengan dataset training
- History terkontrol & token-aware
- Aman untuk inference jangka panjang
"""

import torch
from core.logger import get_logger

log = get_logger("CHATBOT")


class ChatBot:
    def __init__(
        self,
        tokenizer,
        model,
        instruction: str = "Instruksi: Jawablah dengan bahasa Indonesia yang jelas, singkat, dan benar.",
        max_history_tokens: int = 512,
        device: str | None = None,
    ):
        self.tokenizer = tokenizer
        self.model = model
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.instruction = instruction
        self.max_history_tokens = max_history_tokens

        # history sebagai list of dict
        self.history: list[dict[str, str]] = []

        log.info("ChatBot siap digunakan")

    # ===============================
    # INTERNAL
    # ===============================
    def _build_prompt(self, user_input: str) -> str:
        """
        Bangun prompt konsisten dengan format training
        """
        parts = [self.instruction]

        for h in self.history:
            parts.append(f"User: {h['user']}")
            parts.append(f"AI: {h['ai']}")

        parts.append(f"User: {user_input}")
        parts.append("AI:")

        prompt = "\n".join(parts)

        # Trim token jika terlalu panjang
        tokens = self.tokenizer.encode(
            prompt,
            add_special_tokens=False,
        )

        if len(tokens) > self.max_history_tokens:
            tokens = tokens[-self.max_history_tokens :]
            prompt = self.tokenizer.decode(
                tokens,
                skip_special_tokens=True,
            )

        return prompt

    # ===============================
    # PUBLIC API
    # ===============================
    def reply(
        self,
        user_input: str,
        max_new_tokens: int = 80,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        if not user_input.strip():
            return "Silakan masukkan pertanyaan."

        prompt = self._build_prompt(user_input)

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            add_special_tokens=False,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        decoded = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        )

        ai_response = decoded.rsplit("AI:", 1)[-1].strip()

        # Simpan ke history
        self.history.append(
            {
                "user": user_input,
                "ai": ai_response,
            }
        )

        return ai_response

    def reset(self):
        """
        Reset percakapan
        """
        self.history.clear()
        log.info("History chatbot direset")