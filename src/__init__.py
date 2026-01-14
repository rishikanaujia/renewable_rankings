"""Memory and learning system for renewable energy rankings.

This module provides:
- Memory storage (ChromaDB-based)
- Learning from expert feedback
- Pattern recognition
- Similarity-based retrieval
- Agent integration via mixins

Quick start:
    from src.memory import MemoryManager, MemoryMixin
    
    # Initialize memory
    memory_manager = MemoryManager(config)
    
    # Add to agent
    class MyAgent(BaseAgent, MemoryMixin):
        def __init__(self, ...):
            BaseAgent.__init__(self, ...)
            MemoryMixin.init_memory(self, memory_manager)
"""
from memory_system.src.memory.base import (
    MemoryType,

    MemoryCategory,
    FeedbackType,
    ConfidenceLevel,
    RetrievalStrategy,
    LearningStrategy,
    MemoryMetadata,
    BaseMemoryEntry,
    EpisodicMemoryEntry,
    SemanticMemoryEntry,
    ProceduralMemoryEntry,
    FeedbackMemoryEntry,
    MemoryQuery,
    MemoryStore,
    MemoryStoreRegistry,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TOP_K_RETRIEVAL,
    DEFAULT_MEMORY_TTL_DAYS,
    DEFAULT_EMBEDDING_MODEL,
    MAX_CONTEXT_MEMORIES
)

# Store implementations


# Learning components

# Integration components
from memory_system.src.memory.integration import (
    MemoryManager,
    MemoryMixin,
    MemoryAwareAnalysisMixin
)

__version__ = '1.0.0'

__all__ = [
    # Types and Enums
    'MemoryType',
    'MemoryCategory',
    'FeedbackType',
    'ConfidenceLevel',
    'RetrievalStrategy',
    'LearningStrategy',

    # Constants
    'DEFAULT_SIMILARITY_THRESHOLD',
    'DEFAULT_TOP_K_RETRIEVAL',
    'DEFAULT_MEMORY_TTL_DAYS',
    'DEFAULT_EMBEDDING_MODEL',
    'MAX_CONTEXT_MEMORIES',

    # Memory Entries
    'MemoryMetadata',
    'BaseMemoryEntry',
    'EpisodicMemoryEntry',
    'SemanticMemoryEntry',
    'ProceduralMemoryEntry',
    'FeedbackMemoryEntry',
    'MemoryQuery',

    # Store
    'MemoryStore',
    'MemoryStoreRegistry',
    'ChromaDBMemoryStore',

    # Learning
    'SimilarityEngine',
    'FeedbackProcessor',
    'PatternRecognizer',

    # Integration
    'MemoryManager',
    'MemoryMixin',
    'MemoryAwareAnalysisMixin',
]

from memory_system.src.memory.learning import SimilarityEngine, PatternRecognizer, FeedbackProcessor

from memory_system.src.memory.stores import ChromaDBMemoryStore
