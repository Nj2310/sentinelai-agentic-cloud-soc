import sys
from contextlib import redirect_stdout
import ipaddress

from mcp.server.fastmcp import FastMCP

from src.agents.investigation_tools import lookup_login_activity
from src.agents.tool_registry import TOOL_REGISTRY


mcp = FastMCP("SentinelAI Security Investigation Server")


@mcp.tool()
def lookup_login_activity_mcp(source_ip: str) -> dict:
    """Read-only lookup of CloudTrail login activity for a source IP."""

    tool = TOOL_REGISTRY.get("lookup_login_activity")

    if tool is None or tool.get("read_only") is not True:
        raise ValueError("Investigation tool is not authorized")

    if not isinstance(source_ip, str) or not source_ip.strip():
        raise ValueError("A valid source IP address is required")

    try:
        validated_ip = str(ipaddress.ip_address(source_ip))
    except ValueError as exc:
        raise ValueError("Invalid source IP address") from exc

    with redirect_stdout(sys.stderr):
        return lookup_login_activity(validated_ip)


if __name__ == "__main__":
    mcp.run(transport="stdio")