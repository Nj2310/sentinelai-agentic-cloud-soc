from unittest.mock import patch

from src.agents.llm_client import generate_security_analysis


def test_generate_security_analysis():
    evidence = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "198.51.100.50",
        "failed_attempts": 5,
    }

    class MockMessage:
        content = "Possible brute-force activity. Analyst review recommended."

    class MockResponse:
        message = MockMessage()

    with patch("src.agents.llm_client.chat", return_value=MockResponse()) as mock_chat:
        result = generate_security_analysis(evidence)

    assert "Possible brute-force activity" in result
    assert "Analyst review recommended" in result

    mock_chat.assert_called_once()

    call_kwargs = mock_chat.call_args.kwargs
    assert call_kwargs["model"] == "qwen3:4b"
    assert call_kwargs["think"] is False
    assert "198.51.100.50" in call_kwargs["messages"][1]["content"]