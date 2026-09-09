import json
from app.agent.router import fast_route
from app.agent.planner import plan_action
from app.tools.registry import execute_tool
from app.security.command_policy import get_tool_security_level, SecurityLevel
from app.security.confirmations import require_manual_confirmation
from app.config.settings import CONFIRM_DANGEROUS_ACTIONS

def execute_intent(intent: dict) -> str:
    tool_name = intent.get("tool")
    arguments = intent.get("arguments", {})
    
    if not tool_name:
        return "Invalid action generated."
        
    security_level = get_tool_security_level(tool_name)
    
    if security_level == SecurityLevel.BLOCKED:
        return f"Action {tool_name} is blocked by security policy."
        
    if security_level == SecurityLevel.CONFIRMATION_REQUIRED and CONFIRM_DANGEROUS_ACTIONS:
        action_desc = f"{tool_name} with arguments {json.dumps(arguments)}"
        if not require_manual_confirmation(action_desc):
            return "Action cancelled by user."
            
    print(f"[*] Executing tool: {tool_name}")
    result = execute_tool(tool_name, arguments)
    return result.message

def process_command(user_input: str) -> str:
    """Processes a user command end-to-end."""
    if not user_input.strip():
        return ""
        
    # 1. Fast route
    intents = fast_route(user_input)
    
    # 2. LLM Planner
    if not intents:
        print("[*] Routing to Qwen for planning...")
        intents = plan_action(user_input)
        
    if not intents:
        return "I'm sorry, I didn't understand how to execute that."
        
    # 3. Execution
    responses = []
    for intent in intents:
        res = execute_intent(intent)
        responses.append(res)
        if "cancelled" in res.lower() or "blocked" in res.lower():
            break # Stop executing further intents if one is blocked/cancelled
            
    # Combine responses for TTS
    return " ".join(responses)
