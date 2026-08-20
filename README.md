<<<<<<< HEAD
# elevate-demo-grp6
Elevate team demo for Group 6
=======
# Elevate Demo Group 6 - HR Agentic Solution

This repository contains the multi-agent AI system for enterprise HR and IT service management (WorkWeek HCM, ServiceImmediately ITSM, and HR Policy Q&A).

## 📁 Repository Structure
All agent source code, tools, Docker build configuration, and tests are located inside the master folder:
* **[`hr-agentic-solution/`](./hr-agentic-solution)**: Main master folder containing the complete Google ADK agent implementation.

### Quickstart
1. Navigate to the master folder:
   ```bash
   cd hr-agentic-solution
   ```
2. Configure environment variables (copy `.env.example` to `.env` and add your `MCPToken`):
   ```bash
   cp .env.example .env
   ```
3. Run the agent locally or against the deployed endpoint:
   ```bash
   agents-cli run "How many vacation days do I have left?"
   ```
>>>>>>> 68514a6 (feat: add complete HR Agentic Solution with WorkWeek & ServiceImmediately MCP integration and Policy Q&A)
