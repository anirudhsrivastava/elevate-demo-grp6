
MVP SOLUTION DESIGN DOCUMENT
Document Control
Document Metadata
Field
Value
Author(s)
Group 6
Date
2026-08-17
Status
Draft (Under Review)
Target Audience
Enterprise Security, HR Engineering, Cloud Network Architecture, Gemini Enterprise Platform Team

Revision History
Version
Date
Author
Description of Change
0.1
2026-08-17
Group 6
Initial outline setup
0.2
2026-08-17
Group 6
Full system design draft (Cloud Run custom orchestrator)
0.3
2026-08-17
Group 6
Refactored to Google ADK with 1 Main Root Agent + 3 Subagents surfaced via Gemini Enterprise App.
0.4
2026-08-17
Group 6
Integrated Agent Gateway in Agent-to-Anywhere egress mode.
0.5
2026-08-17
Group 6
Comprehensive Agentic Architecture Update:
- Adopted 'Client-to-Anywhere' variant of Agent Gateway.
- Registered all agents in Agent Registry.
- Enforced A2A (Agent2Agent) protocol for all inter-agent traffic, routed via Agent Gateway.
- Configured AuthzPolicy in Custom mode using Service Extensions delegating authorization to iap.googleapis.com.
- Implemented Agent Platform -> Governance -> IAM allow policies for agent-to-agent permissions.
- Standardized on ADK 2.0 for agent development.
- Formally surfaced via Gemini Enterprise AI Application.
0.6
2026-08-18
Group 6
BRD Alignment & Recommendations Update:
- Added Section 11 detailing Key Recommendations for Implementation & Validation.
- Added explicit cross-system orchestration specifications for UC-2.2 (Medical Leave) and UC-2.3 (Relocation).
- Formulated automated continuous evaluation framework using agents-cli eval and quality benchmarks (<15s SLA, 100% security block rate).
- Defined fine-grained subagent operational guardrails for WorkWeek (date chronology, PTO balance ceilings) and ServiceImmediately (lifecycle state transitions, duplicate scan).
0.7
2026-08-18
Group 6
Tool Interface Contracts, Throttling & Token Governance:
- Added Section 12 defining explicit JSON schemas for WorkWeek and ServiceImmediately.
- Specified OAuth / OBO token lifecycle and instant revocation propagation via OIDC Backchannel Logout.
- Defined API throttling thresholds (50 rps for WorkWeek, 100 rps for ServiceImmediately) and full jitter exponential retry backoff parameters.
0.8
2026-08-18
Group 6
Observability, DR, DLQ, HITL Escalation & Near-Real-Time Indexing:
- Added Section 13 detailing OpenTelemetry/Cloud Trace distributed tracing across multi-agent hops, multi-region DR & failover architecture, 5xx asynchronous DLQ retry via Cloud Tasks, seamless live HR agent escalation protocol, and automated Git PR webhook indexing pipeline (< 5-min SLA).
- Defined Section 8.1 Assumptions and Section 8.2 Constraints & Operational Boundaries.
0.9
2026-08-18
Group 6
Privacy Compliance, FinOps Projections & 24-Month Lifecycle:
- Added Section 14 detailing GDPR/APPs data privacy governance (audit retention, RTBF vector/embedding purging, zero-raw-PII BigQuery pipeline, sync delay for ACLs, UI consent notices).
- Provided concrete FinOps monthly projections ($980-$1,250/mo at 100k queries), financial budget caps/alerts, model deprecation strategy, near-real-time re-indexing cost-benefit, and 24-month portability migration path.



1. Executive Summary & Scope Boundaries
1.1. Business Overview & Context
Enterprise employees face significant friction navigating separate HR portals (WorkWeek) and IT Support tools (ServiceImmediately) to answer policy questions and perform routine administrative tasks. This creates a high volume of Tier 1 helpdesk requests and slows employee productivity.

The HR Agentic Solution delivers a streamlined, conversational virtual assistant surfaced directly within the Gemini Enterprise AI Application . Developed using Google Agent Development Kit 2.0 (ADK 2.0), the solution implements a modular multi-agent system comprising 1 Main Root Agent (HR Concierge) and 3 specialized Subagents (Policy Q&A, WorkWeek HCM, and ServiceImmediately).

To meet the highest standards of enterprise zero-trust security and granular governance:

All ingress (client-to-agent), "Client-to-Agent " variant of Agent Gateway.
All inter-agent (agent-to-agent), and egress (agent-to-tool) traffic is routed through the "Agent to Anywhere" variant of Agent Gateway.
All developed agents and tool endpoints are centrally cataloged in the Agent Registry.
All inter-agent communication strictly uses the A2A (Agent2Agent) protocol, routed and governed through Agent Gateway.
Agent Gateway enforces a Custom AuthzPolicy that delegates real-time access control decisions via Service Extensions to iap.googleapis.com (Cloud Identity-Aware Proxy).
Agent-to-agent authorization is strictly governed by Agent Platform Governance IAM allow policies, ensuring only authorized agents can invoke designated subagents.
We plan to introduce GCP’s runtime security “Model Armor” in Agent to anywhere mode. Ie when agent is calling another agent ; this flow will be routed via GCP Model Armor service
1.2. Scope Boundaries
Dimension
In-Scope (MVP 1)
Out-of-Scope (MVP 1)
Front-End Surface
Gemini Enterprise AI Application 
Custom React/Angular web portals, Voice UI, Mobile native apps.
Agent Framework
Google Agent Development Kit 2.0 (ADK 2.0) 

Agents deployed on GCP Agent Runtime.
Custom LangChain/LlamaIndex frameworks, standalone custom web server frameworks.
Agent Topology
1 Main Root Agent + 3 Subagents . 
The architecture followed is “Orchestrator” mode

