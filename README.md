# VibeArchitect

**The Ultimate Agentic UI & Architect for Vibe Coding**

VibeArchitect is a professional-grade orchestrator that transforms high-level ideas into structured, technical project blueprints. It bridges the gap between "thinking" and "coding" by generating all necessary assets (rules, skills, documentation) for AI coding agents to execute.

## 🚀 Vision & Core Principles

* **No-Sugarcoat Architecture**: Every plan must be technically sound. If an idea is a "fantasy" that current APIs or logic cannot support, the system will flag it.
* **Visible Reasoning**: See the agents' "thoughts" in real-time. No black boxes.
* **Atomic Planning**: Screens are not just names; they are collections of components, logic, and data flows.
* **Agent Native**: Everything generated is designed to be natively consumed by an agent's inner loop.

## 🏗️ Tech Stack

* **Frontend (The Editor)**: Electron.js + React + Tailwind CSS
* **Backend (The Brain)**: Node.js (IPC) + Python (Agent Orchestration)
* **LLM Providers**:
  * Tier 1: Cerebras API (Qwen-2.5-72B) - Primary engine for high-speed planning.
  * Tier 2: Ollama (Local) - Fallback for privacy and offline work.

## 🧠 The 5-Agent Pipeline

1. **The Visionary**: Receives the "vibe," defines the tech stack, and sets the project scope.
2. **UI/UX Architect**: Breaks the vibe into screens, components, and user journeys.
3. **System Engineer**: Drafts API routes, database schemas, and technical rules.
4. **Agent Expert**: Translates the plan into `.md` files, `/rules` folder, and `/skills` scripts.
5. **The Auditor (Final Boss)**: Cross-references the `manifest.json` to ensure the UI and Backend are 100% aligned before final output.

## 🖥️ UI Layout & User Experience

* **Project Initialization**: Select a local directory to populate the initial structure.
* **The Pipeline View**: A visual roadmap showing which agent is currently active.
* **Step-by-Step Approval**: Pause the loop after each agent's output to edit or approve before moving to the next phase.
* **Output Preview**: A split-screen view showing the generated folder structure and the content of the selected file.

## 📁 Target Output Directory Structure

When a project is fully mapped, VibeArchitect populates:

```text
/your-selected-project
├── .vibe_architect/      # Internal state & manifest.json
├── GEMINI.md             # The master plan
├── /rules                # Linter and architectural constraints
├── /skills               # Custom python tools for agents
├── /docs                 # Screen-by-screen & API documentation
└── /phases               # Specific prompts for each development phase
```

## 📜 Workflow Protocol

The pipeline follows a strict read-modify-write pattern utilizing a central `manifest.json`.

* **Phase 0 (Idle)**: System waits for the "Vibe" prompt and folder selection.
* **Phase 1-5**: Agent states representing brainstorming, blueprinting, engineering, translation, and verification.
* **Phase 6 (Output)**: Once approved, the project is completely structured and ready!

VibeArchitect places the user firmly as the "Human-in-the-Loop" allowing pause & pivot, auditor bypass, and re-rolling specific steps when needed.
