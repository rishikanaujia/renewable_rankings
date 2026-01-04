"""Abstract base class for memory storage backends."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from .memory_entry import (
    BaseMemoryEntry, MemoryQuery, EpisodicMemoryEntry,
    SemanticMemoryEntry, ProceduralMemoryEntry, FeedbackMemoryEntry
)
from .memory_types import MemoryType


class MemoryStore(ABC):
    """Abstract base class for memory storage implementations.
    
    This allows multiple backends (ChromaDB, PostgreSQL, Redis, etc.)
    while maintaining consistent interface.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize memory store.
        
        Args:
            config: Configuration dictionary for the store
        """
        self.config = config
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage backend.
        
        Called once before first use. Creates collections,
        connections, schemas, etc.
        """
        pass
    
    @abstractmethod
    def store(self, entry: BaseMemoryEntry) -> str:
        """Store a memory entry.
        
        Args:
            entry: Memory entry to store
            
        Returns:
            ID of stored memory entry
        """
        pass
    
    @abstractmethod
    def retrieve(self, memory_id: str) -> Optional[BaseMemoryEntry]:
        """Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of memory to retrieve
            
        Returns:
            Memory entry if found, None otherwise
        """
        pass
    
    @abstractmethod
    def search(self, query: MemoryQuery) -> List[BaseMemoryEntry]:
        """Search for memories matching query.
        
        Args:
            query: Search query with filters and settings
            
        Returns:
            List of matching memory entries, ordered by relevance
        """
        pass
    
    @abstractmethod
    def search_similar(
        self, 
        embedding: List[float], 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[tuple[BaseMemoryEntry, float]]:
        """Search for similar memories using vector similarity.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        pass
    
    @abstractmethod
    def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry.
        
        Args:
            memory_id: ID of memory to update
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry.
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_expired(self) -> int:
        """Delete all expired memories.
        
        Returns:
            Number of memories deleted
        """
        pass
    
    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count memories matching filters.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Count of matching memories
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored memories.
        
        Returns:
            Dictionary with statistics (counts by type, total size, etc.)
        """
        pass
    
    @abstractmethod
    def clear_all(self) -> bool:
        """Clear all memories from storage.
        
        WARNING: This is destructive!
        
        Returns:
            True if cleared successfully, False otherwise
        """
        pass
    
    def ensure_initialized(self):
        """Ensure store is initialized before use."""
        if not self._initialized:
            self.initialize()
            self._initialized = True
    
    def store_batch(self, entries: List[BaseMemoryEntry]) -> List[str]:
        """Store multiple memory entries.
        
        Default implementation stores one at a time.
        Subclasses can override for batch optimization.
        
        Args:
            entries: List of memory entries to store
            
        Returns:
            List of stored memory IDs
        """
        self.ensure_initialized()
        return [self.store(entry) for entry in entries]
    
    def retrieve_batch(self, memory_ids: List[str]) -> List[Optional[BaseMemoryEntry]]:
        """Retrieve multiple memories by ID.
        
        Default implementation retrieves one at a time.
        Subclasses can override for batch optimization.
        
        Args:
            memory_ids: List of memory IDs to retrieve
            
        Returns:
            List of memory entries (None for not found)
        """
        self.ensure_initialized()
        return [self.retrieve(mid) for mid in memory_ids]
    
    def get_memory_by_type(self, memory_type: MemoryType) -> List[BaseMemoryEntry]:
        """Get all memories of a specific type.
        
        Args:
            memory_type: Type of memories to retrieve
            
        Returns:
            List of memory entries
        """
        self.ensure_initialized()
        query = MemoryQuery(memory_types=[memory_type])
        return self.search(query)
    
    def get_recent_memories(
        self, 
        limit: int = 10,
        memory_types: Optional[List[MemoryType]] = None
    ) -> List[BaseMemoryEntry]:
        """Get most recent memories.
        
        Args:
            limit: Maximum number of memories to return
            memory_types: Optional filter by memory types
            
        Returns:
            List of recent memory entries
        """
        self.ensure_initialized()
        query = MemoryQuery(
            memory_types=memory_types,
            top_k=limit
        )
        return self.search(query)


class MemoryStoreRegistry:
    """Registry for memory store implementations."""
    
    _stores: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, store_class: type):
        """Register a memory store implementation.
        
        Args:
            name: Name to register under
            store_class: Memory store class
        """
        cls._stores[name] = store_class
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Get a registered memory store class.
        
        Args:
            name: Name of store to get
            
        Returns:
            Memory store class if found, None otherwise
        """
        return cls._stores.get(name)
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> MemoryStore:
        """Create a memory store instance.
        
        Args:
            name: Name of store to create
            config: Configuration for the store
            
        Returns:
            Memory store instance
            
        Raises:
            ValueError: If store not registered
        """
        store_class = cls.get(name)
        if not store_class:
            raise ValueError(f"Memory store '{name}' not registered")
        return store_class(config)
    
    @classmethod
    def list_stores(cls) -> List[str]:
        """List all registered store names.
        
        Returns:
            List of store names
        """
        return list(cls._stores.keys())
