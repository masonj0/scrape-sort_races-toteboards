# launcher.py
# Provides enhanced, color-coded feedback for the Windows launch process.
import subprocess
import time
from colorama import Fore, Style, init

init(autoreset=True)

def print_header(text):
    print(Fore.CYAN + Style.BRIGHT + f"\n{'='*50}\n{text.center(50)}\n{'='*50}")

def print_step(num, total, text):
    print(Fore.YELLOW + Style.BRIGHT + f"\n[{num}/{total}] {text}")

def print_info(text):
    print(Fore.WHITE + f"    -> {text}")

def print_success(text):
    print(Fore.GREEN + Style.BRIGHT + f"\n{text}")

if __name__ == "__main__":
    print_header("FORTUNA FAUCET LAUNCHER")

    print_step(1, 3, "Starting Python Backend Server...")
    subprocess.Popen('start "Python Backend" cmd /k "uvicorn python_service.api:app --reload"', shell=True)
    print_info("Backend process launched in a new window.")

    print_step(2, 3, "Starting Frontend Development Server...")
    subprocess.Popen('start "Frontend" cmd /k "cd web_platform/frontend && npm run dev"', shell=True)
    print_info("Frontend process launched in a new window.")
    print_info("IMPORTANT: Look in the 'Frontend' window for a 'ready' message.")

    print_step(3, 3, "Waiting for services to initialize...")
    time.sleep(15)

    print_info("Launching Command Deck in your browser at http://localhost:3000")
    subprocess.Popen('start http://localhost:3000', shell=True)

    print_success("All services are running.")
