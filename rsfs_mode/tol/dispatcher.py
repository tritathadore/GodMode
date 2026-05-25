"""Hand sealed The_Truth to ToL for refinement, documentation, analysis, and
external dissemination.

Transport: in-process function call. ToL is a Python object injected into
iAiA at construction time. Real refinement/documentation/publication sinks
plug in by implementing ``ToLDispatcher`` and composing.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence

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


class FanOutToL(ToLDispatcher):
    """Compose multiple downstream sinks (refine + document + publish).

    Each sink is awaited in order. If one raises, the remaining sinks still
    run; aggregated errors are re-raised at the end so iAiA does not get a
    silent partial dispatch.
    """

    def __init__(self, sinks: Sequence[ToLDispatcher]) -> None:
        self._sinks = tuple(sinks)

    async def dispatch(self, truth: "The_Truth") -> None:
        errors: list[BaseException] = []
        for sink in self._sinks:
            try:
                await sink.dispatch(truth)
            except BaseException as e:  # noqa: BLE001
                errors.append(e)
        if errors:
            raise ExceptionGroup("ToL fan-out had failures", errors)
