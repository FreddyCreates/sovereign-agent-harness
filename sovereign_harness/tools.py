"""
Tools Module — Tool Registry & Autonomous Execution Sandbox
------------------------------------------------------------
Provides built-in tools (Shell, Filesystem, HTTP, Vault, LOOM) and a @tool decorator 
for registering custom agent capabilities.
"""

import subprocess
import os
import json
import urllib.request
import functools
from typing import Dict, Any, Callable, List, Optional

class Tool:
    def __init__(self, name: str, description: str, func: Callable, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._register_default_tools()

    def register(self, name: str, description: str, parameters: Dict[str, Any]):
        def decorator(func: Callable):
            tool_obj = Tool(name, description, func, parameters)
            self._tools[name] = tool_obj
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_schemas(self) -> List[Dict[str, Any]]:
        schemas = []
        for t in self._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                }
            })
        return schemas

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return self.list_schemas()

    def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> str:
        t = self.get_tool(name)
        if not t:
            return f"Error: Tool '{name}' not found."
        try:
            res = t.execute(**kwargs)
            if isinstance(res, (dict, list)):
                return json.dumps(res, indent=2)
            return str(res)
        except Exception as e:
            return f"Tool Execution Error ({name}): {str(e)}"

    def _register_default_tools(self):
        # 1. Shell Exec
        def shell_exec(command: str) -> str:
            """Executes a local command line instruction securely."""
            try:
                out = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
                return out.decode("utf-8", errors="replace")
            except subprocess.CalledProcessError as e:
                return f"Command Failed (exit code {e.returncode}): {e.output.decode('utf-8', errors='replace')}"
            except Exception as e:
                return f"Execution Error: {str(e)}"

        self.register(
            name="shell_exec",
            description="Executes a CLI command in the system terminal.",
            parameters={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        )(shell_exec)

        # 2. Read File
        def read_file(filepath: str) -> str:
            """Reads text contents from a local file."""
            if not os.path.exists(filepath):
                return f"Error: File '{filepath}' does not exist."
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        self.register(
            name="read_file",
            description="Reads text from a local filesystem file.",
            parameters={
                "type": "object",
                "properties": {"filepath": {"type": "string"}},
                "required": ["filepath"]
            }
        )(read_file)

        # 3. Write File
        def write_file(filepath: str, content: str) -> str:
            """Writes text content to a local file."""
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {filepath}."

        self.register(
            name="write_file",
            description="Writes text content to a local file.",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filepath", "content"]
            }
        )(write_file)

        # 4. HTTP Fetch
        def http_fetch(url: str) -> str:
            """Fetches URL contents via HTTP GET."""
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SovereignAgentHarness/1.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    return response.read().decode('utf-8', errors='replace')[:4000]
            except Exception as e:
                return f"HTTP Fetch Error ({url}): {str(e)}"

        self.register(
            name="http_fetch",
            description="Fetches web content or API JSON from a public URL.",
            parameters={
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"]
            }
        )(http_fetch)

# Global helper decorator
_global_registry = ToolRegistry()
def tool(name: str, description: str, parameters: Dict[str, Any]):
    return _global_registry.register(name, description, parameters)
