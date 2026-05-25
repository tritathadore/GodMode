"""Subprocess bridge onto hermes-agent's ``run_agent.py``.

One fork per invocation — no shared in-process state, which preserves the
no-shared-cache rule the single-route-to-truth model depends on. The wrapper
is intentionally narrow: it kicks the subprocess, honors the deadline, and
returns a raw payload + telemetry. Scoring is the competing-agent's job.
"""
from __future__ import annotations

import asyncio
import os
import shlex
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class HermesResult:
    stdout: str
    stderr: str
    returncode: int
    wall_seconds: float
    timed_out: bool = False


@dataclass
class HermesClient:
    """Invokes hermes-agent's run_agent.py as a subprocess.

    Configuration:
      script_path: absolute path to run_agent.py (defaults to env
                   RSFS_HERMES_RUN_AGENT or ./hermes-agent/run_agent.py)
      python:      interpreter to use (defaults to sys.executable)
      extra_args:  extra CLI args appended to every invocation
      env:         additional env vars merged on top of os.environ
    """

    script_path: str = field(
        default_factory=lambda: os.environ.get(
            "RSFS_HERMES_RUN_AGENT", "./hermes-agent/run_agent.py"
        )
    )
    python: str = field(default_factory=lambda: sys.executable)
    extra_args: tuple[str, ...] = ()
    env: Mapping[str, str] = field(default_factory=dict)

    async def invoke(
        self,
        prompt: str,
        *,
        deadline_seconds: float,
        tool_budget: int | None = None,
    ) -> HermesResult:
        cmd: list[str] = [self.python, self.script_path, "--prompt", prompt]
        if tool_budget is not None:
            cmd += ["--tool-budget", str(tool_budget)]
        cmd += list(self.extra_args)

        merged_env = {**os.environ, **self.env}
        started = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=merged_env,
        )
        timed_out = False
        try:
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(), timeout=deadline_seconds
            )
        except asyncio.TimeoutError:
            timed_out = True
            proc.kill()
            stdout_b, stderr_b = await proc.communicate()
        elapsed = time.monotonic() - started
        return HermesResult(
            stdout=stdout_b.decode("utf-8", errors="replace"),
            stderr=stderr_b.decode("utf-8", errors="replace"),
            returncode=proc.returncode if proc.returncode is not None else -1,
            wall_seconds=elapsed,
            timed_out=timed_out,
        )

    def describe(self) -> dict[str, Any]:
        return {
            "transport": "subprocess",
            "script_path": self.script_path,
            "python": self.python,
            "extra_args": list(self.extra_args),
        }
