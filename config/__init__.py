"""Configuration package for TripGenie"""
from .settings import settings
from .prompts import SYSTEM_PROMPT, TRIP_PLANNING_GUIDELINES

__all__ = ['settings', 'SYSTEM_PROMPT', 'TRIP_PLANNING_GUIDELINES']
