# VibeArchitect — Always-On Rules

## R1: Manifest is Truth
Every agent reads from and writes to manifest.json only. If it's not in the manifest, it doesn't exist.

## R2: No Hallucination
"No Data" beats "Fake Data". Never assume a tech stack, field, or feature the Visionary didn't define.

## R3: Atomic Handoff
Each agent sets status: COMMITTED before the next starts. No COMMITTED = no handoff.

## R4: UI ↔ Backend Parity
Every UI component must have a corresponding API endpoint. The Auditor enforces this. No exceptions.

## R5: Non-Blocking UI
The Electron frontend must remain responsive during all agent streaming. Never block the main thread.