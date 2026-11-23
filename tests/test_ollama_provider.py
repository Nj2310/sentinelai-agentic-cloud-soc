# from unittest.mock import patch, SimpleNamespace
from unittest.mock import patch
from types import SimpleNamespace

from src.agents.providers.base import LLMProvider
from src.agents.providers.ollama_provider import OllamaProvider


def test_ollama_provider_implements_interface():
    provider = OllamaProvider()

    assert isinstance(provider, LLMProvider)
    assert provider.model_name == "qwen3:4b"


@patch("src.agents.providers.ollama_provider.chat")
def test_ollama_provider_generates_response(mock_chat):
    mock_chat.return_value = SimpleNamespace(
        message=SimpleNamespace(
            content="Suspicious login activity requires investigation."
        )
    )

    provider = OllamaProvider()
    result = provider.generate(
        system_prompt="You are a security analyst.",
        user_prompt="Analyze synthetic login events.",
    )

    assert result == "Suspicious login activity requires investigation."

    mock_chat.assert_called_once_with(
        model="qwen3:4b",
        messages=[
            {"role": "system", "content": "You are a security analyst."},
            {"role": "user", "content": "Analyze synthetic login events."},
        ],
        think=False,
        options={"temperature": 0},
    )


@patch("src.agents.providers.ollama_provider.chat")
def test_ollama_provider_removes_thinking_content(mock_chat):
    mock_chat.return_value = SimpleNamespace(
        message=SimpleNamespace(
            content="<think>Internal reasoning</think>Final security analysis."
        )
    )

    provider = OllamaProvider()
    result = provider.generate(
        system_prompt="Security instructions",
        user_prompt="Synthetic evidence",
    )

    assert result == "Final security analysis."