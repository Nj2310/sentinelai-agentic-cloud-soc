import os

from src.agents.providers.base import LLMProvider
from src.agents.providers.ollama_provider import OllamaProvider


def get_llm_provider() -> LLMProvider:
    """
    Select the configured LLM provider.

    Defaults to local Ollama unless explicitly configured
    to use Anthropic Claude.
    """
    provider_name = os.getenv("SENTINELAI_LLM_PROVIDER", "ollama")
    provider_name = provider_name.strip().lower()

    if provider_name == "ollama":
        return OllamaProvider()

    if provider_name == "claude":
        # Import only when Claude is selected.
        from src.agents.providers.claude_provider import ClaudeProvider

        return ClaudeProvider()

    raise ValueError(
        f"Unsupported LLM provider: {provider_name}. "
        "Supported providers: ollama, claude."
    )