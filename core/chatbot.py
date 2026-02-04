class ChatBot:
    def __init__(self, tokenizer, model, device="cpu"):
        self.tokenizer = tokenizer
        self.model = model
        self.device = device
        self.history = ""

    def reply(self, text: str):
        prompt = f"{self.history}User: {text}\nAI:"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        output = self.model.generate(
            **inputs,
            max_new_tokens=80,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
        answer = decoded.rsplit("AI:", 1)[-1].strip()

        self.history += f"User: {text}\nAI: {answer}\n"
        return answer

    def reset(self):
        self.history = ""