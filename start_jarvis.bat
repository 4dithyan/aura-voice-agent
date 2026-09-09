@echo off
setlocal

echo Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found. Please run setup_windows.bat first.
    pause
    exit /b 1
)

echo Starting Jarvis...
python run.py

pause
