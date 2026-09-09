import psutil
import platform
import ctypes
import os
from app.tools.base import ToolResult

def get_system_info() -> ToolResult:
    info = {
        "os": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine()
    }
    return ToolResult(success=True, message=f"System is {info['os']} {info['release']}.", data=info)

def get_cpu_usage() -> ToolResult:
    usage = psutil.cpu_percent(interval=1)
    return ToolResult(success=True, message=f"CPU usage is at {usage} percent.")

def get_memory_usage() -> ToolResult:
    mem = psutil.virtual_memory()
    return ToolResult(success=True, message=f"Memory usage is at {mem.percent} percent.")

def mute() -> ToolResult:
    import pyautogui
    pyautogui.press("volumemute")
    return ToolResult(success=True, message="Muted system volume.")

def unmute() -> ToolResult:
    import pyautogui
    pyautogui.press("volumemute") # Toggle
    return ToolResult(success=True, message="Unmuted system volume.")

def lock_pc() -> ToolResult:
    ctypes.windll.user32.LockWorkStation()
    return ToolResult(success=True, message="Locked the computer.")

def sleep_pc() -> ToolResult:
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return ToolResult(success=True, message="Putting computer to sleep.")

def restart_pc() -> ToolResult:
    os.system("shutdown /r /t 0")
    return ToolResult(success=True, message="Restarting computer.")

def shutdown_pc() -> ToolResult:
    os.system("shutdown /s /t 0")
    return ToolResult(success=True, message="Shutting down computer.")
