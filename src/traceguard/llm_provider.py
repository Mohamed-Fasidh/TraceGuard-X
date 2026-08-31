import os
from dataclasses import dataclass

@dataclass
class LLMProvider:
    """
    Optional reasoning provider.

    TraceGuard remains fully reproducible without an API key. If an
    OpenAI-compatible endpoint is configured, higher-level agents can use it
    for requirement interpretation while deterministic tools remain the final
    evidence source.
    """
    base_url: str | None = os.getenv("TRACEGUARD_LLM_BASE_URL")
    api_key: str | None = os.getenv("TRACEGUARD_LLM_API_KEY")
    model: str | None = os.getenv("TRACEGUARD_LLM_MODEL")

    @property
    def enabled(self):
        return bool(self.base_url and self.api_key and self.model)

    def status(self):
        return {
            "enabled": self.enabled,
            "model": self.model if self.enabled else None,
            "deterministic_fallback": True,
        }
