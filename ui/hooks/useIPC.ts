import { useEffect, useRef } from "react";
import { useStore } from "../store";
import { AgentMessage } from "../types/electron";

export const useIPC = () => {
    const { setAgentStatus, setBackendStatus, updateManifest, addException } = useStore();
    const heartbeatInterval = useRef<NodeJS.Timeout>();

    useEffect(() => {
        // Listen for backend status (heartbeat monitoring)
        const removeStatusListener = window.electronAPI.onBackendStatus((status: "connected" | "disconnected" | "error") => {
            setBackendStatus(status);
        });

        // Listen for agent state updates
        const removeAgentListener = window.electronAPI.onAgentUpdate((data: any) => {
            if (data.status === "error" && data.data_update?.traceback) {
                addException(data.data_update.title || "Exception Caught", data.data_update.traceback);
            }
            if (data.status === "error" || data.agent) {
                setAgentStatus(data as AgentMessage);
                if (data.manifest) updateManifest(data.manifest);
            }
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
    }, [setAgentStatus, setBackendStatus, updateManifest, addException]);

    return {
        selectFolder: window.electronAPI.selectFolder,
        startAgentLoop: window.electronAPI.startAgentLoop,
        retryPipeline: window.electronAPI.retryPipeline,
    };
};
