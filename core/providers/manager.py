import os
from typing import AsyncGenerator, Optional
from core.providers.cerebras import CerebrasProvider
from core.providers.ollama import OllamaProvider
from core.providers.mock import MockProvider
from core.exceptions import ProviderTimeout


class ProviderManager:
    def __init__(self, primary_provider: str = "cerebras"):
        self.primary_name = primary_provider
        self.cerebras = CerebrasProvider()
        self.ollama = OllamaProvider()
        self.mock = MockProvider()

    async def stream_chat(
        self, prompt: str, system_prompt: str
    ) -> AsyncGenerator[tuple[str, str], None]:
        """
        Streams from the primary provider, with automatic fallback to Ollama, and ultimately MockProvider.
        """
        use_fallback = False

        if self.primary_name == "cerebras":
            try:
                # Check for API key first
                if not self.cerebras.api_key:
                    yield "\n[WARNING] Cerebras API key missing. Falling back to Ollama.", "system"
                    use_fallback = True
                else:
                    async for chunk in self.cerebras.stream_chat(prompt, system_prompt):
                        yield chunk, "cerebras"
                    return  # Success
            except ProviderTimeout as e:
                yield f"\n[WARNING] Cerebras Error: {e}. Falling back to Ollama.", "system"
                use_fallback = True
            except Exception as e:
                yield f"\n[ERROR] Unexpected Cerebras Error: {e}. Falling back to Ollama.", "system"
                use_fallback = True

        use_mock = False
        if use_fallback or self.primary_name == "ollama":
            try:
                # Context Compression for local offline mode
                fallback_instruction = (
                    "\n\n[CONTEXT COMPRESSION ACTIVE: You are running in local fallback mode. "
                    "Keep responses concise, prioritize strict JSON formatting over prose, "
                    "and focus only on the core requirements.]"
                )
                compressed_system_prompt = system_prompt + fallback_instruction
                async for chunk in self.ollama.stream_chat(
                    prompt, compressed_system_prompt
                ):
                    yield chunk, "ollama"
                return  # Success
            except ProviderTimeout as e:
                yield f"\n[WARNING] Ollama Error: {e}. Falling back to MockProvider.", "system"
                use_mock = True
            except Exception as e:
                yield f"\n[ERROR] Unexpected Ollama Error: {e}. Falling back to MockProvider.", "system"
                use_mock = True

        if use_mock or self.primary_name == "mock":
            yield "\n[EMERGENCY] Activating MockProvider to maintain state machine...", "system"
            async for chunk in self.mock.stream_chat(prompt, system_prompt):
                yield chunk, "mock"
