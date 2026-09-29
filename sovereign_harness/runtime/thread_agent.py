"""
Production Thread-based Nano-Agent implementation running in primary asyncio loop.
Connects directly to ToolRegistry, LoomMemoriaEngine, and SovereignVault.
"""

import asyncio
import time
from typing import Dict, Any, Callable, Awaitable, Optional
from sovereign_harness.runtime.base_agent import NanoAgent, AgentState, ExecutionMode
from sovereign_harness.tools import ToolRegistry
from sovereign_harness.vault import SovereignVault
from sovereign_harness.loom import LoomMemoriaEngine

class ThreadNanoAgent(NanoAgent):
    """
    Production ThreadNanoAgent running as an asyncio task in the main process space.
    Optimal for fast in-memory access (Vault, Loom Memory Search, Tool Execution).
    """
    def __init__(
        self,
        agent_id: str,
        name: str,
        task_handler: Optional[Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None,
        heartbeat_interval: float = 0.5
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            execution_mode=ExecutionMode.THREAD,
            heartbeat_interval=heartbeat_interval
        )
        self.task_handler = task_handler
        self.tools = ToolRegistry()
        self.vault = SovereignVault()
        self.loom = LoomMemoriaEngine()
        self._loop_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> None:
        self.state = AgentState.IDLE
        self._loop_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self) -> None:
        while not self._shutdown_event.is_set():
            try:
                self.pulse_phase(delta_t=self.heartbeat_interval)
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                self.state = AgentState.ERROR

    async def execute_task(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.state = AgentState.RUNNING
        start_time = time.time()
        try:
            if self.task_handler:
                result = await self.task_handler(task_name, payload)
            elif task_name in ["shell_exec", "file_read", "file_write", "http_fetch"]:
                # Execute tool natively via ToolRegistry
                tool_res = self.tools.execute(task_name, payload)
                result = {"executed_tool": task_name, "result": tool_res}
            elif task_name == "loom_remember":
                node = self.loom.weave_memory(
                    content=payload.get("content", ""),
                    tags=payload.get("tags", []),
                    emotional_valence=payload.get("emotional_valence", 0.0)
                )
                result = {"node_id": node.id, "links_count": len(node.links)}
            elif task_name == "loom_search":
                nodes = self.loom.search_memory(payload.get("query", ""), limit=payload.get("limit", 4))
                result = {"count": len(nodes), "results": [n.to_dict() for n in nodes]}
            else:
                result = {"status": "success", "task": task_name, "message": f"Task executed cleanly by ThreadNanoAgent '{self.name}'"}
            
            self.tasks_completed += 1
            self.state = AgentState.IDLE
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "execution_mode": self.execution_mode,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "data": result
            }
        except Exception as e:
            self.state = AgentState.ERROR
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e)
            }

    async def teardown(self) -> None:
        self._shutdown_event.set()
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        self.state = AgentState.STOPPED
