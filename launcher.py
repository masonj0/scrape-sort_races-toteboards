"""
CHECKMATE RACING - MASTER LAUNCHER
Creates a single entry point that orchestrates all system components.
This script is the sanctioned operational roof for the Penta-Hybrid architecture.
"""

import sys
import os
import subprocess
import webbrowser
import time
import threading
import sqlite3
from pathlib import Path

class CheckmateLauncher:
    """Master orchestrator for the Checkmate Racing System"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.db_path = self.base_path / "shared_database" / "races.db" # Corrected DB name
        self.processes = []

    def initialize_database(self):
        """Initialize SQLite database with all schemas"""
        print("📊 Initializing database...")
        # All schemas must be applied for all platforms to function.
        schema_paths = [
            self.base_path / "shared_database" / "schema.sql",
            self.base_path / "shared_database" / "web_schema.sql"
        ]

        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.db_path))
        for schema_path in schema_paths:
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
                print(f"✓ Schema applied: {schema_path.name}")
            else:
                print(f"⚠ Warning: Schema file not found at {schema_path}")
        conn.close()
        print("✓ Database initialization complete.")

    def start_python_service(self):
        """Start the Python data collection service"""
        print("🐍 Starting Python Collection Corps...")
        service_main = self.base_path / "python_service" / "main.py"
        if service_main.exists():
            process = subprocess.Popen([sys.executable, "-m", "python_service.main"], cwd=str(self.base_path))
            self.processes.append(("Python Service", process))
            print("✓ Python service started.")
            return True
        else:
            print("❌ FATAL: python_service/main.py not found. Cannot start.")
            return False

    def start_typescript_api(self):
        """Start the TypeScript API gateway"""
        print("📡 Starting TypeScript API Gateway...")
        api_path = self.base_path / "web_platform" / "api_gateway"
        if (api_path / "src" / "server.ts").exists():
            process = subprocess.Popen(["npm", "start"], cwd=str(api_path), shell=True)
            self.processes.append(("TypeScript API", process))
            print("✓ API Gateway started.")
            return True
        return False

    def start_web_frontend(self):
        """Start the Next.js frontend"""
        print("🌐 Starting TypeScript Live Cockpit (Frontend)...")
        frontend_path = self.base_path / "web_platform" / "frontend"
        if (frontend_path / "app" / "page.tsx").exists():
            process = subprocess.Popen(["npm", "run", "dev"], cwd=str(frontend_path), shell=True)
            self.processes.append(("Web Frontend", process))
            print("✓ Web Frontend started.")
            self.open_browser()
            return True
        return False

    def start_csharp_desktop(self):
        """Launch the C# desktop application"""
        print("🖥️  Launching C# Command Deck...")
        desktop_exe = self.base_path / "desktop_app" / "bin" / "Release" / "net6.0-windows" / "CheckmateDeck.exe" # Adjusted for modern .NET path
        if desktop_exe.exists():
            process = subprocess.Popen([str(desktop_exe)], cwd=str(desktop_exe.parent))
            self.processes.append(("C# Desktop", process))
            print("✓ C# Command Deck launched.")
            return True
        print("ℹ️  Note: C# Command Deck not built. Run build_all.bat to create it.")
        return False

    def open_browser(self):
        """Open browser to the web interface"""
        url = 'http://localhost:3000'
        print(f"🚀 Opening browser to {url} in 5 seconds...")
        threading.Timer(5, lambda: webbrowser.open(url)).start()

    def monitor_services(self):
        """Monitor running services"""
        print("\n" + "="*60)
        print("✅ CHECKMATE V8 PENTA-HYBRID SYSTEM IS RUNNING")
        print("="*60)
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down all services...")
            self.shutdown()

    def shutdown(self):
        """Gracefully shutdown all components"""
        for name, process in reversed(self.processes):
            if process.poll() is None:
                print(f"   Terminating {name}...")
                process.terminate()
        time.sleep(2) # Give processes time to exit
        for name, process in reversed(self.processes):
            if process.poll() is None:
                print(f"   Killing unresponsive process: {name}...")
                process.kill()
        print("\n✅ All services stopped. Goodbye!")

    def launch(self):
        """Main launch sequence"""
        self.initialize_database()
        if not self.start_python_service():
            return
        time.sleep(3)
        self.start_typescript_api()
        time.sleep(3)
        self.start_web_frontend()
        self.start_csharp_desktop()
        self.monitor_services()

if __name__ == "__main__":
    CheckmateLauncher().launch()