All the agents to be registered in Agent Registry.
Monolithic single-agent, un-registered shadow agents.
Inter-Agent Protocol
A2A Protocol (Agent2Agent) for all agent-to-agent communication.
Proprietary custom RPCs, unencrypted in-memory subagent calls.
Gateway & Traffic Control
Agent Gateway ("Client-to-Anywhere" as well as “Agent to anywhere” variant) governing ingress as well as A2A routing, and egress.
Direct un-proxied agent-to-agent or agent-to-tool networking.
Authorization & Security
AuthzPolicy (Custom Mode) with Service Extensions calling iap.googleapis.com; Agent Platform Governance IAM Allow Policies; 

Model Armor for Runtime security
Static API keys, perimeter-only network firewalls.
Integrations
Static HR Policy Documents ingested using OKF
RAG

1.3. Target Architecture Overview (Client-to-Anywhere Agent Gateway)
The solution establishes an end-to-end governed data plane using Google Cloud's Gemini Enterprise Agent Platform, ADK 2.0, and Agent Gateway ("Client-to-Anywhere" Mode).


→ Agent gateway1 : ingress ( client to agent )
→ Agent gateway1 : Egress ( agent to Anywhere )

Core Architectural Components:
Client Surface (Gemini Enterprise AI Application): The primary user interface for employees, handling SSO authentication and passing verified user identity context to the Agent Gateway.
Agent Gateway ("Client-to-Anywhere"):
Ingress Proxy: Secures client traffic from the Gemini Enterprise AI Application to the ADK Root Agent.
A2A Inter-Agent Proxy: Mediates all agent-to-agent communication over the A2A protocol, evaluating caller permissions against Agent Platform IAM allow policies.
Egress Proxy: Governs all outbound tool execution, RAG search queries, and LLM model invocations.
Agent Registry: The authoritative catalog registering all project entities: hr_root_orchestrator, policy_qa_agent, workweek_agent, service_immediately_agent, and all downstream tool endpoints.
Custom AuthzPolicy with Service Extensions: Integrates iap.googleapis.com via gRPC Service Extensions to validate client tokens, mTLS identities, and agent credentials on every hop.
ADK 2.0 Multi-Agent System:
Root Agent (hr_root_orchestrator): Main entry point; parses intent, maintains session context, and delegates tasks to subagents via A2A protocol.
Policy Q&A Subagent (policy_qa_agent): Executes grounded search over enterprise HR policies.
WorkWeek HCM Subagent (workweek_agent): Executes employee profile and time-off operations.
ServiceImmediately ITSM Subagent (service_immediately_agent): Manages IT incident tickets and support workflows.


2. Production-Ready Future State Design
As the solution transitions to enterprise-wide production:

Cross-Departmental A2A Federation:
Leveraging the open A2A protocol and Agent Registry, the HR Agent can securely discover and collaborate with external departmental agents (e.g., Legal, Finance, Facilities) hosted across different GCP projects or clusters via Agent Gateway cross-project mesh.
Model Context Protocol (MCP) Standardized Tools:
Migrate custom REST tools to enterprise-managed Model Context Protocol (MCP) servers registered in Agent Registry, allowing dynamic tool capability discovery.
Context-Aware Access (CAA) & Ephemeral Credentials:
Enhance Service Extension integration with iap.googleapis.com to enforce device health, geographic access tiers, and short-lived DPoP (Demonstrating Proof-of-Possession) token validation.
Automated Continuous Evaluation (CI/CD):
Integrate agents-cli eval in Cloud Build to automatically validate A2A contract compliance, regression safety, and task completion accuracy before updating Agent Registry production tags.


3. System Flows, Sequence Diagrams & Agent Design
3.1. ADK 2.0 Agent Design & A2A Gateway Configuration
ADK 2.0 agents are defined with explicit A2A communication endpoints pointing to the Agent Gateway:


from google.adk.agents import Agent
from google.adk.tools import LoadMemoryTool, PreloadMemoryTool
from google.adk.mcp import MCPToolset
from google.adk.http import StreamableHTTPConnectionParams

# --- 1. Memory Bank Configuration ---
# Callbacks handle async memory generation post-turn
async def generate_memories_callback(callback_context):
    # Condense session events into long-term memories in Vertex AI Memory Bank
    await callback_context.add_events_to_memory(
        events=callback_context.session.events[-5:-1]
    )
    return None

# --- 2. OKF RAG & Document Search Setup ---
# The policy agent uses OKF bundles (markdown + YAML frontmatter) for grounding
policy_agent = Agent(
    name="policy_qa_agent",
    model="gemini-2.0-flash",
    instruction="""Answer HR policy inquiries. Ground responses strictly in the OKF catalog 
    (3 verified policy documents). Cite the OKF metadata tags.""",
    tools=[search_okf_datastore_tool], # Custom tool hooked to OKF Datastore
    after_agent_callback=generate_memories_callback, # Captures user preferences
    protocol="a2a/v1"
)

# --- 3. MCP Server for BigQuery Setup ---
# Setup MCP Toolset using Streamable HTTP to fetch analytical data
bq_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://bigquery.googleapis.com/mcp",
        headers={
            "Authorization": "Bearer <user_oauth_token>",
            "x-goog-user-project": "PROJECT_ID"
        }
    )
)

# New Data Analyst Subagent using MCP
data_analyst_agent = Agent(
    name="data_analyst_agent",
    model="gemini-2.0-flash",
    instruction="Run analytical queries on employee history and equipment procurement via BigQuery.",
    tools=[bq_mcp_toolset],
    protocol="a2a/v1"
)

# --- 4. Main Root Orchestrator Agent ---
root_agent = Agent(
    name="hr_root_orchestrator",
    model="gemini-1.5-pro",
    instruction="""Main HR Concierge. Analyze user intent and delegate:
    - policy_qa_agent: policy questions (uses OKF RAG + Memory Bank)
    - data_analyst_agent: analytical/history queries (uses MCP BigQuery)
    - workweek_agent: profile/leave operations
    - service_immediately_agent: support tickets""",
    a2a_gateway="projects/PROJECT_ID/locations/REGION/agentGateways/hr-client-to-anywhere-gw",
    # PreloadMemoryTool pulls user context/history at start of orchestrator turn
    tools=[PreloadMemoryTool()], 
    subagents=[policy_agent, data_analyst_agent, workweek_agent, service_immediately_agent]
)



