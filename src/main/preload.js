const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    selectFolder: () => ipcRenderer.invoke('select-folder'),
    startAgentLoop: (vibe, projectPath) => ipcRenderer.invoke('start-agent-loop', vibe, projectPath),
    readDir: (dirPath) => ipcRenderer.invoke('read-dir', dirPath),
    readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
    saveFile: (filePath, content) => ipcRenderer.invoke('save-file', filePath, content),
    deleteFile: (filePath) => ipcRenderer.invoke('delete-file', filePath),
    getManifest: (projectPath) => ipcRenderer.invoke('get-manifest', projectPath),
    saveManifest: (projectPath, manifest) => ipcRenderer.invoke('save-manifest', projectPath, manifest),
    watchDir: (dirPath) => ipcRenderer.invoke('watch-dir', dirPath),
    proceedNextPhase: () => ipcRenderer.send('next-phase'),
    stopGeneration: () => ipcRenderer.send('stop-generation'),
    retryPipeline: () => ipcRenderer.send('retry-pipeline'),

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
    },

    onFileChanged: (callback) => {
        const subscription = (event, filename) => callback(filename);
        ipcRenderer.on('file-changed', subscription);
        return () => ipcRenderer.removeListener('file-changed', subscription);
    },

    // HitL
    approveDeployment: () => ipcRenderer.send('approve-deployment')
});
