import os
import json
from pathlib import Path
from typing import AsyncGenerator
from core.providers.manager import ProviderManager
from core.schema import Manifest


class ChatAgent:
    def __init__(self, project_path: str, manifest: Manifest):
        self.project_path = Path(project_path)
        self.manifest = manifest
        self.provider_manager = ProviderManager()
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        return f"""You are the VibeArchitect Context-Aware Chat Agent.
You are currently in IDE_MODE. Your job is to help the user edit the project files.
The project is located at {self.project_path}.

When the user asks you to modify something, you MUST respond with a specific JSON structure representing the modifications, and nothing else.
DO NOT OUTPUT RAW TEXT. ONLY OUTPUT JSON.

Your output MUST match this exact schema:
{{
  "thought_process": "Explain what you are doing",
  "files_to_edit": [
    {{
      "filepath": "relative/path/from/project/root/file.ext",
      "original_content": "the existing full content of the file or null if creating new",
      "modified_content": "the full new content of the file, or null if you want to explicitly delete the file"
    }}
  ],
  "manifest_updates": {{}} // Any updates to the manifest fields
}}

Use your absolute best software engineering skills.
"""

    async def handle_message(self, user_message: str) -> AsyncGenerator[str, None]:
        # Context gathering
        # Read the GEMINI.md or just pass the manifest state as context.
        context = {
            "manifest_status": str(self.manifest.status),
            "project_name": self.manifest.project_name,
        }

        prompt = f"Context: {json.dumps(context)}\nUser Request: {user_message}\n\nRespond strictly in the JSON format."

        # Stream the response
        full_response = ""
        async for chunk, provider in self.provider_manager.stream_chat(
            prompt, self.system_prompt
        ):
            full_response += chunk
            yield chunk

        # After streaming is done, it is up to the orchestrator/bridge to parse `full_response` into JSON and return it to UI.
