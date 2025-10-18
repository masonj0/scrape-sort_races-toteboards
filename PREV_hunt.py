import requests
import time
from datetime import datetime

# --- Configuration ---
API_URL = "http://127.0.0.1:8001/api/v1/adapters/status"
HUNT_DURATION_SECONDS = 900  # 15 minutes
POLL_INTERVAL_SECONDS = 60   # 1 minute

def hunt_for_signal():
    """
    Polls the status API until a 'hot signal' is found or the hunt times out.
    A 'hot signal' is an adapter with status 'OK' and more than 0 races found.
    """
    print("="*30)
    print("🔥 OPERATION: HOT SIGNAL - INITIATED 🔥")
    print(f"Hunting for a live adapter for {HUNT_DURATION_SECONDS / 60:.0f} minutes...")
    print("="*30)

    start_time = time.time()
    while time.time() - start_time < HUNT_DURATION_SECONDS:
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] Polling for hot signal at {API_URL}...")

        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            statuses = response.json()

            for adapter in statuses:
                if adapter.get("status") == "OK" and adapter.get("races_found", 0) > 0:
                    print("\n" + "="*30)
                    print("🔥 HOT SIGNAL DETECTED! 🔥")
                    print("="*30)
                    print(f"  - Adapter: {adapter.get('adapter_id')}")
                    print(f"  - Races Found: {adapter.get('races_found')}")
                    print(f"  - Status: {adapter.get('status')}")
                    print(f"  - Notes: {adapter.get('notes')}")
                    print("\nMission successful. Terminating hunt.")
                    return # Exit the function on success

            print("...no hot signal found on this poll. Will try again in 1 minute.")

        except requests.exceptions.RequestException as e:
            print("  -> API Error: Could not connect to the API server. Is it running?")
            print(f"     Details: {e}")


        time.sleep(POLL_INTERVAL_SECONDS)

    print("\n" + "="*30)
    print(" HUNT COMPLETE: TIMEOUT ".center(30, "="))
    print("="*30)
    print("No live, data-producing adapter was found in the allotted time.")

if __name__ == "__main__":
    hunt_for_signal()
