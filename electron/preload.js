// electron/preload.js
// This script runs in a privileged environment with access to Node.js APIs.
// It's used to securely expose specific functionality to the renderer process (the web UI).

const { contextBridge, ipcRenderer } = require('electron');

// Expose a safe, limited API to the frontend.
contextBridge.exposeInMainWorld('electronAPI', {
  // Example: expose a function to send a message to the main process
  // send: (channel, data) => ipcRenderer.send(channel, data),

  // Example: expose a function to receive a message from the main process
  // on: (channel, func) => {
  //   ipcRenderer.on(channel, (event, ...args) => func(...args));
  // }
});

console.log('Preload script loaded.');
