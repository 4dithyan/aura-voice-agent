# JARVIS Local PC Agent

A fully local, offline-capable, voice-controlled Windows PC management agent.

## Architecture
- **Language**: Python 3.10+
- **LLM Engine**: Ollama (local) with Qwen model
- **Speech-to-Text (STT)**: `faster-whisper`
- **Text-to-Speech (TTS)**: Piper TTS
- **PC Control**: PyAutoGUI, psutil, built-in libraries
- **Browser Automation**: Webbrowser / Playwright (future expansion)

## Installation

1. Ensure you have **Python 3.10+** installed and added to your PATH.
2. Ensure you have [Ollama](https://ollama.com) installed and running locally.
3. Download a Qwen model in Ollama: `ollama run qwen2.5:0.5b` (or another small variant).
4. Run the setup script:
   ```cmd
   setup_windows.bat
   ```
   This script will:
   - Create a virtual environment.
   - Install all required Python packages.
   - Download Piper TTS binaries and a default voice model.
   - Create required directories.

## Configuration
Edit `.env` to configure your agent:
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL= # Leave blank to auto-detect a Qwen model
WHISPER_MODEL=tiny
TTS_ENABLED=true
CONFIRM_DANGEROUS_ACTIONS=true
```

## Running Jarvis
```cmd
python run.py
```
Jarvis will start listening. Speak your command, or press `Ctrl+C` once to type your command in the terminal.

## Safety & Security
Dangerous actions (like deleting files, shutting down, or running complex terminal commands) require **manual terminal confirmation**. When such an action is attempted, Jarvis will pause and prompt you with `[y/N]` in the terminal.

## Supported Commands
- **App Control**: "Open Chrome", "Close Spotify", "Focus VS Code"
- **System**: "Mute volume", "Increase volume", "Lock my PC", "Sleep"
- **Files**: "Open my Downloads folder", "Find files matching invoice"
- **Peripherals**: "Take a screenshot", "Type hello world"

## Future Expansions
- **Vision Integration**: Screen analysis tools can be added to V2 by integrating an LLaVA model into Ollama and passing screenshots to it.
- **Wake Word**: Continuous low-power listening for "Hey Jarvis" can be added using Porcupine or specific whisper stream pipelines.
- **Web UI**: A FastAPI backend can be connected to the existing `process_command` function to serve a React/Next.js dashboard.
