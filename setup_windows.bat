@echo off
setlocal

echo ==================================================
echo JARVIS LOCAL AGENT SETUP
echo ==================================================

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10+.
    exit /b 1
)

echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

echo Installing Playwright browsers...
playwright install

echo Creating .env file...
if not exist ".env" (
    copy .env.example .env
)

echo Checking Ollama installation...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not running on localhost:11434. Please ensure Ollama is installed and running.
) else (
    echo Ollama is running. Available models:
    ollama list
)

echo Creating directories...
mkdir models\piper 2>nul
mkdir data 2>nul
mkdir logs 2>nul

echo Downloading Piper TTS binaries...
if not exist "models\piper\piper.exe" (
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip' -OutFile 'models\piper.zip'"
    powershell -Command "Expand-Archive -Path 'models\piper.zip' -DestinationPath 'models\piper_extracted' -Force"
    xcopy /y /e /i models\piper_extracted\piper\* models\piper\
    rmdir /s /q models\piper_extracted
    del models\piper.zip
    echo Piper TTS downloaded to D drive.
) else (
    echo Piper TTS already installed.
)

echo Downloading Piper voice model...
if not exist "models\piper\en_US-lessac-medium.onnx" (
    powershell -Command "Invoke-WebRequest -Uri 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true' -OutFile 'models\piper\en_US-lessac-medium.onnx'"
    powershell -Command "Invoke-WebRequest -Uri 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json?download=true' -OutFile 'models\piper\en_US-lessac-medium.onnx.json'"
) else (
    echo Voice model already downloaded.
)

echo ==================================================
echo Setup Complete!
echo You can now run the agent with: python run.py
echo ==================================================
pause
