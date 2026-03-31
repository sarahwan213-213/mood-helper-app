const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const net = require('net');
const { spawn } = require('child_process');
const express = require('express');

const WEB_PORT = 3000;
const API_PORT = 5001;
let pythonProcess = null;
let mainWindow = null;

function resolveResource(...segments) {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, ...segments);
  }
  return path.join(__dirname, ...segments);
}

function getPythonExecutable() {
  const candidate1 = resolveResource('venv-embedded', 'bin', 'python3');
  const candidate2 = resolveResource('venv-embedded', 'bin', 'python');
  if (fs.existsSync(candidate1)) return candidate1;
  if (fs.existsSync(candidate2)) return candidate2;
  return 'python3';
}

function startFlaskServer() {
  return new Promise((resolve, reject) => {
    const scriptPath = resolveResource('mood_api.py');
    if (!fs.existsSync(scriptPath)) {
      return reject(new Error(`Could not find mood_api.py at ${scriptPath}`));
    }

    const python = getPythonExecutable();
    pythonProcess = spawn(python, [scriptPath], {
      cwd: path.dirname(scriptPath),
      stdio: ['ignore', 'pipe', 'pipe']
    });

    pythonProcess.stdout.on('data', data => {
      console.log(`[Flask] ${data.toString().trim()}`);
    });

    pythonProcess.stderr.on('data', data => {
      console.error(`[Flask] ${data.toString().trim()}`);
    });

    pythonProcess.on('exit', (code, signal) => {
      console.log(`Flask process exited with code=${code} signal=${signal}`);
    });

    pythonProcess.on('error', err => {
      console.error(`[Flask] spawn error: ${err.message}`);
    });

    waitForPort(API_PORT, 20000)
      .then(resolve)
      .catch(err => {
        if (pythonProcess && !pythonProcess.killed) {
          pythonProcess.kill();
        }
        reject(new Error(`Flask server failed to start: ${err.message}`));
      });
  });
}

function startWebServer() {
  return new Promise((resolve, reject) => {
    const server = express();
    const publicFolder = resolveResource('node-website', 'public');

    if (!fs.existsSync(publicFolder)) {
      return reject(new Error(`Could not find public folder at ${publicFolder}`));
    }

    server.use(express.static(publicFolder));
    server.get('/', (req, res) => res.redirect('/mood.html'));

    server.listen(WEB_PORT, err => {
      if (err) return reject(err);
      resolve();
    });
  });
}

function waitForPort(port, timeoutMs = 20000) {
  return new Promise((resolve, reject) => {
    const start = Date.now();

    function tryConnect() {
      const socket = net.createConnection(port, '127.0.0.1');
      socket.setTimeout(1000);
      socket.once('connect', () => {
        socket.destroy();
        resolve();
      });
      socket.once('error', () => {
        socket.destroy();
        if (Date.now() - start > timeoutMs) {
          reject(new Error(`Timeout waiting for port ${port}`));
        } else {
          setTimeout(tryConnect, 250);
        }
      });
      socket.once('timeout', () => {
        socket.destroy();
        if (Date.now() - start > timeoutMs) {
          reject(new Error(`Timeout waiting for port ${port}`));
        } else {
          setTimeout(tryConnect, 250);
        }
      });
    }

    tryConnect();
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 900,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  mainWindow.loadURL(`http://127.0.0.1:${WEB_PORT}/mood.html`);
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function shutdownServers() {
  if (pythonProcess && !pythonProcess.killed) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}

app.on('window-all-closed', () => {
  shutdownServers();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  shutdownServers();
});

app.whenReady()
  .then(() => Promise.all([startWebServer(), startFlaskServer()]))
  .then(() => {
    createWindow();
  })
  .catch(err => {
    dialog.showErrorBox('Startup Error', err.message);
    app.quit();
  });
