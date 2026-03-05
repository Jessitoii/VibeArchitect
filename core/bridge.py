from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from core.orchestrator import Orchestrator
from core.schema import AgentMessage
import json
import asyncio

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "VibeArchitect Orchestrator API"}


@app.websocket("/pipeline")
async def pipeline_websocket(websocket: WebSocket, project_path: str, vibe: str):
    await websocket.accept()
    orchestrator = Orchestrator(project_path)

    try:
        async for message in orchestrator.run_pipeline(vibe):
            # Send message as JSON to Electron UI
            await websocket.send_text(message.model_dump_json())
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
    finally:
        await websocket.close()


# For local testing without WebSocket
@app.get("/stream")
async def stream_pipeline(project_path: str, vibe: str):
    orchestrator = Orchestrator(project_path)

    async def event_generator():
        async for message in orchestrator.run_pipeline(vibe):
            yield f"data: {message.model_dump_json()}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
