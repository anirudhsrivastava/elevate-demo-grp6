with open("/usr/local/google/home/anujshaunj/hr-agentic-solution/hr-agentic-solution/app/agent.py", "r") as f:
    content = f.read()

target = """# MCP Toolset replacing the previous BigQuery approach
mock_saas_mcp = McpToolset(
    connection_params=SseConnectionParams(
        url="https://mock-saas.aishprabhat.demo.altostrat.com/sse"
    )
)"""

replacement = """# MCP Toolset replacing the previous BigQuery approach
mock_saas_mcp = McpToolset(
    connection_params=SseConnectionParams(
        url="https://mock-saas.aishprabhat.demo.altostrat.com/sse",
        headers={"Authorization": f"Bearer {os.environ.get('MCPToken', '')}"}
    )
)"""

if target in content:
    content = content.replace(target, replacement)
    with open("/usr/local/google/home/anujshaunj/hr-agentic-solution/hr-agentic-solution/app/agent.py", "w") as f:
        f.write(content)
    print("Updated successfully")
else:
    print("Target not found")
