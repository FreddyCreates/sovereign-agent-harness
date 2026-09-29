"""
Quickstart Example — Sovereign Agent Harness Single-Agent Task
"""

import sys
import os

# Include package root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_harness import SovereignAgentHarness

def main():
    print("=== SOVEREIGN AGENT HARNESS — QUICKSTART DEMO ===")
    
    agent = SovereignAgentHarness(
        name="SecurityAuditor",
        role="Zero-Trust System Auditor"
    )

    # Store test key in zero-custody vault
    agent.vault.set_key("ANTHROPIC_API_KEY", "sk-ant-api03-test-12345")

    # Execute task
    result = agent.run("Verify system shell operational status and sanitize sensitive keys.")

    print("\n--- Execution Result ---")
    print(f"Agent Name       : {result['agent']}")
    print(f"Task             : {result['task']}")
    print(f"Status           : {result['status']}")
    print(f"Recalled Memories: {result['recalled_memories']}")
    print(f"Woven Memory ID  : {result['woven_memory_id']}")
    print(f"Swarm Coherence R: {result['swarm_coherence']}")
    print(f"Output           : {result['output']}")

if __name__ == "__main__":
    main()
