"""Thin wrapper around hermes-agent.

The real surface depends on which hermes entrypoint we standardise on
(`run_agent.py`, the `hermes_cli` package, or the in-proc API). Capturing that
here is `TODO(pyraclaw-spec)` once the orchestrator-side contract is fixed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HermesClient:
    """Placeholder bridge. Real implementation must:

    1. Accept a prompt + tool budget + deadline.
    2. Invoke hermes-agent (CLI subprocess OR in-proc) deterministically.
    3. Return a raw payload + telemetry that `agents/` can score against.
    """

    endpoint: str = "in-proc"  # TODO(pyraclaw-spec): or HTTP, or subprocess.

    async def invoke(self, prompt: str, **kwargs: Any) -> Any:
        raise NotImplementedError(
            "HermesClient.invoke is a placeholder — wire to hermes-agent. "
            "See hermes-agent docs/rsfs_mode_integration.md."
        )
