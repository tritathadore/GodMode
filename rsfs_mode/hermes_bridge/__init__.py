"""Adapter onto the hermes-agent dependency.

Kept deliberately thin so that swapping hermes versions is a one-file change.
Transport: subprocess fork of run_agent.py (see client.py).
"""
from .client import HermesClient, HermesResult

__all__ = ["HermesClient", "HermesResult"]
