"""End-to-end hermetic test: HermesCompetingAgent → arbiter → sealed truth.

Replaces ``HermesClient.invoke`` with an in-process stub so the test does not
actually fork run_agent.py.
"""
from __future__ import annotations

import asyncio
import os

from agents.hermes_agent import HermesCompetingAgent
from agents.rubric import DefaultRubric
from hermes_bridge.client import HermesClient, HermesResult
from iaia.orchestrator import IAiA, Request
from tol.dispatcher import InMemoryToL
from truth.arbiter import Arbiter
from truth.models import verify

os.environ.setdefault("RSFS_TRUTH_KEY", "test-key-do-not-use-in-prod")


class _StubClient(HermesClient):
    def __init__(self, *, stdout: str, wall: float, rc: int = 0, stderr: str = "") -> None:
        super().__init__()
        self._stdout = stdout
        self._wall = wall
        self._rc = rc
        self._stderr = stderr

    async def invoke(self, prompt: str, *, deadline_seconds: float, tool_budget=None):  # type: ignore[override]
        return HermesResult(
            stdout=self._stdout,
            stderr=self._stderr,
            returncode=self._rc,
            wall_seconds=self._wall,
            timed_out=False,
        )


def test_hermes_agents_compete() -> None:
    fast = HermesCompetingAgent(
        name="fast",
        client=_StubClient(stdout="fast answer", wall=0.2),
        rubric=DefaultRubric(accuracy_floor=0.6),
    )
    slow = HermesCompetingAgent(
        name="slow",
        client=_StubClient(stdout="slow answer", wall=2.0),
        rubric=DefaultRubric(accuracy_floor=0.6),
    )
    noisy = HermesCompetingAgent(
        name="noisy",
        client=_StubClient(stdout="noisy answer", wall=0.3, stderr="warning: x"),
        rubric=DefaultRubric(accuracy_floor=0.6),
    )
    tol = InMemoryToL()
    iaia = IAiA(agents=[fast, slow, noisy], arbiter=Arbiter(), tol=tol)
    truth = asyncio.run(iaia.run(Request(payload="prompt", deadline_seconds=3.0)))
    # fast wins: identical precision/accuracy across all three, but better speed
    # and tied (max) neatness against noisy.
    assert truth.producer == "fast"
    assert tol.received == [truth]
    assert verify(truth)
