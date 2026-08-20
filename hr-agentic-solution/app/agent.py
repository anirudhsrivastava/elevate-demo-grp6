# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import datetime
import random
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import load_memory, preload_memory
from google.genai import types
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

MODEL = "gemini-2.5-flash"
GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "geap-poc")

_mcp_token = os.environ.get("MCPToken", "").strip()
_mcp_headers = {"X-MCP-Token": _mcp_token} if _mcp_token else {}

# WorkWeek MCP Server
workweek_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/",
        headers=_mcp_headers,
    )
)

# ServiceImmediately MCP Server
serviceimmediately_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/",
        headers=_mcp_headers,
    )
)


# Policy Search Tool
def search_hr_policies(query_topic: str) -> list[dict[str, Any]]:
    """Search HR policy documents and OKF policy bundles for guidelines, rules, and benefits.

    Args:
        query_topic: The topic, keyword, or policy type to search for (e.g. 'bereavement', 'parental', 'remote work', 'sick', 'vacation').

    Returns:
        List of matching policy documents containing doc_id, title, category, content, and source_url.
    """
    try:
        from google.cloud import bigquery
        policy_project = os.environ.get("POLICY_PROJECT", "geap-poc")
        client = bigquery.Client(project=policy_project)
        
        words = [w.strip() for w in query_topic.split() if len(w.strip()) > 2]
        if not words:
            words = [query_topic.strip()]
            
        conditions = []
        params = []
        for i, w in enumerate(words):
            pname = f"kw_{i}"
            conditions.append(f"(LOWER(title) LIKE LOWER(@{pname}) OR LOWER(content) LIKE LOWER(@{pname}) OR LOWER(tags) LIKE LOWER(@{pname}))")
            params.append(bigquery.ScalarQueryParameter(pname, "STRING", f"%{w}%"))
            
        where_clause = " OR ".join(conditions) if conditions else "1=1"
        query = f"""
            SELECT doc_id, title, category, content, source_url
            FROM `{policy_project}.hr_policies_dataset.hr_policies`
            WHERE {where_clause}
            LIMIT 5
        """
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        results = [dict(row) for row in client.query(query, job_config=job_config).result()]
        if not results:
            fallback_query = f"SELECT doc_id, title, category, content, source_url FROM `{policy_project}.hr_policies_dataset.hr_policies` LIMIT 5"
            results = [dict(row) for row in client.query(fallback_query).result()]
        return results
    except Exception as e:
        return [{"error": f"Failed to retrieve policy documents: {e}"}]


# Policy Q&A Subagent
policy_qa_agent = Agent(
    name="policy_qa_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="""Answer employee HR policy inquiries dynamically.
    Use the search_hr_policies tool to retrieve matching policy documents and OKF Policy Bundles.
    Ground all responses strictly in the retrieved policy content.
    Always include explicit source citations (source_url and doc_id) in every response.""",
    tools=[search_hr_policies, workweek_mcp, serviceimmediately_mcp],
)

# WorkWeek HCM Subagent
workweek_agent = Agent(
    name="workweek_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="""Execute employee profile and time-off operations dynamically via the WorkWeek HCM MCP server tools.
    IMPORTANT: Always first call get_current_employee_id() to obtain the logged-in employee ID before calling get_employee_balances(employee_id), get_personal_info(employee_id), or requesting leave.""",
    tools=[workweek_mcp],
)

# ServiceImmediately ITSM Subagent
service_immediately_agent = Agent(
    name="service_immediately_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="""Manage IT incident tickets and support workflows dynamically via the ServiceImmediately MCP server.
    IMPORTANT: Always first call get_current_employee_id() to obtain the logged-in employee ID when listing or creating tickets for the user.
    You can retrieve ticket details, create new support tickets, and close or update ticket status using the provided MCP tools.""",
    tools=[workweek_mcp, serviceimmediately_mcp],
)

# Main Root Orchestrator Agent
hr_root_orchestrator = Agent(
    name="hr_root_orchestrator",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="""Main HR Concierge. Analyze user intent and delegate:
    - policy_qa_agent: HR policy inquiries (queries via MCP catalog dynamically)
    - workweek_agent: profile/leave operations (queries via WorkWeek HCM MCP dynamically)
    - service_immediately_agent: support tickets, issue creation, status checks, and ticket closure via MCP""",
    tools=[load_memory, preload_memory],
    sub_agents=[policy_qa_agent, workweek_agent, service_immediately_agent],
)

root_agent = hr_root_orchestrator

app = App(name="hr_agentic_solution", root_agent=root_agent)