3.3.1. Knowledge Retrieval with OKF & Datastore (RAG)
For Policy Q&A, the system doesn't rely on raw text chunks but OKF Bundles (Open Knowledge Format).
Datastore Composition: Holds 3 highly structured Markdown files with YAML frontmatter (e.g., remote_work_policy.md, equipment_budget.md, leave_policy.md).
Search Mechanism: The agent filters queries based on YAML frontmatter tags (e.g., type: policy, category: equipment) before scanning document prose, minimizing hallucinations.
4. Security, Governance & Identity
4.1. Agent Gateway "Client-to-Anywhere" Architecture
The Client-to-Anywhere variant of Agent Gateway establishes a unified, bi-directional security boundary:

Client Ingress: Secures incoming sessions from the Gemini Enterprise AI Application, terminating mTLS and enforcing user authentication.
A2A Inter-Agent Routing: All subagent invocations transition across the Agent Gateway via the A2A protocol. Direct un-proxied inter-agent memory calls are strictly prohibited.
Tool & Model Egress: Mediates all outbound calls to Vertex AI Search, WorkWeek, ServiceImmediately, and Gemini LLMs.
4.2. AuthzPolicy (Custom Mode) with Service Extensions (iap.googleapis.com)
Agent Gateway utilizes a Custom Mode Authorization Policy (AuthzPolicy) connected to Service Extensions:

[Incoming Request (Ingress / A2A / Egress)] 
                    │
                    ▼
          [Agent Gateway L7 Envoy]
                    │
                    ▼
     [AuthzExtension (gRPC Call)] ──────> [Identity-Aware Proxy (iap.googleapis.com)]
                    │                                    │
                    ▼                                    ▼
     [Evaluate IAM Allow Policy] <────────── [Validate JWT / Token Claims]
                    │
                    ├─► [ALLOW] ──> Proceed to Target Agent / Tool
                    └─► [DENY]  ──> Return 403 Forbidden & Log Audit Event

Delegated Authorization: On every request (client-to-agent, agent-to-agent, or agent-to-tool), Agent Gateway makes a real-time gRPC authorization call via Service Extensions to iap.googleapis.com.
Token Verification: IAP verifies the caller's JWT token, cryptographic signature, and OAuth claims.
Zero-Trust Enforcement: If a token is expired, tampered with, or lacks the required IAM role, the request is immediately dropped at the gateway layer.
4.3. Agent Platform Governance & IAM Allow Policies for A2A
Access between agents is explicitly governed by Agent Platform Governance IAM Allow Policies:

Source Agent Principal
Target Agent / Resource
Purpose
hr_root_orchestrator
policy_qa_agent
Authorizes Root Agent to delegate policy queries over A2A.
hr_root_orchestrator
workweek_agent
Authorizes Root Agent to delegate HCM transactions over A2A.
hr_root_orchestrator
service_immediately_agent
Authorizes Root Agent to delegate ITSM ticket actions over A2A.
Subagents (policy_qa, workweek, si)
hr_root_orchestrator
Subagents cannot invoke the Root Agent (prevents cyclical A2A loops).
Subagents
Other Subagents
Direct subagent-to-subagent calls are disallowed; all routing must go through Root.
workweek_agent
WorkWeek Mock API Endpoint
Authorizes WorkWeek subagent egress via Agent Gateway.
service_immediately_agent
ServiceImmediately Endpoint
Authorizes ServiceImmediately subagent egress via Agent Gateway.

4.4. Agent Registry Governance
Central Asset Catalog: Every agent, subagent, and tool endpoint is formally registered in the Agent Registry (agentregistry.googleapis.com).
Discovery & Metadata: Agents discover valid subagent A2A endpoints and tool schemas through Agent Registry metadata.
Anti-Shadow Agent Defense: Any A2A invocation targeting an un-registered agent ID or un-registered tool URL is rejected by Agent Gateway.
4.5. Inline Model Armor 
Prompt Injection Defense: Model Armor runs inline at the Agent Gateway, inspecting both client input and inter-agent A2A payloads to block adversarial jailbreaks 
PII Masking: Cloud SDP integration redacts sensitive personal identifiers 

4.6. Dual-Token Authentication for MCP & BigQuery
To ensure strict Principle of Least Privilege (PoLP) when accessing BigQuery via MCP:
End-User OAuth Token: Carried in the Authorization header. Ensures BigQuery IAM policies enforce row-level security on the data based on the caller's identity.
Service-to-Service OIDC Token: Carried in the X-Serverless-Authorization header. Authenticates the ADK Agent (running on Agent Engine) against the Managed MCP Server (running on Cloud Run/Gateway).
4.7. Memory Bank Privacy & Scoping
Data Isolation: Memories are rigidly scoped via {"user_id": USER_ID, "app_name": APP_NAME}. Agents cannot access memories assigned to a different user ID or another ADK application registry.
SPII Scrubbing: Before Memory Bank processes conversation events to generate permanent memories, Inline Model Armor and DLP rules run to sanitize Social Security Numbers or passwords.
4.8. OKF Catalog Governance
Immutability Hierarchy: The 3 core documents in the OKF Datastore are marked as .ref.md (read-only reference layers) for agents.
Auditability: Because OKF bundles rely on standard Markdown and YAML, catalog updates (e.g., changes to equipment allowance) are mediated via Git Pull Requests rather than API patches, ensuring zero-trust governance.


