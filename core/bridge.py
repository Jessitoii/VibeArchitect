from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from core.orchestrator import Orchestrator
from core.schema import AgentMessage, Manifest
from core.state_manager import StateManager
from core.agents.chat_agent import ChatAgent
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

    # Listen for approve command in background
    approval_event = asyncio.Event()
    next_phase_event = asyncio.Event()

    app.state.pipeline_tasks = getattr(app.state, "pipeline_tasks", {})

    async def listen_for_approval():
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    payload = json.loads(data)
                    if payload.get("action") == "USER_APPROVAL":
                        approval_event.set()
                    elif payload.get("action") == "NEXT_PHASE":
                        next_phase_event.set()
                    elif payload.get("action") == "STOP":
                        task = app.state.pipeline_tasks.get(project_path)
                        if task and not task.done():
                            task.cancel()
                    elif payload.get("action") == "RETRY_PIPELINE":
                        # Cancel old task just in case
                        old_task = app.state.pipeline_tasks.get(project_path)
                        if old_task and not old_task.done():
                            old_task.cancel()
                        # Clear queue
                        while not pipeline_queue.empty():
                            pipeline_queue.get_nowait()

                        # Start new task with resume_pipeline
                        async def run_resume_task():
                            try:
                                async for message in orchestrator.resume_pipeline(vibe):
                                    if interrupt_event.is_set():
                                        pass
                                    await pipeline_queue.put(message)
                                await pipeline_queue.put(None)
                            except asyncio.CancelledError:
                                await pipeline_queue.put(Exception("__STOPPED__"))
                            except Exception as e:
                                import sys

                                e.__traceback__ = sys.exc_info()[2]
                                await pipeline_queue.put(e)

                        new_task = asyncio.create_task(run_resume_task())
                        app.state.pipeline_tasks[project_path] = new_task
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

    app.state.pipeline_interrupts = getattr(app.state, "pipeline_interrupts", {})
    interrupt_event = asyncio.Event()
    app.state.pipeline_interrupts[project_path] = interrupt_event

    listen_task = asyncio.create_task(listen_for_approval())

    pipeline_queue = asyncio.Queue()

    async def run_pipeline_task():
        current_agent_name = "System"
        try:
            async for message in orchestrator.run_pipeline(vibe):
                if hasattr(message, "agent"):
                    current_agent_name = message.agent
                if interrupt_event.is_set():
                    # Stop yielding but finish clean
                    break
                await pipeline_queue.put(message)
            await pipeline_queue.put(None)  # Signal completion
        except asyncio.CancelledError:
            await pipeline_queue.put(Exception("__STOPPED__"))
        except Exception as e:
            import sys
            import traceback

            error_msg = f"Pipeline failed during {current_agent_name} phase: {str(e)}"
            print(f"[CRITICAL] {error_msg}")

            # Put the exception with enhanced context into the queue
            e.current_agent = current_agent_name
            e.__traceback__ = sys.exc_info()[2]
            await pipeline_queue.put(e)

    worker_task = asyncio.create_task(run_pipeline_task())
    app.state.pipeline_tasks[project_path] = worker_task

    try:
        import os
        from core.schema import AgentStatus, PipelineStatus

        # Load local auto_accept pref
        auto_accept = os.getenv("AUTO_ACCEPT", "False").lower() == "true" or getattr(
            orchestrator.manifest, "auto_accept", False
        )

        while True:
            message = await pipeline_queue.get()
            if message is None:
                # If task was restarted, make sure we only break if the current task is actually done
                current_task = app.state.pipeline_tasks.get(project_path)
                if current_task is None or current_task.done():
                    break
                continue
            if isinstance(message, Exception):
                e = message
                if str(e) == "__STOPPED__":
                    await websocket.send_text(
                        json.dumps(
                            {
                                "agent": "System",
                                "status": "error",
                                "thought_process": "Generation was stopped by the user.",
                                "data_update": {},
                                "conflicts": [],
                            }
                        )
                    )
                else:
                    import traceback

                    error_details = (
                        "".join(traceback.format_exception(type(e), e, e.__traceback__))
                        if hasattr(e, "__traceback__")
                        else traceback.format_exc()
                    )
                    failed_agent = getattr(e, "current_agent", "Unknown")

                    await websocket.send_text(
                        json.dumps(
                            {
                                "agent": "System",
                                "status": "error",
                                "thought_process": f"CRITICAL PIPELINE FAILURE: Phase [{failed_agent}] crashed. Internal error: {str(e)}",
                                "data_update": {
                                    "title": getattr(e, "__class__", type(e)).__name__,
                                    "traceback": error_details,
                                    "failed_agent": failed_agent,
                                },
                                "conflicts": [f"Pipeline failed at {failed_agent}"],
                            }
                        )
                    )
                continue
            try:
                msg_str = message.model_dump_json()
                # Validate JSON integrity
                json.loads(msg_str)
                await websocket.send_text(msg_str)

                # Signal Filtering: Only show scaffold if Auditor Approved
                manifest_status = orchestrator.manifest.status

                # Check for Phase Completion - wait for user if auto_accept is False
                if message.status == AgentStatus.AGENT_FINISHED:
                    # Refresh auto_accept from disk to pick up user toggles during loop
                    latest = orchestrator.state_manager.load_latest()
                    if latest:
                        orchestrator.manifest = latest
                        auto_accept = getattr(latest, "auto_accept", auto_accept)

                    if not auto_accept:
                        # Change status for UI to show "Proceed" button
                        updated_msg = message.model_dump()
                        updated_msg["status"] = "WAITING_NEXT_PHASE"

                        # Send updated message and wait
                        msg_to_send = AgentMessage(**updated_msg)
                        await websocket.send_text(msg_to_send.model_dump_json())

                        next_phase_event.clear()
                        await next_phase_event.wait()

                        # Reload AGAIN after pause in case they edited manifest during pause
                        latest = orchestrator.state_manager.load_latest()
                        if latest:
                            orchestrator.manifest = latest

                        continue  # Already sent the update, move to next message
                    else:
                        # Just pass through to UI as progress
                        pass

                if message.status == AgentStatus.WAITING_APPROVAL:
                    if manifest_status != PipelineStatus.AUDITOR_APPROVED:
                        # Should not happen with new orchestrator logic, but for safety:
                        message.status = AgentStatus.WRITING
                    else:
                        # Success Signal: Inject SHOW_SCAFFOLD_BUTTON
                        updated_msg = message.model_dump()
                        updated_msg["data_update"]["SHOW_SCAFFOLD_BUTTON"] = True
                        msg_to_send = AgentMessage(**updated_msg)
                        await websocket.send_text(msg_to_send.model_dump_json())
                        continue  # Already sent
            except (NameError, AttributeError) as e:
                # Requirement: Log clearly to AGENT LOGS (UI) instead of crashing
                await websocket.send_text(
                    json.dumps(
                        {
                            "agent": "System",
                            "status": "error",
                            "thought_process": f"[CRITICAL LOGIC ERROR]: {str(e)}",
                            "data_update": {"error_type": type(e).__name__},
                            "conflicts": [str(e)],
                        }
                    )
                )
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                print(f"[Warning] Dropped malformed message chunk to UI: {e}")

        # Only wait for approval and scaffold IF the auditor approved the project
        if orchestrator.manifest.status == PipelineStatus.AUDITOR_APPROVED:
            if not auto_accept:
                # The orchestrator now yields WAITING_APPROVAL, so we just wait for the approval event here
                await approval_event.wait()

            await websocket.send_text(
                json.dumps(
                    {
                        "agent": "System",
                        "status": "writing",
                        "thought_process": "[SYSTEM] Approval received. Transitioning to COMPLETED and starting Scaffolder...",
                        "data_update": {},
                        "conflicts": [],
                        "raw_stream": "\n\n[SYSTEM] Approval received. Transitioning to COMPLETED and starting Scaffolder...\n",
                    }
                )
            )

            from core.schema import PipelineStatus

            orchestrator.manifest.status = PipelineStatus.COMPLETED
            orchestrator.state_manager.persist(orchestrator.manifest)

            # Once approved, perform generating
            orchestrator.generate()

            await websocket.send_text(
                json.dumps(
                    {
                        "agent": "System",
                        "status": "IDE_MODE",
                        "thought_process": "Brain Scaffold Complete. Entering Vibe Coding IDE Mode.",
                        "data_update": {},
                        "conflicts": [],
                    }
                )
            )
        else:
            print(
                f"[Warning] Pipeline finished with status {orchestrator.manifest.status}. Skipping scaffolding."
            )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "agent": "System",
                        "status": "error",
                        "thought_process": f"Connection/system error: {str(e)}",
                        "data_update": {
                            "title": getattr(e, "__class__", type(e)).__name__,
                            "traceback": error_details,
                        },
                        "conflicts": [str(e)],
                    }
                )
            )
        except Exception:
            pass
    finally:
        listen_task.cancel()
        worker_task.cancel()
        app.state.pipeline_interrupts.pop(project_path, None)
        app.state.pipeline_tasks.pop(project_path, None)
        await websocket.close()


