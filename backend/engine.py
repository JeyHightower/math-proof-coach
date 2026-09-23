import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rules import system_prompt

load_dotenv()
client = genai.Client()
sessions = {}


def get_or_create_session(session_id: str):
    """
    Retrieves an existing chat session or creates
    a new one with the Socratic system instructions attached.
    """

    if session_id not in sessions:
        sessions[session_id] = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instructions=system_prompt,
                temperature=0.3,
            )
        )
    return sessions[session_id]
    

def process_student_message(session_id:str, student_message:str) -> str:
    """
    Sends the student's message to their active chat session
    and returns the agent's Socratic response.
    """

    chat_session = get_or_create_session(session_id)
    response = chat_session.send_message(student_message)
    return response.text
