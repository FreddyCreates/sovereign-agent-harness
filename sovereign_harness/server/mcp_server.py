"""
Model Context Protocol (MCP) Server for Sovereign Agent Harness.
Supports stdio and SSE transport streams with 6 standard tools:
- vault_get
- vault_set
- loom_search
- loom_remember
- execute_nano_task
- check_swarm_coherence
"""

import sys
import json
import asyncio
from typing import Dict, Any, List

from sovereign_harness.vault import SovereignVault
from sovereign_harness.loom import LoomMemoriaEngine
from sovereign_harness.runtime.manager import NanoAgentManager, ExecutionMode

class SovereignMCPServer:
    """
    Model Context Protocol (MCP) JSON-RPC 2.0 Server.
    """
    def __init__(self):
        self.vault = SovereignVault()
        self.loom = LoomMemoriaEngine()
        self.manager = NanoAgentManager()
        self._is_running = False

    def get_tool_definitions() -> List[Dict[str, Any]]:
        return [
            {
                "name": "vault_get",
                "description": "Retrieve an encrypted secret key securely from the local zero-custody vault.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key_name": {"type": "string", "description": "Key identifier to retrieve"},
                        "passphrase": {"type": "string", "description": "Vault passphrase"}
                    },
                    "required": ["key_name", "passphrase"]
                }
            },
            {
                "name": "vault_set",
                "description": "Encrypt and store a secret key in the local zero-custody vault.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key_name": {"type": "string", "description": "Key identifier"},
                        "key_value": {"type": "string", "description": "Secret value to encrypt"},
                        "passphrase": {"type": "string", "description": "Vault passphrase"}
                    },
                    "required": ["key_name", "key_value", "passphrase"]
                }
            },
            {
                "name": "loom_search",
                "description": "Search the LOOM Memoria graph for contextual memories.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Semantic query string"},
                        "limit": {"type": "integer", "default": 4}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "loom_remember",
                "description": "Weave a new memory node or learning into the LOOM graph.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Memory text payload"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "emotional_valence": {"type": "number", "default": 0.0}
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "execute_nano_task",
                "description": "Dispatch an autonomous task execution request to a nano-agent.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_name": {"type": "string"},
                        "payload": {"type": "object"},
                        "execution_mode": {"type": "string", "enum": ["thread", "process"], "default": "thread"}
                    },
                    "required": ["task_name"]
                }
            },
            {
                "name": "check_swarm_coherence",
                "description": "Query the SQPL Kuramoto coherence parameter R and swarm phase lock status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def handle_tool_call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "vault_get":
            val = self.vault.retrieve_key(args["key_name"], args["passphrase"])
            return {"status": "success", "key_name": args["key_name"], "key_value": val}

        elif name == "vault_set":
            self.vault.store_key(args["key_name"], args["key_value"], args["passphrase"])
            return {"status": "success", "key_name": args["key_name"], "message": "Key stored"}

        elif name == "loom_search":
            nodes = self.loom.search_memory(args["query"], limit=args.get("limit", 4))
            return {"status": "success", "count": len(nodes), "results": [n.to_dict() for n in nodes]}

        elif name == "loom_remember":
            node = self.loom.weave_memory(
                content=args["content"],
                tags=args.get("tags", []),
                emotional_valence=args.get("emotional_valence", 0.0)
            )
            return {"status": "success", "node_id": node.id, "links_count": len(node.links)}

        elif name == "execute_nano_task":
            mode = ExecutionMode.PROCESS if args.get("execution_mode") == "process" else ExecutionMode.THREAD
            res = await self.manager.dispatch_task(
                task_name=args["task_name"],
                payload=args.get("payload", {}),
                preferred_mode=mode
            )
            return res

        elif name == "check_swarm_coherence":
            return self.manager.get_swarm_status()

        else:
            raise ValueError(f"Unknown MCP tool: {name}")

    async def run_stdio_server(self) -> None:
        """Run JSON-RPC 2.0 stdio server loop for Cursor / Claude / Antigravity integration."""
        await self.manager.start()
        sys.stderr.write("Sovereign MCP Server started (stdio mode)\n")
        sys.stderr.flush()

        while True:
            try:
                # Use asyncio.to_thread for Windows-safe stdio reading without 0x800700e8 pipe errors
                line_str = await asyncio.to_thread(sys.stdin.readline)
                if not line_str:
                    break

                line_str = line_str.strip()
                if not line_str:
                    continue

                msg = json.loads(line_str)
                rpc_id = msg.get("id")
                method = msg.get("method")

                if method == "initialize":
                    resp = {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "sovereign-agent-harness-mcp", "version": "1.0.0"}
                        }
                    }
                elif method == "tools/list":
                    resp = {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "result": {"tools": self.get_tool_definitions()}
                    }
                elif method == "tools/call":
                    params = msg.get("params", {})
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})
                    result_data = await self.handle_tool_call(tool_name, tool_args)
                    resp = {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(result_data, indent=2)}],
                            "isError": False
                        }
                    }
                else:
                    resp = {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": "Method not found"}}

                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

        await self.manager.stop()

if __name__ == "__main__":
    server = SovereignMCPServer()
    asyncio.run(server.run_stdio_server())
