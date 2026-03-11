import React, { useState, useEffect } from "react";
import Editor from "@monaco-editor/react";
import { useStore } from "../store";
import { Lock, Unlock, FileJson } from "lucide-react";

const ManifestEditor: React.FC = () => {
    const { manifest, updateManifest, isAgentActive } = useStore();
    const [ollamaModels, setOllamaModels] = useState<string[]>([]);

    useEffect(() => {
        const fetchModels = async () => {
            try {
                const res = await fetch("http://localhost:11434/api/tags");
                const data = await res.json();
                const names = data.models?.map((m: any) => m.name) || [];
                setOllamaModels(names);
            } catch (e) {
                // Ignore
            }
        };
        fetchModels();
    }, []);

    const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const provider = e.target.value;
        const newManifest = { ...manifest };
        if (!newManifest.instructional_brain) {
            newManifest.instructional_brain = { provider_config: {} };
        } else if (!newManifest.instructional_brain.provider_config) {
            newManifest.instructional_brain.provider_config = {};
        }
        newManifest.instructional_brain.provider_config.selected_provider = provider;

        if (provider === "cerebras") newManifest.instructional_brain.provider_config.selected_model = "openai/gpt-oss-120b";
        else if (provider === "groq") newManifest.instructional_brain.provider_config.selected_model = "meta-llama/llama-3.3-70b-versatile";
        else if (provider === "ollama") newManifest.instructional_brain.provider_config.selected_model = ollamaModels.length > 0 ? ollamaModels[0] : "qwen2.5-coder:latest";

        updateManifest(newManifest);
    };

    const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const model = e.target.value;
        const newManifest = { ...manifest };
        if (!newManifest.instructional_brain) {
            newManifest.instructional_brain = { provider_config: {} };
        } else if (!newManifest.instructional_brain.provider_config) {
            newManifest.instructional_brain.provider_config = {};
        }
        newManifest.instructional_brain.provider_config.selected_model = model;
        updateManifest(newManifest);
    };

    return (
        <div className="flex h-full flex-col bg-surface border border-border rounded-xl overflow-hidden shadow-2xl">
            <div className="h-10 border-b border-border flex items-center px-4 justify-between bg-background/30 backdrop-blur-sm shrink-0">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <FileJson size={14} className="text-primary" />
                        <span className="text-[10px] font-bold uppercase tracking-widest text-text">manifest.json</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <select
                            className="bg-background border border-border rounded px-2 py-0.5 text-[10px] uppercase font-bold text-text disabled:opacity-50"
                            value={manifest?.instructional_brain?.provider_config?.selected_provider || "cerebras"}
                            onChange={handleProviderChange}
                            disabled={isAgentActive}
                        >
                            <option value="cerebras">Cerebras</option>
                            <option value="groq">Groq</option>
                            <option value="ollama">Ollama</option>
                        </select>

                        <select
                            className="bg-background border border-border rounded px-2 py-0.5 text-[10px] uppercase font-bold text-text disabled:opacity-50"
                            value={manifest?.instructional_brain?.provider_config?.selected_model || ""}
                            onChange={handleModelChange}
                            disabled={isAgentActive}
                        >
                            {manifest?.instructional_brain?.provider_config?.selected_provider === "cerebras" && (
                                <>
                                    <option value="openai/gpt-oss-120b">gpt-oss-120b</option>
                                    <option value="meta-llama/llama-3.1-8b-instant">llama-3.1-8b-instant</option>
                                </>
                            )}
                            {manifest?.instructional_brain?.provider_config?.selected_provider === "groq" && (
                                <>
                                    <option value="openai/gpt-oss-120b">gpt-oss-120b</option>
                                    <option value="openai/gpt-oss-20b">gpt-oss-20b</option>
                                    <option value="meta-llama/llama-3.3-70b-versatile">llama-3.3-70b-versatile</option>
                                    <option value="meta-llama/llama-3.1-8b-instant">llama-3.1-8b-instant</option>
                                    <option value="qwen/qwen-3-32b">qwen-3-32b</option>
                                </>
                            )}
                            {manifest?.instructional_brain?.provider_config?.selected_provider === "ollama" && (
                                <>
                                    {ollamaModels.map(name => (
                                        <option key={name} value={name}>{name}</option>
                                    ))}
                                    {ollamaModels.length === 0 && <option value="qwen2.5-coder:latest">qwen2.5-coder:latest</option>}
                                </>
                            )}
                        </select>
                    </div>
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
                    onChange={(value) => {
                        if (!isAgentActive && value) {
                            try {
                                const parsed = JSON.parse(value);
                                updateManifest(parsed);
                            } catch (e) { }
                        }
                    }}
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
                        lineNumbersMinChars: 3
                    }}
                />
            </div>
        </div>
    );
};

export default ManifestEditor;
