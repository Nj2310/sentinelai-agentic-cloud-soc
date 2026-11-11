from unittest.mock import patch
from types import SimpleNamespace

from src.agents.tool_selector import select_investigation_tool


def test_ai_tool_selection_preserves_original_ip():
    """AI must not be allowed to change the investigation IP."""

    alert = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "198.51.100.50",
        "severity": "high",
    }

    # Simulate Qwen3 returning an incorrect IP.
    mock_response = SimpleNamespace(
        message=SimpleNamespace(
            content=(
                '{"tool_name": "lookup_login_activity", '
                '"parameters": {"source_ip": "198.5:100.50"}}'
            )
        )
    )

    with patch(
        "src.agents.tool_selector.chat",
        return_value=mock_response,
    ):
        result = select_investigation_tool(alert)

    assert result["tool_name"] == "lookup_login_activity"
    assert result["parameters"]["source_ip"] == "198.51.100.50"


def test_ai_tool_selection_rejects_invalid_ip():
    """Reject malformed source IP addresses from alerts."""
    import pytest

    alert = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "not-a-valid-ip",
        "severity": "high",
    }

    mock_response = SimpleNamespace(
        message=SimpleNamespace(
            content=(
                '{"tool_name": "lookup_login_activity", '
                '"parameters": {"source_ip": "not-a-valid-ip"}}'
            )
        )
    )

    with patch(
        "src.agents.tool_selector.chat",
        return_value=mock_response,
    ):
        with pytest.raises(
            ValueError,
            match="Alert contains an invalid source IP",
        ):
            select_investigation_tool(alert)


def test_ai_tool_selection_rejects_unauthorized_tool():
    """AI cannot select tools outside the approved registry."""
    import pytest

    alert = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "198.51.100.50",
        "severity": "high",
    }

    mock_response = SimpleNamespace(
        message=SimpleNamespace(
            content=(
                '{"tool_name": "delete_iam_user", '
                '"parameters": {"username": "test-admin"}}'
            )
        )
    )

    with patch(
        "src.agents.tool_selector.chat",
        return_value=mock_response,
    ):
        with pytest.raises(
            ValueError,
            match="AI selected an unauthorized tool",
        ):
            select_investigation_tool(alert)


def test_ai_tool_selection_rejects_invalid_structure():
    """Reject AI responses with unexpected JSON fields."""
    import pytest

    alert = {
        "alert_type": "BRUTE_FORCE",
        "source_ip": "198.51.100.50",
        "severity": "high",
    }

    mock_response = SimpleNamespace(
        message=SimpleNamespace(
            content=(
                '{"tool_name": "lookup_login_activity", '
                '"parameters": {"source_ip": "198.51.100.50"}, '
                '"extra_action": "delete_logs"}'
            )
        )
    )

    with patch(
        "src.agents.tool_selector.chat",
        return_value=mock_response,
    ):
        with pytest.raises(
            ValueError,
            match="Invalid tool selection structure",
        ):
            select_investigation_tool(alert)