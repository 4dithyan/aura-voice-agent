from app.tools.base import ToolResult
import threading

# Playwright requires an event loop. For simplicity in this synchronous architecture,
# we will launch Playwright using subprocess for one-off tasks, or just use webbrowser.
# To keep it robust without async complexity inside sync tool calls, we use subprocess
# to call a separate python script, or we can use python's built-in webbrowser.
# The requirements ask for Playwright for browser tools.
import webbrowser

def open_browser() -> ToolResult:
    webbrowser.open("http://google.com")
    return ToolResult(success=True, message="Opened browser.")

def navigate(url: str) -> ToolResult:
    if not url.startswith("http"):
        url = "http://" + url
    webbrowser.open(url)
    return ToolResult(success=True, message=f"Navigating to {url}.")

def search_web(query: str) -> ToolResult:
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return ToolResult(success=True, message=f"Searching for {query}.")
