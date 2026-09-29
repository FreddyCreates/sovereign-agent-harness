"""
Pydantic schemas for FastAPI REST endpoints and MCP server tool parameters.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import time

# --- Vault Schemas ---
class VaultKeyStoreRequest(BaseModel):
    key_name: str = Field(..., description="Credential identifier (e.g. OPENAI_API_KEY)")
    key_value: str = Field(..., description="Plaintext secret value to encrypt")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class VaultKeyRetrieveRequest(BaseModel):
    key_name: str = Field(..., description="Key identifier to retrieve")
    passphrase: str = Field(..., description="Vault passphrase")

class VaultKeyResponse(BaseModel):
    key_name: str
    metadata: Dict[str, Any]
    stored_at: float = Field(default_factory=time.time)

# --- LOOM Schemas ---
class LoomMemoryWeaveRequest(BaseModel):
    content: str = Field(..., description="Memory payload string")
    tags: Optional[List[str]] = Field(default_factory=list)
    language: str = Field(default="es-ES")
    emotional_valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    provenance: str = Field(default="sovereign-agent-harness")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class LoomSearchRequest(BaseModel):
    query: str = Field(..., description="Semantic search prompt")
    limit: int = Field(default=4, ge=1, le=50)

# --- Nano-Agent Schemas ---
class TaskDispatchPayload(BaseModel):
    task_name: str = Field(..., description="Task identifier or tool command")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Task argument payload")
    preferred_mode: Optional[str] = Field(default=None, description="Optional 'thread' or 'process' execution mode")

# --- SQPL Swarm Schemas ---
class SwarmTelemetryResponse(BaseModel):
    total_agents: int
    coherence_r: float
    is_phase_locked: bool
    agents: List[Dict[str, Any]]
