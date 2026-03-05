import { create } from "zustand";

import { AgentMessage } from "./types/electron";

interface AppState {
    projectPath: string | null;
    vibePrompt: string;
    currentAgent: string | null;
    currentProvider: string | null;
    agentStatus: "idle" | "thinking" | "writing" | "validating" | "complete" | "error";
    isAgentActive: boolean;
    backendStatus: "connected" | "disconnected" | "error";
    manifest: any;

    // Actions
    setProjectPath: (path: string | null) => void;
    setVibePrompt: (vibe: string) => void;
    setAgentStatus: (status: AgentMessage) => void;
    setBackendStatus: (status: "connected" | "disconnected" | "error") => void;
    updateManifest: (manifest: any) => void;
    reset: () => void;
}

export const useStore = create<AppState>((set) => ({
    projectPath: null,
    vibePrompt: "",
    currentAgent: null,
    currentProvider: null,
    agentStatus: "idle",
    isAgentActive: false,
    backendStatus: "connected",
    manifest: {},

    setProjectPath: (projectPath: string | null) => set({ projectPath }),
    setVibePrompt: (vibePrompt: string) => set({ vibePrompt }),
    setAgentStatus: (status: AgentMessage) => set({
        currentAgent: status.agent,
        currentProvider: status.provider || null,
        agentStatus: status.status,
        isAgentActive: status.status !== "idle" && status.status !== "complete" && status.status !== "error"
    }),
    setBackendStatus: (status: "connected" | "disconnected" | "error") => set({ backendStatus: status }),
    updateManifest: (manifest: any) => set({ manifest }),
    reset: () => set({
        projectPath: null,
        vibePrompt: "",
        currentAgent: null,
        currentProvider: null,
        agentStatus: "idle",
        isAgentActive: false,
        backendStatus: "connected",
        manifest: {}
    })
}));
