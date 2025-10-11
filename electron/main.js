// electron/main.js
const { app, BrowserWindow, Tray, Menu, nativeImage } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

class FortunaDesktopApp {
  constructor() {
    this.backendProcess = null;
    this.frontendProcess = null;
    this.mainWindow = null;
    this.tray = null;
  }

  async startBackend() {
    return new Promise((resolve, reject) => {
      // Corrected pathing for a packaged app
      const isDev = process.env.NODE_ENV !== 'production';
      const rootPath = isDev ? path.join(__dirname, '..') : process.resourcesPath;
      const pythonPath = path.join(rootPath, '.venv', 'Scripts', 'python.exe');
      const apiPath = path.join(rootPath, 'python_service', 'api.py');

      this.backendProcess = spawn(pythonPath, ['-m', 'uvicorn', 'api:app', '--host', '127.0.0.1', '--port', '8000'], {
        cwd: path.join(rootPath, 'python_service')
      });

      this.backendProcess.stdout.on('data', (data) => {
        console.log(`Backend STDOUT: ${data}`);
        if (data.toString().includes('Uvicorn running')) {
          console.log('Backend started successfully.');
          resolve();
        }
      });

      this.backendProcess.stderr.on('data', (data) => {
        console.error(`Backend STDERR: ${data}`);
      });

      this.backendProcess.on('error', reject);
    });
  }

  async startFrontend() {
    const isDev = process.env.NODE_ENV !== 'production';
    if (isDev) {
        // In development, we assume the Next.js dev server is already running.
        return Promise.resolve();
    } else {
        // In production, we would serve the built Next.js app.
        // This part needs a production-ready server like Express or Next.js's standalone output.
        // For now, we will assume the build is served and we just load the URL.
        return Promise.resolve();
    }
  }

  createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1600,
      height: 1000,
      title: 'Fortuna Faucet - Racing Analysis',
      icon: path.join(__dirname, 'assets', 'icon.ico'),
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      },
      autoHideMenuBar: true,
      backgroundColor: '#1a1a2e'
    });

    // In development, load from the Next.js dev server.
    this.mainWindow.loadURL('http://localhost:3000');
  }

  createSystemTray() {
    const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
    const icon = nativeImage.createFromPath(iconPath);
    this.tray = new Tray(icon.resize({ width: 16, height: 16 }));

    const contextMenu = Menu.buildFromTemplate([
      { label: 'Open Dashboard', click: () => this.mainWindow.show() },
      { type: 'separator' },
      { label: 'Exit', click: () => app.quit() }
    ]);

    this.tray.setToolTip('Fortuna Faucet - Monitoring Races');
    this.tray.setContextMenu(contextMenu);
  }

  async initialize() {
    console.log('Starting Fortuna Faucet backend...');
    await this.startBackend();

    console.log('Frontend server is assumed to be running in dev mode...');
    await this.startFrontend();

    // Wait for frontend to be ready
    await new Promise(resolve => setTimeout(resolve, 5000));

    this.createMainWindow();
    this.createSystemTray();
  }

  cleanup() {
    console.log('Cleaning up processes...');
    if (this.backendProcess) this.backendProcess.kill();
    if (this.frontendProcess) this.frontendProcess.kill();
  }
}

let fortunaApp;

app.whenReady().then(() => {
  fortunaApp = new FortunaDesktopApp();
  fortunaApp.initialize();
});

app.on('window-all-closed', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (process.platform !== 'darwin') {
    // Do not quit here, let it run in the tray
  }
});

app.on('before-quit', () => {
  if(fortunaApp) {
    fortunaApp.cleanup();
  }
});
