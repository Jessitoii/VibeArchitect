const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const isDev = !app.isPackaged;

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

ipcMain.handle('read-dir', async (event, dirPath) => {
    try {
        const entries = fs.readdirSync(dirPath, { withFileTypes: true });
        return entries.map(dirent => ({
            name: dirent.name,
            isDirectory: dirent.isDirectory(),
            path: path.join(dirPath, dirent.name)
        })).sort((a, b) => b.isDirectory - a.isDirectory || a.name.localeCompare(b.name));
    } catch (e) {
        console.error("Failed to read directory:", e);
        return [];
    }
});

ipcMain.handle('read-file', async (event, filePath) => {
    try {
        return fs.readFileSync(filePath, 'utf-8');
    } catch (e) {
        console.error("Failed to read file:", e);
        return null;
    }
});

ipcMain.handle('save-file', async (event, filePath, content) => {
    try {
        fs.writeFileSync(filePath, content, 'utf-8');
        return { success: true };
    } catch (e) {
        console.error("Failed to save file:", e);
        return { success: false, error: e.message };
    }
});

ipcMain.handle('delete-file', async (event, filePath) => {
    try {
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
        }
        return { success: true };
    } catch (e) {
        console.error("Failed to delete file:", e);
        return { success: false, error: e.message };
    }
});

let fileWatcher = null;
ipcMain.handle('watch-dir', (event, dirPath) => {
    if (fileWatcher) fileWatcher.close();
    try {
        fileWatcher = fs.watch(dirPath, { recursive: true }, (eventType, filename) => {
            if (mainWindow && !mainWindow.isDestroyed()) {
                mainWindow.webContents.send('file-changed', filename);
            }
        });
        return { success: true };
    } catch (e) {
        console.error("Failed to watch dir:", e);
        return { success: false, error: e.message };
    }
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

        ipcMain.removeAllListeners('approve-deployment');
        ipcMain.on('approve-deployment', () => {
            if (agentWebSocket && agentWebSocket.readyState === WebSocket.OPEN) {
                agentWebSocket.send(JSON.stringify({ action: "USER_APPROVAL" }));
            }
        });

        ipcMain.removeAllListeners('next-phase');
        ipcMain.on('next-phase', () => {
            if (agentWebSocket && agentWebSocket.readyState === WebSocket.OPEN) {
                agentWebSocket.send(JSON.stringify({ action: "NEXT_PHASE" }));
            }
        });

        ipcMain.removeAllListeners('stop-generation');
        ipcMain.on('stop-generation', () => {
            if (agentWebSocket && agentWebSocket.readyState === WebSocket.OPEN) {
                agentWebSocket.send(JSON.stringify({ action: "STOP" }));
            }
        });

        ipcMain.removeAllListeners('retry-pipeline');
        ipcMain.on('retry-pipeline', () => {
            if (agentWebSocket && agentWebSocket.readyState === WebSocket.OPEN) {
                agentWebSocket.send(JSON.stringify({ action: "RETRY_PIPELINE" }));
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
