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
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class AgentStatus(str, Enum):
    THINKING = "thinking"
    WRITING = "writing"
    VALIDATING = "validating"
    COMPLETE = "complete"
    COMMITTED = "COMMITTED"


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


class InstructionalBrain(BaseModel):
    gemini_md: str = ""
    context_md: str = ""
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    rules: List[AgentRule] = Field(default_factory=list)
    workflows: List[AgentWorkflow] = Field(default_factory=list)
    docs: List[AgentFile] = Field(default_factory=list)
    skills: List[AgentFile] = Field(default_factory=list)


class AuditEntry(BaseModel):
    severity: str  # info, warning, critical
    message: str
    location: Optional[str] = None
    check_id: Optional[str] = None


class Manifest(BaseModel):
    version: str = "1.0.0"
    project_name: str
    status: PipelineStatus = PipelineStatus.IDLE
    product_scope: Optional[ProductScope] = None
    ui_map: Optional[UIMap] = None
    tech_specs: Optional[TechSpecs] = None
    instructional_brain: Optional[InstructionalBrain] = None
    audit_log: List[AuditEntry] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
    current_agent: Optional[str] = None


class AgentMessage(BaseModel):
    agent: str
    status: AgentStatus
    data_update: Dict[str, Any] = Field(default_factory=dict)
    thought_process: str
    conflicts: List[str] = Field(default_factory=list)
    raw_stream: Optional[str] = None
    manifest: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
