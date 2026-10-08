import os
import logging

from engine import process_student_message
from exceptions import RateLimitError, ServiceUnavailableError, UpstreamAPIError
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length= 4000)


class ChatResponse(BaseModel):
    response:str

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Math Proof Coach API",
    description="Backend API for the Socratic Math Proof Coach AI Agent",
    version="1.0.0"
)


default_origins = "http://localhost:3000,https://math-proof-coach.vercel.app"
raw_origins = os.getenv("ALLOWED_ORIGINS", default_origins)

origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitError)
async def rate_limit_exception_handler(request:Request, exc:RateLimitError):
    logger.error(f"RateLimitError caught at API boundary: {exc}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "RateLimitExceeded",
            "message": "The system is currently experiencing high demand. Please wait a few seconds and try again.",
        },
    )

@app.exception_handler(ServiceUnavailableError)
async def service_unavailable_exception_handler(request:Request, exc: ServiceUnavailableError):
    logger.error(f"ServiceUnavailableError caught at API boundary: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "ServiceUnavailable",
            "message": "The AI service is temporarily unavailable. Please try again shortly.",        
        },
    )

@app.exception_handler(UpstreamAPIError)
async def upstream_api_exception_handler(request:Request, exc:UpstreamAPIError):
    logger.error(f"UpstreamAPIError caught at API boundary: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while communicating with the AI service.",
        }
    )



@app.api_route("/", methods=["GET", "HEAD"])
def health_check():
    """Simple health check endpoint to confirm the server is running."""
    return {"status": "online", "message": "Math Proof Coach API is running."}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request:ChatRequest):
    """
    Receives student prompt, routes it to the Engine Session manager,
    and returns the agent's Socratic feedback.
    """

    ai_response = process_student_message(
        session_id = request.session_id,
        student_message = request.message
    )
    return ChatResponse(response=ai_response)