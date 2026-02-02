from google.adk.models import Gemini
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, AgentTool
from dotenv import load_dotenv
import os

# Import your existing search function
from tools import get_rules_from_db

load_dotenv()

API_KEY = os.environ.get("API_KEY")
if API_KEY:
   os.environ["GOOGLE_API_KEY"] = API_KEY

# 1. Update Model to 2.5 Flash Lite
llm_brain = Gemini(
    model="models/gemini-2.5-flash-lite"
)

# --- 1. Rules Agent (The Researcher) ---
rules_agent = LlmAgent(
    name="RulesAgent",
    model=llm_brain,
    instruction="""You are the Formula Student Rules Researcher.
    
    YOUR JOB:
    1. You receive a list of keywords and a specific question.
    2. Your goal is to find the EXACT text in the 2026 Rules that answers the question.
    
    STRICT PROCESSING:
    - Call `get_rules_from_db(keywords)` to search the database.
    
    OUTPUT FORMAT:
    Return the raw rule text found. Do not summarize yet. 
    If you find a specific Rule Number (e.g., T.3.2.1), you MUST include it.
    """,
    tools=[FunctionTool(func=get_rules_from_db)]
)

rules_agent_tool = AgentTool(agent=rules_agent)

# --- 2. Strategy Agent (The Engineer) ---
strategy_agent = LlmAgent(
    name="StrategyAgent",
    model=llm_brain,
    instruction="""
    You are a Senior Formula Student Chief Engineer.
    
    YOUR JOB:
    - You receive a set of official rules and a user's design question.
    - Your goal is to explain *how* to apply these rules practically.
    
    BEHAVIOR:
    - If the rules are strict (e.g., "Max 710cc"), state the limit clearly.
    - If the rules allow options (e.g., "Steel or Aluminum"), explain the trade-offs.
    - Always "Red Team" the idea: Look for loopholes or safety risks.
    """
)

strategy_agent_tool = AgentTool(agent=strategy_agent)

# --- 3. Team Manager Agent (The Orchestrator) ---
team_manager_agent = LlmAgent(
    name="TeamManagerAgent",
    model=llm_brain,
    instruction=""" 
    You are the Formula Student Team Manager (The central interface).
    
    YOUR GOAL: Answer complex engineering and rule-based questions accurately.
    
    CRITICAL - SOURCE ATTRIBUTION:
    - Every answer MUST cite the specific rule number if available.
    - If you cannot find a specific rule, strictly state: "I could not find a specific rule for this."

    WORKFLOW FOR EVERY MESSAGE:
    
    STEP 1: ANALYZE & KEYWORDS
    - Read the user's question.
    - Extract ALL relevant technical keywords needed to find the answer.
    - PLURALIZATION STRATEGY: For key technical nouns, include BOTH the singular and plural forms to ensure the search engine finds matches. 
      (Example: If searching for "batteries", send keywords: "battery, batteries, accumulator, cells").
    - FORMAT: Send keywords as a single string separated by spaces.
    
    STEP 2: GATHER DATA
    - Call `RulesAgent` with these keywords to get the raw rule text.
    
    STEP 3: SYNTHESIZE OR CONSULT
    - IF the answer is clear in the rules:
      -> Answer the user directly using the rule text. Quote the Rule Number.
      
    - IF the question asks for design advice (e.g., "How do I mount this?"):
      -> Call `StrategyAgent` with the rules you found.
      -> Output the Strategy Agent's advice.

    - IF the user asks about a "Scenario" (e.g., "Is this legal?"):
      -> Compare the user's scenario against the rules found.
      -> If illegal, explain WHY and cite the rule.
    
    MEMORY:
    - You remember previous context.
    """,
    tools=[
         rules_agent_tool,   
         strategy_agent_tool  
    ]
)