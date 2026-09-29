"""
Nano-Agent Manager & Dispatcher for hybrid Thread and Process runtime orchestration.
"""

import asyncio
import math
import time
from typing import Dict, Any, List, Optional
from sovereign_harness.runtime.base_agent import NanoAgent, AgentState, ExecutionMode
from sovereign_harness.runtime.thread_agent import ThreadNanoAgent
from sovereign_harness.runtime.process_agent import ProcessNanoAgent

class NanoAgentManager:
    """
    Central orchestration manager responsible for:
    1. Registering and maintaining Thread-based and Process-based Nano-Agents.
    2. Dispatching tasks to optimal execution environments (in-process threads vs subprocesses).
    3. Calculating real-time SQPL Kuramoto coherence (R order parameter).
    4. Graceful lifecycle initialization and teardown.
    """
    def __init__(self, heartbeat_interval: float = 0.2):
        self.heartbeat_interval = heartbeat_interval
        self.agents: Dict[str, NanoAgent] = {}
        self._pulse_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def start(self) -> None:
        """Start the background manager pulse loop."""
        self._is_running = True
        self._pulse_task = asyncio.create_task(self._pulse_loop())

    async def stop(self) -> None:
        """Shutdown all registered nano-agents cleanly."""
        self._is_running = False
        if self._pulse_task:
            self._pulse_task.cancel()
            try:
                await self._pulse_task
            except asyncio.CancelledError:
                pass
        
        # Teardown all registered agents
        for agent_id, agent in list(self.agents.items()):
            await agent.teardown()
        self.agents.clear()

    async def create_thread_agent(
        self,
        name: str,
        task_handler: Optional[Any] = None,
        heartbeat_interval: float = 1.0
    ) -> ThreadNanoAgent:
        agent_id = f"thread_agent_{len(self.agents) + 1}_{int(time.time()*1000)%10000}"
        agent = ThreadNanoAgent(
            agent_id=agent_id,
            name=name,
            task_handler=task_handler,
            heartbeat_interval=heartbeat_interval
        )
        await agent.initialize()
        self.agents[agent_id] = agent
        return agent

    async def create_process_agent(
        self,
        name: str,
        heartbeat_interval: float = 1.0
    ) -> ProcessNanoAgent:
        agent_id = f"process_agent_{len(self.agents) + 1}_{int(time.time()*1000)%10000}"
        agent = ProcessNanoAgent(
            agent_id=agent_id,
            name=name,
            heartbeat_interval=heartbeat_interval
        )
        await agent.initialize()
        self.agents[agent_id] = agent
        return agent

    def compute_coherence_r(self) -> float:
        """
        Calculate Kuramoto Order Parameter R across all active agents.
        R = |(1/N) * sum(exp(i * theta_j))|
        """
        if not self.agents:
            return 1.0
        
        sum_cos = 0.0
        sum_sin = 0.0
        count = 0

        for agent in self.agents.values():
            if agent.state != AgentState.STOPPED:
                sum_cos += math.cos(agent.phase_angle)
                sum_sin += math.sin(agent.phase_angle)
                count += 1

        if count == 0:
            return 1.0

        return math.sqrt(sum_cos**2 + sum_sin**2) / count

    async def _pulse_loop(self) -> None:
        """Maintain Kuramoto phase locking across active hybrid agents (K coupling factor)."""
        while self._is_running:
            try:
                coherence_r = self.compute_coherence_r()
                if self.agents:
                    # Calculate mean phase angle psi
                    sum_cos = sum(math.cos(a.phase_angle) for a in self.agents.values())
                    sum_sin = sum(math.sin(a.phase_angle) for a in self.agents.values())
                    mean_psi = math.atan2(sum_sin, sum_cos)

                    K = 2.5  # Coupling constant for phase lock convergence
                    for agent in self.agents.values():
                        if agent.state in [AgentState.RUNNING, AgentState.IDLE, AgentState.PULSING]:
                            # Kuramoto coupling step: d_theta = K * sin(mean_psi - theta)
                            phase_shift = K * math.sin(mean_psi - agent.phase_angle) * self.heartbeat_interval
                            agent.phase_angle = (agent.phase_angle + phase_shift) % (2 * math.pi)

                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def dispatch_task(
        self,
        task_name: str,
        payload: Dict[str, Any],
        preferred_mode: Optional[ExecutionMode] = None
    ) -> Dict[str, Any]:
        """
        Intelligently dispatch a task to a matching thread or process agent.
        """
        internal_actions = ["compute", "loom_remember", "loom_search", "vault_set", "vault_get", "file_read", "file_write", "http_fetch"]
        
        # If task_name is a freeform shell command or prompt, map to shell_exec
        actual_task_name = task_name
        actual_payload = dict(payload)
        if task_name not in internal_actions and "command" not in actual_payload:
            actual_task_name = "shell_exec"
            actual_payload["command"] = task_name

        # Determine execution mode if not specified
        if preferred_mode is None:
            if actual_task_name in ["shell_exec", "tool_exec", "sandbox", "heavy_compute"]:
                mode = ExecutionMode.PROCESS
            else:
                mode = ExecutionMode.THREAD
        else:
            mode = preferred_mode

        # Find or create candidate agent
        target_agent: Optional[NanoAgent] = None
        for agent in self.agents.values():
            if agent.execution_mode == mode and agent.state == AgentState.IDLE:
                target_agent = agent
                break

        if target_agent is None:
            if mode == ExecutionMode.THREAD:
                target_agent = await self.create_thread_agent(name=f"AutoThreadWorker_{actual_task_name}")
            else:
                target_agent = await self.create_process_agent(name=f"AutoProcessWorker_{actual_task_name}")

        result = await target_agent.execute_task(actual_task_name, actual_payload)
        result["swarm_coherence_r"] = round(self.compute_coherence_r(), 4)
        return result

    def get_swarm_status(self) -> Dict[str, Any]:
        coherence_r = self.compute_coherence_r()
        return {
            "total_agents": len(self.agents),
            "coherence_r": round(coherence_r, 4),
            "is_phase_locked": coherence_r >= 0.99,
            "agents": [agent.get_status() for agent in self.agents.values()]
        }
