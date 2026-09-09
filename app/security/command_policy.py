from enum import Enum

class SecurityLevel(Enum):
    SAFE = "SAFE"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    BLOCKED = "BLOCKED"

POLICY = {
    # Safe tools
    "open_app": SecurityLevel.SAFE,
    "close_app": SecurityLevel.SAFE,
    "restart_app": SecurityLevel.SAFE,
    "get_running_apps": SecurityLevel.SAFE,
    "focus_app": SecurityLevel.SAFE,
    "find_file": SecurityLevel.SAFE,
    "find_folder": SecurityLevel.SAFE,
    "open_file": SecurityLevel.SAFE,
    "open_folder": SecurityLevel.SAFE,
    "create_folder": SecurityLevel.SAFE,
    "copy_file": SecurityLevel.SAFE,
    "move_file": SecurityLevel.SAFE,
    "take_screenshot": SecurityLevel.SAFE,
    "type_text": SecurityLevel.SAFE,
    "press_key": SecurityLevel.SAFE,
    "hotkey": SecurityLevel.SAFE,
    "move_mouse": SecurityLevel.SAFE,
    "click": SecurityLevel.SAFE,
    "double_click": SecurityLevel.SAFE,
    "right_click": SecurityLevel.SAFE,
    "scroll": SecurityLevel.SAFE,
    "get_system_info": SecurityLevel.SAFE,
    "get_cpu_usage": SecurityLevel.SAFE,
    "get_memory_usage": SecurityLevel.SAFE,
    "get_volume": SecurityLevel.SAFE,
    "set_volume": SecurityLevel.SAFE,
    "mute": SecurityLevel.SAFE,
    "unmute": SecurityLevel.SAFE,
    "open_browser": SecurityLevel.SAFE,
    "navigate": SecurityLevel.SAFE,
    "search_web": SecurityLevel.SAFE,
    
    # Confirmation required
    "rename_file": SecurityLevel.CONFIRMATION_REQUIRED,
    "delete_file": SecurityLevel.CONFIRMATION_REQUIRED,
    "sleep_pc": SecurityLevel.CONFIRMATION_REQUIRED,
    "restart_pc": SecurityLevel.CONFIRMATION_REQUIRED,
    "shutdown_pc": SecurityLevel.CONFIRMATION_REQUIRED,
    "lock_pc": SecurityLevel.CONFIRMATION_REQUIRED,
    "run_terminal_command": SecurityLevel.CONFIRMATION_REQUIRED,
}

# Blocked arguments/commands (applied in tools specifically)
BLOCKED_COMMAND_KEYWORDS = [
    "format", "del /s", "rmdir /s", "diskpart", "reg add", "reg delete",
    "shutdown -s -t 0", "powershell -EncodedCommand", "Invoke-WebRequest", 
    "Net.WebClient"
]

def get_tool_security_level(tool_name: str) -> SecurityLevel:
    return POLICY.get(tool_name, SecurityLevel.BLOCKED)
