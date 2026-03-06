import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useIPC } from "./hooks/useIPC";
import { useStore } from "./store";
import { FolderOpen, Settings, ChevronRight, AlertTriangle, RefreshCcw, XCircle, Copy, Trash2, X } from "lucide-react";
import PipelineStepper from "./components/PipelineStepper";
import ManifestEditor from "./components/ManifestEditor";
import AgentLogs from "./components/AgentLogs";
import ReviewAndDeploy from "./components/ReviewAndDeploy";
import FileExplorer from "./components/FileExplorer";
import CodeEditor from "./components/CodeEditor";
import ChatSidebar from "./components/ChatSidebar";
import DiffViewer from "./components/DiffViewer";

const App: React.FC = () => {
    const { selectFolder, startAgentLoop } = useIPC();
    const {
        projectPath, setProjectPath,
        vibePrompt, setVibePrompt,
        currentAgent, currentProvider, agentStatus,
        isAgentActive,
        backendStatus, currentView, setCurrentView,
        pendingEdits, popPendingEdit, manifest,
        exceptions, dismissException, clearExceptions
    } = useStore();
    const [isInitializing, setIsInitializing] = useState(false);
    const [expandedException, setExpandedException] = useState<string | null>(null);

    React.useEffect(() => {
        if (agentStatus === "IDE_MODE") {
            setCurrentView("ide");
        }
    }, [agentStatus, setCurrentView]);

    const handleSelectFolder = async () => {
        const path = await selectFolder();
        if (path) setProjectPath(path);
    };

    const handleStart = async () => {
        if (!projectPath || !vibePrompt) return;
        setIsInitializing(true);
        await startAgentLoop(vibePrompt, projectPath);
    };

    const handleStop = () => {
        if (window.electronAPI && window.electronAPI.stopGeneration) {
            window.electronAPI.stopGeneration();
        }
    };

    return (
        <div className="flex h-screen w-screen flex-col overflow-hidden bg-background text-text relative">
            {/* Custom Title Bar */}
            <header className="h-10 w-full shrink-0 border-b border-border flex items-center px-4 bg-surface/80 backdrop-blur-md z-50">
                <span className="text-[10px] font-bold text-text-dim tracking-widest uppercase pl-20">VibeArchitect</span>
                <div className="flex-1 flex justify-center">
                    {agentStatus === "IDE_MODE" || currentView === "ide" || projectPath ? (
                        <div className="flex bg-surface border border-border rounded-lg overflow-hidden text-xs font-bold">
                            <button
                                onClick={() => setCurrentView("blueprint")}
                                className={`px-4 py-1.5 transition-colors ${currentView === "blueprint" ? "bg-primary text-white" : "text-text-dim hover:bg-background"}`}
                            >
                                Blueprint
                            </button>
                            <button
                                onClick={() => setCurrentView("ide")}
                                className={`px-4 py-1.5 transition-colors ${currentView === "ide" ? "bg-primary text-white" : "text-text-dim hover:bg-background"}`}
                            >
                                IDE
                            </button>
                        </div>
                    ) : null}
                </div>
                <div className="flex items-center gap-4">
                    {/* Stop Generation Button */}
                    {isAgentActive && (
                        <button
                            onClick={handleStop}
                            className="flex items-center gap-2 px-3 py-1 bg-error hover:bg-error/80 text-white rounded-md text-[9px] uppercase font-bold tracking-wider transition-colors shadow-lg shadow-error/20"
                        >
                            <XCircle size={12} />
                            Stop
                        </button>
                    )}

                    {/* Provider Visualization */}
                    {isInitializing && currentProvider && (
                        <div className={`flex items-center gap-2 px-3 py-1 rounded-full border text-[9px] uppercase font-bold tracking-wider transition-colors ${currentProvider === "cerebras" ? "bg-secondary/10 text-secondary border-secondary/20" :
                            currentProvider === "ollama" ? "bg-[#f59e0b]/10 text-[#f59e0b] border-[#f59e0b]/20" :
                                "bg-error/10 text-error border-error/20"
                            }`}>
                            <span>Provider: {currentProvider}</span>
                            {currentProvider !== "cerebras" && <span className="animate-pulse">⚠️ FALLBACK</span>}
                        </div>
                    )}

                    {backendStatus !== "connected" && (
                        <div className="flex items-center gap-2 px-3 py-1 bg-error/10 text-error rounded-full animate-pulse border border-error/20">
                            <AlertTriangle size={12} />
                            <span className="text-[10px] uppercase font-bold">Backend Offline</span>
                        </div>
                    )}
                </div>
            </header>

            <main className="flex-1 overflow-hidden relative">
                <AnimatePresence mode="wait">
                    {!isInitializing ? (
                        <motion.div
                            key="hero"
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 1.02 }}
                            className="flex h-full items-center justify-center p-12 bg-[radial-gradient(circle_at_center,_#1a1d23_0%,_#0f1115_100%)]"
                        >
                            <div className="w-full max-w-2xl space-y-10 text-center">
                                <div className="space-y-4">
                                    <h1 className="text-6xl font-black tracking-tighter text-text leading-tight">
                                        Architect Your <span className="text-primary">Vision</span>.
                                    </h1>
                                    <p className="text-text-dim/60 text-xl font-medium">
                                        Transform high-level "vibes" into technically sound technical blueprints using a 5-agent pipeline.
                                    </p>
                                </div>

                                <div className="relative group p-[2px] rounded-3xl bg-gradient-to-br from-accent/20 to-primary/20 focus-within:from-accent focus-within:to-primary transition-all duration-500 shadow-2xl">
                                    <div className="bg-surface rounded-[22px] p-6">
                                        <textarea
                                            value={vibePrompt}
                                            onChange={(e) => setVibePrompt(e.target.value)}
                                            placeholder="I want to build a decentralized task manager for small teams..."
                                            className="w-full h-44 bg-transparent border-none text-text text-xl focus:ring-0 placeholder:text-text-dim/20 font-medium resize-none"
                                        />
                                    </div>
                                </div>

                                <div className="flex items-center justify-center gap-6">
                                    <button
                                        onClick={handleSelectFolder}
                                        className="flex items-center gap-3 px-8 py-4 bg-surface/50 hover:bg-border border border-border rounded-2xl font-bold transition-all hover:scale-105 active:scale-95 text-sm uppercase tracking-widest"
                                    >
                                        <FolderOpen size={18} className="text-text-dim" />
                                        {projectPath ? "Folder Selected" : "Select Project Folder"}
                                    </button>

                                    <button
                                        disabled={!projectPath || !vibePrompt || backendStatus !== "connected"}
                                        onClick={handleStart}
                                        className="flex items-center gap-3 px-10 py-4 bg-accent hover:bg-accent/80 disabled:opacity-30 rounded-2xl font-black transition-all hover:scale-105 active:scale-95 text-white shadow-2xl shadow-accent/40 text-sm uppercase tracking-widest"
                                    >
                                        Deploy Agents
                                        <ChevronRight size={18} />
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="dashboard"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex h-full flex-col relative"
                        >
                            <PipelineStepper currentId={manifest?.status || "VISIONARY_ACTIVE"} status={agentStatus} />

                            <AnimatePresence>
                                {agentStatus === "WAITING_NEXT_PHASE" && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="w-full bg-accent/20 border-b border-accent/30 p-3 flex items-center justify-between px-12"
                                    >
                                        <span className="text-sm font-bold text-accent">Phase {currentAgent} complete! You can manually review/edit the Blueprint below before proceeding.</span>
                                        <button
                                            onClick={() => window.electronAPI.proceedNextPhase()}
                                            className="px-6 py-2 bg-accent hover:bg-accent/80 transition-colors text-white font-bold rounded-lg shadow-lg flex items-center gap-2 text-sm uppercase tracking-widest"
                                        >
                                            Proceed to Next Step <ChevronRight size={16} />
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            <div className="flex-1 flex gap-4 p-4 overflow-hidden">
                                {currentView === "blueprint" ? (
                                    <>
                                        <div className="flex-1 h-full min-w-0">
                                            <ManifestEditor />
                                        </div>
                                        <div className="w-[450px] shrink-0 h-full flex flex-col gap-4">
                                            <AgentLogs />
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <FileExplorer />
                                        <CodeEditor />
                                        <ChatSidebar />
                                    </>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Exception Toast Library overlay */}
                <div className="absolute bottom-6 left-6 z-[200] flex flex-col gap-3 max-w-lg">
                    <AnimatePresence>
                        {exceptions.map(exc => (
                            <motion.div
                                key={exc.id}
                                initial={{ opacity: 0, x: -50, scale: 0.95 }}
                                animate={{ opacity: 1, x: 0, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                className="bg-surface border border-error/50 rounded-xl shadow-2xl overflow-hidden flex flex-col"
                            >
                                <div className="p-4 bg-error/10 flex items-start justify-between gap-4 border-b border-error/20">
                                    <div className="flex items-center gap-3 flex-1">
                                        <AlertTriangle className="text-error shrink-0" size={20} />
                                        <div className="flex flex-col">
                                            <span className="text-sm font-bold text-error break-words">{exc.title}</span>
                                            <span className="text-[10px] text-text-dim/80">{new Date(exc.timestamp).toLocaleTimeString()}</span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => dismissException(exc.id)}
                                        className="text-text-dim hover:text-white transition-colors"
                                    >
                                        <X size={16} />
                                    </button>
                                </div>
                                <div className="p-3 bg-background flex items-center justify-between">
                                    <button
                                        onClick={() => {
                                            navigator.clipboard.writeText(`Error: ${exc.title}\n\nTraceback:\n${exc.traceback}`);
                                        }}
                                        className="flex items-center gap-2 text-[10px] font-bold uppercase text-text-dim hover:text-text transition-colors"
                                    >
                                        <Copy size={12} /> Copy Error
                                    </button>
                                    <button
                                        onClick={() => setExpandedException(expandedException === exc.id ? null : exc.id)}
                                        className="text-[10px] font-bold uppercase text-primary hover:text-primary/80 transition-colors"
                                    >
                                        {expandedException === exc.id ? "Hide Stack Trace" : "View Stack Trace"}
                                    </button>
                                </div>
                                <AnimatePresence>
                                    {expandedException === exc.id && (
                                        <motion.div
                                            initial={{ height: 0 }}
                                            animate={{ height: "auto" }}
                                            exit={{ height: 0 }}
                                            className="overflow-hidden"
                                        >
                                            <div className="p-4 bg-[#0a0a0c] border-t border-border mt-0">
                                                <pre className="text-[10px] text-text-dim font-mono whitespace-pre-wrap max-h-64 overflow-auto">
                                                    {exc.traceback}
                                                </pre>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                    {exceptions.length > 1 && (
                        <button
                            onClick={clearExceptions}
                            className="flex items-center justify-center gap-2 py-2 bg-error/20 hover:bg-error/30 text-error rounded-lg text-xs font-bold transition-colors"
                        >
                            <Trash2 size={14} /> Clear All Errors
                        </button>
                    )}
                </div>

                {/* Backend Failure Overlay */}
                <AnimatePresence>
                    {backendStatus === "disconnected" && isInitializing && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-background/80 backdrop-blur-xl z-[100] flex items-center justify-center p-8"
                        >
                            <div className="bg-surface border border-error/30 p-10 rounded-3xl shadow-2xl text-center max-w-md space-y-6">
                                <div className="w-16 h-16 bg-error/10 text-error rounded-full flex items-center justify-center mx-auto">
                                    <AlertTriangle size={32} />
                                </div>
                                <div className="space-y-2">
                                    <h2 className="text-2xl font-bold">Backend Failure</h2>
                                    <p className="text-text-dim text-sm">
                                        The Python agent loop has crashed or stopped responding. Check the crash logs in your project directory.
                                    </p>
                                </div>
                                <button
                                    onClick={() => window.location.reload()}
                                    className="w-full flex items-center justify-center gap-2 py-4 bg-error hover:bg-error/80 text-white font-bold rounded-2xl transition-all active:scale-95"
                                >
                                    <RefreshCcw size={18} />
                                    Restart Pipeline
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Human-in-the-Loop Overlay */}
                <AnimatePresence>
                    {agentStatus === "WAITING_APPROVAL" && (
                        <ReviewAndDeploy
                            onApprove={() => {
                                window.electronAPI.approveDeployment();
                            }}
                        />
                    )}
                </AnimatePresence>

                {/* Diff Viewer Overlay */}
                <AnimatePresence>
                    {pendingEdits.length > 0 && (
                        <DiffViewer
                            filePath={pendingEdits[0].filepath}
                            original={pendingEdits[0].original_content || ""}
                            modified={pendingEdits[0].modified_content || ""}
                            isDeletion={pendingEdits[0].modified_content === null}
                            onApprove={async () => {
                                const edit = pendingEdits[0];

                                if (edit.modified_content === null) {
                                    await window.electronAPI.deleteFile(edit.filepath);
                                    if (useStore.getState().activeFilePath === edit.filepath) {
                                        useStore.getState().setActiveFile(null, null);
                                    }
                                } else {
                                    await window.electronAPI.saveFile(edit.filepath, edit.modified_content);
                                    if (useStore.getState().activeFilePath === edit.filepath) {
                                        useStore.getState().setActiveFile(edit.filepath, edit.modified_content);
                                    }
                                }

                                popPendingEdit();
                            }}
                            onReject={() => {
                                popPendingEdit();
                            }}
                        />
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
};

export default App;
