import shutil
import os
import subprocess
from pathlib import Path
from app.tools.base import ToolResult
from app.agent.memory import get_alias

def _resolve_path(path_str: str) -> Path:
    # Check if it's a known alias
    alias_path = get_alias(path_str)
    if alias_path:
        return Path(alias_path)
    
    # Expand user
    p = Path(path_str).expanduser()
    if not p.is_absolute():
         # Assume relative to user home or current dir? Let's assume absolute or relative to home
         p = Path.home() / path_str
    return p

def open_file(path: str) -> ToolResult:
    p = _resolve_path(path)
    if p.exists() and p.is_file():
        os.startfile(p)
        return ToolResult(success=True, message=f"Opened file {p.name}.")
    return ToolResult(success=False, message=f"File not found: {path}.")

def open_folder(path: str) -> ToolResult:
    p = _resolve_path(path)
    if p.exists() and p.is_dir():
        os.startfile(p)
        return ToolResult(success=True, message=f"Opened folder {p.name}.")
    return ToolResult(success=False, message=f"Folder not found: {path}.")

def create_folder(path: str) -> ToolResult:
    p = _resolve_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return ToolResult(success=True, message=f"Created folder {p.name}.")

def delete_file(path: str) -> ToolResult:
    p = _resolve_path(path)
    if not p.exists():
        return ToolResult(success=False, message=f"Could not find {path} to delete.")
    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return ToolResult(success=True, message=f"Deleted {p.name}.")
    except Exception as e:
        return ToolResult(success=False, message=f"Failed to delete {path}. Error: {str(e)}")

def find_file(query: str) -> ToolResult:
    # A fast, shallow search in typical user directories
    search_dirs = [Path.home() / "Documents", Path.home() / "Downloads", Path.home() / "Desktop"]
    found = []
    for d in search_dirs:
        if not d.exists(): continue
        for p in d.rglob(f"*{query}*"):
            if p.is_file():
                found.append(str(p))
                if len(found) > 5:
                    break
        if len(found) > 5:
            break
            
    if found:
        return ToolResult(success=True, message=f"Found {len(found)} files matching {query}.", data={"files": found})
    return ToolResult(success=False, message=f"Could not find any file matching {query}.")
