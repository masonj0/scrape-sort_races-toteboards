import requests
import time
import subprocess
import sys
import socket
from datetime import datetime

def find_free_port():
    """Finds and returns an available port on the host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def launch_and_hunt():
    api_process = None
    cockpit_process = None
    try:
        # --- PHASE 1: Port Hunting ---
        print("="*40)
        print("OPERATION: PORT HUNTER - INITIATED".center(40))
        print("Searching for available ports...")
        api_port = find_free_port()
        cockpit_port = find_free_port()
        print(f"  - API Server will use port: {api_port}")
        print(f"  - Cockpit Server will use port: {cockpit_port}")
        print("="*40)

        # --- PHASE 2: Dynamic Server Launch ---
        api_url = f"http://127.0.0.1:{api_port}"
        status_url = f"{api_url}/api/v1/adapters/status"

        print("\nLaunching application servers...")

        # Command to launch the API server on the found port
        api_command = [
            "uvicorn",
            "src.checkmate_v7.api:app",
            "--host", "0.0.0.0",
            "--port", str(api_port)
        ]
        api_process = subprocess.Popen(api_command)

        # Command to launch the Cockpit on its found port, pointing to the new API port
        cockpit_command = [
            "python",
            "src/checkmate_v7/cockpit.py",
            "--port", str(cockpit_port),
            "--api-url", api_url
        ]
        cockpit_process = subprocess.Popen(cockpit_command)

        # --- PHASE 3: The Hunt ---
        SERVER_STARTUP_TIME_SECONDS = 15
        print(f"\nServers launched. Waiting {SERVER_STARTUP_TIME_SECONDS}s for initialization...")
        time.sleep(SERVER_STARTUP_TIME_SECONDS)

        HUNT_DURATION_SECONDS = 900
        POLL_INTERVAL_SECONDS = 60
        start_time = time.time()

        print("\n" + "="*40)
        print("🔥 HUNT FOR HOT SIGNAL - INITIATED 🔥".center(40))
        print("="*40)

        while time.time() - start_time < HUNT_DURATION_SECONDS:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] Polling for hot signal at {status_url}...")

            try:
                response = requests.get(status_url, timeout=15)
                if response.status_code == 200:
                    statuses = response.json()
                    for adapter in statuses:
                        if adapter.get("status") == "OK" and adapter.get("races_found", 0) > 0:
                            print("\n" + "="*40)
                            print("🔥 HOT SIGNAL DETECTED! 🔥".center(40))
                            print("="*40)
                            print(f"  - Adapter: {adapter.get('adapter_id')}")
                            print(f"  - Races Found: {adapter.get('races_found')}")
                            print(f"  - Status: {adapter.get('status')}")
                            print(f"  - Notes: {adapter.get('notes')}")
                            print("\nMission successful. Terminating hunt.")
                            return
                    print("...no hot signal found. Will try again in 1 minute.")
                else:
                    print(f"  -> API Warning: Received status code {response.status_code}. Retrying.")

            except requests.exceptions.RequestException as e:
                print(f"  -> API Error: Could not connect. Details: {str(e)[:100]}")

            time.sleep(POLL_INTERVAL_SECONDS)

        print("\n" + "="*40)
        print(" HUNT COMPLETE: TIMEOUT ".center(40, "="))
        print("="*40)

    finally:
        print("\n--- SHUTDOWN SEQUENCE ---")
        if api_process:
            print("Terminating API server...")
            api_process.terminate()
            api_process.wait()
            print("API server terminated.")
        if cockpit_process:
            print("Terminating Cockpit server...")
            cockpit_process.terminate()
            cockpit_process.wait()
            print("Cockpit server terminated.")
        print("-------------------------")

if __name__ == "__main__":
    launch_and_hunt()
