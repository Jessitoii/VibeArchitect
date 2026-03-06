import React from 'react';
import { useStore } from '../store';
import Editor from '@monaco-editor/react';

export default function CodeEditor() {
    const { activeFilePath, activeFileContent, setActiveFile } = useStore();

    if (!activeFilePath) {
        return (
            <div className="flex-1 flex items-center justify-center bg-background text-text-dim">
                <div className="text-center">
                    <p className="text-xl font-bold mb-2">Editor</p>
                    <p className="text-sm">Select a file from the explorer to view or edit it.</p>
                </div>
            </div>
        );
    }

    // Determine language based on extension
    let language = "plaintext";
    if (activeFilePath.endsWith('.ts') || activeFilePath.endsWith('.tsx')) language = "typescript";
    else if (activeFilePath.endsWith('.js') || activeFilePath.endsWith('.jsx')) language = "javascript";
    else if (activeFilePath.endsWith('.py')) language = "python";
    else if (activeFilePath.endsWith('.json')) language = "json";
    else if (activeFilePath.endsWith('.md')) language = "markdown";
    else if (activeFilePath.endsWith('.css')) language = "css";
    else if (activeFilePath.endsWith('.html')) language = "html";

    const handleEditorChange = (value: string | undefined) => {
        if (value !== undefined) {
            setActiveFile(activeFilePath, value);
            // Optionally, we could add auto-save logic here or a save button
        }
    };

    return (
        <div className="flex-1 flex flex-col min-w-0 bg-background overflow-hidden relative">
            <div className="bg-surface border-b border-border py-2 px-4 flex items-center justify-between text-sm">
                <span className="font-mono text-text-dim">{activeFilePath.split(/[\\/]/).pop()}</span>
                {/* Save button can be added here or handled automatically depending on HitL */}
                <button
                    onClick={() => window.electronAPI.saveFile(activeFilePath, activeFileContent || "")}
                    className="bg-primary/20 hover:bg-primary/40 text-primary px-3 py-1 rounded text-xs font-bold"
                >
                    SAVE
                </button>
            </div>
            <div className="flex-1 relative">
                <Editor
                    height="100%"
                    language={language}
                    value={activeFileContent || ""}
                    theme="vs-dark"
                    options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        wordWrap: "on",
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                    }}
                    onChange={handleEditorChange}
                />
            </div>
        </div>
    );
}
