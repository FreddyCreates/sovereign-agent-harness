# Sovereign Agent Harness (`sovereign-agent-harness`)

> **Enterprise Client-Side Sovereign Vault, LOOM Memoria Engine & Open-Source AI Agent Harness**

`sovereign-agent-harness` is a production-grade runtime framework for building, running, and releasing autonomous AI agents. It equips AI agents with client-side zero-custody key storage (**Sovereign Vault**), persistent multi-lingual memory weaving (**LOOM Memoria Engine**), swarm phase synchronization (**SQPL Router**), and zero-trust security guardrails.

---

## Key Features

- 🔐 **Zero-Custody Client-Side Vault**: Users hold 100% of all API keys, model credentials, and seed keys on-device with AES-256-GCM encryption. No vendor key leakage.
- 🧠 **LOOM (Memoria De Intelligencia) Engine**: Based on *Paper XVIII (Archivum Memoriae Sovereignae)*. Auto-recalls relevant memories before agent reasoning steps and weaves post-execution learnings back into the user's graph.
- ⚡ **SQPL Swarm Router**: Synchronizes agent heartbeat execution and phase angles ($R \ge 0.999$) for multi-agent collaboration.
- 🛡️ **Zero-Trust Security Guardrails**: Detects and blocks high-risk command patterns, masks secrets in output logs, and supports human-in-the-loop approval.
- 🛠️ **Autonomous Tool Execution Sandbox**: Built-in shell runner, file reader/writer, HTTP fetcher, and custom `@tool` decorator.
- 🖥️ **Network MCP Server**: Integrated Model Context Protocol (MCP) server running on `http://localhost:8088` providing one unified gateway for all AI models & tools.

---

## Installation

```bash
pip install sovereign-agent-harness
```

Or install locally:
```bash
git clone https://github.com/FreddyCreates/sovereign-engine.git
cd sovereign-agent-harness
pip install -e .
```

---

## Quickstart (Python SDK)

```python
from sovereign_harness import SovereignAgentHarness, tool

# 1. Initialize Harness
agent = SovereignAgentHarness(
    name="ArchitectAgent",
    role="System Architecture Specialist"
)

# 2. Register Custom Tool (Optional)
@tool(
    name="custom_calculator",
    description="Calculates math expressions",
    parameters={"type": "object", "properties": {"expr": {"type": "string"}}}
)
def custom_calculator(expr: str) -> str:
    return str(eval(expr))

# 3. Run Autonomous Task
result = agent.run("Check system status and record findings in LOOM")

print(f"Status: {result['status']}")
print(f"Output: {result['output']}")
print(f"Woven Memory ID: {result['woven_memory_id']}")
```

---

## Command Line Interface (CLI)

### Run an Agent Task
```bash
sovereign-harness run "Analyze local repository structure and summarize"
```

### Store Key in Local Zero-Custody Vault
```bash
sovereign-harness vault set --key OPENAI_API_KEY --val sk-proj-123456789
```

### Inspect Vault Status
```bash
sovereign-harness vault status
```

### Search LOOM Memoria
```bash
sovereign-harness loom search --query "system architecture"
```

---

## Architecture Specification

For full technical specifications, see [SOVEREIGN_VAULT_LOOM_MCP_SPEC.md](../docs/SOVEREIGN_VAULT_LOOM_MCP_SPEC.md).

---

## License

MIT License © 2026 Alfredo Medina Hernandez (Medina Tech / Sovereign OS Inc.)
