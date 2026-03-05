import React, { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import "xterm/css/xterm.css";

const AgentLogs: React.FC = () => {
    const terminalRef = useRef<HTMLDivElement>(null);
    const xtermRef = useRef<Terminal | null>(null);

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

    return (
        <div className="h-full w-full bg-surface border-t border-border flex flex-col overflow-hidden">
            <div className="h-8 border-b border-border flex items-center px-4 justify-between bg-background/50 shrink-0">
                <span className="text-[10px] font-bold uppercase tracking-widest text-text-dim">Agent Logs</span>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
                    <span className="text-[10px] text-text-dim">Streaming Active</span>
                </div>
            </div>
            <div ref={terminalRef} className="flex-1 p-2" />
        </div>
    );
};

export default AgentLogs;
