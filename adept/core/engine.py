import httpx
import os
from dotenv import load_dotenv
from adept.core.config import MODEL_CONFIG

load_dotenv()

def execute_task(task: str, provider: str, model: str, conversation_history: list = None) -> tuple[str, list]:
    """Core engine that handles conversations for multiple providers."""
    
    if provider not in MODEL_CONFIG:
        raise ValueError(f"Provider '{provider}' is not supported.")

    config = MODEL_CONFIG[provider]
    model_name = config["models"].get(model, config["models"]["default"])
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    if not api_key:
        raise ValueError(f"{provider.upper()}_API_KEY not found in .env")

    # --- Provider-Specific Logic ---
    if provider == "gemini":
        url = config["url_template"].format(model_name=model_name)
        headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        params = None
        
        # The history from the UI is already in Gemini's format.
        current_conversation = conversation_history if conversation_history else []
        current_conversation.append({"role": "user", "parts": [{"text": task}]})
        payload = {"contents": current_conversation}

    elif provider == "groq":
        url = config["url_template"]
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        params = None

        # Translate our standard (Gemini) history format to Groq's format.
        groq_history = []
        if conversation_history:
            for msg in conversation_history:
                # Our standard format uses 'model', Groq expects 'assistant'
                role = "assistant" if msg["role"] == "model" else "user"
                groq_history.append({"role": role, "content": msg["parts"][0]["text"]})
        
        groq_history.append({"role": "user", "content": task})
        payload = {"messages": groq_history, "model": model_name}

    # --- Common API Call Logic ---
    with httpx.Client(timeout=60) as client:
        response = client.post(url, json=payload, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()

    # --- Provider-Specific Response Parsing ---
    # We always return the history in our standard (Gemini) format.
    if provider == "gemini":
        response_text = result["candidates"][0]["content"]["parts"][0]["text"]
        current_conversation.append({"role": "model", "parts": [{"text": response_text}]})
        final_history = current_conversation
    elif provider == "groq":
        response_text = result["choices"][0]["message"]["content"]
        # Translate Groq's response back to our standard format before appending.
        groq_history.append({"role": "assistant", "content": response_text})
        
        final_history = []
        for msg in groq_history:
            role = "model" if msg["role"] == "assistant" else "user"
            final_history.append({"role": role, "parts": [{"text": msg["content"]}]})

    return response_text, final_history
