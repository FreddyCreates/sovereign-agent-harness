"""
CLI Module — Sovereign Agent Harness Production Command Line Utility
--------------------------------------------------------------------
Provides `sovereign-harness` command line access for:
- Starting full production FastAPI & MCP servers
- Running autonomous tasks
- Managing zero-custody local vault keys
- Querying LOOM memory graphs
- Inspecting live SQPL Kuramoto swarm coherence (R)
"""

import sys
import os
import argparse
import json
import asyncio
from sovereign_harness.harness import SovereignAgentHarness
from sovereign_harness.sdk import AsyncSovereignClient, SovereignSDK

def main():
    import multiprocessing
    multiprocessing.freeze_support()

    parser = argparse.ArgumentParser(
        prog="sovereign-harness",
        description="Sovereign Agent Harness — Production Zero-Custody Vault & Agentic Runtime"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    # 1. Run Task Command
    run_parser = subparsers.add_parser("run", help="Run an autonomous task with Sovereign Agent Harness")
    run_parser.add_argument("task", type=str, help="Task prompt or instruction")
    run_parser.add_argument("--mode", choices=["thread", "process"], default="thread", help="Nano-Agent execution mode")

    # 2. Serve Server Command (FastAPI + MCP)
    serve_parser = subparsers.add_parser("serve", help="Start full production FastAPI REST & MCP Server")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface to bind")
    serve_parser.add_argument("--port", type=int, default=8088, help="Port to listen on")
    serve_parser.add_argument("--mcp-stdio", action="store_true", help="Launch MCP JSON-RPC server on stdio")

    # 3. Vault Management Command
    vault_parser = subparsers.add_parser("vault", help="Client-Side Zero-Custody Vault operations")
    vault_parser.add_argument("action", choices=["list", "set", "get", "status", "mask"], help="Vault action")
    vault_parser.add_argument("--key", type=str, help="Key identifier for set/get")
    vault_parser.add_argument("--val", type=str, help="Secret value for set")
    vault_parser.add_argument("--text", type=str, help="Text string to mask secrets")

    # 4. LOOM Memory Command
    loom_parser = subparsers.add_parser("loom", help="LOOM Memoria Graph operations")
    loom_parser.add_argument("action", choices=["list", "search", "weave"], help="LOOM action")
    loom_parser.add_argument("--query", type=str, default="", help="Query for memory search")
    loom_parser.add_argument("--content", type=str, help="Content to weave into LOOM")
    loom_parser.add_argument("--tags", type=str, help="Comma-separated tags for LOOM node")

    # 5. Swarm Telemetry & Status Command
    status_parser = subparsers.add_parser("status", help="Show live system and SQPL swarm status")

    args = parser.parse_args()

    if args.command == "serve":
        if args.mcp_stdio:
            from sovereign_harness.server.mcp_server import SovereignMCPServer
            mcp_server = SovereignMCPServer()
            asyncio.run(mcp_server.run_stdio_server())
        else:
            import uvicorn
            from sovereign_harness.server.api import app
            print(f"Starting Sovereign Harness Control Plane on http://{args.host}:{args.port}")
            uvicorn.run(app, host=args.host, port=args.port)

    elif args.command == "run":
        sdk = SovereignSDK()
        res = sdk.execute_task(args.task, mode=args.mode)
        print(json.dumps(res, indent=2))

    elif args.command == "vault":
        sdk = SovereignSDK()
        harness = SovereignAgentHarness()
        if args.action == "list":
            keys = harness.vault.list_keys()
            print(f"Stored Vault Keys ({len(keys)}): {keys}")
        elif args.action == "set":
            if not args.key or not args.val:
                print("Error: --key and --val are required for 'vault set'")
                sys.exit(1)
            harness.vault.set_key(args.key, args.val)
            print(f"[OK] Key '{args.key}' securely encrypted in client-side vault.")
        elif args.action == "get":
            if not args.key:
                print("Error: --key is required for 'vault get'")
                sys.exit(1)
            val = harness.vault.get_key(args.key)
            print(f"Key '{args.key}': {val}")
        elif args.action == "mask":
            if not args.text:
                print("Error: --text is required for 'vault mask'")
                sys.exit(1)
            masked = harness.vault.mask_secrets_in_text(args.text)
            print(f"Sanitized Output: {masked}")
        elif args.action == "status":
            print(json.dumps(harness.vault.get_status(), indent=2))

    elif args.command == "loom":
        harness = SovereignAgentHarness()
        if args.action == "search":
            results = harness.loom.recall(args.query)
            print(json.dumps(results, indent=2))
        elif args.action == "weave":
            if not args.content:
                print("Error: --content is required for 'loom weave'")
                sys.exit(1)
            tags_list = [t.strip() for t in args.tags.split(",")] if args.tags else []
            node = harness.loom.weave_memory(args.content, tags=tags_list)
            print(f"[OK] Memory Woven into LOOM Graph. Node ID: {node.id}")
        elif args.action == "list":
            summary = {
                "total_memories": len(harness.loom.nodes),
                "storage_path": harness.loom.storage_path,
                "paper_reference": "Paper XVIII — Archivum Memoriae"
            }
            print(json.dumps(summary, indent=2))

    elif args.command == "status":
        harness = SovereignAgentHarness()
        status_info = {
            "harness": harness.name,
            "version": "1.0.0",
            "vault": harness.vault.get_status(),
            "loom_memories_count": len(harness.loom.nodes),
            "registered_tools_count": len(harness.tools.list_schemas()),
            "status": "PRODUCTION_READY"
        }
        print(json.dumps(status_info, indent=2))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
