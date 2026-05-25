"""The_Truth — the sealed, immutable deliverable."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True)
class The_Truth:
    request_id: str
    payload: Any
    producer: str
    scores: Mapping[str, float]
    sealed_at: datetime
    # TODO(pyraclaw-spec): cryptographic seal? signature scheme?
