export interface AgentMessage {
    agent: string;
    status: "thinking" | "writing" | "validating" | "complete" | "error";
    data_update: any;
    thought_process: string;
    conflicts: string[];
    raw_stream?: string;
    manifest?: any;
    provider?: string;
}

export interface ElectronAPI {
    selectFolder: () => Promise<string | null>;
    startAgentLoop: (vibe: string, projectPath: string) => Promise<{ success: boolean; error?: string }>;
    sendHeartbeat: () => void;
    onBackendStatus: (callback: (status: "connected" | "disconnected" | "error") => void) => () => void;
    onAgentUpdate: (callback: (data: AgentMessage) => void) => () => void;
    onLogUpdate: (callback: (data: string) => void) => () => void;
}

declare global {
    interface Window {
        electronAPI: ElectronAPI;
    }
}
