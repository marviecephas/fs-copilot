import os
import uuid
from fastapi import FastAPI, Form, BackgroundTasks, Response
from pydantic import BaseModel
from twilio.rest import Client  # <--- Essential Import

# ADK & Agent Imports
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents import team_manager_agent
import memory 

# --- CONFIGURATION ---
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

app = FastAPI()

# Initialize Services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

@app.on_event("startup")
def on_startup():
    memory.init_db()
    print("✅ Server Started & DB Initialized")

# --- 1. THE SHARED BRAIN (Core Logic) ---
async def run_agent_process(user_id: str, message_text: str) -> str:
    """
    The Thinking Engine. Returns text.
    Used by BOTH /chat (Curl) and /twilio (WhatsApp).
    """
    APP_NAME = "Formula Student Co-Pilot"
    runner_session_id = str(uuid.uuid4())
    
    # Setup Session
    await session_service.create_session(runner_session_id, user_id, APP_NAME)

    # Fetch History
    raw_history = memory.get_history(user_id)
    context_string = ""
    if raw_history:
        context_string += "HISTORY:\n"
        for turn in raw_history:
            text_val = turn["parts"][0] if isinstance(turn["parts"], list) else turn["parts"]
            role = "User" if turn["role"] == "user" else "AI"
            context_string += f"{role}: {text_val}\n"
        context_string += "[END HISTORY]\n"

    # Run Agent
    memory.add_message(user_id, "user", message_text)
    full_prompt = context_string + "NEW QUESTION: " + message_text
    
    agent_runner = Runner(
        agent=team_manager_agent,
        session_service=session_service,
        memory_service=memory_service,
        app_name=APP_NAME
    )

    user_msg = types.Content(role="user", parts=[types.Part(text=full_prompt)])
    final_text = ""

    try:
        async for event in agent_runner.run_async(user_id, runner_session_id, user_msg):
            if event.is_final_response() and event.content and event.content.parts:
                part = event.content.parts[0]
                if hasattr(part, 'text') and part.text:
                    final_text = part.text
        
        await session_service.delete_session(runner_session_id, user_id, APP_NAME)

        if final_text:
            memory.add_message(user_id, "model", final_text)
            return final_text
        return "Task processed, but no text output."

    except Exception as e:
        print(f"Agent Error: {e}")
        return "I encountered an error."

# --- 2. THE BACKGROUND WORKER (Twilio Only) ---
async def process_and_reply(user_phone: str, message_text: str):
    """
    Wrapper function: Calls the Brain, then texts the user via Twilio.
    """
    print(f"⚙️ BACKGROUND: Processing for {user_phone}...")
    
    # CALL THE BRAIN
    response_text = await run_agent_process(user_phone, message_text)
    
    # SEND THE SMS
    print(f"📤 SENDING REPLY: {response_text[:50]}...")
    try:
        twilio_client.messages.create(
            body=response_text,
            from_=TWILIO_NUMBER,
            to=user_phone
        )
    except Exception as e:
        print(f"❌ Twilio Error: {e}")

# --- 3. ENDPOINTS ---

# Endpoint A: JSON (Curl / React) - Returns JSON immediately
class ChatRequest(BaseModel):
    message: str
    user_id: str = "member-02"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response_text = await run_agent_process(request.user_id, request.message)
    return {"response": response_text}

# Endpoint B: Twilio (WhatsApp) - Returns Silence, Works in Background
@app.post("/twilio")
async def twilio_endpoint(
    background_tasks: BackgroundTasks,
    Body: str = Form(...), 
    From: str = Form(...)
):
    print(f"📩 RECEIVED: {Body} from {From}")
    
    # Schedule the worker task
    background_tasks.add_task(process_and_reply, From, Body)
    
    # Return 200 OK (Silence) instantly
    return Response(status_code=200)

@app.get("/")
def home():
    return {"status": "FS Co-Pilot Online", "mode": "Hybrid"}
