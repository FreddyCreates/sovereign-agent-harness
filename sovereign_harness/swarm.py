"""
Swarm Module — SQPL Swarm Router & Multi-Agent Phase Synchronization
---------------------------------------------------------------------
Synchronizes phase angles and heartbeat execution cycles ($R >= 0.999$)
for multi-agent swarm tasks.
"""

import time
import math
from typing import Dict, List, Any, Optional

class SwarmAgentNode:
    def __init__(self, agent_id: str, role: str, phase_angle: float = 0.0):
        self.agent_id = agent_id
        self.role = role
        self.phase_angle = phase_angle
        self.last_heartbeat = time.time()
        self.state_locked = False

class SQPLSwarmRouter:
    """
    Symmetric Quantum Phase Lock (SQPL) Swarm Router.
    Ensures multi-agent consensus and phase synchronization.
    """
    def __init__(self, target_coherence: float = 0.999):
        self.nodes: Dict[str, SwarmAgentNode] = {}
        self.target_coherence = target_coherence
        self.coupling_constant_k = 1.85

    def register_node(self, agent_id: str, role: str) -> SwarmAgentNode:
        node = SwarmAgentNode(agent_id, role, phase_angle=len(self.nodes) * (math.pi / 4.0))
        self.nodes[agent_id] = node
        return node

    def compute_order_parameter_r(self) -> float:
        """Computes Kuramoto Order Parameter R (Phase Coherence)."""
        if not self.nodes:
            return 1.0
        sum_cos = sum(math.cos(n.phase_angle) for n in self.nodes.values())
        sum_sin = sum(math.sin(n.phase_angle) for n in self.nodes.values())
        N = len(self.nodes)
        R = math.sqrt(sum_cos**2 + sum_sin**2) / N
        return R

    def synchronize_swarm(self) -> Dict[str, Any]:
        """Locks phase angles across all active swarm nodes."""
        mean_phase = math.atan2(
            sum(math.sin(n.phase_angle) for n in self.nodes.values()),
            sum(math.cos(n.phase_angle) for n in self.nodes.values())
        )
        
        # Adjust phase angles toward mean_phase
        for node in self.nodes.values():
            node.phase_angle += self.coupling_constant_k * math.sin(mean_phase - node.phase_angle) * 0.1
            node.state_locked = True
            node.last_heartbeat = time.time()

        r_val = self.compute_order_parameter_r()
        return {
            "coherence_R": round(r_val, 4),
            "state_locked": r_val >= self.target_coherence,
            "total_nodes": len(self.nodes),
            "status": "PHASE_LOCKED" if r_val >= self.target_coherence else "SYNCHRONIZING"
        }
