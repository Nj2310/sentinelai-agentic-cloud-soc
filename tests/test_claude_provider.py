from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.agents.providers.base import LLMProvider
from src.agents.providers.claude_provider import ClaudeProvider


def test_claude_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        ClaudeProvider()


@patch("src.agents.providers.claude_provider.Anthropic")
def test_claude_provider_implements_interface(mock_anthropic, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

    provider = ClaudeProvider()

    assert isinstance(provider, LLMProvider)
    assert provider.model_name == "claude-sonnet-4-5"

    mock_anthropic.assert_called_once_with(
        api_key="test-key-not-real"
    )


@patch("src.agents.providers.claude_provider.Anthropic")
def test_claude_provider_generates_response(mock_anthropic, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

    mock_client = mock_anthropic.return_value
    mock_client.messages.create.return_value = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text="Suspicious login activity requires investigation.",
            )
        ]
    )

    provider = ClaudeProvider()

    result = provider.generate(
        system_prompt="You are a security analyst.",
        user_prompt="Analyze synthetic login events.",
    )

    assert result == "Suspicious login activity requires investigation."

    mock_client.messages.create.assert_called_once_with(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        temperature=0,
        system="You are a security analyst.",
        messages=[
            {
                "role": "user",
                "content": "Analyze synthetic login events.",
            }
        ],
    )


@patch("src.agents.providers.claude_provider.Anthropic")
def test_claude_provider_ignores_non_text_blocks(
    mock_anthropic, monkeypatch
):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

    mock_client = mock_anthropic.return_value
    mock_client.messages.create.return_value = SimpleNamespace(
        content=[
            SimpleNamespace(type="other"),
            SimpleNamespace(type="text", text="Investigation required."),
        ]
    )

    provider = ClaudeProvider()

    result = provider.generate(
        system_prompt="Security instructions",
        user_prompt="Synthetic evidence",
    )

    assert result == "Investigation required."