import sys
from colorama import Fore
import time
from app.voice.microphone import record_audio
from app.voice.speech_to_text import transcribe
from app.voice.text_to_speech import speak
from app.agent.agent import process_command
from app.agent.ollama_client import check_ollama, get_default_model

def main():
    print(Fore.CYAN + "==================================================")
    print(Fore.CYAN + "JARVIS LOCAL AGENT")
    print(Fore.CYAN + "Status: READY")
    
    try:
        model = get_default_model()
        print(Fore.GREEN + f"AI: Qwen via Ollama (Model: {model})")
    except RuntimeError as e:
        print(Fore.RED + str(e))
        sys.exit(1)
        
    print(Fore.GREEN + "STT: faster-whisper")
    print(Fore.GREEN + "TTS: Piper")
    print(Fore.CYAN + "==================================================")
    
    while True:
        try:
            print(Fore.YELLOW + "\nListening... (Press Ctrl+C to type instead)")
            # Wait for user to speak
            audio_path = record_audio()
            if not audio_path:
                continue
                
            text = transcribe(audio_path)
            if not text:
                continue
                
            from app.config.settings import WAKE_WORD_ENABLED, WAKE_WORD
            
            # Check for wake word if enabled
            if WAKE_WORD_ENABLED:
                text_lower = text.lower()
                # Check if it starts with any of the wake words (if we make it a list)
                wake_words = [w.strip() for w in WAKE_WORD.split(",")]
                matched_wake_word = None
                
                for word in wake_words:
                    if text_lower.startswith(word):
                        matched_wake_word = word
                        break
                
                if not matched_wake_word:
                    # Ignore speech that doesn't start with the wake word
                    continue
                    
                # Strip the wake word from the command
                text = text[len(matched_wake_word):].strip()
                if not text:
                    continue # They just said the wake word and nothing else
                    
            print(Fore.WHITE + f"You: {text}")
            
            if text.lower().strip() in ["stop", "exit", "quit", "jarvis stop"]:
                 print(Fore.CYAN + "Jarvis: Goodbye.")
                 break
                 
            response = process_command(text)
            
            if response:
                 speak(response)
                 
        except KeyboardInterrupt:
            # Fallback to text input
            try:
                text = input(Fore.YELLOW + "\nYou (text): ").strip()
                if not text:
                    continue
                if text.lower() in ["stop", "exit", "quit"]:
                    print(Fore.CYAN + "Jarvis: Goodbye.")
                    break
                    
                response = process_command(text)
                if response:
                    speak(response)
            except (KeyboardInterrupt, EOFError):
                 print("\nExiting...")
                 break
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()
