from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from adept.core.engine import execute_task

app = FastAPI(title="Adept API")

class ChatRequest(BaseModel):
    message: str
    provider: str = "groq"
    model: str = "default"
    conversation_history: list = []

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """Handle conversational AI requests with memory for multiple providers."""
    try:
        response, updated_history = execute_task(
            task=request.message,
            provider=request.provider,
            model=request.model,
            conversation_history=request.conversation_history
        )
        return {
            "status": "success",
            "response": response,
            "conversation_history": updated_history
        }
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
