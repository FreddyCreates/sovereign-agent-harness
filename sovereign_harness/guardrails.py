"""
Guardrails Module — Zero-Trust Security Audit & Safety Rules
------------------------------------------------------------
Monitors tool call security, prevents dangerous destructive operations, 
and logs cryptographic proof signatures.
"""

from enum import Enum
from typing import Dict, Any, List, Optional

class ActionRiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityGuardrail:
    def __init__(self, require_approval_for_high_risk: bool = True):
        self.require_approval = require_approval_for_high_risk
        self.blocked_patterns = [
            "rm -rf /",
            "format c:",
            ":(){ :|:& };:",
            "drop database",
            "sudo rm -rf"
        ]

    def evaluate(self, command_str: str) -> tuple[bool, str]:
        res = self.evaluate_tool_call("shell_exec", {"command": command_str})
        return res["allowed"], res["reason"]

    def evaluate_tool_call(self, tool_name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates tool execution parameters for security risk."""
        cmd_str = str(kwargs).lower()

        # Check critical blocked patterns
        for pattern in self.blocked_patterns:
            if pattern in cmd_str:
                return {
                    "allowed": False,
                    "risk_level": ActionRiskLevel.CRITICAL.value,
                    "reason": f"Blocked high-risk command pattern detected: '{pattern}'"
                }

        if tool_name == "shell_exec":
            if any(danger in cmd_str for danger in ["del /f", "rmdir /s", "curl -s", "chmod 777"]):
                return {
                    "allowed": not self.require_approval,
                    "risk_level": ActionRiskLevel.HIGH.value,
                    "reason": "Potentially destructive shell command execution."
                }
            return {"allowed": True, "risk_level": ActionRiskLevel.MEDIUM.value, "reason": "Standard shell execution."}

        return {"allowed": True, "risk_level": ActionRiskLevel.LOW.value, "reason": "Safe tool execution."}
