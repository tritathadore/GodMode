"""Contract every competing agent must satisfy.

Agents do not see each other and do not score themselves — separation of
producer and arbiter is load-bearing for the single-route-to-truth property.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from iaia.orchestrator import Request


class Scores(TypedDict):
    precision: float
    speed: float
    accuracy: float
    neatness: float


@dataclass(frozen=True)
class Candidate:
    producer: str
    payload: Any
    scores: Scores


class CompetingAgent(ABC):
    """Base class for any agent that wants to compete for The_Truth."""

    name: str

    @abstractmethod
    async def produce(self, request: "Request") -> Candidate:
        """Produce one candidate. May raise; raising == not competing this round."""
        raise NotImplementedError
