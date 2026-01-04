"""Base memory entry models for the memory system."""
from abc import ABC
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from uuid import uuid4

from .memory_types import (
    MemoryType, MemoryCategory, FeedbackType, 
    ConfidenceLevel, RetrievalStrategy
)


@dataclass
class MemoryMetadata:
    """Metadata for memory entries."""
    source: str  # Who/what created this memory
    confidence: float = 1.0  # Confidence in this memory (0-1)
    access_count: int = 0  # Times accessed
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    version: int = 1  # For tracking updates
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source': self.source,
            'confidence': self.confidence,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'tags': self.tags,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryMetadata':
        """Create from dictionary."""
        if data.get('last_accessed'):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)


@dataclass
class BaseMemoryEntry(ABC):
    """Abstract base class for all memory entries."""
    id: str = field(default_factory=lambda: str(uuid4()))
    memory_type: MemoryType = MemoryType.EPISODIC
    category: MemoryCategory = MemoryCategory.COUNTRY_ANALYSIS
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: MemoryMetadata = field(default_factory=lambda: MemoryMetadata(source="system"))
    
    # Core content (specific to memory type)
    content: Dict[str, Any] = field(default_factory=dict)
    
    # Embedding for similarity search
    embedding: Optional[List[float]] = None
    
    # Relationships to other memories
    related_memory_ids: List[str] = field(default_factory=list)
    parent_memory_id: Optional[str] = None
    
    # Temporal information
    ttl_days: Optional[int] = None  # Time-to-live
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary."""
        return {
            'id': self.id,
            'memory_type': self.memory_type.value,
            'category': self.category.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata.to_dict(),
            'content': self.content,
            'embedding': self.embedding,
            'related_memory_ids': self.related_memory_ids,
            'parent_memory_id': self.parent_memory_id,
            'ttl_days': self.ttl_days,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseMemoryEntry':
        """Create memory entry from dictionary."""
        data['memory_type'] = MemoryType(data['memory_type'])
        data['category'] = MemoryCategory(data['category'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['metadata'] = MemoryMetadata.from_dict(data['metadata'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if memory has expired."""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    def update_access(self):
        """Update access statistics."""
        self.metadata.access_count += 1
        self.metadata.last_accessed = datetime.now()


@dataclass
class EpisodicMemoryEntry(BaseMemoryEntry):
    """Memory of a specific analysis session or event."""
    
    def __init__(
        self,
        agent_name: str,
        country: str,
        period: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            memory_type=MemoryType.EPISODIC,
            **kwargs
        )
        self.content = {
            'agent_name': agent_name,
            'country': country,
            'period': period,
            'input_data': input_data,
            'output_data': output_data,
            'execution_time_ms': execution_time_ms,
            'success': success,
            'error_message': error_message
        }


@dataclass
class SemanticMemoryEntry(BaseMemoryEntry):
    """Memory of facts and knowledge about countries/markets."""
    
    def __init__(
        self,
        subject: str,  # Country, region, or market
        fact_type: str,  # e.g., "policy", "infrastructure", "market_condition"
        fact_content: str,
        source: str,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        **kwargs
    ):
        super().__init__(
            memory_type=MemoryType.SEMANTIC,
            category=MemoryCategory.MARKET_KNOWLEDGE,
            **kwargs
        )
        self.content = {
            'subject': subject,
            'fact_type': fact_type,
            'fact_content': fact_content,
            'source': source,
            'valid_from': valid_from.isoformat() if valid_from else None,
            'valid_until': valid_until.isoformat() if valid_until else None
        }


@dataclass
class ProceduralMemoryEntry(BaseMemoryEntry):
    """Memory of reasoning patterns and strategies."""
    
    def __init__(
        self,
        pattern_name: str,
        pattern_type: str,  # e.g., "scoring_strategy", "weighting_rule"
        context: Dict[str, Any],  # When this pattern applies
        action: Dict[str, Any],  # What to do
        outcome: Optional[Dict[str, Any]] = None,  # Historical outcome
        confidence_score: float = 0.5,
        **kwargs
    ):
        super().__init__(
            memory_type=MemoryType.PROCEDURAL,
            category=MemoryCategory.SCORING_PATTERN,
            **kwargs
        )
        self.content = {
            'pattern_name': pattern_name,
            'pattern_type': pattern_type,
            'context': context,
            'action': action,
            'outcome': outcome,
            'confidence_score': confidence_score
        }


@dataclass
class FeedbackMemoryEntry(BaseMemoryEntry):
    """Memory of expert feedback and corrections."""
    
    def __init__(
        self,
        feedback_type: FeedbackType,
        original_analysis_id: str,
        expert_id: str,
        original_value: Any,
        corrected_value: Any,
        reasoning: str,
        impact_scope: str = "specific",  # specific, category, global
        **kwargs
    ):
        super().__init__(
            memory_type=MemoryType.FEEDBACK,
            category=MemoryCategory.USER_CORRECTION,
            **kwargs
        )
        self.content = {
            'feedback_type': feedback_type.value,
            'original_analysis_id': original_analysis_id,
            'expert_id': expert_id,
            'original_value': original_value,
            'corrected_value': corrected_value,
            'reasoning': reasoning,
            'impact_scope': impact_scope
        }


@dataclass
class MemoryQuery:
    """Query for retrieving memories."""
    query_text: Optional[str] = None
    query_embedding: Optional[List[float]] = None
    
    # Filters
    memory_types: Optional[List[MemoryType]] = None
    categories: Optional[List[MemoryCategory]] = None
    countries: Optional[List[str]] = None
    agents: Optional[List[str]] = None
    time_range: Optional[tuple[datetime, datetime]] = None
    
    # Retrieval settings
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    top_k: int = 5
    similarity_threshold: float = 0.75
    include_expired: bool = False
    
    # Metadata filters
    min_confidence: float = 0.0
    min_access_count: int = 0
    tags: Optional[List[str]] = None
    
    def to_filter_dict(self) -> Dict[str, Any]:
        """Convert query to filter dictionary for storage backends."""
        filters = {}
        
        if self.memory_types:
            filters['memory_type'] = {'$in': [mt.value for mt in self.memory_types]}
        
        if self.categories:
            filters['category'] = {'$in': [c.value for c in self.categories]}
        
        if self.countries:
            filters['content.country'] = {'$in': self.countries}
        
        if self.agents:
            filters['content.agent_name'] = {'$in': self.agents}
        
        if self.time_range:
            start, end = self.time_range
            filters['timestamp'] = {
                '$gte': start.isoformat(),
                '$lte': end.isoformat()
            }
        
        if not self.include_expired:
            filters['$or'] = [
                {'expires_at': None},
                {'expires_at': {'$gt': datetime.now().isoformat()}}
            ]
        
        return filters
