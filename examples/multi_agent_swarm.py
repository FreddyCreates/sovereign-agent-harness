"""
Multi-Agent Swarm Example — SQPL Swarm Router & LOOM Coherence
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_harness import SovereignAgentHarness, SQPLSwarmRouter

def main():
    print("=== SOVEREIGN MULTI-AGENT SWARM DEMO ===")
    
    # 1. Initialize Swarm Router
    router = SQPLSwarmRouter(target_coherence=0.999)

    # 2. Spawn Agents
    agent_architect = SovereignAgentHarness(name="Aura", role="Chief Architect")
    agent_security = SovereignAgentHarness(name="Vance", role="Security Officer")
    agent_product = SovereignAgentHarness(name="Freya", role="Product Director")

    # 3. Synchronize Swarm Phase Angles
    sync_status = router.synchronize_swarm()
    print(f"\n[SQPL Swarm Router] Coherence R: {sync_status['coherence_R']} ({sync_status['status']})")

    # 4. Run Tasks Parallelly / Sequentially
    res_arch = agent_architect.run("Design C++ shared memory wormhole specification")
    res_sec = agent_security.run("Audit zero-knowledge proof biometric signatures")
    res_prod = agent_product.run("Verify multi-tenant user UI design system")

    print("\n--- Swarm Execution Output Summary ---")
    print(f"Architect Woven Memory : {res_arch['woven_memory_id']}")
    print(f"Security Woven Memory  : {res_sec['woven_memory_id']}")
    print(f"Product Woven Memory   : {res_prod['woven_memory_id']}")

if __name__ == "__main__":
    main()
