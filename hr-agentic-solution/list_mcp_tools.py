import asyncio
import sys
import os
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from dotenv import load_dotenv
load_dotenv()

async def main():
    token = os.environ.get("MCPToken", "").strip()
    headers = {"X-MCP-Token": token} if token else {}
    
    servers = [
        ("WorkWeek", "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/"),
        ("ServiceImmediately", "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/"),
    ]
    
    for name, url in servers:
        print(f"\n--- {name} MCP Server ({url}) ---")
        mcp = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=url,
                headers=headers
            )
        )
        tools = await mcp.get_tools()
        for tool in tools:
            print(f"Tool: {tool.name}")

if __name__ == "__main__":
    asyncio.run(main())