5. Integration Details & Error Handling
5.1. ADK 2.0 Toolsets & A2A Endpoint Mapping
Entity
Interface Type
Protocol
Gateway Route / URI
Governance Policy
hr_root_orchestrator
Agent Ingress
HTTPS / A2A
https://agw.corp/agents/hr_root
IAP Ingress Policy (User Auth)
policy_qa_agent
Subagent Invocation
A2A Protocol
a2a://agw.corp/agents/policy_qa
A2A IAM Allow Policy (Root -> Policy)
workweek_agent
Subagent Invocation
A2A Protocol
a2a://agw.corp/agents/workweek
A2A IAM Allow Policy (Root -> WorkWeek)
service_immediately_agent
Subagent Invocation
A2A Protocol
a2a://agw.corp/agents/service_immediately
A2A IAM Allow Policy (Root -> SI)
search_hr_policies
Tool Egress
gRPC
vais://discoveryengine.googleapis.com
Vertex AI Search Grounding Check
get_profile / update_contact
Tool Egress
REST
https://workweek.corp/api/v1/...
roles/iap.egressor + Identity Binding
create_incident / update_status
Tool Egress
REST
https://serviceimmediately.corp/api/v1/...
roles/iap.egressor + Guardrail Check

5.2. Error Handling & Resilience Matrix
Failure Scenario
Detection Point
Gateway / ADK 2.0 Mitigation Logic
User-Facing Message
A2A IAM Permission Denied
Agent Gateway (IAP)
Gateway returns 403 Forbidden. Root Agent logs authorization violation and aborts delegation.
"You are not authorized to perform this operation."
A2A Protocol Timeout
Agent Gateway
Gateway retries A2A call once with 2s timeout. If subagent unresponsive, returns 504 Gateway Timeout.
"The requested HR service is temporarily slow to respond. Please try again."
Model Armor 
Agent Gateway (Inline)
Gateway intercepts malicious injection payload and halts execution branch immediately.
"I cannot fulfill this request as it violates company safety guidelines."
Tool Execution Error (WorkWeek / SI)
Target Tool API
Subagent catches 4xx/5xx error, formats user-friendly summary, and returns structured failure over A2A.
"Unable to update contact information at this time. Please verify your details."
Partial Cross-System Failure
Root Orchestrator
Step 1 (WorkWeek) succeeds, Step 2 (SI) fails. Root logs failure trace and provides explicit manual instructions.
"Your leave was submitted in WorkWeek, but we could not open the IT coverage ticket. Please contact IT support."



6. Cost Estimation & FinOps
6.1. Key Cost Drivers
Agent Gateway ("Client-to-Anywhere"): Provisioned gateway instances + data processing fee (covering ingress, A2A, and egress throughput).
Gemini Foundation Models:
All agents in Gemini 3.1 flash
Service Extensions & IAP Calls: Per-request invocation charges for delegated authorization.
Vertex AI Search & Agent Registry: Document indexing and query search fees.
Agent Runtime Compute: Serverless execution of ADK 2.0 container workloads.
6.2. FinOps Optimization Tactics
Subagent Model Tiering: Running the three subagents on Gemini 2.0 Flash reduces total token execution costs by ~70%.
Authz Decision Caching: Agent Gateway caches positive IAP authorization decisions for short TTLs to reduce redundant Service Extension calls.
A2A Payload Optimization: Subagent responses pass compact, structured JSON summaries back to the Root Agent, avoiding raw document dumps that inflate context windows.


7. Deployment & Delivery Plan
7.1. Infrastructure as Code (Terraform) Architecture
terraform/
├── main.tf                    # GCP Provider & project APIs setup
├── agent_gateway.tf           # google_network_services_agent_gateway (Client-to-Anywhere)
├── service_extensions.tf      # google_network_services_authz_extension (iap.googleapis.com)
├── authz_policies.tf          # google_network_security_authz_policy (Custom Mode)
├── agent_registry.tf          # google_agent_registry registration for all 4 agents
├── iam_policies.tf            # Agent Platform IAM allow policies for A2A
├── vertex_agent_runtime.tf    # ADK 2.0 Agent deployments & Gateway bindings
└── outputs.tf                 # Registered agent URIs & Gateway endpoints
Deployment Sequence:
Deploy Agent Gateway & Service Extensions: Provision the Client-to-Anywhere Agent Gateway, configure AuthzPolicy in Custom mode, and bind the Service Extension to iap.googleapis.com.
Populate Agent Registry: Register hr_root_orchestrator, policy_qa_agent, workweek_agent, and service_immediately_agent.
Apply Agent Platform IAM Allow Policies: Bind roles/agentplatform.agentInvoker to the Root Agent for each subagent resource.
Deploy ADK 2.0 Agents: Deploy the Root and Subagents to Vertex AI Agent Runtime with gateway bindings.
Register with Gemini Enterprise AI Application: Expose the Root Agent in the Gemini Enterprise AI Application catalog.
7.2. Phased Delivery Roadmap
gantt
    title MVP 1 Delivery Roadmap (ADK 2.0 + Client-to-Anywhere AGW)
    dateFormat  YYYY-MM-DD
    section Sprint 1: Foundation & Gateway
    Terraform Gateway, IAP Service Extension & Registry :active, 2026-09-01, 5d
    Agent Platform IAM Policies & Model Armor : 2026-09-06, 4d
    section Sprint 2: ADK 2.0 Subagents
    Policy Q&A Subagent (A2A Enabled) : 2026-09-10, 6d
    WorkWeek & ServiceImmediately Subagents (A2A Enabled) : 2026-09-16, 7d
    section Sprint 3: Root Orchestrator & A2A Mesh
    ADK 2.0 Root Agent & A2A Gateway Routing : 2026-09-23, 6d
    Cross-System Workflow Validation (UC-2.x) : 2026-09-29, 6d
    section Sprint 4: Application Surface & UAT
    Gemini Enterprise AI Application Integration : 2026-10-05, 4d
    End-to-End Security & Evaluation Benchmark : 2026-10-09, 6d


