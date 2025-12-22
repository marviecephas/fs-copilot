from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents import team_manager_agent


app = FastAPI()

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
class ChatRequest(BaseModel):
    message: str
    session_id: str = "member-02"

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        current_session =  await session_service.get(request.session_id)
    except:
        current_session = None
    if not current_session:
        current_session = await session_service.create_session(
            session_id = request.session_id,
            user_id = request.session_id,
            app_name = "Formula Student Co-Pilot"
)  
    agent_runner = Runner(
        agent=team_manager_agent,
        session_service=session_service,
        memory_service=memory_service,
        app_name = "Formula Student Co-Pilot"
    )

    user_msg = types.Content(role="user", parts=[types.Part(text=request.message)])
    final_text = ""

    try:
        async for event in agent_runner.run_async(
            user_id=request.session_id,
            session_id=request.session_id,
            new_message=user_msg
        ):
            if event.is_final_response() and event.content:
                final_text = event.content.parts[0].text
        
        if final_text:
            return {"response": final_text}
        else:
            return {"response": "Error: Agent did not produce a response."}

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "Online", "system": "Formula Student Co-Pilot"}