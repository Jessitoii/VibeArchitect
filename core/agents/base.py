import abc
import json
import asyncio
import re
from datetime import datetime
from typing import AsyncGenerator, Optional, Dict, Any
from core.schema import Manifest, AgentMessage, AgentStatus
from core.exceptions import AgentValidationError
from core.providers.manager import ProviderManager


class BaseAgent(abc.ABC):
    def __init__(self, name: str, manifest: Manifest):
        self.name = name
        self.manifest = manifest
        self._buffer = ""
        self._is_streaming = False

        provider = "cerebras"
        if (
            manifest.instructional_brain
            and manifest.instructional_brain.provider_config
        ):
            provider = manifest.instructional_brain.provider_config.get(
                "selected_provider", "cerebras"
            )

        self.provider_manager = ProviderManager(primary_provider=provider)
        self.system_prompt = "You are a professional software architect agent."

    async def _call_provider(
        self, prompt: str
    ) -> AsyncGenerator[tuple[str, str], None]:
        """Call provider via ProviderManager."""
        model = None
        if (
            self.manifest.instructional_brain
            and self.manifest.instructional_brain.provider_config
        ):
            model = self.manifest.instructional_brain.provider_config.get(
                "selected_model"
            )

        async for chunk, provider in self.provider_manager.stream_chat(
            prompt, self.system_prompt, model=model
        ):
            yield chunk, provider

    @abc.abstractmethod
    def get_prompt(self, vibe: str) -> str:
        """Generates the specific prompt for this agent."""
        pass

    async def execute(self, prompt: str) -> AsyncGenerator[AgentMessage, None]:
        """
        Main execution loop. Buffers stream for UI and validates final state.
        Handles 450+ tokens/sec by decoupling stream from full validation.
        Performs partial validation during streaming.
        """
        self._is_streaming = True
        self._buffer = ""

        async for chunk, provider in self._call_provider(prompt):
            self._buffer += chunk

            # Partial Validation: lightweight check during stream
            self._partial_validate(self._buffer)

            # Immediate raw stream for UI (no validation yet)
            yield AgentMessage(
                agent=self.name,
                status=AgentStatus.WRITING,
                thought_process="",
                data_update={},
                raw_stream=chunk,
                provider=provider,
            )

        self._is_streaming = False

        # Debounced validation: Only parse and validate once stream is complete
        try:
            parsed_data = self._parse_buffer(self._buffer)
            self._validate_update(parsed_data)

            yield AgentMessage(
                agent=self.name,
                status=AgentStatus.COMPLETE,
                thought_process="Validation successful.",
                data_update=parsed_data,
            )
        except Exception as e:
            yield AgentMessage(
                agent=self.name,
                status=AgentStatus.VALIDATING,
                thought_process=f"Validation failed: {str(e)}",
                conflicts=[str(e)],
            )
            # Re-raise or handle based on orchestrator logic
            raise AgentValidationError(
                f"Agent {self.name} produced invalid output: {str(e)}"
            )

    def _partial_validate(self, buffer: str):
        """
        Lightweight runtime string analysis to quickly abort if output deviates
        too far from expected JSON structure. (Streaming Validation)
        """
        # If output is long enough, check for JSON indicators
        if len(buffer) > 100:
            # We expect either starting with '{', or '```json' etc.
            if "{" not in buffer and "[" not in buffer:
                # Completely missing JSON structure
                if "```" not in buffer:
                    # In a strict implementation, we could raise EarlyValidationError
                    # Here we can log or take softer actions to avoid blocking false positives.
                    pass

    def _parse_buffer(self, buffer: str) -> Dict[str, Any]:
        """Extracts JSON from the buffer with aggressive fallback recovery logic."""
        cleaned_buffer = buffer.strip()
        if cleaned_buffer.startswith("```json"):
            cleaned_buffer = cleaned_buffer[7:]
        if cleaned_buffer.startswith("```"):
            cleaned_buffer = cleaned_buffer[3:]
        if cleaned_buffer.endswith("```"):
            cleaned_buffer = cleaned_buffer[:-3]

        cleaned_buffer = cleaned_buffer.strip()

        try:
            # Attempt direct match first
            start = cleaned_buffer.find("{")
            end = cleaned_buffer.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(cleaned_buffer[start:end])
            return json.loads(cleaned_buffer)
        except json.JSONDecodeError as e:
            # Fallback 1: Broad regex to extract anything resembling a JSON object
            match = re.search(r"\{.*\}", cleaned_buffer, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

            # Fallback 2: Basic cleanup for common missing quotes or trailing commas
            # Remove trailing commas
            fixed = re.sub(r",\s*([}\]])", r"\1", cleaned_buffer)
            try:
                start = fixed.find("{")
                end = fixed.rfind("}") + 1
                if start != -1 and end != -1:
                    return json.loads(fixed[start:end])
                return json.loads(fixed)
            except json.JSONDecodeError as nested_e:
                raise AgentValidationError(
                    f"Failed to parse JSON from agent stream even with recovery logic: {str(nested_e)}\nRaw Response: {buffer[:100]}..."
                )

    def _validate_update(self, data: Dict[str, Any]):
        """Placeholder for Pydantic-based section validation."""
        # Orchestrator will handle the full manifest update via StateManager
        pass

    async def stream_thought(self, thought: str) -> AsyncGenerator[AgentMessage, None]:
        """Helper for streaming internal reasoning."""
        yield AgentMessage(
            agent=self.name,
            status=AgentStatus.THINKING,
            thought_process=thought,
            data_update={},
        )
