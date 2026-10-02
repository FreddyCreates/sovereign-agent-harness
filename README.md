# Sovereign Agent Harness (`sovereign-agent-harness`)

> **Enterprise Client-Side Sovereign Vault, LOOM Memoria Engine, Hugging Face Qwen 2.5 Integration & Super-Intelligence Agent Harness**

`sovereign-agent-harness` is a production-grade runtime framework for building, running, and deploying autonomous AI agents and multi-agent super-intelligence swarms. It equips AI agents with Hugging Face **Qwen 2.5 (Coder & VL)** model support, client-side zero-custody key storage (**Sovereign Vault**), persistent multi-lingual memory weaving (**LOOM Memoria Engine**), swarm phase synchronization (**SQPL Router**), zero-trust security guardrails, and autonomic self-healing execution loops.

---

## 🚀 Key Features

- 🤖 **Hugging Face Qwen 2.5 Model Integration**: Built-in support for **Qwen2.5-Coder** (code generation, 128k context, terminal execution) and **Qwen2.5-VL** (multimodal vision-language visual agents). ChatML prompt formatting with `<tool_call>` JSON parsing.
- ⚡ **Super-Intelligence DAG Pipelines**: `SuperIntelligencePipeline` executes complex multi-stage cognitive workflows across thread-confined and process-confined nano-agents under SQPL phase lock ($R \ge 0.9995$).
- 🧠 **Cognitive Telepathy Relay**: Zero-copy inter-agent state entanglement ($S_t$ float32 state vectors) for sub-millisecond inter-agent communication across swarm nodes.
- 🛠️ **Self-Healing AST Runtime**: Autonomic code AST inspector that catches `SyntaxError` and runtime exceptions, mutating broken python code into valid state on the fly.
- 📐 **Holographic Projection Engine**: 1024-dimensional Vector Symbolic Architecture (VSA) implementing Hadamard multiplicative binding, superposition bundling, and cosine similarity state matching.
- 👻 **GHOST 2b Context Bridge**: Semantic chunker and context vault allowing short-context models (e.g., 2048-token window limits) to maintain narrative coherence across 10,000+ token runs.
- 🔐 **Zero-Custody Client-Side Vault**: 100% on-device key management with client-side AES-256-GCM encryption and Merkle root state receipts.
- 🧠 **LOOM (Memoria De Intelligencia) Engine**: Recalls relevant memory context before reasoning steps and weaves post-execution learnings back into the user graph.
- 🛡️ **Zero-Trust Security Guardrails**: Detects and blocks high-risk command patterns and automatically masks secrets in output logs.

---

## 📦 Installation

```bash
pip install sovereign-agent-harness
```

Or install from source:
```bash
git clone https://github.com/FreddyCreates/sovereign-agent-harness.git
cd sovereign-agent-harness
pip install -e .
```

---

## 💻 Quickstart: Qwen 2.5 Hugging Face Model Agent

```python
from sovereign_harness import QwenModelConfig, QwenSovereignHarness

# 1. Initialize Qwen 2.5 Coder Config (Hugging Face / Ollama / Custom Endpoint)
config = QwenModelConfig(
    model_id="Qwen/Qwen2.5-Coder-7B-Instruct",
    temperature=0.1,
    context_window=131072 # 128k native context window
)

# 2. Instantiate Qwen Sovereign Agent Harness
agent = QwenSovereignHarness(
    name="QwenCoderSpecialist",
    role="Autonomous Software Engineering Agent",
    config=config
)

# 3. Execute Autonomous Agent Loop with ChatML <tool_call> Parsing
result = agent.run_qwen_loop("Inspect system status and write report to report.md")

print(f"Status:            {result['status']}")
print(f"Turns Executed:    {result['turns_executed']}")
print(f"Swarm Coherence R: {result['swarm_coherence_r']}")
print(f"Woven Memory ID:   {result['woven_memory_id']}")
print(f"Output:\n{result['output']}")
```

---

## 🌐 Supported Qwen 2.5 Models on Hugging Face

| Model Identifier | Primary Specialty | Context Window | Mode |
| :--- | :--- | :--- | :--- |
| **`Qwen/Qwen2.5-Coder-7B-Instruct`** | Code generation, terminal tools, multi-turn loops | 128,000 tokens | ChatML + Tools |
| **`Qwen/Qwen2.5-Coder-32B-Instruct`** | Enterprise code reasoning & bug fixing | 128,000 tokens | ChatML + Tools |
| **`Qwen/Qwen2.5-VL-7B-Instruct`** | Multimodal visual agent, desktop/UI automation | 128,000 tokens | Vision + Tools |
| **`Qwen/Qwen2.5-72B-Instruct`** | Flagship multi-domain reasoning & synthesis | 128,000 tokens | ChatML + Tools |

---

## ⚡ Super-Intelligence Architecture Quickstart

```python
import asyncio
from sovereign_harness.super_intelligence import (
    SuperIntelligencePipeline,
    CognitiveTelepathyRelay,
    SelfHealingASTRuntime,
    HolographicProjectionEngine
)
from sovereign_harness.runtime import ExecutionMode

async def main():
    pipeline = SuperIntelligencePipeline()
    telepathy = CognitiveTelepathyRelay()

    async def ingest_step(ctx):
        telepathy.transmit_telepathic_signal("agent_a", "agent_b", {"status": "READY"})
        return {"data_count": 1000}

    async def process_step(ctx):
        return {"status": "SUCCESS"}

    pipeline.add_node("ingest", "Data Ingest", ingest_step, execution_mode=ExecutionMode.THREAD)
    pipeline.add_node("process", "Process Core", process_step, dependencies=["ingest"], execution_mode=ExecutionMode.PROCESS)

    res = await pipeline.execute()
    print(f"Pipeline Status: {res['status']} | Swarm Phase Lock R: {res['swarm_coherence_r']}")

asyncio.run(main())
```

---

## 🛠️ Command Line Interface (CLI)

### Run Qwen Task Loop via CLI
```bash
sovereign-harness run --model Qwen/Qwen2.5-Coder-7B-Instruct "Analyze repo and write tests"
```

### Store Key in Local Zero-Custody Vault
```bash
sovereign-harness vault set --key HF_TOKEN --val hf_xxxxxxxxxxxxxxxxx
```

---

## 📄 License

MIT License © 2026 Alfredo Medina Hernandez (ItsnotAILabs / Sovereign OS Inc.)
