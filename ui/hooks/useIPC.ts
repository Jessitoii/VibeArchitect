import { useEffect, useRef } from "react";
import { useStore } from "../store";
import { AgentMessage } from "../types/electron";

export const useIPC = () => {
    const { setAgentStatus, setBackendStatus, updateManifest } = useStore();
    const heartbeatInterval = useRef<NodeJS.Timeout>();

    useEffect(() => {
        // Listen for backend status (heartbeat monitoring)
        const removeStatusListener = window.electronAPI.onBackendStatus((status: "connected" | "disconnected" | "error") => {
            setBackendStatus(status);
        });

        // Listen for agent state updates
        const removeAgentListener = window.electronAPI.onAgentUpdate((data: AgentMessage) => {
            setAgentStatus(data);
            if (data.manifest) updateManifest(data.manifest);
        });

        // Setup Heartbeat Emission
        heartbeatInterval.current = setInterval(() => {
            window.electronAPI.sendHeartbeat();
        }, 1000);

        return () => {
            removeStatusListener();
            removeAgentListener();
            if (heartbeatInterval.current) clearInterval(heartbeatInterval.current);
        };
    }, [setAgentStatus, setBackendStatus, updateManifest]);

    return {
        selectFolder: window.electronAPI.selectFolder,
        startAgentLoop: window.electronAPI.startAgentLoop,
    };
};
