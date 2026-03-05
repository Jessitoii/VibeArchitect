const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

let mainWindow;
let heartbeatTimeout;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 768,
        titleBarStyle: 'hiddenInset',
        backgroundColor: '#0f1115',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: false,
        },
    });

    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../../dist/index.html'));
    }
}

// IPC Handlers
ipcMain.handle('select-folder', async () => {
    const result = await dialog.showOpenDialog({
        properties: ['openDirectory', 'createDirectory'],
        title: 'Select Project Directory',
    });
    return result.canceled ? null : result.filePaths[0];
});

const WebSocket = require('ws');
let agentWebSocket = null;

ipcMain.handle('start-agent-loop', async (event, vibe, projectPath) => {
    console.log(`Starting loop for project: ${projectPath}...`);
    startHeartbeatWatchdog();

    if (agentWebSocket) {
        agentWebSocket.close();
    }

    try {
        const wsUrl = `ws://localhost:8000/pipeline?project_path=${encodeURIComponent(projectPath)}&vibe=${encodeURIComponent(vibe)}`;
        agentWebSocket = new WebSocket(wsUrl);

        agentWebSocket.on('open', () => {
            console.log('Connected to Orchestrator WebSocket');
            if (mainWindow) {
                mainWindow.webContents.send('backend-status', 'connected');
            }
        });

        agentWebSocket.on('message', (data) => {
            try {
                const message = JSON.parse(data.toString());

                // Fast path for raw tokens (bypasses React state)
                if (message.raw_stream && mainWindow) {
                    mainWindow.webContents.send('log-update', message.raw_stream);
                }

                // Emit state updates, provider metadata, and manifest changes
                if (mainWindow) {
                    // We always send the full message to agent-update so the UI can check status, provider, etc.
                    mainWindow.webContents.send('agent-update', message);
                }
            } catch (e) {
                console.error("Error parsing WS chunk:", e);
            }
        });

        agentWebSocket.on('close', () => {
            console.log('Orchestrator WebSocket closed.');
        });

        agentWebSocket.on('error', (err) => {
            console.error('Orchestrator WebSocket error:', err);
            if (mainWindow) {
                mainWindow.webContents.send('backend-status', 'error');
            }
        });

        return { success: true };
    } catch (e) {
        console.error("Failed to start agent loop:", e);
        return { success: false, error: e.message };
    }
});

// Heartbeat Watchdog
function startHeartbeatWatchdog() {
    resetHeartbeat();
}

function resetHeartbeat() {
    if (heartbeatTimeout) clearTimeout(heartbeatTimeout);
    heartbeatTimeout = setTimeout(() => {
        if (mainWindow) {
            mainWindow.webContents.send('backend-status', 'disconnected');
        }
    }, 2500); // 2.5s threshold
}

ipcMain.on('heartbeat', () => {
    resetHeartbeat();
    if (mainWindow) {
        mainWindow.webContents.send('backend-status', 'connected');
    }
});

app.whenReady().then(createWindow);
app.on('window-all-closed', () => process.platform !== 'darwin' && app.quit());
app.on('activate', () => BrowserWindow.getAllWindows().length === 0 && createWindow());
