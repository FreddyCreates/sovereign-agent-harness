"""
Durable Agent Checkpointing & Recovery System for Sovereign Harness Runtime.
Provides Write-Ahead Logging (WAL) and snapshot recovery across restarts/crashes.
"""

import os
import json
import time
from typing import Dict, Any, Optional, List

DEFAULT_CHECKPOINT_DIR = os.path.expanduser("~/.sovereign_vault/checkpoints")

class AgentCheckpointManager:
    """
    Manages durable state snapshots and WAL event streams for Nano-Agents.
    """
    def __init__(self, checkpoint_dir: str = DEFAULT_CHECKPOINT_DIR):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.wal_file = os.path.join(self.checkpoint_dir, "runtime_wal.jsonl")

    def append_wal_event(self, agent_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Appends an execution event to the Write-Ahead Log."""
        entry = {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "event_type": event_type,
            "data": data
        }
        with open(self.wal_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def save_snapshot(self, swarm_status: Dict[str, Any]) -> str:
        """Saves a complete snapshot of all active agent phase angles and state."""
        snapshot_id = f"snap_{int(time.time() * 1000)}"
        file_path = os.path.join(self.checkpoint_dir, f"{snapshot_id}.json")
        snapshot_data = {
            "snapshot_id": snapshot_id,
            "created_at": time.time(),
            "swarm_status": swarm_status
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2)
        return file_path

    def load_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Loads the most recent snapshot file if available."""
        files = [f for f in os.listdir(self.checkpoint_dir) if f.startswith("snap_") and f.endswith(".json")]
        if not files:
            return None
        files.sort(reverse=True)
        latest_path = os.path.join(self.checkpoint_dir, files[0])
        try:
            with open(latest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[AgentCheckpointManager] Failed to load snapshot: {e}")
            return None
