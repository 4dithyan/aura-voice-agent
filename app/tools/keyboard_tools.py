import pyautogui
from app.tools.base import ToolResult

def type_text(text: str) -> ToolResult:
    pyautogui.write(text, interval=0.05)
    return ToolResult(success=True, message=f"Typed text.")

def press_key(key: str) -> ToolResult:
    pyautogui.press(key)
    return ToolResult(success=True, message=f"Pressed {key}.")

def hotkey(keys: list) -> ToolResult:
    pyautogui.hotkey(*keys)
    return ToolResult(success=True, message=f"Pressed hotkey.")

def move_mouse(x: int, y: int) -> ToolResult:
    pyautogui.moveTo(x, y)
    return ToolResult(success=True, message="Moved mouse.")

def click() -> ToolResult:
    pyautogui.click()
    return ToolResult(success=True, message="Clicked.")

def double_click() -> ToolResult:
    pyautogui.doubleClick()
    return ToolResult(success=True, message="Double clicked.")

def right_click() -> ToolResult:
    pyautogui.rightClick()
    return ToolResult(success=True, message="Right clicked.")

def scroll(amount: int) -> ToolResult:
    pyautogui.scroll(amount)
    return ToolResult(success=True, message="Scrolled.")
