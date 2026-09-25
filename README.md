
# Math Proof Coach

An AI-powered Socratic tutoring system designed to guide students through real analysis and abstract mathematics proofs. Instead of providing outright solutions, the system engages students through guided questions, definition checks, and logical scaffolding.

Built using the **Rule, Engine, System** architectural pattern, the application pairs a Next.js frontend with a resilient FastAPI backend that orchestrates multi-tiered model fallbacks, circuit breaking, request pacing, and session history management across the Google Gemini model suite.

---

## Architecture Overview

The system adheres strictly to the **Rule, Engine, System** design paradigm:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM LAYER                               │
│  ┌─────────────────────────┐                ┌─────────────────────────┐ │
│  │   Next.js React Client  │ ◄── HTTP/JSON ─►  FastAPI REST Service   │ │
│  └─────────────────────────┘                └────────────┬────────────┘ │
└──────────────────────────────────────────────────────────┼──────────────┘
                                                           │
┌──────────────────────────────────────────────────────────▼──────────────┐
│                              ENGINE LAYER                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  - Model Fallback & Selection (Gemini 3.8/3.7/3.5/flash)            │  │
│  │  - Circuit Breaker & Cooldown Tracking                            │  │
│  │  - Session History Transfer & Persistence                         │  │
│  │  - Exponential Backoff & Transient Retry Logic                     │  │
│  │  - Request Pacing & In-Memory Response Caching                    │  │
│  └─────────────────────────────────┬─────────────────────────────────┘  │
└────────────────────────────────────┼────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                               RULE LAYER                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  - Socratic Pedagogy Constraints (No direct code/answers)         │  │
│  │  - Definition Checking & Conceptual Scaffolding                   │  │
│  │  - Step-by-Step Proof Verification Prompt Rules                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

* **Rule Layer (`rules.py`):** Defines system prompts, Socratic constraints, and pedagogical boundaries. Ensures the model acts as a Socratic coach that checks definitions and guides proofs rather than providing direct answers.
* **Engine Layer (`engine.py`, `cache.py`, `exceptions.py`):** Manages multi-model orchestration, session state, fault tolerance, exponential backoffs, circuit breakers for failing models, and rate-limiting safeguards.
* **System Layer (`main.py`, Next.js app):** Provides REST API routes, handles CORS, processes standard payloads, and renders the chat user interface.

---

## Key Features

* **Socratic Proof Guidance:** Guides students through analysis problems (e.g., Abbott's *Understanding Analysis*) by prompting for formal definitions and logical step checks before addressing the proof structure.
* **Multi-Model Dynamic Fallback:** Automatically attempts execution across primary and secondary models (`gemini-3.8-flash` → `gemini-3.7-flash` → `gemini-3.5-flash` → `gemini-2.5-pro`) during upstream rate limits or outages.
* **Circuit Breaker Engine:** Tracks API errors (`503`, `429`, `404`) and temporarily places failing models into a cooldown state to prevent added network latency on subsequent turns.
* **Session Model Persistence:** Remembers the last known working model for an active user session, bypassing known failing models on subsequent user messages.
* **Chat History Transfer:** Preserves the complete context and conversation history when transferring a session from a failing model to a fallback model.
* **In-Memory Caching & Pacing:** Prevents redundant API calls on identical queries and enforces request intervals to maintain rate compliance.

---

## Tech Stack

* **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic, `google-genai` SDK
* **Frontend:** Next.js 14+, React, TypeScript, Tailwind CSS
* **LLM Engine:** Google Gemini API (`google-genai`)
* **Environment Management:** `python-dotenv`

---

## Project Structure

```text
math-proof-coach/
├── backend/
│   ├── main.py              # FastAPI application entrypoint & API routes
│   ├── engine.py            # Execution engine, session manager & circuit breaker
│   ├── rules.py             # System prompts & Socratic rule specifications
│   ├── cache.py             # In-memory query caching & request pacing
│   ├── exceptions.py        # Domain-specific API error abstractions
│   ├── requirements.txt     # Python backend dependencies
│   └── .env                 # API keys & server configuration
└── frontend/
    ├── src/
    │   └── app/
    │       ├── page.tsx     # Main chat interface component
    │       └── layout.tsx   # Next.js root layout
    ├── package.json         # Node dependencies
    └── tsconfig.json        # TypeScript configuration
```

---

## Getting Started

### Prerequisites

* Python 3.11 or higher
* Node.js 18.x or higher
* A valid Google Gemini API Key (`GEMINI_API_KEY`)

---

### Backend Setup

1. **Navigate to the backend directory:**
```bash
cd backend
```

2. **Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
```

5. **Start the development server:**
```bash
uvicorn main:app --reload --port 8000
```

The backend service will run at `http://127.0.0.1:8000`.

---

### Frontend Setup

1. **Navigate to the frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the Next.js development server:**
```bash
npm run dev
```

The client application will run at `http://localhost:3000`.

---

## API Documentation

### `POST /api/chat`

Sends a message to a student's active session and receives a Socratic response.

#### Request Body

```json
{
  "session_id": "d241af12-2a2c-4bd3-baa2-c1a49e9bf05d",
  "message": "Exercise 4.4.6: Give an example of a continuous function f: (0,1) -> R and a Cauchy sequence (xn) such that f(xn) is not Cauchy."
}
```

#### Response (`200 OK`)

```json
{
  "response": "To get started on this exercise, let's break down the key concepts...\n\nStep 1: Definition Check\nHow would you formally define a Cauchy sequence in R?"
}
```

#### Error Responses

* `429 Too Many Requests`: Rate limits exhausted across all available Gemini models.
* `503 Service Unavailable`: Upstream Gemini services unavailable across all candidate models.
* `500 Internal Server Error`: Unhandled upstream or engine execution error.

---

## Resilience & Circuit Breaker Logic

1. **Query Ingest:** Checks in-memory cache for matching `(session_id, query)`.
2. **Pacing Enforcement:** Ensures minimum delay between consecutive upstream calls.
3. **Model Selection:** Prioritizes the session's active working model, then filters remaining candidates in `FALLBACK_MODELS` by checking against active circuit breaker cooldown timers.
4. **Execution & Retry:** Executes request up to `max_retries_per_model` with exponential backoff on `429` / `503` status codes.
5. **Cooldown Activation:** If a model fails all retries or returns unrecoverable errors, it is placed on a 5-minute cooldown (`COOLDOWN_DURATION_SECONDS`), and the engine seamlessly switches session history to the next healthy fallback model.