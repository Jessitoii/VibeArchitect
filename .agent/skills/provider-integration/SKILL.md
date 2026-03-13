---
name: provider-integration
description: Adding and managing LLM providers (Cerebras, Groq, Ollama) in VibeArchitect
triggers: ["provider", "cerebras", "groq", "ollama", "llm", "model", "api key", "fallback"]
---

# Provider Integration Skill

## Structure
- `core/providers/manager.py` — Selects active provider, handles fallback chain
- `core/providers/cerebras.py` — Primary (Qwen-2.5-72B, high speed)
- `core/providers/groq.py` — Tier 2 fallback
- `core/providers/ollama.py` — Local fallback
- `core/providers/mock.py` — Dev/test, no API calls

## Adding a New Provider
```python
# core/providers/your_provider.py
class YourProvider:
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        # Must yield raw text chunks
        ...

# Register in manager.py provider chain
```

## Fallback Chain
Cerebras (TPM limit hit) → Groq → Ollama → raise ProviderExhaustedError

## Rate Limiting
- Cerebras: Exponential backoff on 429, max 3 retries
- Track TPM with sliding window in manager.py
- Never hardcode sleep() — use `asyncio.sleep(backoff_time)`

## Rules
- All providers must implement same `stream(prompt)` interface
- API keys in `core/.env` only — never in code
- Mock provider must be usable with zero env vars for CI/testing