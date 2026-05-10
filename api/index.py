from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os, sys

# Allow importing from chatmodels/ relative to the api/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "chatmodels"))
from model_loader import get_mistral_model

load_dotenv()

app = FastAPI(title="AI Chat Bot")
model = get_mistral_model()

# ── Request / Response schemas ───────────────────────────────────────────────
class Message(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    reply: str
    input_tokens: int
    output_tokens: int
    total_tokens: int

# ── Chat endpoint ────────────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    lc_messages = [SystemMessage(content="You are a helpful assistant.")]
    for m in req.messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        else:
            lc_messages.append(AIMessage(content=m.content))

    response = model.invoke(lc_messages)
    usage = response.response_metadata.get("token_usage", {})

    return ChatResponse(
        reply=response.content,
        input_tokens=usage.get("prompt_tokens", 0),
        output_tokens=usage.get("completion_tokens", 0),
        total_tokens=usage.get("total_tokens", 0),
    )
