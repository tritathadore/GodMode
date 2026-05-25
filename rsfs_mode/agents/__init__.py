"""Competing subordinate agents."""
from .base import Candidate, CompetingAgent, Scores
from .hermes_agent import HermesCompetingAgent
from .rubric import DefaultRubric, Rubric

__all__ = [
    "Candidate",
    "CompetingAgent",
    "DefaultRubric",
    "HermesCompetingAgent",
    "Rubric",
    "Scores",
]
