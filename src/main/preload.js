const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    selectFolder: () => ipcRenderer.invoke('select-folder'),
    startAgentLoop: (vibe, projectPath) => ipcRenderer.invoke('start-agent-loop', vibe, projectPath),

    // Heartbeat
    sendHeartbeat: () => ipcRenderer.send('heartbeat'),
    onBackendStatus: (callback) => {
        const subscription = (event, value) => callback(value);
        ipcRenderer.on('backend-status', subscription);
        return () => ipcRenderer.removeListener('backend-status', subscription);
    },

    // Agent Events
    onAgentUpdate: (callback) => {
        const subscription = (event, value) => callback(value);
        ipcRenderer.on('agent-update', subscription);
        return () => ipcRenderer.removeListener('agent-update', subscription);
    },

    // RAW LOG PIPELINE (Direct to Xterm.js)
    onLogUpdate: (callback) => {
        const subscription = (event, value) => callback(value);
        ipcRenderer.on('log-update', subscription);
        return () => ipcRenderer.removeListener('log-update', subscription);
    }
});
