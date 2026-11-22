import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.agents.mcp_server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]

            assert tool_names == ["lookup_login_activity_mcp"]
            print("PASS: MCP server exposes exactly one approved tool")

            result = await session.call_tool(
                "lookup_login_activity_mcp",
                {"source_ip": "198.51.100.50"},
            )

            assert not result.isError
            assert result.content

            data = json.loads(result.content[0].text)

            assert data["source_ip"] == "198.51.100.50"
            assert data["event_count"] == len(data["matching_events"])

            print("PASS: MCP stdio investigation completed")
            print("Matching events:", data["event_count"])


if __name__ == "__main__":
    asyncio.run(main())