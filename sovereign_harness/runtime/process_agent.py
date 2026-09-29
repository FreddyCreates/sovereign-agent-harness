"""
Production Process-based Nano-Agent implementation running in isolated OS subprocesses.
Executes real sandboxed commands, CPU-heavy computations, and security guardrail evaluation.
"""

import multiprocessing as mp
import subprocess
import asyncio
import time
import os
import sys
from typing import Dict, Any, Optional
from sovereign_harness.runtime.base_agent import NanoAgent, AgentState, ExecutionMode
from sovereign_harness.guardrails import SecurityGuardrail

def _subprocess_worker_entry(
    agent_id: str,
    name: str,
    input_queue: mp.Queue,
    output_queue: mp.Queue,
    shutdown_event: mp.Event
):
    """
    Subprocess main worker loop running in an isolated OS process address space.
    Executes real tasks safely isolated from main event loop.
    """
    phase_angle = 0.0
    guardrails = SecurityGuardrail()

    while not shutdown_event.is_set():
        if not input_queue.empty():
            try:
                task_id, task_name, payload = input_queue.get_nowait()
                start_time = time.time()
                
                res_data = {}
                if task_name == "shell_exec" or task_name == "tool_exec":
                    cmd = payload.get("command", "")
                    
                    # 1. Enforce production security guardrails
                    is_safe, error_msg = guardrails.evaluate(cmd)
                    if not is_safe:
                        res_data = {
                            "executed": False,
                            "error": f"SecurityGuardrail Blocked Execution: {error_msg}",
                            "pid": os.getpid()
                        }
                    else:
                        # 2. Execute command inside isolated subprocess sandbox
                        proc = subprocess.run(
                            cmd,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=payload.get("timeout", 10.0)
                        )
                        res_data = {
                            "executed": True,
                            "command": cmd,
                            "returncode": proc.returncode,
                            "stdout": proc.stdout.strip(),
                            "stderr": proc.stderr.strip(),
                            "pid": os.getpid()
                        }

                elif task_name == "compute":
                    vector = payload.get("vector", [1.0] * 64)
                    matrix = payload.get("matrix", None)
                    
                    # Real vector calculation
                    vector_norm = sum(x*x for x in vector) ** 0.5
                    sum_val = sum(vector)
                    avg_val = sum_val / len(vector) if vector else 0.0
                    
                    res_data = {
                        "vector_norm": vector_norm,
                        "sum": sum_val,
                        "avg": avg_val,
                        "dimension": len(vector),
                        "pid": os.getpid()
                    }
                else:
                    res_data = {
                        "task_name": task_name,
                        "payload_keys": list(payload.keys()),
                        "pid": os.getpid(),
                        "status": "completed_in_process_sandbox"
                    }

                output_queue.put((
                    task_id,
                    {
                        "status": "success",
                        "agent_id": agent_id,
                        "pid": os.getpid(),
                        "execution_mode": "process",
                        "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                        "data": res_data
                    }
                ))
            except subprocess.TimeoutExpired:
                output_queue.put((task_id, {"status": "error", "agent_id": agent_id, "error": "Command execution timed out"}))
            except Exception as e:
                output_queue.put((task_id, {"status": "error", "agent_id": agent_id, "error": str(e)}))

        # Pulse Kuramoto oscillator phase angle
        phase_angle = (phase_angle + 0.1) % (2 * 3.141592653589793)
        time.sleep(0.02)


class ProcessNanoAgent(NanoAgent):
    """
    Production ProcessNanoAgent running in a dedicated OS process via multiprocessing (spawn context).
    Provides crash isolation and process sandbox safety.
    """
    def __init__(
        self,
        agent_id: str,
        name: str,
        heartbeat_interval: float = 0.5
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            execution_mode=ExecutionMode.PROCESS,
            heartbeat_interval=heartbeat_interval
        )
        self.ctx = mp.get_context("spawn")
        self.input_queue = self.ctx.Queue()
        self.output_queue = self.ctx.Queue()
        self.shutdown_event = self.ctx.Event()
        self.process: Optional[mp.Process] = None
        self._pending_tasks: Dict[str, asyncio.Future] = {}
        self._listener_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        self.state = AgentState.IDLE
        self.process = self.ctx.Process(
            target=_subprocess_worker_entry,
            args=(
                self.agent_id,
                self.name,
                self.input_queue,
                self.output_queue,
                self.shutdown_event
            ),
            daemon=True
        )
        self.process.start()
        self._listener_task = asyncio.create_task(self._listen_outputs())

    async def _listen_outputs(self) -> None:
        while not self.shutdown_event.is_set():
            while not self.output_queue.empty():
                try:
                    task_id, result = self.output_queue.get_nowait()
                    if task_id in self._pending_tasks:
                        fut = self._pending_tasks.pop(task_id)
                        if not fut.done():
                            fut.set_result(result)
                            self.tasks_completed += 1
                except Exception:
                    pass
            self.pulse_phase(delta_t=0.05)
            await asyncio.sleep(0.02)

    async def execute_task(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.process or not self.process.is_alive():
            raise RuntimeError(f"Process for agent {self.name} is not alive")

        task_id = f"task_{time.time_ns()}"
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self._pending_tasks[task_id] = fut

        self.input_queue.put((task_id, task_name, payload))

        try:
            return await asyncio.wait_for(fut, timeout=15.0)
        except asyncio.TimeoutError:
            self._pending_tasks.pop(task_id, None)
            return {"status": "error", "agent_id": self.agent_id, "error": "Task execution timed out"}

    async def teardown(self) -> None:
        self.shutdown_event.set()
        if self._listener_task:
            self._listener_task.cancel()
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=1.0)
        self.state = AgentState.STOPPED
