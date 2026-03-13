---
name: react-ui
description: React + Tailwind component conventions and state management for VibeArchitect UI
triggers: ["react", "component", "ui", "tailwind", "store", "zustand", "tsx", "frontend"]
---

# React UI Skill

## Structure
- `ui/App.tsx` — Root, routing between pipeline stages
- `ui/store.ts` — Zustand store, single source of UI truth
- `ui/components/` — One file per component
- `ui/hooks/useIPC.ts` — All Electron IPC calls go here

## Component Convention
```tsx
// Always typed props, no `any`
interface AgentCardProps {
  agent: AgentMessage
  isActive: boolean
}

export const AgentCard = ({ agent, isActive }: AgentCardProps) => {
  // Tailwind only — no inline styles
}
```

## Store Pattern
```ts
// ui/store.ts — Zustand
interface AppState {
  messages: AgentMessage[]
  manifest: Manifest | null
  status: PipelineStatus
  addMessage: (msg: AgentMessage) => void
}
```

## Rules
- All agent messages go through `store.addMessage()` — never local state for pipeline data
- Monaco Editor and Xterm.js are heavy — lazy load with `React.lazy()`
- No direct `window.electronAPI` calls in components — always through `useIPC` hook
- Pipeline status drives UI rendering — no separate `isLoading` booleans