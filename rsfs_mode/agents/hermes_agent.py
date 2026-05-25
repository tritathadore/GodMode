"""A competing agent backed by a hermes-agent subprocess.

One ``HermesCompetingAgent`` instance == one persona in the competition. Use
different ``name`` + ``extra_args`` (model flag, tool budget, system prompt)
to stand up a pool of differentiated competitors against the same prompt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from hermes_bridge.client import HermesClient

from .base import Candidate, CompetingAgent
from .rubric import DefaultRubric, Rubric

if TYPE_CHECKING:
    from iaia.orchestrator import Request


@dataclass
class HermesCompetingAgent(CompetingAgent):
    name: str
    client: HermesClient = field(default_factory=HermesClient)
    rubric: Rubric = field(default_factory=DefaultRubric)
    tool_budget: int | None = None

    async def produce(self, request: "Request") -> Candidate:
        # Prompt is whatever the caller put in request.payload. iAiA does not
        # transform it — transformation would create a second route to truth.
        result = await self.client.invoke(
            prompt=str(request.payload),
            deadline_seconds=request.deadline_seconds,
            tool_budget=self.tool_budget,
        )
        if result.timed_out:
            # Raising == not competing this round. Honest failure beats a low score.
            raise TimeoutError(f"{self.name} hit deadline at {result.wall_seconds:.2f}s")
        scores = self.rubric.score(request, result)
        return Candidate(
            producer=self.name,
            payload=result.stdout,
            scores=scores,
        )
