---
trigger: always_on
---

Workflow Protocol: VibeArchitect
1. The Pipeline Lifecycle
The pipeline follows a strict state-machine logic. An agent cannot start until the previous agent has set its status to COMMITTED in the manifest.json.
Phase State Trigger Description
0. Idle AWAITING_INPUT User launches app The system waits for the "Vibe" prompt and folder selection.
1. Brainstorming VISIONARY_ACTIVE User clicks "Start" Agent 1 defines the scope and stack.
2. Blueprinting ARCHITECT_ACTIVE Visionary COMMITTED Agent 2 maps screens and components.
3. Engineering ENGINEER_ACTIVE Architect COMMITTED Agent 3 defines APIs and schemas.
4. Translation EXPERT_ACTIVE Engineer COMMITTED Agent 4 creates Antigravity assets.
5. Verification AUDITOR_ACTIVE Expert COMMITTED Agent 5 performs the final cross-check.
6. Output COMPLETED Auditor APPROVED
2. The Handoff Mechanism (The "Commit" Rule)
Every agent transition must follow the Read-Modify-Write pattern:
Read: Pull the entire manifest.json.
Process: Execute the internal logic (Cerebras/Ollama).
Validate: Ensure the new data doesn't break existing keys.
Write: Update the manifest with status: "COMMITTED" and the new payload.
Constraint: If an agent fails to generate valid JSON or misses a mandatory field, the state reverts to ERROR and the pipeline pauses.
3. User Intervention Points (The "Human-in-the-Loop")
VibeArchitect is not a "black box." The user has three specific intervention powers:
The Pause & Pivot: After any agent finishes, the UI will present a "Review & Edit" screen. You can modify the JSON directly before the next agent reads it.
The Auditor Bypass: If the Auditor flags a "Logic Gap" that you find acceptable, you can manually trigger an OVERRIDE_APPROVE to force the output.
The Re-Roll: If a specific agent's output is "weak," you can trigger a RE_GENERATE command for that specific step with a hint (e.g., "Add more detail to the Login screen logic").
4. Conflict Resolution & Retries
If the Auditor finds a mismatch (e.g., UI needs a field the API doesn't provide):
Conflict Flagged: The system marks the specific fields in manifest.json.
Logic Feedback: The system generates a "Correction Prompt" for the responsible agent.
Automatic Retry (Max 2): The system attempts to fix the conflict twice. If it fails a third time, it triggers a USER_REQUIRED block.
5. Antigravity Deployment
Once the pipeline hits COMPLETED, the Antigravity Expert agent performs the following file operations:
Injects the manifest.json into .vibe_architect/.
Scaffolds the /rules and /skills folders.
Generates a PROMPT_QUEUE.md—a sequential list of prompts you can copy-paste into Antigravity to build the project phase-by-phase.
