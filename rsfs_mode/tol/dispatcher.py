"""Hand sealed The_Truth to ToL for refinement, documentation, analysis, and
external dissemination.

The dispatcher is intentionally an interface: ToL's real transport (in-proc,
HTTP, queue) is `TODO(pyraclaw-spec)`. The in-memory implementation here is
for local development and tests only.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from truth.models import The_Truth


class ToLDispatcher(ABC):
    @abstractmethod
    async def dispatch(self, truth: "The_Truth") -> None:
        raise NotImplementedError


class InMemoryToL(ToLDispatcher):
    """Dev/test sink. Captures every sealed truth in order."""

    def __init__(self) -> None:
        self.received: list["The_Truth"] = []

    async def dispatch(self, truth: "The_Truth") -> None:
        self.received.append(truth)
