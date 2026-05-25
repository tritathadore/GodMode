"""The_Truth — the sealed, immutable deliverable.

Seal is HMAC-SHA256 over a canonical byte form of the truth's fields
(excluding the signature itself). Key is read from ``RSFS_TRUTH_KEY``.
TODO(pyraclaw-spec): confirm scheme — HMAC vs detached signature vs notarized.
"""
from __future__ import annotations

import dataclasses
import hashlib
import hmac
import json
import os
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Mapping

_KEY_ENV = "RSFS_TRUTH_KEY"


@dataclass(frozen=True)
class The_Truth:
    request_id: str
    payload: Any
    producer: str
    scores: Mapping[str, float]
    sealed_at: datetime
    signature: str


def _key() -> bytes:
    raw = os.environ.get(_KEY_ENV)
    if not raw:
        raise RuntimeError(
            f"{_KEY_ENV} is not set; The_Truth cannot be sealed. "
            "Set a strong shared secret before running iAiA."
        )
    return raw.encode("utf-8")


def _canonical(truth: The_Truth) -> bytes:
    body = {
        "request_id": truth.request_id,
        "payload": truth.payload,
        "producer": truth.producer,
        "scores": dict(sorted(truth.scores.items())),
        "sealed_at": truth.sealed_at.isoformat(),
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def seal(truth: The_Truth) -> The_Truth:
    """Return a new The_Truth with the signature field populated."""
    sig = hmac.new(_key(), _canonical(truth), hashlib.sha256).hexdigest()
    return replace(truth, signature=sig)


def verify(truth: The_Truth) -> bool:
    expected = hmac.new(_key(), _canonical(truth), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, truth.signature)
