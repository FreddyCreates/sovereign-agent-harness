"""
LOOM Engine Module — Memoria De Intelligencia Graph & Memory Weaver
------------------------------------------------------------------
Derived from Paper XVIII (Archivum Memoriae Sovereignae).
Weaves persistent semantic memories into an immutable client-side graph.
Automatically recalls prior memories before agent reasoning steps, and 
weaves post-execution learnings back into the user's LOOM.
"""

import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional

DEFAULT_LOOM_PATH = os.path.expanduser("~/.sovereign_vault/harness_loom.json")

class LoomMemoryNode:
    def __init__(
        self,
        content: str,
        language: str = "es-ES",
        emotional_valence: float = 0.0,
        provenance: str = "agent-harness",
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        node_id: Optional[str] = None,
        created_at: Optional[float] = None
    ):
        self.id = node_id or f"mem_{uuid.uuid4().hex[:10]}"
        self.content = content
        self.language = language
        self.emotional_valence = emotional_valence
        self.provenance = provenance
        self.tags = tags or []
        self.context = context or {}
        self.links: List[str] = []
        self.created_at = created_at or time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "language": self.language,
            "emotional_valence": self.emotional_valence,
            "provenance": self.provenance,
            "tags": self.tags,
            "context": self.context,
            "links": self.links,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'LoomMemoryNode':
        node = cls(
            content=d["content"],
            language=d.get("language", "es-ES"),
            emotional_valence=d.get("emotional_valence", 0.0),
            provenance=d.get("provenance", "agent-harness"),
            tags=d.get("tags"),
            context=d.get("context"),
            node_id=d.get("id"),
            created_at=d.get("created_at")
        )
        node.links = d.get("links", [])
        return node

class LoomMemoriaEngine:
    def __init__(self, storage_path: str = DEFAULT_LOOM_PATH):
        self.storage_path = storage_path
        self.nodes: Dict[str, LoomMemoryNode] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    for item in raw.get("memories", []):
                        node = LoomMemoryNode.from_dict(item)
                        self.nodes[node.id] = node
            except Exception as e:
                print(f"[LOOM] Load warning ({e}); initializing empty graph.")

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "version": "1.0.0",
            "paper_reference": "Paper XVIII — Archivum Memoriae",
            "total_memories": len(self.nodes),
            "memories": [node.to_dict() for node in self.nodes.values()]
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def weave_memory(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        language: str = "es-ES",
        emotional_valence: float = 0.0,
        provenance: str = "agent-harness",
        context: Optional[Dict[str, Any]] = None
    ) -> LoomMemoryNode:
        node = LoomMemoryNode(
            content=content,
            tags=tags,
            language=language,
            emotional_valence=emotional_valence,
            provenance=provenance,
            context=context
        )

        # Auto-link related tags
        if node.tags:
            for existing in self.nodes.values():
                if any(t in existing.tags for t in node.tags):
                    node.links.append(existing.id)
                    existing.links.append(node.id)

        self.nodes[node.id] = node
        self.save()
        return node

    def recall(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Recalls relevant memories for prompt context injection."""
        query_terms = set(query.lower().split())
        scored = []

        for node in self.nodes.values():
            words = set(node.content.lower().split())
            score = len(query_terms.intersection(words)) * 2.0
            score += sum(2.0 for t in node.tags if t.lower() in query.lower())
            if score > 0 or not query:
                scored.append((score, node.to_dict()))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

    def search_memory(self, query: str, limit: int = 4) -> List[LoomMemoryNode]:
        """Returns LoomMemoryNode objects matching query."""
        recalled = self.recall(query, limit)
        return [self.nodes[d["id"]] for d in recalled if d["id"] in self.nodes]
