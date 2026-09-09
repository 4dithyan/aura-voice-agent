import os
import sys
from colorama import Fore

def require_manual_confirmation(action_description: str) -> bool:
    """
    Prompts the user for manual terminal confirmation before executing a dangerous action.
    """
    print(Fore.RED + "\n" + "!" * 50)
    print(Fore.RED + f"SECURITY ALERT: CONFIRMATION REQUIRED")
    print(Fore.YELLOW + f"The agent is attempting to: {action_description}")
    print(Fore.RED + "!" * 50)
    
    while True:
        try:
            choice = input(Fore.CYAN + "Allow this action? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                print(Fore.GREEN + "Action approved by user.")
                return True
            elif choice in ['n', 'no', '']:
                print(Fore.YELLOW + "Action denied by user.")
                return False
            else:
                print("Please enter 'y' or 'n'.")
        except (KeyboardInterrupt, EOFError):
            print(Fore.YELLOW + "\nAction denied by user (interrupted).")
            return False
