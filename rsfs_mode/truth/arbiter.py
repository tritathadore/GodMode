"""Deterministic, stateless selection of The_Truth.

The arbiter is the only component allowed to pick a winner. iAiA never inlines
selection logic, agents never self-score — this is the chokepoint.

Scoring is a fixed-weight linear combination of the four axes. Ties resolve
by fan-out arrival order: the earliest-submitted candidate wins (Python's
sort is stable, so the order in the input sequence is preserved).
"""
from __future__ import annotations

from typing import Sequence

from agents.base import Candidate

_WEIGHTS = {
    "precision": 0.40,
    "accuracy": 0.30,
    "speed": 0.15,
    "neatness": 0.15,
}
assert abs(sum(_WEIGHTS.values()) - 1.0) < 1e-9


class Arbiter:
    def select(self, candidates: Sequence[Candidate]) -> Candidate:
        if not candidates:
            raise ValueError("arbiter received zero candidates")
        scored = [(self._score(c), c) for c in candidates]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[0][1]

    @staticmethod
    def _score(c: Candidate) -> float:
        return sum(_WEIGHTS[k] * float(c.scores.get(k, 0.0)) for k in _WEIGHTS)
