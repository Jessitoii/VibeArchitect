export interface AgentMessage {
    agent: string;
    status: "thinking" | "writing" | "validating" | "complete" | "error" | "WAITING_APPROVAL" | "IDE_MODE" | "WAITING_NEXT_PHASE" | "AGENT_FINISHED";
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
    readDir: (dirPath: string) => Promise<{ name: string; isDirectory: boolean; path: string }[]>;
    readFile: (filePath: string) => Promise<string | null>;
    saveFile: (filePath: string, content: string) => Promise<{ success: boolean; error?: string }>;
    deleteFile: (filePath: string) => Promise<{ success: boolean; error?: string }>;
    getManifest: (projectPath: string) => Promise<any | null>;
    saveManifest: (projectPath: string, manifest: any) => Promise<{ success: boolean; error?: string }>;
    watchDir: (dirPath: string) => Promise<{ success: boolean; error?: string }>;
    proceedNextPhase: () => void;
    stopGeneration: () => void;
    retryPipeline: () => void;
    sendHeartbeat: () => void;
    onBackendStatus: (callback: (status: "connected" | "disconnected" | "error") => void) => () => void;
    onAgentUpdate: (callback: (data: AgentMessage) => void) => () => void;
    onLogUpdate: (callback: (data: string) => void) => () => void;
    onFileChanged: (callback: (filename: string) => void) => () => void;
    approveDeployment: () => void;
}

declare global {
    interface Window {
        electronAPI: ElectronAPI;
    }
}
