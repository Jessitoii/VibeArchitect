---
name: electron-ipc
description: Electron main/renderer communication patterns for VibeArchitect
triggers: ["electron", "ipc", "preload", "main.js", "ipcMain", "ipcRenderer", "bridge"]
---

# Electron IPC Skill

## Structure
- `src/main/main.js` — Electron main process, IPC handlers
- `src/main/preload.js` — Context bridge, exposes safe APIs to renderer
- `ui/hooks/useIPC.ts` — React hook wrapping all IPC calls

## IPC Pattern
```js
// preload.js — expose to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  startPipeline: (vibe) => ipcRenderer.invoke('start-pipeline', vibe),
})

// main.js — handle in main process
ipcMain.handle('start-pipeline', async (event, vibe) => {
  // spawn Python bridge
})
```

## Streaming from Python to UI
Python → stdout (NDJSON) → main.js reads line by line → `win.webContents.send('agent-message', parsed)` → useIPC hook receives

## Rules
- Never use `nodeIntegration: true` — always contextIsolation
- All Python communication goes through `bridge.py` HTTP, not direct process spawn in renderer
- Preload only exposes what the UI strictly needs