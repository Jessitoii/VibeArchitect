from typing import AsyncGenerator
import json
import asyncio


class MockProvider:
    def __init__(self):
        self.primary_name = "mock"

    async def stream_chat(
        self, prompt: str, system_prompt: str
    ) -> AsyncGenerator[str, None]:
        """
        Emergency Mock Provider for Offline/Firewall block scenarios.
        Returns pre-defined dummy JSON structures so the orchestrator state machine can proceed
        with UI and pipeline testing when completely isolated.
        """

        system_prompt_lower = system_prompt.lower()
        prompt_lower = prompt.lower()

        if "visionary" in system_prompt_lower:
            output = {
                "features": ["Emergency Mock Feature 1", "Offline Development Mode"],
                "tech_stack": {
                    "frontend": "React",
                    "backend": "Python/FastAPI",
                    "database": "SQLite",
                },
                "constraints": ["Mock Environment", "No Live LLM Connection Allowed"],
                "high_level_goals": [
                    "Test Orchestrator State Machine",
                    "Bypass Corporate Firewall",
                ],
            }
        elif "architect" in system_prompt_lower or "ui map" in prompt_lower:
            output = {
                "screens": [
                    {
                        "name": "Mock Emergency Dashboard",
                        "components": [
                            {
                                "name": "MockConnectionStatus",
                                "description": "Displays offline mode",
                                "logic": "Loads status locally",
                                "data_source_id": "MOCK_STATUS_API",
                            }
                        ],
                        "user_journey": "User opens dashboard and sees mock items because the firewall blocked everything.",
                    }
                ],
                "theme": {"primary": "#ff0000", "secondary": "#000000"},
            }
        elif "engineer" in system_prompt_lower or "api routes" in prompt_lower:
            output = {
                "api_routes": [
                    {
                        "id": "MOCK_STATUS_API",
                        "path": "/api/v1/mock-status",
                        "method": "GET",
                        "request": {},
                        "response": {
                            "status": "offline_mode",
                            "items": ["array of mock data"],
                        },
                    }
                ],
                "database_schema": {
                    "tables": [{"name": "mock_status", "columns": ["id", "status"]}]
                },
                "external_integrations": ["Mock API"],
            }
        elif "antigravity expert" in system_prompt_lower:
            output = {
                "detected_domains": ["frontend"],
                "agent_md": (
                    "# AGENT.md\n\n"
                    "## ① Project Soul\nMock offline-resilient dashboard (frontend-only, no backend/DB).\n\n"
                    "## ② Detected Infrastructure\n"
                    "| Domain | Included | Reason |\n|---|---|---|\n"
                    "| frontend | ✅ | UI screens in manifest |\n"
                    "| backend | ❌ | No API routes |\n"
                    "| database | ❌ | No schema |\n"
                    "| infra | ❌ | No deploy requirements |\n\n"
                    "## ③ Strategic Pointers\n- Rules: `.agent/RULES.md`\n- Docs: `/docs/ui/`\n- Skills: `.agent/skills/`\n\n"
                    "## ④ Parallel Execution Map\nSingle domain — no parallelism needed.\n\n"
                    "## ⑤ Operational State\nPhase: Expert. Status: COMMITTED."
                ),
                "rules_md": (
                    "# RULES.md — Constitution\n\n"
                    "## § ALWAYS-ON META-RULES\n\n"
                    "### M-1 · Immutable Manifest\nAll agents read/write manifest.json only.\n\n"
                    "### M-2 · No Hallucination\nEmit null over fabricated data.\n\n"
                    "### M-3 · Atomic Commit\nRead → Process → Validate → Write.\n\n"
                    "### M-4 · Visible Reasoning\nAll output matches the protocol JSON.\n\n"
                    "## § ON-DEMAND RULES\n\n"
                    "### [FRONTEND] Rules\n> **Trigger:** frontend, react, component\n"
                    "- Components: PascalCase\n- Hooks: useXxx\n- No inline styles\n- Error boundaries on every data-fetching component"
                ),
                "sub_agent_rules": [
                    {
                        "domain": "frontend",
                        "filename": "frontend_agent.md",
                        "content": (
                            "# Frontend Agent Rulebook\n\n"
                            "## Tech Stack\n- React 18 + TypeScript\n- Tailwind CSS 3.x\n- Zustand (state)\n\n"
                            "## Naming Conventions\n- Components: PascalCase\n- Hooks: useXxx\n- Files: kebab-case\n\n"
                            "## Constraints\n- No inline styles\n- All API calls via `services/` layer\n- Error boundaries on every data-fetching component\n\n"
                            "## Parallel Safety\n- This agent owns: /src/components/, /src/pages/, /src/hooks/\n- Do NOT touch: /server/, /db/, /infra/"
                        ),
                        "description": "Frontend sub-agent rulebook. Load before any UI/component/Tailwind work.",
                        "trigger_words": [
                            "frontend",
                            "react",
                            "component",
                            "tailwind",
                            "ui",
                            "typescript",
                        ],
                    }
                ],
                "metadata_index": [
                    {
                        "path": "AGENT.md",
                        "description": "Identity hub. Detected domains, parallel execution map, pointers to all assets. Read FIRST.",
                        "trigger_words": ["identity", "overview", "domains", "vibe"],
                    },
                    {
                        "path": "RULES.md",
                        "description": "Constitution. Always-on meta-rules + on-demand frontend rules.",
                        "trigger_words": ["rules", "constraint", "protocol"],
                    },
                    {
                        "path": "rules/sub_agents/frontend_agent.md",
                        "description": "Frontend sub-agent rulebook. Load before any React/Tailwind/component work.",
                        "trigger_words": ["frontend", "react", "component", "tailwind"],
                    },
                    {
                        "path": "skills/offline-resilience-expert/SKILL.md",
                        "description": "Offline handling capability doc. Load for network-resilient features.",
                        "trigger_words": ["offline", "network", "resilience", "cache"],
                    },
                    {
                        "path": "../docs/ui/mock_dashboard.md",
                        "description": "Visual spec for Mock Dashboard — offline state UI, empty states.",
                        "trigger_words": ["dashboard", "offline", "ui"],
                    },
                ],
                "rules": [
                    {
                        "filename": "auto_offline_rule.md",
                        "content": "# Preventative Rule: OFFLINE_HANDLING\n\n**Severity:** warning\n\n**Reason:** All data fetches must have offline fallback states.\n\n**Action:** Implement error boundaries and local cache for every network call.",
                        "description": "Ensures all data-fetching components gracefully handle offline/network failure.",
                    }
                ],
                "workflows": [
                    {
                        "filename": "phase_1_setup.md",
                        "content": "# Phase 1: Project Setup\n\n**Domains:** [all]\n**Required Resources:** None (bootstrapping)\n\n## Steps\n1. Initialize repo\n2. Install deps: `npm install`\n3. Configure Tailwind and TypeScript",
                        "success_criteria": [
                            "Dev server starts",
                            "TypeScript compiles without errors",
                        ],
                        "parent_phase": None,
                    },
                    {
                        "filename": "phase_2.1_dashboard_layout.md",
                        "content": "# Phase 2.1: Dashboard Layout\n\n**Domain:** frontend\n**Required Resources:**\n- Doc: `/docs/ui/mock_dashboard.md`\n- Sub-Agent Rulebook: `.agent/rules/sub_agents/frontend_agent.md`\n- Skill: `.agent/skills/offline-resilience-expert/SKILL.md`\n\n## Steps\n1. Build Dashboard shell with Tailwind\n2. Add header, sidebar, content area\n3. Add offline status banner",
                        "success_criteria": [
                            "Dashboard renders with mock data",
                            "Offline banner visible when navigator.onLine is false",
                        ],
                        "parent_phase": "phase_2",
                    },
                    {
                        "filename": "phase_2.2_data_loading.md",
                        "content": "# Phase 2.2: Data Loading States\n\n**Domain:** frontend\n**Required Resources:**\n- Doc: `/docs/ui/mock_dashboard.md`\n- Sub-Agent Rulebook: `.agent/rules/sub_agents/frontend_agent.md`\n- Skill: `.agent/skills/offline-resilience-expert/SKILL.md`\n\n## Steps\n1. Implement loading skeleton\n2. Implement empty state\n3. Cache last-known-good data in localStorage",
                        "success_criteria": [
                            "Loading skeleton visible during fetch",
                            "Empty state shown when list is empty",
                            "Cached data shown when offline",
                        ],
                        "parent_phase": "phase_2",
                    },
                ],
                "docs": [
                    {
                        "filename": "ui/mock_dashboard.md",
                        "content": (
                            "# Mock Dashboard\n\n"
                            "## Visual Hierarchy\nFull-screen alert banner (top) → Status indicator (header) → Cached data list (main)\n\n"
                            "## Component Placements\n- `<OfflineBanner>` — sticky top, z-50\n- `<StatusIndicator>` — header right\n- `<DataList>` — main content, virtualized\n\n"
                            "## State Management\n- `isOnline: boolean` — derived from navigator.onLine + online/offline events\n- `data: Entry[] | null` — fetched, null on first load\n- `lastSynced: Date | null` — timestamp of last successful fetch\n\n"
                            "## Empty States\n- No data: 'No entries yet. Data will appear once connected.'\n- Offline + cached: 'Showing cached data from {lastSynced}'\n- Error: 'Failed to load. Check your connection.'\n\n"
                            "## User Psychology\nOffline-first pattern: user must always see something. Never a blank screen."
                        ),
                    }
                ],
                "skills": [
                    {
                        "filename": "offline-resilience-expert/SKILL.md",
                        "content": (
                            "---\n"
                            "name: offline-resilience-expert\n"
                            "description: Expert reasoning for offline-first architecture, network failure handling, localStorage caching, and service worker strategies. Load for any offline, network error, or resilience task.\n"
                            "trigger_words: [offline, network, resilience, cache, service-worker]\n"
                            "disable-model-invocation: false\n"
                            "---\n\n"
                            "# Offline Resilience Expert\n\n"
                            "## Reasoning Process\n"
                            "1. Identify all network-dependent operations\n"
                            "2. Implement local cache layer (localStorage or IndexedDB)\n"
                            "3. Add retry with exponential backoff (max 3 retries)\n"
                            "4. Add online/offline event listeners\n\n"
                            "## Edge Cases\n"
                            "- Partial sync failures: show stale data with staleness indicator\n"
                            "- Cache invalidation on reconnect: fetch fresh data, merge with local\n"
                            "- Storage quota exceeded: gracefully degrade to in-memory\n\n"
                            "## Strategic Constraints\n"
                            "- Never show raw network errors to users\n"
                            "- Always provide last-known-good data when available\n"
                            "- Offline-first: assume network is unreliable"
                        ),
                    }
                ],
            }
        elif "auditor" in system_prompt_lower:
            output = {
                "approved": True,
                "audit_log": [
                    {
                        "severity": "info",
                        "message": "Mock audit passed successfully during offline mode simulation.",
                        "location": "mock_layer",
                        "check_id": "MOCK_AUDIT_OK",
                    }
                ],
            }
        else:
            output = {"status": "Mock fallback general success"}

        # Simulate streaming latency
        json_str = json.dumps(output, indent=2)

        chunk_size = 20
        # Yield 'thinking' thought process explicitly if possible, or just raw tokens
        for i in range(0, len(json_str), chunk_size):
            await asyncio.sleep(0.01)
            yield json_str[i : i + chunk_size]
