---
trigger: always_on
---

# Phase 1: Electron + React + Tailwind Initialization

Since we've nailed down the rules and the architecture, it's time to stop talking and start building. We're going with Electron for the shell and React/Tailwind for the UI.

---

## 1. Project Scaffolding

We need a structure that keeps the **Agent Logic (Python)** and the **UI Logic (Node/React)** separate but communicative.

### Proposed Directory Structure
/vibe-architect
├── /src # Electron Main & Preload scripts
├── /ui # React + Tailwind Frontend
├── /core # Python Agent Logic (The 5-Agent Loop)
├── /shared # Types and JSON Schemas (manifest.json)
├── package.json
└── tailwind.config.js


---

## 2. The Entry Point (`main.js`)

This is where we handle the native folder selection.

```js
// src/main.js
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    titleBarStyle: 'hiddenInset', // Modern, clean look
  });

  win.loadURL('http://localhost:3000'); // Assuming React dev server
}

// Handling Folder Selection
ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});

app.whenReady().then(createWindow);
```
3\. The "Vibe" Dashboard (UI)
-----------------------------

For the editor-like feel, we'll use a dark, high-contrast theme.

### Component Breakdown

*   **Sidebar**: Tree view of the selected project
    
*   **Main Stage**: The Agent Pipeline — a horizontal stepper showing the state of the Visionary, Architect, Engineer, etc.
    
*   **Console**: A streaming text area for the Cerebras/Qwen logs
