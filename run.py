import os
import sys
from colorama import init, Fore

# Ensure colorama works on Windows
init(autoreset=True)

def check_environment():
    print(Fore.CYAN + "==================================================")
    print(Fore.CYAN + "JARVIS LOCAL AGENT")
    print(Fore.CYAN + "==================================================")
    print("Checking system...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(Fore.RED + "x Python 3.8+ required.")
        sys.exit(1)
    else:
        print(Fore.GREEN + f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
        
    # App is modular, so we'll import here to let env checks happen first
    try:
        from app.main import main
    except ImportError as e:
        print(Fore.RED + f"x Failed to load modules. Did you run setup_windows.bat? Error: {e}")
        sys.exit(1)
        
    main()

if __name__ == "__main__":
    check_environment()
