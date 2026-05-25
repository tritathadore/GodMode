"""Scoring rubric for HermesCompetingAgent.

Scoring lives in the wrapper, not inside hermes, and not inside the arbiter.
The arbiter only combines axes; each axis is computed here.

The default rubric is intentionally cheap: it uses signals available from
the subprocess result (exit code, wall time, stderr). Domain accuracy is the
one axis no generic rubric can supply — plug your own ``Rubric`` in for that.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from .base import Scores

if TYPE_CHECKING:
    from hermes_bridge.client import HermesResult
    from iaia.orchestrator import Request


class Rubric(Protocol):
    def score(self, request: "Request", result: "HermesResult") -> Scores: ...


class DefaultRubric:
    """Cheap, signal-based rubric. Replace ``accuracy`` for real domains."""

    def __init__(self, accuracy_floor: float = 0.5) -> None:
        self._accuracy_floor = accuracy_floor

    def score(self, request: "Request", result: "HermesResult") -> Scores:
        precision = 0.0 if result.timed_out or result.returncode != 0 else 1.0
        deadline = max(request.deadline_seconds, 1e-6)
        speed = max(0.0, 1.0 - min(result.wall_seconds / deadline, 1.0))
        neatness = 1.0 if not result.stderr.strip() else 0.5
        # accuracy: no generic signal. Caller should subclass / supply a real rubric.
        accuracy = self._accuracy_floor if precision > 0 else 0.0
        return Scores(
            precision=precision,
            speed=speed,
            accuracy=accuracy,
            neatness=neatness,
        )
