import React from "react";
import Editor from "@monaco-editor/react";
import { useStore } from "../store";
import { Lock, Unlock, FileJson } from "lucide-react";

const ManifestEditor: React.FC = () => {
    const { manifest, updateManifest, isAgentActive } = useStore();

    const handleEditorChange = (value: string | undefined) => {
        if (!isAgentActive && value) {
            try {
                const parsed = JSON.parse(value);
                updateManifest(parsed);
            } catch (e) {
                // Handle JSON parse error (could show a toast or validation state)
            }
        }
    };

    return (
        <div className="flex h-full flex-col bg-surface border border-border rounded-xl overflow-hidden shadow-2xl">
            <div className="h-10 border-b border-border flex items-center px-4 justify-between bg-background/30 backdrop-blur-sm shrink-0">
                <div className="flex items-center gap-2">
                    <FileJson size={14} className="text-primary" />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-text">manifest.json</span>
                </div>

                <div className={`flex items-center gap-2 px-2 py-1 rounded-md text-[9px] font-bold uppercase ${isAgentActive ? 'bg-error/10 text-error' : 'bg-secondary/10 text-secondary'}`}>
                    {isAgentActive ? (
                        <><Lock size={10} /> Read-Only (Loop Active)</>
                    ) : (
                        <><Unlock size={10} /> Editable</>
                    )}
                </div>
            </div>

            <div className="flex-1">
                <Editor
                    height="100%"
                    defaultLanguage="json"
                    theme="vs-dark"
                    value={JSON.stringify(manifest, null, 2)}
                    onChange={handleEditorChange}
                    options={{
                        readOnly: isAgentActive,
                        minimap: { enabled: false },
                        fontSize: 13,
                        lineHeight: 1.6,
                        padding: { top: 16 },
                        fontFamily: "'JetBrains Mono', monospace",
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        glyphMargin: false,
                        folding: true,
                        lineNumbersMinChars: 3,
                        backgroundColor: "#0f1115"
                    }}
                />
            </div>
        </div>
    );
};

export default ManifestEditor;
