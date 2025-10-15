# setup_wizard.py - Enhanced Version
import os
from pathlib import Path
import getpass
import secrets
import requests
from datetime import datetime
import shutil

class SetupWizard:
    def __init__(self):
        self.config = {}
        self.env_file = Path('.env')

    def run(self):
        print("\n" + "="*60)
        print("   Fortuna Faucet Setup Wizard v2.0")
        print("="*60 + "\n")

        # Backup existing config
        if self.env_file.exists():
            backup_path = self.env_file.with_suffix('.env.backup')
            print(f"📋 Creating backup at {backup_path}")
            shutil.copy2(self.env_file, backup_path)

        print("\n🔧 Step 1: Core Configuration")
        print("-" * 60)
        self._configure_core()

        print("\n🔑 Step 2: Betfair API (Required for Live Monitoring)")
        print("-" * 60)
        self._configure_betfair()

        print("\n📊 Step 3: Optional Data Sources")
        print("-" * 60)
        self._configure_optional_sources()

        self._write_config()
        self._validate_config()
        self._display_summary()

    def _configure_core(self):
        """Configure essential settings"""
        print("\nGenerating secure API key...")
        api_key = secrets.token_urlsafe(32)
        self.config['API_KEY'] = api_key
        print(f"✅ API Key generated: {api_key[:8]}...{api_key[-8:]}")

    def _configure_betfair(self):
        """Configure Betfair Exchange API with validation"""
        print("\n📖 Betfair provides live odds data.")
        print("🔗 Get credentials at: https://docs.developer.betfair.com\n")

        configure = input("Configure Betfair now? (Y/n): ").lower()
        if configure != 'n':
            self.config['BETFAIR_APP_KEY'] = input("App Key: ").strip()
            self.config['BETFAIR_USERNAME'] = input("Username: ").strip()
            self.config['BETFAIR_PASSWORD'] = getpass.getpass("Password: ").strip()

            if input("Test connection now? (Y/n): ").lower() != 'n':
                if self._test_betfair_connection():
                    print("✅ Betfair connection successful")
                else:
                    print("⚠️ Betfair connection failed - please verify credentials")
        else:
            self.config['BETFAIR_APP_KEY'] = ""
            self.config['BETFAIR_USERNAME'] = ""
            self.config['BETFAIR_PASSWORD'] = ""
            print("⏭️  Skipped - Live monitoring will be disabled")

    def _configure_optional_sources(self):
        """Configure optional data sources"""
        print("\nOptional: The Racing API (UK/Ireland data)")

        configure = input("Configure The Racing API? (y/N): ").lower()
        if configure == 'y':
            self.config['THE_RACING_API_KEY'] = input("API Key: ").strip()
        else:
            self.config['THE_RACING_API_KEY'] = ""

        print("\nOptional: TVG API (US data)")
        configure = input("Configure TVG API? (y/N): ").lower()
        if configure == 'y':
            self.config['TVG_API_KEY'] = input("API Key: ").strip()
        else:
            self.config['TVG_API_KEY'] = ""

    def _test_betfair_connection(self):
        """Test Betfair API connection"""
        try:
            auth_url = "https://identitysso.betfair.com/api/login"
            headers = {
                'X-Application': self.config['BETFAIR_APP_KEY'],
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            payload = f"username={self.config['BETFAIR_USERNAME']}&password={self.config['BETFAIR_PASSWORD']}"

            response = requests.post(auth_url, headers=headers, data=payload, timeout=10)
            data = response.json()

            return data.get('status') == 'SUCCESS'
        except Exception as e:
            print(f"Connection test error: {e}")
            return False

    def _write_config(self):
        """Write configuration to .env file"""
        with open(self.env_file, 'w') as f:
            f.write("# Fortuna Faucet Configuration\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

            f.write("# --- Core Settings ---\n")
            f.write(f"API_KEY=\"{self.config['API_KEY']}\"\n\n")

            f.write("# --- Betfair Exchange ---\n")
            f.write(f"BETFAIR_APP_KEY=\"{self.config['BETFAIR_APP_KEY']}\"\n")
            f.write(f"BETFAIR_USERNAME=\"{self.config['BETFAIR_USERNAME']}\"\n")
            f.write(f"BETFAIR_PASSWORD=\"{self.config['BETFAIR_PASSWORD']}\"\n\n")

            f.write("# --- Optional Sources ---\n")
            f.write(f"THE_RACING_API_KEY=\"{self.config.get('THE_RACING_API_KEY', '')}\"\n")
            f.write(f"TVG_API_KEY=\"{self.config.get('TVG_API_KEY', '')}\"\n")

        try:
            os.chmod(self.env_file, 0o600)
        except Exception as e:
            print(f"⚠️  Could not set file permissions: {e}")

    def _validate_config(self):
        """Validate configuration"""
        print("\n🔍 Validating configuration...")

        if not self.config['API_KEY']:
            print("❌ API Key is missing")
        else:
            print("✅ API Key configured")

        if self.config['BETFAIR_APP_KEY']:
            print("✅ Betfair configured")
        else:
            print("⚠️ Betfair not configured (optional)")

    def _display_summary(self):
        """Display setup summary"""
        print("\n" + "="*60)
        print("   ✅ Setup Complete!")
        print("="*60)
        print(f"\n📁 Configuration saved to '{self.env_file}'")
        print("\n🚀 Next Steps:")
        print("   1. Review .env file if needed")
        print("   2. Run 'INSTALL_FORTUNA.bat' to install dependencies")
        print("   3. Run 'LAUNCH_FORTUNA.bat' to launch the application")
        print("\n💡 Tip:")
        print("   Re-run this wizard anytime to update your configuration")
        print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    wizard = SetupWizard()
    try:
        wizard.run()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
