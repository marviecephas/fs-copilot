from pydantic import BaseModel
from agents import team_manager_agent
from fastapi import FastAPI
import asyncio
from google.adk.runners import runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.genai import types

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "member-02"

@app.get("/chat")
async def chat(request: ChatRequest):
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    runner = runner(
        agent=team_manager_agent,
        session_service=session_service,
        memory_service=memory_service
    )
    user_msg = types.Content(role="user", parts=[types.Part(text=request.message)])
    final_text = ""
    try:
        async for event in runner.run_async(
            user_id=request.session_id,
            session_id=request.session_id,
            new_message=user_msg
        ):
            if event.is_final_response() and event.content:
                final_text = event.content.parts[0].text
                return {"response": final_text}
    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.get("/")
def home():
    return {"status": "Online", "system": "Formula Student Co-Pilot"}
