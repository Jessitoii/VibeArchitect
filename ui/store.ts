import { create } from "zustand";

import { AgentMessage } from "./types/electron";

export interface AppException {
    id: string;
    title: string;
    traceback: string;
    timestamp: number;
}

interface AppState {
    projectPath: string | null;
    vibePrompt: string;
    currentAgent: string | null;
    currentProvider: string | null;
    agentStatus: "idle" | "thinking" | "writing" | "validating" | "complete" | "error" | "WAITING_APPROVAL" | "IDE_MODE" | "WAITING_NEXT_PHASE";
    isAgentActive: boolean;
    backendStatus: "connected" | "disconnected" | "error";
    manifest: any;
    exceptions: AppException[];

    // IDE State
    currentView: "blueprint" | "ide";
    activeFilePath: string | null;
    activeFileContent: string | null;
    chatHistory: { role: string; content: string }[];
    autoAccept: boolean;
    pendingEdits: { filepath: string; original_content: string | null; modified_content: string }[];

    // Actions
    setProjectPath: (path: string | null) => void;
    setVibePrompt: (vibe: string) => void;
    setAgentStatus: (status: AgentMessage) => void;
    setBackendStatus: (status: "connected" | "disconnected" | "error") => void;
    updateManifest: (manifest: any) => void;
    addException: (title: string, traceback: string) => void;
    dismissException: (id: string) => void;
    clearExceptions: () => void;
    setCurrentView: (view: "blueprint" | "ide") => void;
    setActiveFile: (path: string | null, content: string | null) => void;
    appendChatMessage: (message: { role: string; content: string }) => void;
    setAutoAccept: (autoAccept: boolean) => void;
    setPendingEdits: (edits: { filepath: string; original_content: string | null; modified_content: string }[]) => void;
    popPendingEdit: () => void;
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
    exceptions: [],
    currentView: "blueprint",
    activeFilePath: null,
    activeFileContent: null,
    chatHistory: [],
    autoAccept: false,
    pendingEdits: [],

    setProjectPath: (projectPath: string | null) => set({ projectPath }),
    setVibePrompt: (vibePrompt: string) => set({ vibePrompt }),
    setAgentStatus: (status: AgentMessage) => set({
        currentAgent: status.agent,
        currentProvider: status.provider || null,
        agentStatus: status.status,
        isAgentActive: status.status !== "complete" && status.status !== "error" && status.status !== "WAITING_APPROVAL" && status.status !== "IDE_MODE" && status.status !== "WAITING_NEXT_PHASE"
    }),
    setBackendStatus: (status: "connected" | "disconnected" | "error") => set({ backendStatus: status }),
    updateManifest: (manifest: any) => set({ manifest }),
    addException: (title: string, traceback: string) => set((state) => ({
        exceptions: [...state.exceptions, { id: Math.random().toString(36).substr(2, 9), title, traceback, timestamp: Date.now() }]
    })),
    dismissException: (id: string) => set((state) => ({
        exceptions: state.exceptions.filter(e => e.id !== id)
    })),
    clearExceptions: () => set({ exceptions: [] }),
    setCurrentView: (view: "blueprint" | "ide") => set({ currentView: view }),
    setActiveFile: (path: string | null, content: string | null) => set({ activeFilePath: path, activeFileContent: content }),
    appendChatMessage: (message: { role: string; content: string }) => set((state) => ({ chatHistory: [...state.chatHistory, message] })),
    setAutoAccept: (autoAccept: boolean) => set({ autoAccept }),
    setPendingEdits: (edits) => set({ pendingEdits: edits }),
    popPendingEdit: () => set((state) => ({ pendingEdits: state.pendingEdits.slice(1) })),
    reset: () => set({
        projectPath: null,
        vibePrompt: "",
        currentAgent: null,
        currentProvider: null,
        agentStatus: "idle",
        isAgentActive: false,
        backendStatus: "connected",
        manifest: {},
        exceptions: [],
        currentView: "blueprint",
        activeFilePath: null,
        activeFileContent: null,
        chatHistory: [],
        autoAccept: false
    })
}));
