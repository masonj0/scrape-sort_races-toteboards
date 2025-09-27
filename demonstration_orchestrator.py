# demonstration_orchestrator.py
# A robust, self-contained script to demonstrate the full application pipeline.

import subprocess
import time
import os
import signal
import sys

def print_header(title):
    """Prints a formatted header."""
    print("\n" + "="*80)
    print(f"--- {title}")
    print("="*80)

def main():
    """
    Orchestrates the execution of the Python service and the API gateway,
    captures their output, and queries the final endpoint to demonstrate
    the end-to-end data pipeline.
    """
    api_gateway_log = "api_gateway.log"
    python_service_log = "python_service.log"

    # Clean up old log files
    if os.path.exists(api_gateway_log): os.remove(api_gateway_log)
    if os.path.exists(python_service_log): os.remove(python_service_log)

    # --- Step 1: Run the Python Data Collection Service ---
    print_header("STEP 1: EXECUTING PYTHON DATA COLLECTION SERVICE")
    try:
        # We run this as a blocking call first to ensure the database is populated.
        python_command = [sys.executable, "run_python_service_demonstration.py"]
        python_process = subprocess.run(
            python_command,
            capture_output=True,
            text=True,
            check=True, # Raise an exception if it fails
            cwd=os.path.dirname(os.path.abspath(__file__)) # Run from project root
        )
        with open(python_service_log, "w") as f:
            f.write("--- STDOUT ---\n")
            f.write(python_process.stdout)
            f.write("\n--- STDERR ---\n")
            f.write(python_process.stderr)
        print("Python service executed successfully. See python_service.log for details.")
    except subprocess.CalledProcessError as e:
        print(f"FATAL: Python service script failed with exit code {e.returncode}.")
        print("\n--- STDERR ---")
        print(e.stderr)
        sys.exit(1)

    # --- Step 2: Start the TypeScript API Gateway ---
    print_header("STEP 2: STARTING TYPESCRIPT API GATEWAY")
    api_gateway_process = None
    try:
        api_command = [
            "./web_platform/api_gateway/node_modules/.bin/ts-node",
            "./web_platform/api_gateway/src/server.ts"
        ]
        log_file = open(api_gateway_log, "w")
        # Start as a non-blocking background process
        api_gateway_process = subprocess.Popen(
            api_command,
            stdout=log_file,
            stderr=log_file,
            preexec_fn=os.setsid # To kill the whole process group later
        )
        print(f"API Gateway started in the background (PID: {api_gateway_process.pid}).")
    except Exception as e:
        print(f"FATAL: Failed to start API Gateway: {e}")
        if os.path.exists(api_gateway_log):
            with open(api_gateway_log, "r") as f:
                print("\n--- LOGS ---")
                print(f.read())
        sys.exit(1)

    # --- Step 3: Wait for Services and Query API ---
    print_header("STEP 3: WAITING FOR API INITIALIZATION & QUERYING ENDPOINT")
    print("Waiting 15 seconds for the API server to initialize...")
    time.sleep(15)

    try:
        curl_command = ["curl", "-s", "http://localhost:8080/api/races/qualified"]
        print(f"Executing: {' '.join(curl_command)}")
        api_response = subprocess.check_output(curl_command, text=True)

        print_header("FINAL API RESPONSE (from /api/races/qualified)")
        print(api_response)

    except subprocess.CalledProcessError as e:
        print(f"ERROR: curl command failed with exit code {e.returncode}")
        print("\n--- STDERR ---")
        print(e.stderr)
    except Exception as e:
        print(f"ERROR: An exception occurred while querying the API: {e}")

    # --- Step 4: Shutdown and Cleanup ---
    finally:
        print_header("STEP 4: SHUTTING DOWN SERVICES")
        if api_gateway_process:
            print(f"Terminating API Gateway process group (PGID: {os.getpgid(api_gateway_process.pid)})...")
            os.killpg(os.getpgid(api_gateway_process.pid), signal.SIGTERM)
            api_gateway_process.wait(timeout=5)
            print("API Gateway shut down.")

        print("\nDemonstration complete. Final logs are in:")
        print(f"- {python_service_log}")
        print(f"- {api_gateway_log}")

if __name__ == "__main__":
    main()