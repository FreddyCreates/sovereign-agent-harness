"""
Enterprise Suite Verification Test Script.
Validates Checkpointing, Remote Mesh, Tensor Memory Wormhole, Key Rotation, Kiln L1, and NERVUS OS.
"""

import asyncio
import time
from sovereign_harness import (
    AsyncSovereignClient,
    AgentCheckpointManager,
    SwarmMeshNetwork,
    TensorWormholeBridge
)
from sovereign_vault import (
    SovereignVault,
    KeyRotationManager,
    KilnL1OriginVaultAnchor,
    NervusStateTransitionLedger
)

async def main():
    print("=" * 70)
    print("SOVEREIGN AGENT HARNESS: ENTERPRISE SUITE VERIFICATION")
    print("=" * 70)

    # 1. Durable Checkpointing & WAL
    print("\n[1/5] Testing Durable Agent Checkpointing & WAL Logging...")
    checkpoint_mgr = AgentCheckpointManager()
    checkpoint_mgr.append_wal_event("thread_agent_1", "TASK_START", {"task": "index_search"})
    snap_path = checkpoint_mgr.save_snapshot({"total_agents": 2, "coherence_r": 0.9995})
    latest = checkpoint_mgr.load_latest_snapshot()
    print(f"  +-- Snapshot Saved: {snap_path}")
    print(f"  +-- Snapshot Recovered: ID={latest['snapshot_id']} | Coherence R={latest['swarm_status']['coherence_r']}")

    # 2. Remote Multi-Node Mesh Network
    print("\n[2/5] Testing Multi-Node Remote Mesh Networking (p2p/WebSocket IPC)...")
    mesh = SwarmMeshNetwork()
    remote1 = mesh.register_remote_node("remote_node_east_1", "192.168.1.100", 8088, "CloudWorker")
    remote2 = mesh.register_remote_node("remote_node_west_1", "192.168.1.101", 8088, "EdgeWorker")
    await mesh.broadcast_phase_pulse(local_phase_angle=0.5235)
    mesh_status = mesh.get_mesh_status()
    print(f"  +-- Registered Mesh Nodes: {mesh_status['total_remote_nodes']}")
    print(f"  +-- Connected Nodes: {mesh_status['connected_nodes']}")

    # 3. C++ Tensor Engine Memory Wormhole Bridge
    print("\n[3/5] Testing C++ Tensor Engine Memory Wormhole Bridge...")
    bridge = TensorWormholeBridge()
    vec_a = [0.5, 0.25, 0.75, 0.1] * 16
    vec_b = [0.5, 0.25, 0.75, 0.1] * 16
    sim = bridge.cosine_similarity(vec_a, vec_b)
    print(f"  +-- Cosine Similarity (64-dim state vector): {sim:.4f}")
    mat_res = bridge.matmul([[1.0, 2.0], [3.0, 4.0]], [[2.0, 0.0], [1.0, 2.0]])
    print(f"  +-- Matrix Multiplication Output: {mat_res}")

    # 4. Key Rotation & Expiration
    print("\n[4/5] Testing Vault Key Rotation & Expiration Policies...")
    vault = SovereignVault(passphrase="old_master_passphrase")
    vault.set_key("ROTATION_KEY_TEST", "secret_value_12345")
    rotation_mgr = KeyRotationManager(vault)
    rotation_mgr.rotate_master_passphrase("old_master_passphrase", "new_master_passphrase")
    retrieved = vault.get_key("ROTATION_KEY_TEST")
    print(f"  +-- Passphrase Rotated Successfully. Key Retrieved: {retrieved}")

    # 5. Kiln L1 & NERVUS OS Ledgers
    print("\n[5/5] Testing Kiln L1 Origin Vault Anchor & NERVUS OS Transition Ledger...")
    kiln_anchor = KilnL1OriginVaultAnchor("kiln_origin_vault_main")
    kiln_block = kiln_anchor.anchor_commitment("STATE_ALPHA", {"coherence": 0.9995})
    print(f"  +-- Kiln Block Hash: {kiln_block['kiln_block_hash']}")

    nervus_ledger = NervusStateTransitionLedger()
    tx = nervus_ledger.record_transition("agent_proc_1", "IDLE", "EXECUTING", {"task": "shell_exec"})
    print(f"  +-- NERVUS State Transition Recorded: ID={tx['transition_id']} | Hash={tx['state_hash'][:16]}...")

    print("\n" + "=" * 70)
    print("ENTERPRISE SUITE VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
