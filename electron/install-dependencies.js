// electron/install-dependencies.js
// This script is executed by the MSI installer to set up the environment.
const { execSync } = require('child_process');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const PYTHON_SERVICE_DIR = path.join(ROOT_DIR, 'python_service');
const FRONTEND_DIR = path.join(ROOT_DIR, 'web_platform', 'frontend');

function log(message) {
    console.log(`[INSTALLER] ${message}`);
}

function runCommand(command, cwd) {
    log(`Executing: ${command} in ${cwd}`);
    try {
        execSync(command, { cwd, stdio: 'inherit' });
        log(`SUCCESS: ${command}`);
    } catch (error) {
        log(`ERROR: Command failed: ${command}`);
        log(error.message);
        // In a real scenario, you might want to throw to halt installation
    }
}

log('--- Starting Fortuna Faucet Dependency Installation ---');

// 1. Install Python Dependencies
log('Step 1: Installing Python dependencies...');
const venvPython = path.join(ROOT_DIR, '.venv', 'Scripts', 'python.exe');
runCommand(`"${venvPython}" -m pip install -r requirements.txt`, PYTHON_SERVICE_DIR);

// 2. Install Frontend Dependencies
log('Step 2: Installing Frontend dependencies...');
runCommand('npm install', FRONTEND_DIR);

log('--- Dependency Installation Complete ---');