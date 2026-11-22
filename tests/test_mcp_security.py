import asyncio

import pytest

from src.agents.mcp_server import (
    lookup_login_activity_mcp,
    mcp,
)


def test_mcp_rejects_invalid_ip():
    with pytest.raises(ValueError, match="Invalid source IP"):
        lookup_login_activity_mcp("not-an-ip-address")


def test_mcp_rejects_empty_ip():
    with pytest.raises(ValueError, match="valid source IP"):
        lookup_login_activity_mcp("")


def test_mcp_exposes_only_approved_tool():
    tools = asyncio.run(mcp.list_tools())

    assert len(tools) == 1
    assert tools[0].name == "lookup_login_activity_mcp"


def test_mcp_rejects_unapproved_registry_tool(monkeypatch):
    from src.agents.tool_registry import TOOL_REGISTRY

    monkeypatch.setitem(
        TOOL_REGISTRY["lookup_login_activity"],
        "read_only",
        False,
    )

    with pytest.raises(ValueError, match="not authorized"):
        lookup_login_activity_mcp("198.51.100.50")