"""Smoke test: a fake competing agent + arbiter + in-mem ToL produce a sealed
The_Truth via the iAiA orchestrator. Verifies the route exists; nothing more.
"""
from __future__ import annotations

import asyncio

from agents.base import Candidate, CompetingAgent
from iaia.orchestrator import IAiA, Request
from tol.dispatcher import InMemoryToL
from truth.arbiter import Arbiter


class _Fake(CompetingAgent):
    name = "fake"

    def __init__(self, name: str, score: float) -> None:
        self.name = name
        self._score = score

    async def produce(self, request: Request) -> Candidate:
        return Candidate(
            producer=self.name,
            payload=f"{self.name}:{request.payload}",
            scores={
                "precision": self._score,
                "accuracy": self._score,
                "speed": self._score,
                "neatness": self._score,
            },
        )


def test_single_route_to_truth() -> None:
    tol = InMemoryToL()
    iaia = IAiA(
        agents=[_Fake("alpha", 0.6), _Fake("beta", 0.9), _Fake("gamma", 0.7)],
        arbiter=Arbiter(),
        tol=tol,
    )
    truth = asyncio.run(iaia.run(Request(payload="ping")))
    assert truth.producer == "beta"
    assert tol.received == [truth]