8. Assumptions, Constraints, Risk & Mitigations
8.1. Operational & Architectural Assumptions
1. User Identity & Authentication: All employee client sessions originate from authenticated enterprise Google Workspace accounts via Google Cloud IAP, propagating verified claims (user email, employee ID) in JWT headers.
2. Agent Runtime & Colocation: Agent Gateway, Service Extensions (iap.googleapis.com), and ADK 2.0 agents are co-located in the primary GCP region (australia-southeast1) to ensure sub-15 ms inter-agent network transit.
3. Source Document Authority: The OKF GCS policy datastore is the single source of truth for all enterprise HR policies, with automated CI/CD synchronization from the approved Git repository.
4. Target Backend Availability: WorkWeek HCM and ServiceImmediately ITSM REST APIs provide standard enterprise SLAs (99.9% uptime) with OAuth 2.0 token endpoint support.
8.2. Environmental & Technical Constraints
1. Latency Ceiling (SLA): Total end-to-end user response time must not exceed 15.0 seconds under peak concurrency, with an initial streaming response target < 10.0 seconds.
2. Zero-Trust Boundary: No subagent may be directly invoked by external clients or peers without traversing Agent Gateway and passing Agent Platform IAM allow policies and Model Armor inspection.
3. Stateless Agent Topology: Agents maintain zero persistent local disk state; all session memory is stored in ephemeral Memory Bank with strict 30-minute inactivity timeouts.
4. Downstream Rate Caps: Egress invocations to WorkWeek are capped at 50 rps and ServiceImmediately at 100 rps per tenant, enforced via token bucket rate limiters.
8.3. Risk Assessment & Mitigation Strategy

Risk Description
Impact
Probability
Mitigation Strategy
Unauthorized Inter-Agent Invocation
High
Low
Agent Gateway enforces strict Agent Platform IAM allow policies on all A2A traffic.
Prompt Injection / Tool Override
High
Low
Model Armor inspects all ingress and A2A payloads inline at the gateway.
A2A Latency Overhead
Medium
Low
Gateway operates on an optimized L7 data plane (<15ms per hop); subagents use Gemini 2.0 Flash.
Service Extension Failure
High
Low
Service Extension configured with health checks and fallback deny-by-default posture.
Tool API Throttling & Peak Load Failure
High
Medium
Enforce Token Bucket rate limiting at Agent Gateway Egress with exponential retry backoff (full jitter) & circuit breakers.
Orphaned OBO Token / Session Termination Gap
High
Low
Implement OIDC Backchannel Logout integration in Service Extensions with immediate token cache invalidation upon session termination.



9. Quality Evaluation & UAT Framework
9.1. Quantitative Targets
Policy Q&A Accuracy: $\ge 95%$ on 100 benchmark questions with verified source citations.
A2A Protocol Correctness: $100%$ valid message schema exchange and error propagation across agents.
Security & IAM Enforcement: $100%$ blocking rate on unauthorized A2A invocation attempts or unregistered tool calls.
Total Response Latency: Average $< 5.0$ seconds for single-domain queries; $< 8.0$ seconds for multi-step cross-system flows.
9.2. Core UAT Scenarios
UC-1.1 (Policy Q&A via A2A): Ask "What is the bereavement leave policy?" -> Verify Root Agent delegates to Policy Subagent over A2A via Gateway and returns citations.
UC-1.2 (WorkWeek Self-Service via A2A): Ask "How many vacation days do I have?" -> Verify Root Agent delegates to WorkWeek Subagent over A2A via Gateway and returns balance.
UC-1.3 (ITSM Incident via A2A): Ask "Open an IT ticket for VPN issues." -> Verify Root Agent delegates to ServiceImmediately Subagent over A2A via Gateway and creates ticket.
UC-2.1 (Cross-System Workflow via A2A): Ask "Verify my remote status and order a monitor." -> Verify Root Agent sequentially invokes Policy Subagent, WorkWeek Subagent, and ServiceImmediately Subagent over A2A via Gateway.
UC-3.1 (A2A Unauthorized Access Test): Simulate direct invocation of WorkWeek Subagent from an unauthorized client -> Verify Agent Gateway drops request with 403 Forbidden via IAP Service Extension.


