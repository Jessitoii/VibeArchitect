from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, UUID4
import uuid


class PipelineStatus(str, Enum):
    IDLE = "IDLE"
    VISIONARY_ACTIVE = "VISIONARY_ACTIVE"
    ARCHITECT_ACTIVE = "ARCHITECT_ACTIVE"
    ENGINEER_ACTIVE = "ENGINEER_ACTIVE"
    EXPERT_ACTIVE = "EXPERT_ACTIVE"
    AUDITOR_ACTIVE = "AUDITOR_ACTIVE"
    AUDITOR_APPROVED = (
        "AUDITOR_APPROVED"  # All agents done; awaiting user approval + scaffolding
    )
    COMPLETED = "COMPLETED"  # Scaffolding succeeded; entering IDE Mode
    IDE_MODE = "IDE_MODE"
    ERROR = "ERROR"


class AgentStatus(str, Enum):
    THINKING = "thinking"
    WRITING = "writing"
    VALIDATING = "validating"
    COMPLETE = "complete"
    COMMITTED = "COMMITTED"
    AGENT_FINISHED = "AGENT_FINISHED"  # Internal phase completion
    PIPELINE_FINISHED = "PIPELINE_FINISHED"  # Entire pipeline ready
    WAITING_APPROVAL = "WAITING_APPROVAL"
    WAITING_NEXT_PHASE = "WAITING_NEXT_PHASE"
    ERROR = "error"
    PAUSED = "paused"


class ProductScope(BaseModel):
    features: List[str] = Field(default_factory=list)
    tech_stack: Dict[str, str] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    high_level_goals: List[str] = Field(default_factory=list)


class UIComponent(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    description: str
    logic: Optional[str] = None
    data_source_id: Optional[str] = Field(
        None, description="Cross-ref ID to an API endpoint or data model"
    )


class Screen(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    components: List[UIComponent] = Field(default_factory=list)
    user_journey: Optional[str] = None


class UIMap(BaseModel):
    screens: List[Screen] = Field(default_factory=list)
    theme: Dict[str, str] = Field(default_factory=dict)


class APIRoute(BaseModel):
    id: str = Field(
        ..., description="Unique ID for cross-referencing (e.g., 'GET_USER_PROFILE')"
    )
    path: str
    method: str
    request: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None


class TechSpecs(BaseModel):
    api_routes: List[APIRoute] = Field(default_factory=list)
    database_schema: Dict[str, Any] = Field(default_factory=dict)
    external_integrations: List[str] = Field(default_factory=list)


class AgentFile(BaseModel):
    filename: str
    content: str


class AgentRule(AgentFile):
    description: str


class AgentWorkflow(AgentFile):
    success_criteria: List[str] = Field(default_factory=list)

    # Optional parent phase (e.g. "phase_3" for sub-phases like "phase_3.1_auth")
    parent_phase: Optional[str] = None


class SubAgentRule(BaseModel):
    """
    Domain-specific rulebook for a parallel sub-agent.
    Written to .agent/rules/sub_agents/{domain}_agent.md
    """

    domain: str = Field(
        ...,
        description="Domain identifier (e.g. 'frontend', 'backend', 'database', 'infra', 'mobile')",
    )
    filename: str = Field(
        ...,
        description="Filename inside .agent/rules/sub_agents/ (e.g. 'frontend_agent.md')",
    )
    content: str = Field(
        ...,
        description="Full rulebook content: tech stack, naming conventions, constraints for this domain",
    )
    description: str = Field(
        ..., description="≤150-token summary for metadata.json lazy-load index"
    )
    trigger_words: List[str] = Field(
        default_factory=list, description="Keywords that activate this agent's rulebook"
    )


class MetadataEntry(BaseModel):
    """A single enriched entry in metadata.json for lazy-loading by the execution agent."""

    path: str = Field(
        ...,
        description="Relative path from .agent/ root (e.g., 'skills/optimistic_rendering_expert.md')",
    )
    description: str = Field(
        ...,
        description="Max 150-token summary of what this file does and when it matters",
    )
    trigger_words: List[str] = Field(
        default_factory=list,
        description="Keywords that signal this file should be loaded (e.g., ['animation', 'framer-motion'])",
    )


class InstructionalBrain(BaseModel):
    # ── Identity & Constitution ─────────────────────────────────────────
    # Single identity file (soul + strategic pointers + operational state)
    agent_md: str = ""
    # Single constitution (always-on meta-rules + on-demand phase rules)
    rules_md: str = ""

    # ── Domain Discovery ────────────────────────────────────────────────
    # Domains detected from the manifest (e.g. ["frontend", "backend", "database"])
    # Only domains in this list get phases, sub-agent rules, and skills generated.
    detected_domains: List[str] = Field(
        default_factory=list,
        description="Minimum Viable Infrastructure domains. Empty = full-stack.",
    )

    # ── Smart Lazy-Load Index ───────────────────────────────────────────
    metadata_index: List[MetadataEntry] = Field(default_factory=list)
    # Legacy dict field kept for backward-compat with bridge/UI
    metadata_json: Dict[str, Any] = Field(default_factory=dict)

    # ── Rules ───────────────────────────────────────────────────────────
    # Auditor-generated preventative rules → .agent/rules/auto_*.md
    rules: List[AgentRule] = Field(default_factory=list)
    # Domain-specific sub-agent rulebooks → .agent/rules/sub_agents/{domain}_agent.md
    sub_agent_rules: List[SubAgentRule] = Field(default_factory=list)

    # ── Workflows ───────────────────────────────────────────────────────
    # Phase and sub-phase prompts → .agent/workflows/
    # Naming: phase_N_*.md or phase_N.M_*.md for sub-phases
    workflows: List[AgentWorkflow] = Field(default_factory=list)

    # ── External Library ────────────────────────────────────────────────
    # Docs → /docs/ at project root (NOT inside .agent/)
    docs: List[AgentFile] = Field(default_factory=list)
    # Claude-style skill directories → .agent/skills/{name}/SKILL.md
    skills: List[AgentFile] = Field(default_factory=list)

    provider_config: Dict[str, str] = Field(default_factory=dict)


class AuditEntry(BaseModel):
    severity: str  # info, warning, critical
    message: str
    location: Optional[str] = None
    check_id: Optional[str] = None


class Manifest(BaseModel):
    version: str = "1.0.0"
    project_name: str
    status: PipelineStatus = PipelineStatus.IDLE
    user_in_the_loop: bool = True
    auto_accept: bool = False
    product_scope: Optional[ProductScope] = None
    ui_map: Optional[UIMap] = None
    tech_specs: Optional[TechSpecs] = None
    instructional_brain: Optional[InstructionalBrain] = None
    audit_log: List[AuditEntry] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
    current_agent: Optional[str] = None
    user_feedback: Optional[str] = None


class AgentMessage(BaseModel):
    agent: str
    status: AgentStatus
    data_update: Dict[str, Any] = Field(default_factory=dict)
    thought_process: str
    conflicts: List[str] = Field(default_factory=list)
    raw_stream: Optional[str] = None
    manifest: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
