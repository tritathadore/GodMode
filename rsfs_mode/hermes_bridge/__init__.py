"""Adapter onto the hermes-agent dependency.

Kept deliberately thin so that swapping hermes versions is a one-file change.
"""
from .client import HermesClient

__all__ = ["HermesClient"]
