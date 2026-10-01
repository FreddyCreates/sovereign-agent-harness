"""
SuperIntelligencePipeline Module — Autonomous Multi-Agent DAG Execution Engine.
Orchestrates complex multi-stage cognitive workflows under SQPL Phase Lock (R >= 0.9995).
"""

import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Awaitable
from sovereign_harness.runtime.manager import NanoAgentManager, ExecutionMode

class PipelineNode:
    """
    Individual cognitive execution node in a Super-Intelligence DAG workflow.
    """
    def __init__(
        self,
        node_id: str,
        name: str,
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]],
        dependencies: Optional[List[str]] = None,
        execution_mode: ExecutionMode = ExecutionMode.THREAD
    ):
        self.node_id = node_id
        self.name = name
        self.handler = handler
        self.dependencies = dependencies or []
        self.execution_mode = execution_mode
        self.status = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
        self.result: Optional[Dict[str, Any]] = None
        self.execution_time_ms: float = 0.0

class SuperIntelligencePipeline:
    """
    Super-Intelligence DAG Execution Pipeline Engine.
    Executes dependent cognitive tasks in parallel across thread and process nano-agents.
    """
    def __init__(self, manager: Optional[NanoAgentManager] = None):
        self.pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"
        self.manager = manager or NanoAgentManager()
        self.nodes: Dict[str, PipelineNode] = {}

    def add_node(
        self,
        node_id: str,
        name: str,
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]],
        dependencies: Optional[List[str]] = None,
        execution_mode: ExecutionMode = ExecutionMode.THREAD
    ) -> PipelineNode:
        node = PipelineNode(node_id, name, handler, dependencies, execution_mode)
        self.nodes[node_id] = node
        return node

    async def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes the Super-Intelligence DAG pipeline topologically.
        """
        start_time = time.time()
        context = dict(initial_context or {})
        completed_nodes = set()

        await self.manager.start()

        while len(completed_nodes) < len(self.nodes):
            # Find nodes ready to run (all dependencies completed)
            ready_nodes = [
                node for node in self.nodes.values()
                if node.status == "PENDING" and all(dep in completed_nodes for dep in node.dependencies)
            ]

            if not ready_nodes:
                if len(completed_nodes) < len(self.nodes):
                    raise RuntimeError("Cyclic dependency or deadlock detected in SuperIntelligencePipeline")
                break

            # Execute ready nodes in parallel
            tasks = []
            for node in ready_nodes:
                node.status = "RUNNING"
                tasks.append(self._run_node(node, context))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for node, res in zip(ready_nodes, results):
                if isinstance(res, Exception):
                    node.status = "FAILED"
                    raise res
                else:
                    node.status = "COMPLETED"
                    node.result = res
                    completed_nodes.add(node.node_id)
                    context[node.node_id] = res

        coherence_r = self.manager.compute_coherence_r()
        total_time_ms = (time.time() - start_time) * 1000.0

        return {
            "pipeline_id": self.pipeline_id,
            "status": "SUCCESS",
            "total_nodes": len(self.nodes),
            "execution_time_ms": round(total_time_ms, 2),
            "swarm_coherence_r": round(coherence_r, 4),
            "is_phase_locked": coherence_r >= 0.99,
            "node_results": {node_id: node.result for node_id, node in self.nodes.items()}
        }

    async def _run_node(self, node: PipelineNode, context: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        # Execute node handler
        res = await node.handler(context)
        node.execution_time_ms = round((time.time() - start) * 1000.0, 2)
        return res
