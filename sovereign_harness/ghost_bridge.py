"""
Context Chunker & Dynamic Plot Summarizer for GHOST 2b / Short-Context Models (2048 Tokens).
Prevents narrative degradation by chunking long stories and weaving plot nodes into LOOM & Vault.
"""

import math
import time
from typing import List, Dict, Any, Optional
from sovereign_harness.loom import LoomMemoriaEngine, LoomMemoryNode
from sovereign_harness.vault import SovereignVault

class ContextChunker:
    """
    Splits long text streams (novels, extended conversations) into semantic token blocks.
    Default chunk size: 512 tokens (~2000 chars) to fit well within GHOST 2b's 2048-token window.
    """
    def __init__(self, max_chunk_chars: int = 2000, overlap_chars: int = 200):
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def chunk_text(self, text: str) -> List[str]:
        if len(text) <= self.max_chunk_chars:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.max_chunk_chars
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap_chars if end < len(text) else len(text)

        return chunks

class GhostContextVault:
    """
    GHOST 2b Context Memory Manager.
    Bridges GHOST 2b's 2048-token context window with LoomMemoriaEngine and Zero-Custody Vault.
    Stores plot trajectories, character arcs, and world state across 10,000+ token narratives.
    """
    def __init__(self, vault: Optional[SovereignVault] = None, loom: Optional[LoomMemoriaEngine] = None):
        self.vault = vault or SovereignVault()
        self.loom = loom or LoomMemoriaEngine()
        self.chunker = ContextChunker()
        self.active_story_id: str = f"story_{int(time.time())}"

    def ingest_long_narrative(self, narrative_text: str, title: str = "Untitled Narrative") -> Dict[str, Any]:
        """
        Processes long narrative text exceeding 2048 tokens:
        1. Chunks text into 512-token semantic blocks.
        2. Weaves each chunk into LOOM Memoria graph with tags and plot links.
        3. Encrypts plot state vector into SovereignVault.
        """
        chunks = self.chunker.chunk_text(narrative_text)
        woven_nodes = []

        for idx, chunk in enumerate(chunks):
            node = self.loom.weave_memory(
                content=chunk,
                tags=["ghost2b", self.active_story_id, f"chunk_{idx}"],
                context={"story_title": title, "chunk_index": idx, "total_chunks": len(chunks)}
            )
            woven_nodes.append(node.id)

        # Encrypt storyline state summary into Vault
        summary_key = f"GHOST2B_STORY_{self.active_story_id}"
        story_summary = f"Title: {title} | Chunks: {len(chunks)} | Woven Nodes: {len(woven_nodes)}"
        self.vault.set_key(summary_key, story_summary, metadata={"title": title, "nodes": woven_nodes})

        return {
            "story_id": self.active_story_id,
            "total_chunks": len(chunks),
            "woven_node_ids": woven_nodes,
            "vault_summary_key": summary_key
        }

    def assemble_ghost2b_prompt(self, user_prompt: str, max_context_tokens: int = 500) -> str:
        """
        Assembles a compressed context buffer for GHOST 2b (fits within 2048 tokens).
        Recalls top plot nodes from LOOM and prepends them as a structured context header.
        """
        # Recall top relevant narrative memories
        recalled = self.loom.recall(user_prompt, limit=3)
        
        context_header = "=== LOOM MEMORIA CONTEXT HEADER (GHOST 2b 2048-TOKEN BUFFER) ===\n"
        if recalled:
            for idx, memory in enumerate(recalled):
                content_snippet = memory["content"][:300].replace("\n", " ")
                context_header += f"[{idx+1}] Plot Anchor ({memory['id']}): {content_snippet}...\n"
        else:
            context_header += "[No prior plot memories recalled]\n"
        
        context_header += "=================================================================\n\n"

        full_prompt = context_header + f"User Input: {user_prompt}\nAssistant Response:"
        return full_prompt
