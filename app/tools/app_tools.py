import psutil
import subprocess
from app.tools.base import ToolResult

def open_app(app: str) -> ToolResult:
    """Tries to open a common Windows application."""
    # Simple mapping for common apps
    app_map = {
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "code": "code.cmd",
        "vs code": "code.cmd",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "spotify": "spotify.exe",
        "cmd": "cmd.exe",
        "terminal": "wt.exe",
        "powershell": "powershell.exe"
    }
    
    executable = app_map.get(app.lower(), app)
    
    try:
        # We use start to let Windows resolve the path if it's in the registry/PATH
        subprocess.Popen(f"start {executable}", shell=True)
        return ToolResult(success=True, message=f"Opening {app}.")
    except Exception as e:
        return ToolResult(success=False, message=f"Could not open {app}. Error: {str(e)}")

def close_app(app: str) -> ToolResult:
    """Closes an application by name."""
    closed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if app.lower() in proc.info['name'].lower():
                proc.terminate()
                closed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if closed:
        return ToolResult(success=True, message=f"Closed {app}.")
    return ToolResult(success=False, message=f"Could not find running application {app}.")

def restart_app(app: str) -> ToolResult:
    close_res = close_app(app)
    if close_res.success:
        import time
        time.sleep(1)
        return open_app(app)
    return close_res

def get_running_apps() -> ToolResult:
    apps = set()
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name and name.endswith(".exe"):
                apps.add(name[:-4])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return ToolResult(success=True, message="Retrieved running apps.", data={"apps": list(apps)[:20]}) # Limit to 20

def focus_app(app: str) -> ToolResult:
    # Requires PyGetWindow or similar. Implementing a simple fallback for now.
    import pyautogui
    try:
        windows = pyautogui.getWindowsWithTitle(app)
        if windows:
            windows[0].activate()
            return ToolResult(success=True, message=f"Focused {app}.")
    except Exception as e:
        pass
    return ToolResult(success=False, message=f"Could not focus {app}.")
