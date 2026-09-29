"""
Base Nano-Agent class and lifecycle interfaces for Sovereign Agent Harness.
"""

from abc import ABC, abstractmethod
from enum import Enum
import time
import asyncio
from typing import Dict, Any, Optional

class AgentState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PULSING = "pulsing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class ExecutionMode(str, Enum):
    THREAD = "thread"      # In-process asyncio event loop
    PROCESS = "process"    # Isolated OS subprocess (multiprocessing spawn)

class NanoAgent(ABC):
    """
    Abstract base unit for a Micro/Nano Agent servicing the Sovereign Harness Runtime.
    """
    def __init__(
        self,
        agent_id: str,
        name: str,
        execution_mode: ExecutionMode = ExecutionMode.THREAD,
        heartbeat_interval: float = 1.0
    ):
        self.agent_id = agent_id
        self.name = name
        self.execution_mode = execution_mode
        self.heartbeat_interval = heartbeat_interval
        self.state = AgentState.IDLE
        self.phase_angle: float = 0.0  # SQPL Kuramoto oscillator angle [0, 2pi]
        self.last_heartbeat: float = time.time()
        self.tasks_completed: int = 0

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize resources required by the agent."""
        pass

    @abstractmethod
    async def execute_task(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task assigned by the NanoAgentManager."""
        pass

    @abstractmethod
    async def teardown(self) -> None:
        """Cleanup resources on agent shutdown."""
        pass

    def pulse_phase(self, delta_t: float = 0.1, natural_frequency: float = 1.0) -> float:
        """
        Advance Kuramoto phase oscillator angle for SQPL synchronization.
        """
        self.phase_angle = (self.phase_angle + natural_frequency * delta_t) % (2 * 3.141592653589793)
        self.last_heartbeat = time.time()
        return self.phase_angle

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "execution_mode": self.execution_mode,
            "state": self.state,
            "phase_angle": self.phase_angle,
            "last_heartbeat": self.last_heartbeat,
            "tasks_completed": self.tasks_completed
        }
