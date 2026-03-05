​Project: VibeArchitect
​The Ultimate Agentic UI & Architect for Vibe Coding
​1. Vision
​VibeArchitect is a professional-grade orchestrator that transforms high-level ideas into structured, technical project blueprints. It bridges the gap between "thinking" and "coding" by generating all necessary assets (rules, skills, documentation) for Google Antigravity agents to execute.
​2. Core Principles
​No-Sugarcoat Architecture: Every plan must be technically sound. If an idea is a "fantasy" that current APIs or logic cannot support, the system must flag it.
​Visible Reasoning: The user must see the agents' "thoughts" in real-time. No black boxes.
​Atomic Planning: Screens are not just names; they are collections of components, logic, and data flows.
​Antigravity Native: Everything generated is designed to be consumed by Antigravity's agentic loop.
​3. Tech Stack (The "How")
​Frontend (The Editor): Electron.js + React + Tailwind CSS.
​Key Features: Folder picker (native dialog), Monaco Editor (for code/docs preview), Xterm.js (for agent logs), Framer Motion (for smooth pipeline transitions).
​Backend (The Brain): Node.js (IPC) + Python (Agent Orchestration).
​LLM Providers:
​Tier 1: Cerebras API (Qwen-2.5-72B) - Primary engine for high-speed planning.
​Tier 2: Ollama (Local) - Fallback for privacy and offline work.
​4. The 5-Agent Pipeline
​The Visionary: Receives the "vibe," defines the tech stack, and sets the project scope.
​UI/UX Architect: Breaks the vibe into screens, components, and user journeys.
​System Engineer: Drafts API routes, database schemas, and technical rules.
​Antigravity Expert: Translates the plan into .md files, /rules folder, and /skills scripts.
​The Auditor (Final Boss): Cross-references the manifest.json to ensure the UI and Backend are 100% aligned before final output.
​5. UI Layout & User Experience
​Project Initialization: User selects a local directory. The software populates the initial structure.
​The Pipeline View: A visual roadmap showing which agent is currently active.
​Step-by-Step Approval: The user can pause the loop after each agent's output to edit or approve the manifest.json before moving to the next phase.
​Output Preview: A split-screen view showing the generated folder structure on the left and the content of the selected file on the right.
​6. Generated Directory Structure (Target)
​When the user selects a folder, VibeArchitect populates:
/your-selected-project
├── .vibe_architect/      # Internal state & manifest.json
├── GEMINI.md             # The master plan
├── /rules                # Linter and architectural constraints
├── /skills               # Custom python tools for Antigravity agents
├── /docs                 # Screen-by-screen & API documentation
└── /phases               # Specific prompts for each development phase
