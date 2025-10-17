import tkinter as tk
from tkinter import messagebox, filedialog
import os
import configparser

class ConfigWizard:
    def __init__(self, master):
        self.master = master
        self.master.title("Configuration Wizard")
        self.master.geometry("400x250")

        self.config = configparser.ConfigParser()
        self.config_file = 'config.ini'

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        # API Key
        tk.Label(self.master, text="API Key:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.api_key_entry = tk.Entry(self.master, width=40)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=10)

        # Output Directory
        tk.Label(self.master, text="Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.output_dir_entry = tk.Entry(self.master, width=30)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        tk.Button(self.master, text="Browse...", command=self.browse_directory).grid(row=1, column=1, padx=10, pady=10, sticky='e')

        # Log Level
        tk.Label(self.master, text="Log Level:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.log_level = tk.StringVar(self.master)
        self.log_level.set("INFO")  # default value
        log_level_options = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        tk.OptionMenu(self.master, self.log_level, *log_level_options).grid(row=2, column=1, padx=10, pady=10, sticky='w')

        # Save Button
        tk.Button(self.master, text="Save Configuration", command=self.save_config).grid(row=3, column=0, columnspan=2, pady=20)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)

    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            if 'Settings' in self.config:
                settings = self.config['Settings']
                self.api_key_entry.insert(0, settings.get('ApiKey', ''))
                self.output_dir_entry.insert(0, settings.get('OutputDir', ''))
                self.log_level.set(settings.get('LogLevel', 'INFO'))

    def save_config(self):
        api_key = self.api_key_entry.get()
        output_dir = self.output_dir_entry.get()
        log_level = self.log_level.get()

        if not api_key:
            messagebox.showerror("Error", "API Key cannot be empty.")
            return
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Please select a valid output directory.")
            return

        if 'Settings' not in self.config:
            self.config['Settings'] = {}

        self.config['Settings']['ApiKey'] = api_key
        self.config['Settings']['OutputDir'] = output_dir
        self.config['Settings']['LogLevel'] = log_level

        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            messagebox.showinfo("Success", "Configuration saved successfully.")
            self.master.destroy()
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigWizard(root)
    root.mainloop()