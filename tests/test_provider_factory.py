import pytest

from src.agents.providers.base import LLMProvider
from src.agents.providers.ollama_provider import OllamaProvider
from src.agents.providers.factory import get_llm_provider


def test_factory_defaults_to_ollama(monkeypatch):
    monkeypatch.delenv("SENTINELAI_LLM_PROVIDER", raising=False)

    provider = get_llm_provider()

    assert isinstance(provider, LLMProvider)
    assert isinstance(provider, OllamaProvider)
    assert provider.model_name == "qwen3:4b"


def test_factory_selects_ollama(monkeypatch):
    monkeypatch.setenv("SENTINELAI_LLM_PROVIDER", "ollama")

    provider = get_llm_provider()

    assert isinstance(provider, OllamaProvider)


def test_factory_selects_claude(monkeypatch):
    monkeypatch.setenv("SENTINELAI_LLM_PROVIDER", "claude")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

    from unittest.mock import patch
    from src.agents.providers.claude_provider import ClaudeProvider

    with patch("src.agents.providers.claude_provider.Anthropic"):
        provider = get_llm_provider()

    assert isinstance(provider, ClaudeProvider)
    assert isinstance(provider, LLMProvider)


def test_factory_rejects_unsupported_provider(monkeypatch):
    monkeypatch.setenv("SENTINELAI_LLM_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm_provider()


def test_factory_normalizes_provider_name(monkeypatch):
    monkeypatch.setenv("SENTINELAI_LLM_PROVIDER", "  OLLAMA  ")

    provider = get_llm_provider()

    assert isinstance(provider, OllamaProvider)