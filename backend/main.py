from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import process_student_message


class ChatRequest(BaseModel):
    session_id:str
    message: str


class ChatResponse(BaseModel):
    response:str



app = FastAPI(
    title="Math Proof Coach API",
    description="Backent API for the Socratic Math Proof Coach AI Agent",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Simple health check endpoint to confirm the server is running."""
    return {"status": "online", "message": "Math Proof Coach API is running."}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpont(request:ChatRequest):
    """
    Receives student prompt, routes it to the Engine Session manager,
    and returns the agent's Socratic feedback.
    """

    ai_response = process_student_message(
        session_id = request.session_id,
        student_message = request.message
    )
    return ChatResponse(response=ai_response)