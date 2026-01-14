"""Research System - LLM-powered parameter-country research with versioning

Main Components:
- ResearchOrchestrator: High-level API for research generation
- ResearchAgent: LLM-powered research conductor
- ResearchStore: Versioned document storage
- PromptGenerator: Parameter-specific prompt generation
- VersionManager: Semantic versioning for documents

Example Usage:
    >>> from research_system.src import ResearchOrchestrator
    >>>
    >>> orchestrator = ResearchOrchestrator()
    >>>
    >>> # Get research (from cache or generate new)
    >>> doc = orchestrator.get_research("Ambition", "Germany")
    >>> print(doc.content['overview'])
    >>>
    >>> # Batch generate for multiple countries
    >>> results = orchestrator.batch_generate_research(
    ...     parameters=["Ambition", "Country Stability"],
    ...     countries=["Germany", "Brazil", "India"]
    ... )
"""

from .research_orchestrator import ResearchOrchestrator
from .research_agent import ResearchAgent
from .storage.research_store import ResearchStore, ResearchDocument
from .prompt_generator import PromptGenerator
from .version_manager import VersionManager, VersionStrategy, ChangeType

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