@app.websocket("/chat")
async def chat_websocket(websocket: WebSocket, project_path: str):
    await websocket.accept()
    state_manager = StateManager(project_path)
    manifest = state_manager.load_latest() or Manifest(project_name="Vibe Coding")

    agent = ChatAgent(project_path, manifest)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_message = payload.get("message")

            if not user_message:
                continue

            # Stream thoughts
            full_response = ""
            async for chunk in agent.handle_message(user_message):
                full_response += chunk
                await websocket.send_text(
                    json.dumps({"type": "chunk", "content": chunk})
                )

            # Now parse and send edits
            try:
                # Sometimes LLMs wrap JSON in markdown code blocks
                if full_response.strip().startswith("```"):
                    parts = full_response.split("```")
                    if len(parts) >= 3:
                        full_response = parts[1]
                        if full_response.startswith("json"):
                            full_response = full_response[4:]

                parsed = json.loads(full_response)

                if "manifest_updates" in parsed and parsed["manifest_updates"]:
                    manifest_dict = manifest.model_dump()
                    # Perform a deep merge or simply update top level
                    for k, v in parsed["manifest_updates"].items():
                        manifest_dict[k] = v
                    try:
                        manifest = Manifest(**manifest_dict)
                        # Also attach the direct user message so the pipeline loop sees it if it is running
                        manifest.user_feedback = user_message
                        state_manager.persist(manifest)

                        # Trigger interrupt to reload phase if not completed
                        if manifest.status not in [
                            "COMPLETED",
                            "IDE_MODE",
                            "WAITING_APPROVAL",
                        ]:
                            intr = getattr(app.state, "pipeline_interrupts", {}).get(
                                project_path
                            )
                            if intr:
                                intr.set()
                    except Exception as me:
                        print("Failed to apply manifest_update:", me)

                await websocket.send_text(
                    json.dumps({"type": "edits", "payload": parsed})
                )
            except json.JSONDecodeError as e:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "content": f"Failed to parse agent response as JSON. It answered: {full_response}",
                        }
                    )
                )

    except Exception as e:
        print(f"Chat WS closed: {e}")
    finally:
        await websocket.close()


# For local testing without WebSocket
async def stream_pipeline(project_path: str, vibe: str):
    orchestrator = Orchestrator(project_path)

    async def event_generator():
        async for message in orchestrator.run_pipeline(vibe):
            yield f"data: {message.model_dump_json()}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
