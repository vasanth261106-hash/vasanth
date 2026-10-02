import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "PocketSmart AI")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    description="PocketSmart AI Backend API",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    user_name: Optional[str] = None


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to PocketSmart AI!",
        "status": "running",
        "version": "1.0.0"
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_configured": client is not None
    }


# --------------------------------------------------
# AI Chat endpoint
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the .env file."
        )

    try:
        user_message = request.message.strip()

        prompt = f"""
You are PocketSmart AI, a helpful personal AI assistant.

User name: {request.user_name or "User"}

User message:
{user_message}

Give a clear, friendly and useful response.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        return {
            "success": True,
            "reply": response.text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI request failed: {str(e)}"
        )


# --------------------------------------------------
# Run locally
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )