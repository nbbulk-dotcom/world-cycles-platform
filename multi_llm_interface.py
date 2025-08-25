import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import requests

# Replace with your actual API Keys, endpoints and adjust model IDs per provider docs
API_KEYS = {
    "Perplexity": "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",
    "Manus": "https://manus.im/share/zWdxQuMauDzNwScT6Ax51G?replay=1Y",
    "REnder": "rnd_WQZXNGq8xtUU38yyxRWYcuZdCCsE",
    "Copilot": "YOUR_COPILOT_API_KEY",
    "GROK": "YOUR_GROK_API_KEY",
    "DEVIN": "YOUR_DEVIN_API_KEY",
}

ENDPOINTS = {
    "Perplexity": "https://api.perplexity.ai/v1/chat/completions",
    "Manus": "https://api.manusai.io/v1/chat/completions",
    "MiniMax": "https://api.minimax.chat/v1/completions",
    "Copilot": "https://api.copilot.microsoft.com/v1/chat/completions",
    "GROK": "https://api.xai.grok/v1/chat/completions",
    "DEVIN": "https://api.devin.ai/v1/chat/completions",
}

def send_prompt(model_name, prompt):
    url = ENDPOINTS[model_name]
    headers = {"Authorization": f"Bearer {API_KEYS[model_name]}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,  # Some APIs require a specific model string, adjust if needed
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 512
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()
        # Adjust this line depending on your model's API response format
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not text:
            text = str(data)
        return text
    except Exception as e:
        return f"ERROR: {e}"

class MultiAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-LLM Desktop Research Interface")
        self.geometry("1200x700")
        self._create_widgets()

    def _create_widgets(self):
        # Prompt Entry Section
        prompt_label = tk.Label(self, text="Enter your prompt:")
        prompt_label.pack(pady=(8, 0), anchor="w")

        self.prompt_text = tk.Text(self, height=4, font=("Arial", 14))
        self.prompt_text.pack(fill="x", padx=10, pady=(0, 10))

        submit_btn = tk.Button(self, text="Submit to All Models", command=self._submit_prompt)
        submit_btn.pack(pady=(0, 12))

        # Results Section
        self.notebook = ttk.Notebook(self)
        self.textboxes = {}
        for model in API_KEYS:
            frame = tk.Frame(self.notebook)
            txt = scrolledtext.ScrolledText(frame, wrap="word", font=("Consolas", 11))
            txt.pack(expand=True, fill="both", padx=5, pady=5)
            self.textboxes[model] = txt
            self.notebook.add(frame, text=model)
        self.notebook.pack(expand=True, fill="both")

    def _submit_prompt(self):
        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showwarning("No Prompt", "Please enter a prompt before submitting.")
            return
        for txt in self.textboxes.values():
            txt.delete("1.0", "end")
            txt.insert("end", "Waiting for response...")

        # Run API calls in new threads for responsiveness
        for model in API_KEYS:
            threading.Thread(target=self._query_model, args=(model, prompt)).start()

    def _query_model(self, model, prompt):
        result = send_prompt(model, prompt)
        self.textboxes[model].delete("1.0", "end")
        self.textboxes[model].insert("end", result)

if __name__ == "__main__":
    app = MultiAIApp()
    app.mainloop()
