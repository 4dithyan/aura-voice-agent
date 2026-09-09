"""app/agent/agent.py — Central command processor. Routes to PC or Browser Agent."""
import json
from app.agent.router import fast_route
from app.agent.planner import plan_action
from app.tools.registry import execute_tool
from app.security.command_policy import get_tool_security_level, SecurityLevel
from app.security.confirmations import require_manual_confirmation
from app.config.settings import CONFIRM_DANGEROUS_ACTIONS
from app.core.orchestrator import get_orchestrator


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
    """
    Central command processor.
    1. Fast router (no LLM, handles simple PC commands)
    2. Orchestrator classifies as PC or Browser
    3. Routes accordingly
    """
    if not user_input.strip():
        return ""

    # --- 1. Fast route (no LLM) ---
    intents = fast_route(user_input)
    if intents:
        responses = []
        for intent in intents:
            res = execute_intent(intent)
            responses.append(res)
            if "cancelled" in res.lower() or "blocked" in res.lower():
                break
        return " ".join(responses)

    # --- 2. Classify: PC vs Browser vs Control ---
    orchestrator = get_orchestrator()
    task_type, goal = orchestrator.classify(user_input)

    if task_type == "control":
        return _handle_control_command(goal)

    if task_type == "browser":
        return _handle_browser_task(goal, user_input)

    # --- 3. Default: PC Agent with LLM planner ---
    print("[*] Routing to Qwen for PC planning...")
    intents = plan_action(user_input)
    if not intents:
        return "I'm sorry, I didn't understand how to execute that."

    responses = []
    for intent in intents:
        res = execute_intent(intent)
        responses.append(res)
        if "cancelled" in res.lower() or "blocked" in res.lower():
            break

    return " ".join(responses)


def _handle_browser_task(goal: str, user_input: str) -> str:
    """Delegates to the BrowserAgent."""
    try:
        from app.browser.browser_agent import get_browser_agent
        agent = get_browser_agent()
        print(f"[Browser] Starting task: {goal}")
        return agent.run_task(goal=goal, user_request=user_input)
    except ImportError as e:
        return f"Browser agent is not available: {e}"
    except Exception as e:
        print(f"[Browser] Error: {e}")
        return f"Browser task failed: {str(e)[:80]}"


def _handle_control_command(command: str) -> str:
    """Handles stop/pause/resume for the active browser task."""
    try:
        from app.browser.browser_agent import get_browser_agent
        agent = get_browser_agent()
        if command == "stop":
            agent.cancel()
            return "Task cancelled."
        elif command == "pause":
            agent.pause()
            return "Task paused. Say resume to continue."
        elif command == "resume":
            agent.resume()
            return "Resuming task."
    except Exception:
        pass
    return "Done."
