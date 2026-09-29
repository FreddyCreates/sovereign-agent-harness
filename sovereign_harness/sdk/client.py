"""
Sovereign AI SDK (Python Client Library).
Provides AsyncSovereignClient and SovereignSDK for seamless developer integration.
"""

import asyncio
from typing import Dict, List, Any, Optional

from sovereign_harness.vault import SovereignVault
from sovereign_harness.loom import LoomMemoriaEngine
from sovereign_harness.runtime.manager import NanoAgentManager, ExecutionMode

class AsyncSovereignClient:
    """
    Asynchronous Python Client for Sovereign Agent Harness.
    Supports local in-process direct bindings or remote FastAPI HTTP calls.
    """
    def __init__(self, passphrase: str = "sovereign_secure_passphrase"):
        self.passphrase = passphrase
        self.vault = SovereignVault()
        self.loom = LoomMemoriaEngine()
        self.manager = NanoAgentManager()

    async def __aenter__(self):
        await self.manager.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.manager.stop()

    # --- Vault Methods ---
    async def store_key(self, key_name: str, key_value: str) -> None:
        self.vault.store_key(key_name, key_value, self.passphrase)

    async def retrieve_key(self, key_name: str) -> str:
        return self.vault.retrieve_key(key_name, self.passphrase)

    # --- LOOM Methods ---
    async def weave_memory(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        emotional_valence: float = 0.0,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        node = self.loom.weave_memory(
            content=content,
            tags=tags or [],
            emotional_valence=emotional_valence,
            context=context or {}
        )
        return node.to_dict()

    async def search_memory(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        nodes = self.loom.search_memory(query, limit=limit)
        return [n.to_dict() for n in nodes]

    # --- Task Dispatch Methods ---
    async def execute_task(
        self,
        task_name: str,
        payload: Optional[Dict[str, Any]] = None,
        mode: str = "thread"
    ) -> Dict[str, Any]:
        pref_mode = ExecutionMode.PROCESS if mode == "process" else ExecutionMode.THREAD
        return await self.manager.dispatch_task(
            task_name=task_name,
            payload=payload or {},
            preferred_mode=pref_mode
        )

    async def get_swarm_coherence(self) -> Dict[str, Any]:
        return self.manager.get_swarm_status()


class SovereignSDK:
    """
    Synchronous Facade for simpler scripts and CLI applications.
    """
    def __init__(self, passphrase: str = "sovereign_secure_passphrase"):
        self.passphrase = passphrase

    def execute_task(self, task_name: str, payload: Optional[Dict[str, Any]] = None, mode: str = "thread") -> Dict[str, Any]:
        async def _run():
            async with AsyncSovereignClient(self.passphrase) as client:
                return await client.execute_task(task_name, payload, mode)
        return asyncio.run(_run())

    def search_memory(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        async def _run():
            async with AsyncSovereignClient(self.passphrase) as client:
                return await client.search_memory(query, limit)
        return asyncio.run(_run())
