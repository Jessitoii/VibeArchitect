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

    async def run_pipeline(self, vibe: str) -> AsyncGenerator[AgentMessage, None]:
        """
        Runs the full 5-agent pipeline with in-memory snapshots and rollback.
        """
        for state in self.pipeline_order:
            self.manifest.status = state
            agent = self.agents[state]

            # 1. Take in-memory snapshot before agent starts
            self.state_manager.save_snapshot(
                self.manifest, tag=f"pre_{agent.name.lower()}"
            )

            try:
                # 2. Execute agent
                prompt = agent.get_prompt(vibe)
                async for message in agent.execute(prompt):
                    if message.status == AgentStatus.COMPLETE:
                        # 3. Update manifest section
                        self._update_manifest_section(state, message.data_update)
                        message.manifest = self.manifest.model_dump()

                    yield message

                # 4. Save successful state and persist at critical milestone
                self.state_manager.save_snapshot(
                    self.manifest, tag=f"post_{agent.name.lower()}"
                )
                self.state_manager.persist(self.manifest)

            except AgentValidationError as e:
                # 5. Automatic Rollback on failure using in-memory stack
                print(f"Agent {agent.name} failed. Initiating rollback...")
                self.manifest = self.state_manager.rollback()
                self.manifest.status = PipelineStatus.ERROR
                self.state_manager.persist(self.manifest)
                yield AgentMessage(
                    agent="System",
                    status=AgentStatus.COMPLETE,
                    thought_process=f"Error: {str(e)}. Rolled back to previous state.",
                    conflicts=[str(e)],
                )
                return

        self.manifest.status = PipelineStatus.COMPLETED
        # Final persistence on pipeline completion
        self.state_manager.persist(self.manifest)

        # Flush to .agent directory
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
