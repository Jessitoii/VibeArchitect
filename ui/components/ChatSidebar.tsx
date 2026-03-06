import React, { useState, useEffect, useRef } from 'react';
import { useStore } from '../store';
import { Send, Settings, CheckSquare, Square, Loader2 } from 'lucide-react';

export default function ChatSidebar() {
    const { chatHistory, appendChatMessage, autoAccept, setAutoAccept, currentView, projectPath, setPendingEdits, manifest, updateManifest } = useStore();
    const [inputValue, setInputValue] = useState("");
    const [isThinking, setIsThinking] = useState(false);
    const [activeThought, setActiveThought] = useState("");
    const wsRef = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const handleHotSwap = async (provider: string) => {
        const newManifest = { ...manifest };
        if (!newManifest.instructional_brain) {
            newManifest.instructional_brain = { provider_config: {} };
        } else if (!newManifest.instructional_brain.provider_config) {
            newManifest.instructional_brain.provider_config = {};
        }
        newManifest.instructional_brain.provider_config.selected_provider = provider;

        if (provider === "groq") newManifest.instructional_brain.provider_config.selected_model = "meta-llama/llama-3.3-70b-versatile";
        else if (provider === "ollama") newManifest.instructional_brain.provider_config.selected_model = "qwen2.5-coder:latest";

        updateManifest(newManifest);
        if (projectPath) {
            const fullPath = `${projectPath}/.vibe_architect/manifest.json`;
            try {
                await window.electronAPI.saveFile(fullPath, JSON.stringify(newManifest, null, 2));
                appendChatMessage({ role: "agent", content: `[SYSTEM] Hot-swapped provider to ${provider}. Your manifest has been updated. You can now press "Deploy Agents" or "Proceed to Next Step" to continue.` });
            } catch (e) {
                console.error("Failed to save manifest", e);
            }
        }
    };

    useEffect(() => {
        if (!projectPath) return;

        const ws = new WebSocket(`ws://localhost:8000/chat?project_path=${encodeURIComponent(projectPath)}`);

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === "chunk") {
                    setActiveThought(prev => prev + data.content);
                } else if (data.type === "edits") {
                    setIsThinking(false);
                    appendChatMessage({ role: "agent", content: data.payload.thought_process });
                    setActiveThought("");

                    if (data.payload.files_to_edit && data.payload.files_to_edit.length > 0) {
                        const edits = data.payload.files_to_edit;
                        if (autoAccept) {
                            // Save immediately
                            edits.forEach(async (edit: any) => {
                                const fullPath = `${projectPath}/${edit.filepath}`;

                                if (edit.modified_content === null) {
                                    await window.electronAPI.deleteFile(fullPath);
                                    const store = useStore.getState();
                                    if (store.activeFilePath === fullPath) {
                                        store.setActiveFile(null, null);
                                    }
                                } else {
                                    await window.electronAPI.saveFile(fullPath, edit.modified_content);
                                    const store = useStore.getState();
                                    if (store.activeFilePath === fullPath) {
                                        store.setActiveFile(fullPath, edit.modified_content);
                                    }
                                }
                            });
                        } else {
                            // Enqueue for diff view mapping to full project paths
                            setPendingEdits(edits.map((e: any) => ({
                                filepath: `${projectPath}/${e.filepath}`,
                                original_content: e.original_content,
                                modified_content: e.modified_content
                            })));
                        }
                    }
                } else if (data.type === "error") {
                    setIsThinking(false);
                    appendChatMessage({ role: "error", content: data.content });
                    setActiveThought("");
                }
            } catch (e) {
                console.error("Chat WS parsing error", e);
            }
        };

        wsRef.current = ws;

        return () => {
            if (wsRef.current) wsRef.current.close();
        };
    }, [projectPath, autoAccept, appendChatMessage, setPendingEdits]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chatHistory, activeThought]);

    const handleSend = () => {
        if (!inputValue.trim() || !wsRef.current) return;

        appendChatMessage({ role: "user", content: inputValue.trim() });
        wsRef.current.send(JSON.stringify({ message: inputValue.trim() }));

        setInputValue("");
        setIsThinking(true);
        setActiveThought("");
    };

    return (
        <div className="flex flex-col h-full bg-surface border-l border-border w-[350px] overflow-hidden">
            <div className="p-4 border-b border-border flex items-center justify-between bg-background">
                <h3 className="text-xs font-black uppercase tracking-widest text-primary">Vibe Chat</h3>
                <div
                    className="flex items-center gap-2 cursor-pointer text-text-dim hover:text-text transition-colors"
                    onClick={() => setAutoAccept(!autoAccept)}
                >
                    <span className="text-[10px] uppercase font-bold">Auto-Accept</span>
                    {autoAccept ? <CheckSquare size={14} className="text-success" /> : <Square size={14} />}
                </div>
            </div>

            <div className="flex-1 overflow-auto p-4 space-y-4">
                {chatHistory.length === 0 && !isThinking ? (
                    <div className="text-center text-text-dim/50 text-sm mt-10">
                        <p>Ask the agent to edit files, refactor code, or update the manifest.</p>
                    </div>
                ) : (
                    <>
                        {chatHistory.map((msg, idx) => (
                            <div key={idx} className={`p-3 rounded-lg text-sm ${msg.role === 'user' ? 'bg-primary/20 ml-8 text-right' : msg.role === 'error' ? 'bg-error/10 border border-error/20 mr-8 text-error text-left' : 'bg-background border border-border mr-8'}`}>
                                <span className="font-bold text-[10px] uppercase block mb-1 opacity-50">{msg.role}</span>
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                                {msg.role === 'error' && msg.content.includes("Rate Limit") && (
                                    <div className="flex gap-2 mt-3">
                                        <button className="px-2 py-1 bg-surface border border-border rounded text-[10px] font-bold text-text-dim hover:text-text hover:border-primary transition-colors"
                                            onClick={() => handleHotSwap('groq')}
                                        >
                                            Hot-Swap to Groq
                                        </button>
                                        <button className="px-2 py-1 bg-surface border border-border rounded text-[10px] font-bold text-text-dim hover:text-text hover:border-[#f59e0b] transition-colors"
                                            onClick={() => handleHotSwap('ollama')}
                                        >
                                            Hot-Swap to Ollama
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))}
                        {isThinking && (
                            <div className="p-3 rounded-lg text-sm bg-background border border-border mr-8 relative overflow-hidden">
                                <span className="font-bold text-[10px] uppercase flex items-center gap-2 mb-1 opacity-50"><Loader2 size={10} className="animate-spin" /> THINKING</span>
                                <div className="whitespace-pre-wrap text-text-dim font-mono text-xs">{activeThought}</div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            <div className="p-4 border-t border-border bg-background">
                <div className="relative">
                    <textarea
                        className="w-full bg-surface border border-border rounded-xl p-3 pr-12 text-sm focus:outline-none focus:border-primary resize-none placeholder-text-dim/50"
                        rows={3}
                        placeholder="e.g. Change the primary color to red..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                    />
                    <button
                        className="absolute bottom-3 right-3 p-2 bg-primary hover:bg-primary/80 rounded-lg text-white transition-all active:scale-95"
                        onClick={handleSend}
                    >
                        <Send size={14} />
                    </button>
                </div>
            </div>
        </div>
    );
}