10. Key Recommendations for Implementation & Validation
Based on the comprehensive gap analysis against the Business Requirements Document (BRD), the following key recommendations are defined to ensure successful production implementation and validation:
In addition to UC-2.1 (Equipment Procurement), the solution architecture mandates formal sequence patterns for UC-2.2 and UC-2.3:
1. UC-2.2 (Medical Leave & IT Coverage Setup):
• Step 1 (Policy Check via A2A): Root Agent delegates to policy_qa_agent to retrieve medical leave guidelines and coverage policies (Corporate HR Policy, Section 3.2).
• Step 2 (WorkWeek Leave of Absence via A2A): Root Agent delegates to workweek_agent to submit a formal Leave of Absence record with dates and validation checks.
• Step 3 (ServiceImmediately Coverage Ticket via A2A): Root Agent delegates to service_immediately_agent to open an IT coverage ticket routing urgent email and ticket queues to the employee's manager.
• Step 4 (User Synthesis): Root Agent synthesizes a consolidated response with policy citation, WorkWeek leave request ID, and ServiceImmediately ticket deep link.
2. UC-2.3 (Global Relocation & Office Transfer Workflow):
• Step 1 (Policy Check via A2A): Root Agent queries relocation expense stipends and tier limits (Corporate Global Mobility Guidelines, Section 5.1).
• Step 2 (WorkWeek Address Update via A2A): Root Agent invokes workweek_agent.update_contact to update the employee's official residential and office location.
• Step 3 (Facilities Badge Request via A2A): Root Agent invokes service_immediately_agent.create_incident under Facilities category to initiate security badge issuance for the target office.
• Step 4 (User Synthesis): Root Agent returns confirmation with policy limits, updated address verification, and security badge request ID.
To prevent data corruption, spam, and invalid transitions across integrated systems:
• WorkWeek HCM Guardrails: Enforce chronological consistency on all time-off dates (reject start_date > end_date and past dates); validate that requested vacation/sick days do not exceed remaining accrued balances; enforce regex validation on phone numbers and email formats prior to submitting updates.
• ServiceImmediately ITSM Guardrails: Enforce strict status transition paths (Open -> In Progress -> Resolved -> Closed), preventing invalid transitions (e.g., Open -> Closed); scan for existing open tickets with matching category and description within a 1-hour rolling window; validate priority level tags (P1-P4) against incident keywords and urgency descriptors.
• Policy Q&A Retrieval Guardrails: Enforce confidence thresholds (>0.80) on Vertex AI Search context, explicitly returning 'Information not found in approved policy repository' rather than guessing; reject non-HR inquiries at the subagent prompt boundary; ensure all generated citations resolve to active, verified policy documents and section identifiers.
1. Benchmark Evaluation Suite: Implement an automated test dataset covering 100% of defined use cases (UC-1.1 to UC-2.3) with deterministic assertions for Policy Q&A Groundedness Score >= 0.95 (0% hallucination), clickable citation presence in 100% of policy responses, total round-trip latency < 15.0s (single-domain < 5.0s, multi-agent < 8.0s), Model Armor threat blocking rate = 100% (0% leak on prompt injections / jailbreaks), and Service Extension / Model Armor inline overhead < 300ms.
2. CI/CD Quality Gate in Cloud Build: Integrate agents-cli eval in the deployment pipeline to automatically test agent containers against the benchmark suite before promoting versions in Agent Registry.
3. Compensating Action Protocol on Partial Failures (NFR-4.3): If a multi-step orchestration fails midway (e.g., WorkWeek leave succeeds but ServiceImmediately ticket fails), the Root Agent must log a correlated transaction trace (x-correlation-id) and provide explicit non-technical instructions for manual follow-up or trigger automated retry with exponential backoff.
IAP Service Extension Region: Ensure Service Extension and Agent Gateway are co-located in the same GCP region to minimize authorization latency overhead.
Session Inactivity Timeout: Confirm standard 30-minute session inactivity timeout in the Gemini Enterprise AI Application.
Policy Re-indexing Trigger: Confirm automated GCS bucket event triggers incremental Vertex AI Search index updates via Cloud Functions.
12. Backend Tool Interface Contracts, Throttling & Token Lifecycle Governance
To address production reliability concerns regarding unhandled peak traffic, service degradation, and security vulnerabilities around orphaned sessions, this section formalizes interface schemas, OBO token revocation, and rate limiting policies.
12.1. Explicit Tool Interface Contracts & JSON Schemas
1. WorkWeek HCM Interface Contract:
• get_profile(employee_id: string) -> Request: {"employee_id": "EMP-279"} | Response: {"status": "success", "data": {"employee_id": "EMP-279", "name": "Alex Rivera", "email": "alex.rivera@example.com", "position": "P-00281 Senior Systems Architect", "supervisory_org": "Global Support - APAC Group", "employee_type": "Regular", "location": "George St, Sydney NSW 2000, Australia", "phone": "+61-2-9230-0000"}}

• update_contact(employee_id: string, address?: string, phone?: string) -> Request: {"employee_id": "EMP-279", "address": "6 Pancras Square, London N1C 4AG", "phone": "+44-20-7031-3000"} | Response: {"status": "success", "message": "Contact updated in WorkWeek", "data": {"employee_id": "EMP-279", "location": "6 Pancras Square, London N1C 4AG", "phone": "+44-20-7031-3000"}}

• get_leave_balances(employee_id: string) -> Request: {"employee_id": "EMP-279"} | Response: {"status": "success", "employee_id": "EMP-279", "vacation_balance_days": 18, "sick_balance_days": 10, "leave_requests": [{"request_id": "LR-1092", "type": "Annual Leave", "start_date": "2026-09-10", "end_date": "2026-09-15", "days": 4, "status": "Pending Manager Approval"}]}

• submit_time_off_request(employee_id: string, leave_type: string, start_date: string, end_date: string, days: number, reason?: string) -> Request: {"employee_id": "EMP-279", "leave_type": "Annual Leave", "start_date": "2026-09-10", "end_date": "2026-09-15", "days": 4, "reason": "Personal vacation"} | Response: {"status": "success", "message": "Time Off Request Submitted", "data": {"request_id": "LR-1092", "type": "Annual Leave", "days": 4, "status": "Pending Manager Approval", "submitted_at": "2026-08-18T11:00:00Z"}} | Error (422): {"status": "error", "error_code": 422, "message": "Validation Error: Requested days exceed accrued balance."}
2. ServiceImmediately ITSM Interface Contract:
• get_service_catalog(category?: string) -> Request: {"category": "it_support"} | Response: {"status": "success", "catalog": {"it_support": {"category": "IT Support", "services": [{"id": "it_hw_setup", "name": "Hardware Setup", "sla": "24 hours"}]}}}

• create_support_incident(employee_id: string, title: string, category: string, description: string, priority: string) -> Request: {"employee_id": "EMP-279", "title": "Hardware Order: Ergonomic Monitor", "category": "IT Support", "description": "Ship monitor to 6 Pancras Square", "priority": "P3"} | Response: {"status": "success", "message": "Support ticket INC-55102 created", "data": {"incident_id": "INC-55102", "employee_id": "EMP-279", "title": "Hardware Order: Ergonomic Monitor", "category": "IT Support", "priority": "P3", "status": "Open", "assigned_group": "APAC IT Support Team", "created_at": "2026-08-18T11:00:00Z"}}

• get_incident_status(incident_id: string) -> Request: {"incident_id": "INC-55102"} | Response: {"status": "success", "data": {"incident_id": "INC-55102", "title": "Hardware Order: Ergonomic Monitor", "status": "In Progress", "priority": "P3", "assigned_group": "APAC IT Support Team", "activity_log": ["Ticket created via Portal", "Assigned to APAC IT Logistics"]}}

