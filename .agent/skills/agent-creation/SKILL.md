---
name: agent-creation
description: How to create a new pipeline agent compatible with VibeArchitect's orchestrator
triggers: ["new agent", "agent", "base agent", "pipeline agent", "create agent", "extend"]
---

# Agent Creation Skill

## Base Class Contract
```python
# core/agents/base.py
class BaseAgent:
    name: str                          # Used in AgentMessage + logs
    manifest: Manifest                 # Set by orchestrator before execute()

    def get_prompt(self, vibe: str) -> str:
        # Build prompt from manifest context + vibe
        ...

    async def execute(self, prompt: str) -> AsyncGenerator[AgentMessage, None]:
        # Stream AgentMessage objects
        # Final message MUST have status=AgentStatus.COMPLETE + data_update
        ...
```

## Minimal New Agent
```python
from core.agents.base import BaseAgent
from core.schema import AgentMessage, AgentStatus

class MyAgent(BaseAgent):
    name = "MyAgent"

    def get_prompt(self, vibe: str) -> str:
        return f"Given this vibe: {vibe}\nManifest so far: {self.manifest.model_dump_json()}\nDo X..."

    async def execute(self, prompt: str) -> AsyncGenerator[AgentMessage, None]:
        async for chunk in self.provider.stream(prompt):
            yield AgentMessage(agent=self.name, status=AgentStatus.THINKING, thought_process=chunk)
        
        yield AgentMessage(
            agent=self.name,
            status=AgentStatus.COMPLETE,
            data_update={...}  # Must match schema section
        )
```

## Registering in Orchestrator
```python
# core/orchestrator.py — __init__
self.agents[PipelineStatus.YOUR_STAGE] = MyAgent(self.manifest)
self.pipeline_order.append(PipelineStatus.YOUR_STAGE)
```

## Rules
- `data_update` keys must exactly match the Pydantic model for that pipeline stage
- Never yield `AgentStatus.COMPLETE` more than once per execute() call
- Raise `AgentValidationError` for bad LLM output — orchestrator handles rollback