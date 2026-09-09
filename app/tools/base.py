from typing import Any, Dict
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = {}
