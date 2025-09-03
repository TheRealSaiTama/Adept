MODEL_CONFIG = {
    "gemini": {
        "url_template": "https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent",
        "models": {
            "default": "gemini-1.5-pro",
            "pro": "gemini-1.5-pro",
            "flash": "gemini-1.5-flash"
        }
    },
    "groq": {
        "url_template": "https://api.groq.com/openai/v1/chat/completions",
        "models": {
            "default": "llama-3.1-8b-instant",
            "llama3-8b": "llama-3.1-8b-instant",
            "llama3-70b": "llama-3.1-70b-versatile",
            "mixtral": "mixtral-8x7b-32768",
            "gemma": "gemma2-9b-it"
        }
    }
}
