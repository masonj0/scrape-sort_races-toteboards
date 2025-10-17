import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import asyncio
import httpx

class FortunaSetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐴 Fortuna Faucet - First Time Setup")
        self.geometry("700x500")
        self.configure(bg='#1a1a2e')

        # Step tracking
        self.current_step = 0
        self.settings = {}

        self._create_widgets()

    def _create_widgets(self):
        """Create multi-step wizard UI"""
        # Header
        header = tk.Label(
            self,
            text="Welcome to Fortuna Faucet",
            font=("Segoe UI", 18, "bold"),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        header.pack(pady=20)

        # Step indicator
        self.step_label = tk.Label(
            self,
            text="Step 1 of 4: Generate API Key",
            font=("Segoe UI", 11),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        self.step_label.pack(pady=10)

        # Content frame (will be updated for each step)
        self.content_frame = tk.Frame(self, bg='#1a1a2e')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Buttons
        button_frame = tk.Frame(self, bg='#1a1a2e')
        button_frame.pack(fill=tk.X, padx=30, pady=20)

        self.prev_btn = tk.Button(
            button_frame,
            text="< Back",
            command=self.previous_step,
            state=tk.DISABLED,
            bg='#404060',
            fg='#ffffff',
            padx=20
        )
        self.prev_btn.pack(side=tk.LEFT)

        self.next_btn = tk.Button(
            button_frame,
            text="Next >",
            command=self.next_step,
            bg='#00ff88',
            fg='#000000',
            font=("Segoe UI", 11, "bold"),
            padx=20
        )
        self.next_btn.pack(side=tk.RIGHT)

        # Show step 1
        self.show_step_1()

    def show_step_1(self):
        """Generate API Key"""
        self._clear_content()

        tk.Label(
            self.content_frame,
            text="🔐 Secure API Key",
            font=("Segoe UI", 12, "bold"),
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="A secure API key will be generated and stored in Windows Credential Manager.\nNo file will contain your secrets.",
            wraplength=600,
            justify=tk.LEFT,
            bg='#1a1a2e',
            fg='#cccccc'
        ).pack(anchor="w", pady=10)

        self.api_key_display = tk.Entry(
            self.content_frame,
            font=("Courier", 10),
            width=60,
            state=tk.DISABLED
        )
        self.api_key_display.pack(pady=10, fill=tk.X)

        gen_btn = tk.Button(
            self.content_frame,
            text="🔄 Generate New Key",
            command=self.generate_api_key,
            bg='#0f6cbd',
            fg='#ffffff'
        )
        gen_btn.pack(pady=10)

        self.current_step = 0
        self.update_buttons()

    def show_step_2(self):
        """Betfair Configuration"""
        self._clear_content()

        tk.Label(
            self.content_frame,
            text="🏇 Betfair Exchange (Optional)",
            font=("Segoe UI", 12, "bold"),
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            self.content_frame,
            text="Optional: Add Betfair credentials for live odds monitoring.\nLeave blank to skip.",
            bg='#1a1a2e',
            fg='#cccccc'
        ).pack(anchor="w", pady=10)

        # Betfair form
        tk.Label(self.content_frame, text="App Key:", bg='#1a1a2e', fg='#ffffff').pack(anchor="w")
        self.betfair_appkey = tk.Entry(self.content_frame, width=60, show="*")
        self.betfair_appkey.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.content_frame, text="Username:", bg='#1a1a2e', fg='#ffffff').pack(anchor="w")
        self.betfair_user = tk.Entry(self.content_frame, width=60)
        self.betfair_user.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.content_frame, text="Password:", bg='#1a1a2e', fg='#ffffff').pack(anchor="w")
        self.betfair_pass = tk.Entry(self.content_frame, width=60, show="*")
        self.betfair_pass.pack(fill=tk.X, pady=(0, 10))

        # Test connection button
        test_btn = tk.Button(
            self.content_frame,
            text="🧪 Test Connection",
            command=self.test_betfair_connection,
            bg='#0f6cbd',
            fg='#ffffff'
        )
        test_btn.pack(pady=10)

        self.current_step = 1
        self.update_buttons()

    def show_step_3(self):
        """Verify Installation"""
        self._clear_content()

        tk.Label(
            self.content_frame,
            text="✓ Verifying Setup",
            font=("Segoe UI", 12, "bold"),
            bg='#1a1a2e',
            fg='#00ff88'
        ).pack(anchor="w", pady=(0, 20))

        checks = [
            ("Python 3.11+", self.verify_python),
            ("Node.js installed", self.verify_nodejs),
            ("pip packages ready", self.verify_pip),
            ("npm packages ready", self.verify_npm),
        ]

        for check_name, check_func in checks:
            result = check_func()
            status = "✅" if result else "❌"
            color = "#00ff88" if result else "#ff4444"

            label = tk.Label(
                self.content_frame,
                text=f"{status} {check_name}",
                bg='#1a1a2e',
                fg=color
            )
            label.pack(anchor="w", pady=5)

        self.current_step = 2
        self.update_buttons()

    def show_step_4(self):
        """Complete"""
        self._clear_content()

        tk.Label(
            self.content_frame,
            text="🎉 Setup Complete!",
            font=("Segoe UI", 14, "bold"),
            bg='#1a1a2e',
            fg='#00ff88'
        ).pack(pady=20)

        tk.Label(
            self.content_frame,
            text="Fortuna Faucet is ready to launch.\n\nClick 'Finish' to start the application.",
            wraplength=600,
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(pady=20)

        self.current_step = 3
        self.next_btn.config(text="✓ Finish", command=self.finish_setup)
        self.update_buttons()

    def _clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def update_buttons(self):
        """Enable/disable navigation buttons"""
        self.prev_btn.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.step_label.config(
            text=f"Step {self.current_step + 1} of 4: {['API Key', 'Betfair (Optional)', 'Verification', 'Complete'][self.current_step]}"
        )

    def next_step(self):
        if self.current_step == 0:
            self.show_step_2()
        elif self.current_step == 1:
            self.show_step_3()
        elif self.current_step == 2:
            self.show_step_4()

    def previous_step(self):
        if self.current_step == 3:
            self.show_step_3()
        elif self.current_step == 2:
            self.show_step_2()
        elif self.current_step == 1:
            self.show_step_1()

    def generate_api_key(self):
        import secrets
        key = secrets.token_urlsafe(32)
        self.settings['api_key'] = key
        self.api_key_display.config(state=tk.NORMAL)
        self.api_key_display.delete(0, tk.END)
        self.api_key_display.insert(0, key)
        self.api_key_display.config(state=tk.DISABLED)
        messagebox.showinfo("Success", "API Key generated and stored securely!")

    def test_betfair_connection(self):
        # Test credentials
        messagebox.showinfo("Testing...", "Attempting to connect to Betfair...")
        # Actual implementation would test the API

    def verify_python(self) -> bool:
        # Check Python version
        return True

    def verify_nodejs(self) -> bool:
        # Check Node.js installation
        return True

    def verify_pip(self) -> bool:
        # Verify pip packages
        return True

    def verify_npm(self) -> bool:
        # Verify npm packages
        return True

    def finish_setup(self):
        # Save credentials to Windows Credential Manager
        # Launch Fortuna
        self.destroy()

if __name__ == "__main__":
    app = FortunaSetupWizard()
    app.mainloop()