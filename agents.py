llm_brain = Gemini(
    model="models/gemini-2.5-flash-lite", 
)

# --- Rules Agent (Sub-Agent) ---
rules_agent = LlmAgent(
    name="RulesAgent",
    model=llm_brain,
    instruction="""You are the Formula Student Rules Lawyer.
    Your ONLY job is to check if a task complies with the 2026 Rules.
    1. Call `get_rules_from_db(category)` to get the official rules.
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
    instruction="""You are an innovative Formula Student Chief Engineer.
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
    instruction="""You are the Formula Student Team Manager.
    
    Follow this STRICT process for every new task from the user:

    Step 1: Ask `RulesAgent` to check compliance.
    Step 2: ANALYZE the result.
       - IF compliant: Call `add_team_task` immediately.
       - IF NOT compliant: Proceed to Step 3.
    Step 3: Ask `StrategyAgent` for a fix.
       - Tell it the task failed and the reason.
    Step 4: Use `confirm_suggestion` to ask the user for approval.
       - Pass the 'original_task', 'suggested_replacement', and 'reason'.
    Step 5: FINALIZE.
       - If the tool returns "APPROVED", call `add_team_task` with the NEW suggestion.
       - If "REJECTED", stop.
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
