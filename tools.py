def get_rules_from_db(category: str) -> Dict[str, Any]:
    """Retrieves all rules for a specific category from the database. To be worked"""
    category_cleaned = category.replace(" ", "_")
    if category_cleaned in FORMULA_RULES_DATABASE:
        return FORMULA_RULES_DATABASE[category_cleaned]
    
    # Fuzzy match
    for key in FORMULA_RULES_DATABASE.keys():
        if category.lower() in key.lower():
            return FORMULA_RULES_DATABASE[key]
            
    return {
        "error": f"Category '{category}' not found.",
        "valid_categories": list(FORMULA_RULES_DATABASE.keys())
    }

def add_team_task(tool_context: ToolContext, task: str) -> str:
    """Adds a task to the current session's task list."""
    tasks = tool_context.state.get("tasks", [])
    tasks.append(task)
    tool_context.state["tasks"] = tasks
    return f"Task '{task}' added to database."

def view_team_tasks(tool_context: ToolContext) -> List[str]:
    """Views all tasks in the current session."""
    return tool_context.state.get("tasks", [])

def confirm_suggestion(tool_context: ToolContext, original_task: str, suggested_replacement: str, reason: str) -> dict:
    """Pauses execution to ask for human approval of a design change."""
    # Resume logic
    if tool_context.tool_confirmation:
        if tool_context.tool_confirmation.confirmed:
            return {"status": "APPROVED", "message": f"User approved. Proceeding with: '{suggested_replacement}'."}
        else:
            return {"status": "REJECTED", "message": "User rejected."}

    # Pause logic
    tool_context.request_confirmation(
        hint=f"Approving change: {original_task} -> {suggested_replacement}"
    )
    return {"status": "PENDING_APPROVAL"}

async def auto_save_to_memory(callback_context):
    """Saves session state to long-term memory."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
          )
