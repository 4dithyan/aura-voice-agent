import pyautogui
from datetime import datetime
from pathlib import Path
from app.tools.base import ToolResult

def take_screenshot() -> ToolResult:
    # Save to Pictures/Jarvis
    pics_dir = Path.home() / "Pictures" / "Jarvis"
    pics_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = pics_dir / f"screenshot_{timestamp}.png"
    
    try:
        pyautogui.screenshot(str(filepath))
        return ToolResult(success=True, message="Screenshot saved.", data={"path": str(filepath)})
    except Exception as e:
        return ToolResult(success=False, message=f"Failed to take screenshot. Error: {str(e)}")
