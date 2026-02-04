import torch


class ChatBot:
    def __init__(
        self,
        tokenizer,
        model,
        max_history_tokens: int = 512,
        device: str | None = None,
    ):
        self.tokenizer = tokenizer
        self.model = model

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_history_tokens = max_history_tokens

        self.history = ""

    # ===============================
    # INTERNAL
    # ===============================
    def _trim_history(self):
        if not self.history:
            return

        tokens = self.tokenizer.encode(
            self.history,
            add_special_tokens=False
        )

        if len(tokens) <= self.max_history_tokens:
            return

        tokens = tokens[-self.max_history_tokens :]
        self.history = self.tokenizer.decode(
            tokens,
            skip_special_tokens=True
        )

    def _build_prompt(self, user_input: str) -> str:
        self._trim_history()
        return f"{self.history}User: {user_input}\nAI:"

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
            skip_special_tokens=True
        )

        ai_response = decoded.rsplit("AI:", 1)[-1].strip()

        self.history += f"User: {user_input}\nAI: {ai_response}\n"
        return ai_response

    def reset(self):
        self.history = ""