"""
FastAPI REST & Telemetry Server for Sovereign Agent Harness Control Plane.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
from typing import Dict, Any, Optional

from sovereign_harness.vault import SovereignVault
from sovereign_harness.loom import LoomMemoriaEngine
from sovereign_harness.runtime.manager import NanoAgentManager, ExecutionMode
from sovereign_harness.server.schemas import (
    VaultKeyStoreRequest,
    VaultKeyRetrieveRequest,
    LoomMemoryWeaveRequest,
    LoomSearchRequest,
    TaskDispatchPayload,
    SwarmTelemetryResponse
)

app = FastAPI(
    title="Sovereign Agent Harness Control Plane",
    description="Enterprise Zero-Custody Vault, LOOM Memory Graph, & Hybrid Nano-Agent Runtime API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global singleton runtime instances
_vault_instance = SovereignVault()
_loom_instance = LoomMemoriaEngine()
_runtime_manager = NanoAgentManager()

@app.on_event("startup")
async def startup_event():
    await _runtime_manager.start()

@app.on_event("shutdown")
async def shutdown_event():
    await _runtime_manager.stop()

@app.get("/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "runtime_active": _runtime_manager._is_running,
        "coherence_r": round(_runtime_manager.compute_coherence_r(), 4)
    }

# --- Vault Routes ---
@app.post("/v1/vault/store")
async def store_vault_key(req: VaultKeyStoreRequest, passphrase: str = "sovereign_secure_passphrase"):
    try:
        _vault_instance.store_key(req.key_name, req.key_value, passphrase)
        return {"status": "success", "key_name": req.key_name, "message": "Key encrypted and stored in local vault"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/vault/retrieve")
async def retrieve_vault_key(req: VaultKeyRetrieveRequest):
    try:
        val = _vault_instance.retrieve_key(req.key_name, req.passphrase)
        return {"status": "success", "key_name": req.key_name, "key_value": val}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve key: {str(e)}")

# --- LOOM Memory Routes ---
@app.post("/v1/loom/ingest")
async def weave_memory(req: LoomMemoryWeaveRequest):
    try:
        node = _loom_instance.weave_memory(
            content=req.content,
            tags=req.tags or [],
            language=req.language,
            emotional_valence=req.emotional_valence,
            provenance=req.provenance,
            context=req.context or {}
        )
        return {"status": "success", "node": node.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/loom/search")
async def search_memory(req: LoomSearchRequest):
    try:
        nodes = _loom_instance.search_memory(req.query, limit=req.limit)
        return {"status": "success", "count": len(nodes), "results": [n.to_dict() for n in nodes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Nano-Agent & Task Dispatch Routes ---
@app.post("/v1/agents/dispatch")
async def dispatch_task(payload: TaskDispatchPayload):
    try:
        pref_mode = None
        if payload.preferred_mode == "thread":
            pref_mode = ExecutionMode.THREAD
        elif payload.preferred_mode == "process":
            pref_mode = ExecutionMode.PROCESS

        res = await _runtime_manager.dispatch_task(
            task_name=payload.task_name,
            payload=payload.payload,
            preferred_mode=pref_mode
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/swarm/telemetry", response_model=SwarmTelemetryResponse)
async def get_swarm_telemetry():
    return _runtime_manager.get_swarm_status()

@app.get("/v1/swarm/stream")
async def stream_swarm_telemetry():
    """
    Server-Sent Events (SSE) telemetry stream for real-time SQPL phase lock monitoring.
    """
    async def event_generator():
        while True:
            telemetry = _runtime_manager.get_swarm_status()
            yield f"data: {json.dumps(telemetry)}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
