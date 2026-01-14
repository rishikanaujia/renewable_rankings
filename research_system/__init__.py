"""Research System for Renewable Energy Parameter Analysis

A comprehensive system for generating, versioning, and storing LLM-powered
research documents for renewable energy investment parameters.
"""

from .src import (
    ResearchOrchestrator,
    ResearchAgent,
    ResearchStore,
    ResearchDocument,
    PromptGenerator,
    VersionManager,
    VersionStrategy,
    ChangeType,
)

__version__ = '1.0.0'

__all__ = [
    'ResearchOrchestrator',
    'ResearchAgent',
    'ResearchStore',
    'ResearchDocument',
    'PromptGenerator',
    'VersionManager',
    'VersionStrategy',
    'ChangeType',
]
