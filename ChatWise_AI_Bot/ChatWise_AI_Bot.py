from fastapi import FastAPI, status
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict

# =============================================================
# App initialization & metadata
# =============================================================
app = FastAPI(
    title="ChatWise AI Bot",
    version="1.0.1",
    description="A lightweight demonstration chatbot API. Designed for demos, learning and small integrations."
)

# =============================================================
# Models
# =============================================================
class ChatMessage(BaseModel):
    """Request model for sending a chat message to the bot."""
    message: str = Field(..., min_length=1, example="Hello, how are you?")

class ChatResponse(BaseModel):
    """Standardized bot response model."""
    status: str
    user_message: str
    bot_reply: str
    timestamp: str

# =============================================================
# Internal helpers & lightweight 'knowledge'
# =============================================================
def log_action(action: str) -> None:
    """Simple timestamped console logger for development/troubleshooting."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action}")

# Small, explicit keyword -> response mapping to keep logic obvious and human-written
_KEYWORD_RESPONSES: Dict[str, str] = {
    "hello": "Hey there! I'm ChatWise, your friendly AI bot.",
    "hi": "Hey there! I'm ChatWise, your friendly AI bot.",
    "how are you": "I'm doing great! Thanks for asking. How can I help you today?",
    "your name": "I'm ChatWise — your smart and simple AI assistant.",
    "bye": "Goodbye! Have a wonderful day!",
    "goodbye": "Goodbye! Have a wonderful day!",
    "help": "Sure — you can ask me about my features or just chat casually.",
    "time": "",  # handled dynamically
    "date": "",  # handled dynamically
}

def get_bot_response(user_input: str) -> str:
    """
    Determine the bot's reply based on simple keyword matching.
    This function is intentionally simple and deterministic for demo purposes.
    """
    text = user_input.strip().lower()

    # Exact phrase checks (longer phrases first)
    if "how are you" in text:
        return _KEYWORD_RESPONSES["how are you"]

    # dynamic responses for date/time
    if "time" in text:
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."
    if "date" in text:
        return f"Today's date is {datetime.now().strftime('%d %B %Y')}."

    # check simple keywords
    for key, response in _KEYWORD_RESPONSES.items():
        if key and key in text and response:
            return response

    # fallback
    return "I'm not sure I understand — but I'm learning every day!"

# =============================================================
# Routes
# =============================================================
@app.get("/", tags=["Home"])
def home():
    """
    API root endpoint.
    Returns a short welcome message and a timestamp for quick checks.
    """
    log_action("Home endpoint accessed")
    return {
        "status": "ok",
        "message": "Welcome to ChatWise AI Bot",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
def chat_with_bot(chat: ChatMessage):
    """
    Send a message to the bot and receive a standardized response.
    The response includes status, original user message, bot reply, and a timestamp.
    """
    log_action(f"Received message: {chat.message!r}")

    bot_reply = get_bot_response(chat.message)
    response = ChatResponse(
        status="success",
        user_message=chat.message,
        bot_reply=bot_reply,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    log_action(f"Responding with: {bot_reply!r}")
    return response
