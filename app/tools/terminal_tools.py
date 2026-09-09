import subprocess
from app.tools.base import ToolResult
from app.security.command_policy import BLOCKED_COMMAND_KEYWORDS

# A very restricted allowlist of basic safe commands if we don't want to rely solely on confirmations
ALLOWED_PREFIXES = ["npm", "git", "python", "pip", "node", "dir", "cd", "echo", "ping"]

def run_terminal_command(command: str) -> ToolResult:
    # First check blocked keywords
    cmd_lower = command.lower()
    for blocked in BLOCKED_COMMAND_KEYWORDS:
        if blocked in cmd_lower:
            return ToolResult(success=False, message="Command contains blocked keywords.")
    
    # Check allowlist
    is_allowed = False
    for prefix in ALLOWED_PREFIXES:
        if cmd_lower.startswith(prefix):
            is_allowed = True
            break
            
    if not is_allowed:
        return ToolResult(success=False, message="Command not in the safe allowlist.")
        
    try:
        # Run safely, capture output. Timeout to prevent hanging.
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()
        if not output:
             output = result.stderr.strip()
             
        # Limit output size
        if len(output) > 500:
            output = output[:500] + "... (truncated)"
            
        return ToolResult(success=True, message="Command executed.", data={"output": output})
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, message="Command timed out.")
    except Exception as e:
        return ToolResult(success=False, message=f"Failed to execute command. Error: {str(e)}")
