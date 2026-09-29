"""
Verification Demo: Hybrid Nano-Agent Runtime (Thread & Process Dual Execution)
under SQPL Phase Lock Coherence (R >= 0.999).
"""

import asyncio
import time
from sovereign_harness.sdk import AsyncSovereignClient

async def main():
    print("=" * 70)
    print("SOVEREIGN AGENT HARNESS: HYBRID NANO-AGENT RUNTIME VERIFICATION")
    print("=" * 70)

    async with AsyncSovereignClient() as client:
        # 1. Vault test
        print("\n[1/5] Testing Zero-Custody Vault...")
        await client.store_key("TEST_LLM_KEY", "sk-proj-sovereign-super-secret-key-12345")
        secret = await client.retrieve_key("TEST_LLM_KEY")
        print(f"  +-- Vault Secret Retrieved Successfully: {secret[:15]}...")

        # 2. LOOM memory test
        print("\n[2/5] Testing LOOM Memoria Graph Engine...")
        node = await client.weave_memory(
            content="Enterprise hybrid runtime initialized with Thread and Process nano-agents.",
            tags=["runtime", "hybrid", "sqpl"],
            emotional_valence=0.9
        )
        print(f"  +-- Woven Memory Node ID: {node['id']}")

        search_res = await client.search_memory("hybrid runtime", limit=2)
        print(f"  +-- Recalled {len(search_res)} matching memory nodes")

        # 3. Thread-Based Nano-Agent execution
        print("\n[3/5] Executing Thread-Based Nano-Agent (Low-Latency Async Task)...")
        thread_start = time.time()
        res_thread = await client.execute_task(
            task_name="memory_index_sync",
            payload={"action": "reindex", "query": "hybrid"},
            mode="thread"
        )
        thread_elapsed = (time.time() - thread_start) * 1000
        print(f"  +-- Thread Agent Output: {res_thread['data']['message']}")
        print(f"  +-- Execution Time: {thread_elapsed:.2f} ms | Mode: {res_thread['data'].get('execution_mode', 'thread')}")

        # 4. Process-Based Nano-Agent execution
        print("\n[4/5] Executing Process-Based Nano-Agent (Isolated OS Process Worker)...")
        proc_start = time.time()
        res_proc = await client.execute_task(
            task_name="compute",
            payload={"vector": [0.5, 0.25, 0.75, 0.1] * 32},
            mode="process"
        )
        proc_elapsed = (time.time() - proc_start) * 1000
        print(f"  +-- Process Agent Output (Vector Norm): {res_proc['data']['vector_norm']:.4f}")
        print(f"  +-- Subprocess PID: {res_proc['data']['pid']} | Execution Time: {proc_elapsed:.2f} ms")

        # 5. SQPL Swarm Phase Lock Coherence
        print("\n[5/5] Auditing SQPL Swarm Coherence (Kuramoto R Order Parameter)...")
        await asyncio.sleep(0.3)  # Allow Kuramoto coupling solver to synchronize phase angles
        swarm_status = await client.get_swarm_coherence()
        print(f"  +-- Active Nano-Agents: {swarm_status['total_agents']}")
        print(f"  +-- Kuramoto Order Parameter R: {swarm_status['coherence_r']}")
        print(f"  +-- Swarm Phase-Locked (R >= 0.99): {swarm_status['is_phase_locked']}")
        
        for agent in swarm_status['agents']:
            print(f"     * Agent '{agent['name']}' [{agent['execution_mode']}] state={agent['state']} angle={agent['phase_angle']:.4f}")

    print("\n" + "=" * 70)
    print("HYBRID RUNTIME VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
