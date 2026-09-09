import re

# Simple keyword to intent mappings for fast execution
ROUTER_RULES = [
    (re.compile(r"^open\s+(.+)$", re.IGNORECASE), "open_app", ["app"]),
    (re.compile(r"^close\s+(.+)$", re.IGNORECASE), "close_app", ["app"]),
    (re.compile(r"^(increase|volume)\s+up$", re.IGNORECASE), "press_key", ["volumeup"]),
    (re.compile(r"^(decrease|volume)\s+down$", re.IGNORECASE), "press_key", ["volumedown"]),
    (re.compile(r"^mute$", re.IGNORECASE), "mute", []),
    (re.compile(r"^take\s+(a\s+)?screenshot$", re.IGNORECASE), "take_screenshot", []),
    (re.compile(r"^lock\s+(computer|pc)$", re.IGNORECASE), "lock_pc", []),
]

def fast_route(user_input: str) -> list:
    """
    Attempts to route simple commands without calling the LLM.
    Returns a list of intents if a match is found, otherwise empty list.
    """
    user_input = user_input.strip()
    
    # If the command is complex, send it straight to the LLM (Qwen)
    if " and " in user_input.lower() or " search " in user_input.lower() or " on " in user_input.lower():
        return []
    
    # Very simple exact matches
    if user_input.lower() in ["mute", "mute volume"]:
        return [{"tool": "mute", "arguments": {}}]
    if user_input.lower() in ["unmute"]:
        return [{"tool": "unmute", "arguments": {}}]
    if user_input.lower() in ["volume up"]:
        return [{"tool": "press_key", "arguments": {"key": "volumeup"}}]
    if user_input.lower() in ["volume down"]:
        return [{"tool": "press_key", "arguments": {"key": "volumedown"}}]
    if user_input.lower() in ["take a screenshot", "take screenshot", "screenshot"]:
        return [{"tool": "take_screenshot", "arguments": {}}]
    if user_input.lower() in ["lock pc", "lock computer", "lock screen"]:
        return [{"tool": "lock_pc", "arguments": {}}]
    if user_input.lower() in ["open browser", "open internet", "open the browser"]:
        return [{"tool": "open_browser", "arguments": {}}]
        
    for pattern, tool, arg_keys in ROUTER_RULES:
        match = pattern.match(user_input)
        if match:
            args = {}
            for i, key in enumerate(arg_keys):
                if key == "volumeup" or key == "volumedown":
                     args["key"] = key
                else:
                    args[key] = match.group(i + 1).strip()
            return [{"tool": tool, "arguments": args}]
            
    return []
