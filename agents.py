from google.adk.models import Gemini
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, preload_memory
from dotenv import load_dotenv

from tools import get_rules_from_db, add_team_task, view_team_tasks, confirm_suggestion, auto_save_to_memory

import os

load_dotenv()

API_KEY = os.environ.get("API_KEY")

if API_KEY:
   os.environ["GOOGLE_API_KEY"] = API_KEY

llm_brain = Gemini(
    model="models/gemini-2.5-flash-lite"
)

# --- Rules Agent (Sub-Agent) ---
rules_agent = LlmAgent(
    name="RulesAgent",
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

# --- Strategy Agent (Sub-Agent) ---
strategy_agent = LlmAgent(
    name="StrategyAgent",
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

# --- Team Manager Agent (The Boss) ---
team_manager_agent = LlmAgent(
    name="TeamManagerAgent",
    model=llm_brain,
    instruction=""" 
        You are the Formula Student Team Manager.
    Your Goal: You DO NOT reject tasks. You FIX them.

    You must follow this STRICT Chain of Thought. 

    STEP 1: CHECK COMPLIANCE
    Delegate to the 'RulesAgent' to check the user's request.
    
    STEP 2: EVALUATE & ROUTE (CRITICAL STEP)
    - If RulesAgent returns 'compliant': true:
        -> ACTION: Call `add_team_task` immediately.
        -> RESPONSE: Tell the user "Task added."
    
    - If RulesAgent returns 'compliant': false:
        -> ACTION: DO NOT report failure to the user.
        -> ACTION: You MUST delegate to 'StrategyAgent' immediately.
        -> INPUT TO STRATEGY: Pass the specific "reason" for failure and the original task description.
        -> GOAL: Get a compliant alternative plan.

    STEP 3: CONFIRM THE FIX
    - Once 'StrategyAgent' gives you a new plan:
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
       preload_memory
    ],
    sub_agents=[rules_agent, strategy_agent],
    after_agent_callback=auto_save_to_memory
)