• add_comment(incident_id: string, comment: string, author: string) -> Request: {"incident_id": "INC-55102", "comment": "Delivery scheduled for Thursday morning", "author": "EMP-279"} | Response: {"status": "success", "message": "Comment posted to ticket INC-55102", "data": {"incident_id": "INC-55102", "comments": ["[2026-08-18 11:05] EMP-279: Delivery scheduled for Thursday morning"]}}

• update_ticket_status(incident_id: string, new_status: string, resolution_notes?: string) -> Request: {"incident_id": "INC-55102", "new_status": "Resolved", "resolution_notes": "Monitor delivered and set up"} | Response: {"status": "success", "message": "Ticket INC-55102 transitioned to 'Resolved'", "data": {"incident_id": "INC-55102", "status": "Resolved"}}
12.2. OAuth & On-Behalf-Of (OBO) Token Revocation & Session Security
• On-Behalf-Of (OBO) Token Exchange: When an employee queries the system, Agent Gateway authenticates the user via Google Workspace SSO and exchanges the JWT token for scoped, ephemeral downstream OAuth 2.0 OBO tokens (maximum TTL = 15 minutes) with least-privilege scopes (workweek:profile.read, workweek:leave.write, serviceimmediately:incident.write).
• Real-Time Token Revocation via OIDC Backchannel Logout: To close security gaps around terminated sessions, Agent Gateway registers an OIDC Backchannel Logout webhook. When a user logs out of Gemini Enterprise AI App or their session is revoked by an administrator, Agent Gateway immediately purges the in-memory authorization cache and transmits token revocation requests (POST /oauth2/revoke) to WorkWeek and ServiceImmediately. Any subsequent tool calls with the revoked session return 401 Unauthorized.
12.3. API Throttling Limits, Rate Limiting & Retry Backoff Parameters
• Egress API Throttling Limits: WorkWeek HCM is configured with a tenant ceiling of 50 requests/sec (burst 75 req/s) and a per-user limit of 10 requests/sec. ServiceImmediately ITSM is configured with a tenant ceiling of 100 requests/sec (burst 150 req/s) and a per-user limit of 20 requests/sec. Vertex AI Search supports up to 200 queries/sec.
• Gateway Token Bucket Rate Limiting: Agent Gateway Egress proxy enforces client-side Token Bucket rate limiting per target service to protect backend SaaS endpoints from spike overloads.
• Full Jitter Exponential Backoff Parameters: For transient failures (HTTP 429 / 503 / network timeouts), subagents apply exponential backoff with full jitter: Base Delay T_base = 200ms, Multiplier = 2.0, Max Attempts = 3, Max Backoff Cap T_max = 2000ms. Jitter calculation: T_sleep = random(0, min(T_max, T_base * 2^attempt)).
• Circuit Breaker Integration: If downstream 5xx or 429 failure rates exceed 25% over a rolling 30-second window, Agent Gateway trips the circuit breaker to OPEN for 10 seconds, failing fast with user-friendly fallback messaging without saturating external tools.
13. Distributed Observability, Disaster Recovery, Asynchronous DLQ & Live Agent Escalation
To address operational reliability, debugging complex multi-agent interactions, disaster recovery, and stale knowledge mitigation, this section establishes comprehensive observability, multi-region failover, asynchronous error queuing, and human escalation protocols.
13.1. Distributed Tracing & OpenTelemetry Across Multi-Agent Hops
• End-to-End Context Propagation (W3C Trace Context): Agent Gateway injects and propagates standard W3C trace headers (traceparent, tracestate, and x-correlation-id) across the entire request journey: Client Ingress -> Agent Gateway -> Root Orchestrator -> A2A Gateway Hops -> Subagents -> Tool Egress. This ensures distributed spans across multi-agent hops are correlated under a single trace ID.
• OpenTelemetry & Cloud Trace Integration: All ADK 2.0 agents are instrumented with OpenTelemetry (OTel) exporters shipping latency breakdowns (llm_reasoning_ms, gateway_authz_ms, tool_execution_ms, modelarmor_scan_ms) to Google Cloud Trace for millisecond-precision bottleneck analysis.
• BigQuery Agent Analytics Pipeline: Structured event logs from Agent Gateway and ADK runtime stream into BigQuery Agent Analytics, capturing per-session token utilization, agent routing topologies, Model Armor threat detection telemetry, and policy grounding scores.
13.2. Disaster Recovery (DR), Regional Redundancy & Failover Architecture
• Multi-Region High Availability: The solution deploys across a primary region (australia-southeast1 / Sydney) and a secondary failover region (asia-southeast1 / Singapore). Global Cloud Load Balancing performs automated health checks (/healthz) on Agent Gateway instances and routes traffic with < 60-second DNS failover.
• Stateless Recovery Targets (RTO / RPO): Because agents run statelessly on Vertex AI Agent Runtime with cross-region replicated GCS policy stores and Datastores, Recovery Time Objective (RTO) is < 2 minutes and Recovery Point Objective (RPO) is 0 for all agent services.
13.3. Downstream 5xx Dead-Letter Queue (DLQ) & Asynchronous Cloud Tasks Retry
• Persistent 5xx Failure Queuing: When synchronous exponential retries (3 attempts) fail against external SaaS backends (WorkWeek / ServiceImmediately), the transaction is not abandoned. The Root Agent serializes the action payload into an encrypted Google Cloud Tasks / PubSub Dead-Letter Queue (DLQ).
• Asynchronous Fulfillment & Notification: Cloud Tasks background workers process the DLQ with progressive backoff over a 24-hour window. The employee is immediately informed ('Your request has been queued for background processing due to system maintenance') and receives an automated confirmation email/ticket update once processed.
13.4. Seamless Human-in-the-Loop (HITL) Fallback & Live HR Agent Escalation
• Multi-Tier Escalation Triggers: The agent runtime automatically escalates to a live human representative upon: (a) persistent API/tool failure, (b) low policy confidence score (< 0.60), (c) user distress/frustration sentiment detection, or (d) explicit user request ('talk to a representative').
• Context-Preserving Hand-Off Protocol: Agent Gateway bridges the conversation to ServiceImmediately Live Chat / HR Helpdesk via WebSocket. The live HR specialist receives a structured briefing packet (user ID, synthesized intent, transcript summary, and exact failure point) with zero user re-prompting.
13.5. OKF / Datastore Automated Near-Real-Time Indexing Pipeline & Freshness SLA
• Automated Git PR Webhook Indexing: When policy documents are updated in the enterprise Git repository, a Pull Request merge webhook triggers a Cloud Build / Cloud Functions pipeline. The pipeline validates markdown syntax, syncs the document to the GCS OKF bucket, and invokes the Vertex AI Search incremental document indexing API.
• Indexing Freshness SLA (< 5 Minutes): Policy updates are guaranteed to be indexed and available for live semantic retrieval within 5 minutes of PR merge, eliminating stale business logic and preventing tier-2 escalations.
• Zero-Stale Answer Guarantee: Vertex AI Search datastore revision tags and cache-busting headers at the policy subagent ensure immediate retrieval of updated policies without stale cached vector matches.
14. Data Privacy Compliance, FinOps Projections & 24-Month Lifecycle Architecture
To address enterprise governance concerns regarding data protection compliance (GDPR/APPs), granular cost transparency, model lifecycle deprecation, and anti-lock-in portability, this section establishes concrete policies and architectures.
14.1. Data Privacy Governance, GDPR/APPs Compliance & Right-to-be-Forgotten
• Explicit Audit Log Retention Periods: Operational telemetry and debug logs are retained for 90 days in Cloud Logging and BigQuery before automated expiration. Security & Access Audit Logs (IAP authorization decisions, Model Armor threat blocks, and tool invocation metadata) are retained for 365 days in Google Cloud Storage Coldline with WORM (Write Once, Read Many) Bucket Lock policies for regulatory auditability.
• Right-to-be-Forgotten (RTBF) & Vector/Embedding Purging: Upon employee departure or GDPR Article 17 deletion requests, an automated offboarding workflow is triggered via HR ticket. The pipeline immediately purges the user's conversational Memory Bank sessions, deletes personalized policy datastore document embeddings in Vertex AI Search, and invalidates all cached tokens within 24 hours.
• Zero-Raw-PII in BigQuery Agent Analytics: Model Armor and Cloud DLP execute inline upstream of BigQuery streaming ingestion. All raw prompt payloads are sanitized: sensitive personal identifiers (SSNs, tax IDs, banking details) are permanently masked ([REDACTED_SSN]), and user identifiers are hashed using salted SHA-256 (user_hash). Raw unmasked SPII is strictly never stored in BigQuery analytics datastores.
• Vector Access Control ACL Synchronization SLA: Role changes, department transfers, or IAM access revocations in Google Workspace / Cloud Identity synchronize to Vertex AI Search user datastore ACLs within <= 15 minutes via an automated Cloud Pub/Sub event bridge, ensuring terminated or transferred employees cannot access restricted documents.
• User Consent & Privacy Notices in Gemini Enterprise AI App: A persistent, user-facing privacy notice is rendered in the Gemini Enterprise AI App chat interface ('AI-powered HR assistant. Prompts are DLP-sanitized and never used to train public foundation models'). Users are provided with an explicit Settings tab to view data usage and submit consent withdrawal requests.
14.2. Concrete FinOps Projections, Budget Caps & Re-Indexing Cost-Benefit
• Concrete Monthly Cost Projections (100,000 queries/month enterprise baseline):
1. Root Orchestrator (Gemini 1.5 Pro / Flash, 1.5M in / 500k out tokens): ~$150/mo
2. Subagents (Gemini 2.0 Flash, 8M in / 2M out tokens): ~$80/mo
3. Vertex AI Search (100,000 queries @ $1.50 per 1,000 queries): ~$150/mo
4. Agent Gateway & Service Extensions (L7 proxy & traffic processing): ~$180/mo
5. Vertex AI Agent Runtime Compute (Cloud Run / GKE instances): ~$320/mo
6. Model Armor & Cloud DLP Inspections (100k calls): ~$60/mo
7. BigQuery Analytics & Cloud Logging: ~$40/mo
• Total Estimated Monthly Cost: ~$980 – $1,250 / month (Peak scale 500k queries: ~$4,200/mo).
• Financial Budget Caps & Alerting Thresholds: Google Cloud Billing alerts are configured at 50%, 80%, 100%, and 120% thresholds, notifying Cloud Monitoring and the #finops-hr-agent Slack channel. A hard budget cap automation disables non-critical batch re-indexing tasks if monthly spending exceeds 120%, preserving Tier 1 real-time user query availability.
• Cost-Benefit Analysis of Near-Real-Time Re-Indexing: Incremental document indexing costs < $1.50 per 100 updated pages (~$15/month for ~1,000 monthly policy edits) compared against saving an estimated ~120 hours of Tier 2 HR support escalations (~$6,000/month in human labor savings), achieving a 400x ROI.
14.3. 24-Month Portability Architecture & Model Deprecation Strategy
• Model Deprecation & Upgrade Playbook: Upon Google Cloud deprecation notices for Gemini foundation models, a 90-day testing window is triggered. The platform automatically executes regression test suites with agents-cli eval against benchmark datasets. Traffic is migrated via Blue/Green canary routing in Agent Gateway (10% -> 50% -> 100%) with zero user downtime.
• 24-Month Vendor Portability & Anti-Lock-in Architecture: The solution implements a modular 3-tier architecture: (1) Reasoning Engine, (2) A2A Communication Protocol (standardized JSON-RPC/REST), and (3) Backend Tool Adapters (WorkWeekClient, ServiceImmediatelyClient). If business strategy mandates multi-cloud migration within 24 months, the ADK 2.0 orchestrator and subagents can be migrated to open-source frameworks (LangGraph, AutoGen, Semantic Kernel) or alternative LLM backends with zero modifications to downstream HCM and ITSM tool adapters.

