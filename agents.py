from google.adk.models import Gemini
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, AgentTool
from dotenv import load_dotenv
import os

from tools import get_rules_from_db, add_team_task, view_team_tasks, confirm_suggestion

load_dotenv()

API_KEY = os.environ.get("API_KEY")

if API_KEY:
   os.environ["GOOGLE_API_KEY"] = API_KEY

# 1. Update Model to 2.5 Flash Lite
llm_brain = Gemini(
    model="models/gemini-2.5-flash-lite"
)

# --- 1. Rules Agent (Sub-Agent) ---
rules_agent = LlmAgent(
    name="RulesAgent", # AgentTool will pick this name up automatically
    model=llm_brain,
    instruction="""You are the Formula Student Rules Lawyer.
    Your ONLY job is to check if a task complies with the 2026 Rules.
    1. Call `get_rules_from_db(task)` to get the official rules.
    2. Compare the task description against the rules.
    3. Return a JSON object with:
       - "compliant": true or false
       - "reason": "Quote the specific rule that was violated or satisfied."
    """,
    tools=[FunctionTool(func=get_rules_from_db)]
)

# WRAPPER: Convert Rules Agent into a Tool (Minimal config)
rules_agent_tool = AgentTool(
    agent=rules_agent
)

# --- 2. Strategy Agent (Sub-Agent) ---
strategy_agent = LlmAgent(
    name="StrategyAgent", # AgentTool will pick this name up automatically
    model=llm_brain,
    instruction="""
    You are an innovative Formula Student Chief Engineer.
    Your goal is to find creative solutions to engineering problems.
    
    You will receive a message describing a task that failed compliance.
    Your Process:
    1. Acknowledge the failure.
    2. Think of a new, alternative solution that achieves the same goal but follows the rules.
    3. Output your suggestion.
    """
)

# WRAPPER: Convert Strategy Agent into a Tool (Minimal config)
strategy_agent_tool = AgentTool(
    agent=strategy_agent
)

# --- 3. Team Manager Agent (The Boss) ---
team_manager_agent = LlmAgent(
    name="TeamManagerAgent",
    model=llm_brain,
    instruction=""" 
    You are the Formula Student Team Manager.
    
    CRITICAL - MEMORY & CONTEXT:
    - You have access to the **Previous Conversation History** in the prompt.
    - ALWAYS check this history before asking the user for information they already provided (like their name, car specs, or previous tasks).
    - If the user asks "What is my name?" or "What are we building?", answer directly from this history.

    YOUR GOAL: You DO NOT reject tasks. You FIX them.

    STRICT WORKFLOW:

    STEP 1: CHECK COMPLIANCE
    - Call the tool `RulesAgent` (check_compliance) to verify the user's request.
    
    STEP 2: EVALUATE & ROUTE
    - If `RulesAgent` returns 'compliant': true:
        -> ACTION: Call `add_team_task` immediately.
        -> RESPONSE: Tell the user "Task added."
    
    - If `RulesAgent` returns 'compliant': false:
        -> ACTION: DO NOT report failure to the user yet.
        -> ACTION: You MUST call `StrategyAgent`.
        -> INPUT: Pass the specific "reason" for failure and the original task description.
        -> GOAL: Get a compliant alternative plan.

    STEP 3: CONFIRM THE FIX
    - Once the StrategyAgent gives you a new plan:
        -> ACTION: Call `confirm_suggestion`.
        -> ARGS: 
             original_task = [User's original bad idea]
             suggestion = [StrategyAgent's new idea]
             reason = [Why the first one failed]
    
    Constraint: You are forbidden from outputting "Does not comply" and stopping. You must always offer the path forward provided by the StrategyAgent.
    """,
    tools=[
        FunctionTool(func=add_team_task),
        FunctionTool(func=view_team_tasks),
        FunctionTool(func=confirm_suggestion),
        rules_agent_tool,    
        strategy_agent_tool  
    ]
  )
