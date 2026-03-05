class VibeArchitectError(Exception):
    """Base exception for all VibeArchitect errors."""

    pass


class AgentValidationError(VibeArchitectError):
    """Raised when an agent produces invalid JSON or fails schema validation."""

    pass


class ProviderTimeout(VibeArchitectError):
    """Raised when an LLM provider (Cerebras/Ollama) times out."""

    pass


class ManifestConflictError(VibeArchitectError):
    """Raised when an update conflicts with the existing manifest state."""

    pass


class StateRollbackError(VibeArchitectError):
    """Raised when rolling back to a previous snapshot fails."""

    pass
