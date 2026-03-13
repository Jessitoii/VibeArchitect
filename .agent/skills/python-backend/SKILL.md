---
name: python-backend
description: FastAPI bridge, asyncio orchestrator, and core Python patterns for VibeArchitect
triggers: ["fastapi", "bridge", "orchestrator", "asyncio", "python", "backend", "endpoint"]
---

# Python Backend Skill

## Structure
- `core/bridge.py` — FastAPI app, all IPC endpoints live here
- `core/orchestrator.py` — Pipeline state machine, agent loop
- `core/agents/base.py` — All agents extend BaseAgent
- `core/providers/manager.py` — Provider selection logic

## Rules
- All endpoints stream via `StreamingResponse` + `AsyncGenerator`
- Never block the event loop — use `asyncio.to_thread()` for sync ops
- All agent output must yield `AgentMessage` objects, never raw strings
- Use `core/schema.py` Pydantic models for all data — no raw dicts

## Adding an Endpoint
```python
@app.post("/your-endpoint")
async def handler(req: YourRequest):
    async def stream():
        async for msg in orchestrator.your_method(req.data):
            yield f"data: {msg.model_dump_json()}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")
```

## Common Mistakes
- Do NOT import agents at module level in orchestrator — already instantiated in __init__
- Do NOT mutate manifest directly — use `_update_manifest_section()`