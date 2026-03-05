import asyncio
from typing import AsyncGenerator, Dict, Any
from core.agents.base import BaseAgent
from core.schema import (
    Manifest,
    AgentMessage,
    AgentStatus,
    AuditEntry,
    AgentRule,
    InstructionalBrain,
)


class AuditorAgent(BaseAgent):
    def __init__(self, manifest: Manifest):
        super().__init__("Auditor", manifest)
        self.system_prompt = """
        You are 'The Auditor' (The Final Boss).
        Your job is to find reasons why the project will FAIL.
        
        OUTPUT FORMAT:
        You must output valid JSON:
        {
            "approved": true/false,
            "audit_log": [
                {"severity": "critical/warning/info", "message": "...", "location": "...", "check_id": "..."}
            ]
        }
        
        RULES:
        1. Zero-Trust. Assume there are gaps between the UI and Backend.
        2. Cross-Validation. Check if a UI component's 'data_source_id' exists in the Tech Specs API IDs.
        3. Skepticism. Flag any 'technical debt' or 'security risks' early.
        """

    async def execute(self, prompt: str) -> AsyncGenerator[AgentMessage, None]:
        """
        Modified execute for 'Hybrid Auditing' (LLM + Programmatic checks).
        """
        # 1. Programmatic Check (Cross-Referencing IDs & Dependency Auditing)
        async for _ in self.stream_thought(
            "Starting programmatic validation of dependencies and types..."
        ):
            pass
        programmatic_logs = self._run_programmatic_checks()

        # 2. LLM Audit
        prompt = f"Current Plan: {self.manifest.model_dump_json()}\n\nProgrammatic Initial Findings: {programmatic_logs}\n\nPerform final audit."

        async for msg in super().execute(prompt):
            if msg.status == AgentStatus.COMPLETE:
                # Merge programmatic logs with LLM output
                final_audit_log = programmatic_logs + msg.data_update.get(
                    "audit_log", []
                )
                msg.data_update["audit_log"] = final_audit_log

                # Auditor-to-Rule Bridge
                self._generate_preventative_rules(final_audit_log)
                msg.data_update["instructional_brain"] = (
                    self.manifest.instructional_brain.model_dump()
                    if self.manifest.instructional_brain
                    else {}
                )

            yield msg

    def _generate_preventative_rules(self, audit_log: list):
        """Converts auditor findings into preventative .md rules."""
        if not self.manifest.instructional_brain:
            self.manifest.instructional_brain = InstructionalBrain()

        for idx, entry in enumerate(audit_log):
            if entry.get("severity") in ["critical", "warning"]:
                check_id = entry.get("check_id", f"AUDIT_RULE_{idx}")
                rule = AgentRule(
                    filename=f"auto_{check_id.lower()}.md",
                    description=f"Auto-generated rule preventing: {entry.get('message')}",
                    content=f"# Preventative Rule: {check_id}\n\n**Severity:** {entry.get('severity')}\n\n**Reason:** {entry.get('message')}\n\n**Action:** The execution agent must ensure this issue is actively prevented during implementation.",
                )
                self.manifest.instructional_brain.rules.append(rule)

    def _run_programmatic_checks(self) -> list:
        logs = []
        ui_components = []
        api_routes = {}

        # Collect UI Components
        if self.manifest.ui_map:
            for screen in self.manifest.ui_map.screens:
                for comp in screen.components:
                    ui_components.append((screen.name, comp))

        # Collect API Routes
        if self.manifest.tech_specs:
            for route in self.manifest.tech_specs.api_routes:
                api_routes[route.id] = route

        # Dependency and Type Auditing
        for screen_name, comp in ui_components:
            if not comp.data_source_id:
                continue

            uid = comp.data_source_id
            if uid not in api_routes:
                logs.append(
                    {
                        "severity": "critical",
                        "message": f"UI Component '{comp.name}' (ID: '{uid}') on '{screen_name}' lacks a corresponding API endpoint in tech_specs.",
                        "location": "ui_map -> tech_specs",
                        "check_id": "MISSING_ENDPOINT",
                    }
                )
            else:
                route = api_routes[uid]
                # Dependency Auditing: Check data type compatibility
                # Example: If logic implies list/array but endpoint response is not
                if route.response:
                    desc_logic = f"{comp.description} {comp.logic or ''}".lower()
                    route_resp_str = str(route.response).lower()

                    if (
                        "list" in desc_logic
                        or "array" in desc_logic
                        or "multiple" in desc_logic
                    ):
                        # Heuristic: Check if response implies array/list
                        if (
                            "list" not in route_resp_str
                            and "array" not in route_resp_str
                            and "items" not in route_resp_str
                            and "[" not in route_resp_str
                        ):
                            logs.append(
                                {
                                    "severity": "warning",
                                    "message": f"UI Component '{comp.name}' implies a list/array but endpoint '{uid}' response format might not be compatible.",
                                    "location": "ui_map -> tech_specs",
                                    "check_id": "TYPE_MISMATCH_WARNING",
                                }
                            )

        if not logs:
            logs.append(
                {
                    "severity": "info",
                    "message": "All UI cross-references and baseline types matched API specs.",
                    "check_id": "XREF_OK",
                }
            )

        return logs

    def get_prompt(self, vibe: str) -> str:
        return "Audit the manifest for inconsistencies."
