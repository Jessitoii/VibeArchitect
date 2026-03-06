import React, { useEffect, useRef, useState } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import { useStore } from "../store";
import { useIPC } from "../hooks/useIPC";
import { RefreshCcw } from "lucide-react";
import "xterm/css/xterm.css";

const AgentLogs: React.FC = () => {
    const terminalRef = useRef<HTMLDivElement>(null);
    const xtermRef = useRef<Terminal | null>(null);
    const { agentStatus, isAgentActive, exceptions } = useStore();
    const { retryPipeline } = useIPC();
    const [cooldown, setCooldown] = useState(0);

    const hasRateLimitError = exceptions.some(e =>
        e.title.toLowerCase().includes("rate limit") ||
        e.traceback.includes("429") ||
        e.title.includes("429") ||
        e.traceback.toLowerCase().includes("too many requests")
    );

    useEffect(() => {
        if (agentStatus === "error" && hasRateLimitError) {
            setCooldown(5);
        } else {
            setCooldown(0);
        }
    }, [agentStatus, hasRateLimitError]);

    useEffect(() => {
        if (cooldown > 0) {
            const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
            return () => clearTimeout(timer);
        }
    }, [cooldown]);

    useEffect(() => {
        if (!terminalRef.current) return;

        const term = new Terminal({
            theme: {
                background: "#1a1d23",
                foreground: "#e5e7eb",
                cursor: "#df912a",
                selectionBackground: "rgba(99, 102, 241, 0.3)",
            },
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 13,
            lineHeight: 1.4,
            convertEol: true,
            cursorBlink: true,
        });

        const fitAddon = new FitAddon();
        term.loadAddon(fitAddon);
        term.open(terminalRef.current);
        fitAddon.fit();

        xtermRef.current = term;

        // DIRECT IPC PIPING (Bypasses React State)
        const removeListener = window.electronAPI.onLogUpdate((chunk: string) => {
            term.write(chunk);
        });

        const handleResize = () => fitAddon.fit();
        window.addEventListener("resize", handleResize);

        return () => {
            removeListener();
            window.removeEventListener("resize", handleResize);
            term.dispose();
        };
    }, []);

    const handleRetry = () => {
        if (cooldown === 0) {
            retryPipeline();
        }
    };

    return (
        <div className="h-full w-full bg-surface border-t border-border flex flex-col overflow-hidden relative">
            <div className="h-8 border-b border-border flex items-center px-4 justify-between bg-background/50 shrink-0">
                <span className="text-[10px] font-bold uppercase tracking-widest text-text-dim">Agent Logs</span>
                <div className="flex items-center gap-2">
                    {isAgentActive ? (
                        <>
                            <div className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
                            <span className="text-[10px] text-text-dim">Streaming Active</span>
                        </>
                    ) : agentStatus === "error" ? (
                        <>
                            <div className="w-2 h-2 rounded-full bg-error animate-pulse" />
                            <span className="text-[10px] text-error">Stream Halted</span>
                        </>
                    ) : (
                        <span className="text-[10px] text-text-dim/60">Idle</span>
                    )}
                </div>
            </div>

            <div ref={terminalRef} className="flex-1 p-2" />

            {/* Error Overlay with Retry Button */}
            {agentStatus === "error" && (
                <div className="absolute inset-0 bg-background/60 backdrop-blur-sm z-10 flex flex-col items-center justify-center p-6 text-center">
                    <div className="bg-surface border border-error/30 p-8 rounded-2xl shadow-2xl max-w-sm w-full space-y-6">
                        <div className="space-y-2">
                            <h3 className="text-xl font-bold text-error">Pipeline Failed</h3>
                            <p className="text-sm text-text-dim">
                                The orchestrator caught a critical error. Check the exception dashboard for details.
                            </p>
                        </div>

                        <button
                            disabled={cooldown > 0}
                            onClick={handleRetry}
                            className="w-full flex items-center justify-center gap-3 py-4 bg-accent hover:bg-accent/80 disabled:bg-surface disabled:text-text-dim disabled:border-border disabled:hover:bg-surface border border-transparent transition-all rounded-xl font-bold font-mono tracking-widest uppercase text-sm"
                        >
                            {cooldown > 0 ? (
                                `Cooldown (${cooldown}s)`
                            ) : (
                                <>
                                    <RefreshCcw size={16} />
                                    Retry Phase
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AgentLogs;
