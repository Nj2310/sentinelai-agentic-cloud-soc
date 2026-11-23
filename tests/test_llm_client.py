import json
from unittest.mock import patch

from src.agents.llm_client import generate_security_analysis


def test_generate_security_analysis():
    evidence = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "198.51.100.50",
        "failed_attempts": 5,
    }

    expected_response = (
        "Possible brute-force activity. "
        "Analyst review recommended."
    )

    with patch(
        "src.agents.llm_client.get_llm_provider"
    ) as mock_factory:

        mock_provider = mock_factory.return_value
        mock_provider.generate.return_value = expected_response

        result = generate_security_analysis(evidence)

        assert result == expected_response

        mock_factory.assert_called_once()
        mock_provider.generate.assert_called_once()

        call_kwargs = mock_provider.generate.call_args.kwargs

        system_prompt = call_kwargs["system_prompt"]
        user_prompt = call_kwargs["user_prompt"]

        # Verify the security instructions are preserved.
        assert "cybersecurity SOC investigation assistant" in system_prompt
        assert "Do not invent events" in system_prompt
        assert "analyst review" in system_prompt

        # Verify the original evidence reaches the provider.
        assert json.dumps(evidence, indent=2) in user_prompt

        # Verify the provider receives the correct prompt structure.
        assert "Analyze this synthetic security evidence" in user_prompt