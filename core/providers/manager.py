import os
from pathlib import Path
from dotenv import load_dotenv
from typing import AsyncGenerator, Optional
from core.providers.cerebras import CerebrasProvider
from core.providers.groq import GroqProvider
from core.providers.ollama import OllamaProvider
from core.providers.mock import MockProvider
from core.exceptions import ProviderTimeout

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class ProviderManager:
    def __init__(self, primary_provider: str = "cerebras"):
        self.primary_name = primary_provider
        self.cerebras = CerebrasProvider()
        self.groq = GroqProvider()
        self.ollama = OllamaProvider()
        self.mock = MockProvider()

    async def stream_chat(
        self, prompt: str, system_prompt: str, model: Optional[str] = None
    ) -> AsyncGenerator[tuple[str, str], None]:
        """
        Streams from the primary provider, with automatic fallback handling.
        """
        use_fallback = False

        if self.primary_name == "cerebras":
            try:
                # Check for API key first
                if not self.cerebras.api_key:
                    yield "\n[WARNING] Cerebras API key missing. Falling back to Groq.", "system"
                    use_fallback = "groq"
                else:
                    async for chunk in self.cerebras.stream_chat(
                        prompt, system_prompt, model=model
                    ):
                        yield chunk, "cerebras"
                    return  # Success
            except ProviderTimeout as e:
                yield f"\n[WARNING] Cerebras Error: {e}. Falling back to Groq.", "system"
                use_fallback = "groq"
            except Exception as e:
                yield f"\n[ERROR] Unexpected Cerebras Error: {e}. Falling back to Groq.", "system"
                use_fallback = "groq"

        if use_fallback == "groq" or self.primary_name == "groq":
            try:
                if not self.groq.api_key:
                    yield "\n[WARNING] Groq API key missing. Falling back to Ollama.", "system"
                    use_fallback = "ollama"
                else:
                    async for chunk in self.groq.stream_chat(
                        prompt, system_prompt, model=model
                    ):
                        yield chunk, "groq"
                    return  # Success
            except ProviderTimeout as e:
                yield f"\n[WARNING] Groq Error: {e}. Falling back to Ollama.", "system"
                use_fallback = "ollama"
            except Exception as e:
                yield f"\n[ERROR] Unexpected Groq Error: {e}. Falling back to Ollama.", "system"
                use_fallback = "ollama"

        use_mock = False
        if use_fallback == "ollama" or self.primary_name == "ollama":
            try:
                # Context Compression for local offline mode
                fallback_instruction = (
                    "\n\n[CONTEXT COMPRESSION ACTIVE: You are running in local fallback mode. "
                    "Keep responses concise, prioritize strict JSON formatting over prose, "
                    "and focus only on the core requirements.]"
                )
                compressed_system_prompt = system_prompt + fallback_instruction
                async for chunk in self.ollama.stream_chat(
                    prompt, compressed_system_prompt, model=model
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
