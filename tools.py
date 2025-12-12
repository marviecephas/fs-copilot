from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext
from database import FORMULA_RULES_DATABASE

def get_rules_from_db(category: str) -> Any:
    """
    Retrieves all rules where the category string appears in the rule text 
    OR matches the rule section (e.g., 'CV1.1').
    """
    relevant_rules = []

    # Loop through every rule in the database list
    for rule in FORMULA_RULES_DATABASE:
        # Check if category keyword is in the text (case-insensitive)
        if category.lower() in rule["text"].lower():
            relevant_rules.append(rule)
        # Also check if it matches the section ID
        elif category.lower() in rule["section"].lower():
            relevant_rules.append(rule)

    if relevant_rules:
        return relevant_rules
    else:
        return {"error": f"No rules found for category '{category}'."}

def add_team_task(tool_context: ToolContext, task: str) -> str:
    """Adds a task to the current session's task list."""
    # Get the current list or start a new empty one
    tasks = tool_context.state.get("tasks", [])
    
    # Add the new task
    tasks.append(task)
    
    # Save it back to the state
    tool_context.state["tasks"] = tasks
    return f"Task '{task}' added to database."

def view_team_tasks(tool_context: ToolContext) -> List[str]:
    """Views all tasks in the current session."""
    return tool_context.state.get("tasks", [])

def confirm_suggestion(tool_context: ToolContext, original_task: str, suggested_replacement: str, reason: str) -> Dict[str, str]:
    """Pauses execution to ask for human approval of a design change."""
    
    # 1. RESUME Logic: If the user has already clicked a button/replied
    if tool_context.tool_confirmation:
        if tool_context.tool_confirmation.confirmed:
            return {"status": "APPROVED", "message": f"User approved. Proceeding with: '{suggested_replacement}'."}
        else:
            return {"status": "REJECTED", "message": "User rejected."}

    # 2. PAUSE Logic: If we haven't asked yet, trigger the pause
    tool_context.request_confirmation(
        hint=f"Approving change: {original_task} -> {suggested_replacement}"
    )
    
    return {"status": "PENDING_APPROVAL"}

async def auto_save_to_memory(callback_context):
    """Saves session state to long-term memory."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )
