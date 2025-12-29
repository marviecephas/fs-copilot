import os
import uuid
import logging
from fastapi import FastAPI, Form, HTTPException, Response
from pydantic import BaseModel # <--- We need this for JSON (Curl/React)

# ADK & Agent Imports
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents import team_manager_agent
import memory 

app = FastAPI()

# Initialize Services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

@app.on_event("startup")
def on_startup():
    memory.init_db()
    print("✅ Server Started & DB Initialized")

# --- THE SHARED BRAIN (Used by both endpoints) ---
async def run_agent_process(user_id: str, message_text: str) -> str:
    """
    Standardizes the logic so both Curl and Twilio use the exact same brain.
    """
    # 1. Create a "Burner" Session
    runner_session_id = str(uuid.uuid4())
    
    await session_service.create_session(
        session_id=runner_session_id,
        user_id=user_id,
        app_name="Formula Student Co-Pilot"
    )

    # 2. Fetch History (Sticky Note)
    raw_history = memory.get_history(user_id)
    context_string = ""
    if raw_history:
        context_string += "PREVIOUS CHAT HISTORY:\n"
        for turn in raw_history:
            text_val = turn["parts"][0] if isinstance(turn["parts"], list) else turn["parts"]
            role = "User" if turn["role"] == "user" else "AI"
            context_string += f"{role}: {text_val}\n"
        context_string += "[END HISTORY]\nAnswer the NEW QUESTION below:\n"

    # 3. Add User Message to DB
    memory.add_message(user_id, "user", message_text)

    # 4. Run Agent
    full_prompt = context_string + "NEW QUESTION: " + message_text
    
    agent_runner = Runner(
        agent=team_manager_agent,
        session_service=session_service,
        memory_service=memory_service,
        app_name="Formula Student Co-Pilot"
    )

    user_msg = types.Content(role="user", parts=[types.Part(text=full_prompt)])
    final_text = ""

    try:
        async for event in agent_runner.run_async(
            user_id=user_id,
            session_id=runner_session_id,
            new_message=user_msg
        ):
            if event.is_final_response() and event.content and event.content.parts:
                part = event.content.parts[0]
                if hasattr(part, 'text') and part.text:
                    final_text = part.text
        
        # Cleanup Burner Session
        await session_service.delete_session(
            session_id=runner_session_id,
            user_id=user_id,
            app_name="Formula Student Co-Pilot"
        )

        if final_text:
            memory.add_message(user_id, "model", final_text)
            return final_text
        else:
            return "Error: Agent was silent."

    except Exception as e:
        print(f"Agent Error: {e}")
        return "I encountered an error processing your request."

# --- ENDPOINT 1: JSON (For Curl / React / Postman) ---
class ChatRequest(BaseModel):
    message: str
    user_id: str = "member-02" # Default ID for testing

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # This endpoint expects JSON: {"message": "Hello", "user_id": "123"}
    response_text = await run_agent_process(request.user_id, request.message)
    return {"response": response_text}

# --- ENDPOINT 2: TWILIO (For WhatsApp) ---
@app.post("/twilio")
async def twilio_endpoint(Body: str = Form(...), From: str = Form(...)):
    # This endpoint expects Form Data from Twilio
    print(f"📩 Incoming from {From}: {Body}")
    response_text = await run_agent_process(From, Body)
    return Response(response_text, media_type = "text/plain")

# --- HEALTH CHECK ---
@app.get("/")
def home():
    return {"status": "FS Co-Pilot is Online", "mode": "Hybrid (JSON + Twilio)"}
