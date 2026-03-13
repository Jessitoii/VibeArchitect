import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List
from core.schema import Manifest, PipelineStatus, AgentStatus, AgentMessage
from core.state_manager import StateManager
from core.generator import InstructionalBrainGenerator
from core.agents.visionary import VisionaryAgent
from core.agents.architect import ArchitectAgent
from core.agents.engineer import EngineerAgent
from core.agents.expert import ExpertAgent
from core.agents.auditor import AuditorAgent
from core.exceptions import AgentValidationError, VibeArchitectError


class Orchestrator:
    def __init__(self, project_path: str):
        self.state_manager = StateManager(project_path)
        self.generator = InstructionalBrainGenerator(project_path)
        self.manifest: Manifest = self.state_manager.load_latest() or Manifest(
            project_name="New Project"
        )
        self.agents = {
            PipelineStatus.VISIONARY_ACTIVE: VisionaryAgent(self.manifest),
            PipelineStatus.ARCHITECT_ACTIVE: ArchitectAgent(self.manifest),
            PipelineStatus.ENGINEER_ACTIVE: EngineerAgent(self.manifest),
            PipelineStatus.EXPERT_ACTIVE: ExpertAgent(self.manifest),
            PipelineStatus.AUDITOR_ACTIVE: AuditorAgent(self.manifest),
        }
        self.pipeline_order = [
            PipelineStatus.VISIONARY_ACTIVE,
            PipelineStatus.ARCHITECT_ACTIVE,
            PipelineStatus.ENGINEER_ACTIVE,
            PipelineStatus.EXPERT_ACTIVE,
            PipelineStatus.AUDITOR_ACTIVE,
        ]

    async def resume_pipeline(self, vibe: str) -> AsyncGenerator[AgentMessage, None]:
        """Resumes the pipeline from the last uncompleted phase by checking manifest state."""
        print(f"[DEBUG] resume_pipeline called with vibe: {vibe[:30]}")
        latest = self.state_manager.load_latest()
        print(f"[DEBUG] load_latest result: {latest}")
        print(f"[DEBUG] current manifest status: {self.manifest.status}")
        print(f"[DEBUG] product_scope exists: {bool(self.manifest.product_scope)}")
        latest_manifest = self.state_manager.load_latest()
        if latest_manifest:
            self.manifest = latest_manifest

        # Resume logic: Prioritize content presence to avoid re-running finished phases
        if self.manifest.status in [
            PipelineStatus.AUDITOR_APPROVED,
            PipelineStatus.COMPLETED,
        ]:
            start_index = 4
        elif not getattr(self.manifest, "product_scope", None):
            start_index = 0
            self.manifest.status = PipelineStatus.VISIONARY_ACTIVE
        elif not getattr(self.manifest, "ui_map", None):
            start_index = 1
            self.manifest.status = PipelineStatus.ARCHITECT_ACTIVE
        elif not getattr(self.manifest, "tech_specs", None):
            start_index = 2
            self.manifest.status = PipelineStatus.ENGINEER_ACTIVE
        elif not getattr(self.manifest, "instructional_brain", None):
            start_index = 3
            self.manifest.status = PipelineStatus.EXPERT_ACTIVE
        else:
            start_index = 4
            self.manifest.status = PipelineStatus.AUDITOR_ACTIVE

        async for msg in self._run_pipeline_from(vibe, start_index):
            yield msg

    async def run_pipeline(self, vibe: str) -> AsyncGenerator[AgentMessage, None]:
        """
        Runs the full 5-agent pipeline with in-memory snapshots and rollback.
        """
        async for msg in self._run_pipeline_from(vibe, 0):
            yield msg

    async def _run_pipeline_from(
        self, vibe: str, start_index: int
    ) -> AsyncGenerator[AgentMessage, None]:
        try:
            for state in self.pipeline_order[start_index:]:
                latest_manifest = self.state_manager.load_latest()
                if latest_manifest:
                    self.manifest = latest_manifest

                self.manifest.status = state
                self.manifest.current_agent = state.name  # UI metadata

                try:
                    agent = self.agents[state]
                    agent.manifest = self.manifest

                    # 1. Take in-memory snapshot before agent starts
                    self.state_manager.save_snapshot(
                        self.manifest, tag=f"pre_{agent.name.lower()}"
                    )

                    feedback_loop = True
                    while feedback_loop:
                        feedback_loop = False
                        try:
                            # 2. Execute agent
                            prompt = agent.get_prompt(vibe)

                            latest = self.state_manager.load_latest()
                            if latest and latest.user_feedback:
                                prompt += f"\n\n[USER FEEDBACK/INTERRUPT]: {latest.user_feedback}\nAdjust your output accordingly."
                                latest.user_feedback = None
                                self.manifest.user_feedback = None
                                self.state_manager.persist(latest)

                            async for message in agent.execute(prompt):
                                if message.status == AgentStatus.COMPLETE:
                                    # 3. Update manifest section
                                    self._update_manifest_section(
                                        state, message.data_update
                                    )
                                    # Differentiate between Agent Complete and Global Waiting
                                    message.status = AgentStatus.AGENT_FINISHED
                                    # Fix: Ensure manifest is JSON serializable (handles datetimes)
                                    message.manifest = json.loads(
                                        self.manifest.model_dump_json()
                                    )

                                yield message

                            # Check if new feedback arrived DURING streaming
                            latest = self.state_manager.load_latest()
                            if latest and latest.user_feedback:
                                # Re-run this specific phase with the new feedback!
                                feedback_loop = True
                                yield AgentMessage(
                                    agent="System",
                                    status=AgentStatus.THINKING,
                                    thought_process="User feedback detected during phase stream. Restarting current phase with new feedback...",
                                    conflicts=[],
                                )
                                continue

                            # 4. Save successful state and persist at critical milestone
                            self.state_manager.save_snapshot(
                                self.manifest, tag=f"post_{agent.name.lower()}"
                            )
                            self.state_manager.persist(self.manifest)

                        except AgentValidationError as e:
                            # 5. Automatic Rollback on failure using in-memory stack
                            print(
                                f"Agent {agent.name} failed. Initiating rollback... Error: {str(e)} | Type: {type(e).__name__}"
                            )
                            self.manifest = self.state_manager.rollback()
                            self.manifest.status = PipelineStatus.ERROR
                            self.state_manager.persist(self.manifest)
                            yield AgentMessage(
                                agent="System",
                                status=AgentStatus.ERROR,
                                thought_process=f"Error: {str(e)}. Rolled back to previous state.",
                                conflicts=[str(e)],
                            )
                            return
                except Exception as e:
                    # Handover/Initialization Error
                    yield AgentMessage(
                        agent="System",
                        status=AgentStatus.ERROR,
                        thought_process=f"CRITICAL HANDOVER ERROR on {state}: {str(e)}",
                        conflicts=[str(e)],
                    )
                    return

            # After all 5 agents have finished:
            # Set AUDITOR_APPROVED — pipeline is done but NOT yet COMPLETED.
            print(f"[DEBUG] Loop ended. Final status: {self.manifest.status}")
            print(f"[DEBUG] product_scope: {bool(self.manifest.product_scope)}")
            print(f"[DEBUG] ui_map: {bool(self.manifest.ui_map)}")
            print(f"[DEBUG] tech_specs: {bool(self.manifest.tech_specs)}")
            print(
                f"[DEBUG] instructional_brain: {bool(self.manifest.instructional_brain)}"
            )
            if self.manifest.status == PipelineStatus.AUDITOR_ACTIVE:
                self.manifest.status = PipelineStatus.AUDITOR_APPROVED
                self.state_manager.persist(self.manifest)

                # Global Status Guard: Only yield WAITING_APPROVAL after Auditor success
                yield AgentMessage(
                    agent="System",
                    status=AgentStatus.WAITING_APPROVAL,
                    thought_process="Auditor verification complete. All technical checks passed. Ready for deployment.",
                    data_update={},
                    conflicts=[],
                    manifest=self.manifest.model_dump(),
                )
            else:
                # Loop ended prematurely
                yield AgentMessage(
                    agent="System",
                    status=AgentStatus.ERROR,
                    thought_process="CRITICAL_PIPELINE_INCOMPLETE: The loop terminated before the Auditor could finish.",
                    conflicts=["Pipeline Loop Failure"],
                )
        except asyncio.CancelledError:
            print("[Warning] Pipeline task was cancelled by user. Resetting to IDLE.")
            self.manifest.status = PipelineStatus.IDLE
            self.state_manager.persist(self.manifest)
            raise

    def generate(self):
        """Scaffold physical files. This acts as the final step after approval."""
        print("\n\n--- Synthesizing Instructional Brain ---")
        self.generator.generate(self.manifest)

    def _update_manifest_section(self, status: PipelineStatus, data: Dict[str, Any]):
        """Updates the correct section of the manifest based on the active agent."""
        if status == PipelineStatus.VISIONARY_ACTIVE:
            from core.schema import ProductScope

            self.manifest.product_scope = ProductScope(**data)
        elif status == PipelineStatus.ARCHITECT_ACTIVE:
            from core.schema import UIMap

            self.manifest.ui_map = UIMap(**data)
        elif status == PipelineStatus.ENGINEER_ACTIVE:
            from core.schema import TechSpecs

            routes = data.get("api_routes", [])
            for i, route in enumerate(routes):
                if not route.get("id"):
                    method = route.get("method", "GET").upper()
                    path = route.get("path", f"/unknown/{i}")
                    route["id"] = (
                        f"{method}_{path.replace('/', '_').upper().strip('_')}"
                    )
            data["api_routes"] = routes
            self.manifest.tech_specs = TechSpecs(**data)
        elif status == PipelineStatus.EXPERT_ACTIVE:
            from core.schema import InstructionalBrain

            self.manifest.instructional_brain = InstructionalBrain(**data)
        elif status == PipelineStatus.AUDITOR_ACTIVE:
            # Auditor returns approved status and log
            if "audit_log" in data:
                from core.schema import AuditEntry

                self.manifest.audit_log = [
                    AuditEntry(**entry) for entry in data["audit_log"]
                ]
            pass
