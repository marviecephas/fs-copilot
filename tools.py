from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext
from database import FORMULA_RULES_DATABASE

def get_rules_from_db(task: str) -> Any:
    """
    Retrieves all rules where the category string appears in the rule text 
    OR matches the rule section (e.g., 'CV1.1').
    """
    relevant_rules = []

    keywords = task.split()

    # Loop through every rule in the database list
    for rule in FORMULA_RULES_DATABASE:
        # Check if category keyword is in the text (case-insensitive)
        if task.lower() in rule["text"].lower():
            relevant_rules.append(rule)
        # Also check if it matches the section ID
        elif task.lower() in rule["section"].lower():
            relevant_rules.append(rule)

        else:
            for word in keywords:
                if len(word)>3 and word.lower() in rule["text"].lower():
                    relevant_rules.append(rule)

    if relevant_rules:
        return relevant_rules
    else:
        return {"error": f"No rules found for {task}"}

