from typing import Callable, Dict, Any
from app.tools.base import ToolResult

from app.tools.app_tools import *
from app.tools.file_tools import *
from app.tools.screenshot_tools import *
from app.tools.keyboard_tools import *
from app.tools.system_tools import *
from app.tools.browser_tools import *
from app.tools.terminal_tools import *

TOOL_REGISTRY: Dict[str, Callable[..., ToolResult]] = {
    "open_app": open_app,
    "close_app": close_app,
    "restart_app": restart_app,
    "get_running_apps": get_running_apps,
    "focus_app": focus_app,
    "find_file": find_file,
    "find_folder": find_file, # reuse logic
    "open_file": open_file,
    "open_folder": open_folder,
    "create_folder": create_folder,
    "delete_file": delete_file,
    "take_screenshot": take_screenshot,
    "type_text": type_text,
    "press_key": press_key,
    "hotkey": hotkey,
    "move_mouse": move_mouse,
    "click": click,
    "double_click": double_click,
    "right_click": right_click,
    "scroll": scroll,
    "get_system_info": get_system_info,
    "get_cpu_usage": get_cpu_usage,
    "get_memory_usage": get_memory_usage,
    "mute": mute,
    "unmute": unmute,
    "lock_pc": lock_pc,
    "sleep_pc": sleep_pc,
    "restart_pc": restart_pc,
    "shutdown_pc": shutdown_pc,
    "open_browser": open_browser,
    "navigate": navigate,
    "search_web": search_web,
    "run_terminal_command": run_terminal_command,
}

def execute_tool(tool_name: str, arguments: dict) -> ToolResult:
    if tool_name not in TOOL_REGISTRY:
        return ToolResult(success=False, message=f"Tool {tool_name} not found.")
    
    func = TOOL_REGISTRY[tool_name]
    try:
        return func(**arguments)
    except TypeError as e:
         return ToolResult(success=False, message=f"Invalid arguments for {tool_name}: {str(e)}")
    except Exception as e:
         return ToolResult(success=False, message=f"Execution error in {tool_name}: {str(e)}")
