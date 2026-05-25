"""iAiA — single apex orchestrator.

One route in, one route out. iAiA does not produce candidates itself; it fans
out to competing agents, hands their candidates to the arbiter, and ships
``The_Truth`` to the ToL dispatcher.
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Sequence

from agents.base import Candidate, CompetingAgent
from tol.dispatcher import ToLDispatcher
from truth.arbiter import Arbiter
from truth.models import The_Truth


@dataclass(frozen=True)
class Request:
    payload: Any
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    deadline_seconds: float = 30.0


class IAiA:
    """The apex. Holds the only legitimate route from request to deliverable."""

    def __init__(
        self,
        agents: Sequence[CompetingAgent],
        arbiter: Arbiter,
        tol: ToLDispatcher,
    ) -> None:
        if not agents:
            # TODO(pyraclaw-spec): confirm minimum cardinality.
            raise ValueError("iAiA requires at least one competing agent")
        self._agents = tuple(agents)
        self._arbiter = arbiter
        self._tol = tol

    async def run(self, request: Request) -> The_Truth:
        candidates = await self._fan_out(request)
        if not candidates:
            # TODO(pyraclaw-spec): surface vs. re-fan-out on zero candidates.
            raise RuntimeError(f"no candidates produced for {request.request_id}")
        winner = self._arbiter.select(candidates)
        truth = The_Truth(
            request_id=request.request_id,
            payload=winner.payload,
            producer=winner.producer,
            scores=winner.scores,
            sealed_at=datetime.now(timezone.utc),
        )
        await self._tol.dispatch(truth)
        return truth

    async def _fan_out(self, request: Request) -> list[Candidate]:
        tasks = [asyncio.create_task(a.produce(request)) for a in self._agents]
        done, pending = await asyncio.wait(tasks, timeout=request.deadline_seconds)
        for p in pending:
            p.cancel()
        candidates: list[Candidate] = []
        for t in done:
            try:
                candidates.append(t.result())
            except Exception:  # noqa: BLE001
                # A losing agent is allowed to crash; it just doesn't compete.
                continue
        return candidates


def cli() -> None:  # pragma: no cover
    """Entrypoint stub. TODO(pyraclaw-spec): real CLI surface."""
    raise SystemExit("rsfs_mode CLI not yet wired — see DESIGN.md §6")
