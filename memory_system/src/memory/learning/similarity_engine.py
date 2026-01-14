"""Similarity engine for finding similar past cases."""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from src.core.logger import get_logger

from ..base.memory_store import MemoryStore
from ..base.memory_entry import (
    BaseMemoryEntry, MemoryQuery, EpisodicMemoryEntry
)
from ..base.memory_types import (
    MemoryType, MemoryCategory, RetrievalStrategy,
    ConfidenceLevel, DEFAULT_EMBEDDING_MODEL
)

logger = get_logger(__name__)


class SimilarityEngine:
    """Engine for finding similar memories and cases.
    
    Uses multiple strategies to find relevant past experiences:
    - Vector similarity (semantic)
    - Structural similarity (matching attributes)
    - Temporal proximity
    - Frequency of access
    """
    
    def __init__(
        self,
        memory_store: MemoryStore,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize similarity engine.
        
        Args:
            memory_store: Memory store to search
            embedding_model: Sentence transformer model for embeddings
            config: Optional configuration
        """
        self.memory_store = memory_store
        self.config = config or {}
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}. Embeddings disabled.")
            self.embedding_model = None
    
    def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if model not available
        """
        if not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def find_similar_analyses(
        self,
        country: str,
        parameter: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Find similar past analyses for a country.
        
        Args:
            country: Country to find analyses for
            parameter: Optional specific parameter
            context: Optional context for similarity matching
            top_k: Number of results to return
            strategy: Retrieval strategy to use
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        if strategy == RetrievalStrategy.SIMILARITY:
            return self._find_by_similarity(country, parameter, context, top_k)
        elif strategy == RetrievalStrategy.TEMPORAL:
            return self._find_by_recency(country, parameter, top_k)
        elif strategy == RetrievalStrategy.FREQUENCY:
            return self._find_by_frequency(country, parameter, top_k)
        elif strategy == RetrievalStrategy.HYBRID:
            return self._find_by_hybrid(country, parameter, context, top_k)
        else:
            return self._find_by_relevance(country, parameter, context, top_k)
    
    def _find_by_similarity(
        self,
        country: str,
        parameter: Optional[str],
        context: Optional[Dict[str, Any]],
        top_k: int
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Find by vector similarity."""
        # Create query text from context
        query_text = f"Country: {country}"
        if parameter:
            query_text += f", Parameter: {parameter}"
        if context:
            query_text += f", Context: {str(context)}"
        
        # Generate embedding
        embedding = self.embed_text(query_text)
        if not embedding:
            logger.warning("Embedding not available, falling back to structural matching")
            return self._find_by_structure(country, parameter, top_k)
        
        # Search by embedding
        results = self.memory_store.search_similar(
            embedding=embedding,
            top_k=top_k,
            filters={'memory_type': MemoryType.EPISODIC.value}
        )
        
        return [(mem, score) for mem, score in results if isinstance(mem, EpisodicMemoryEntry)]
    
    def _find_by_structure(
        self,
        country: str,
        parameter: Optional[str],
        top_k: int
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Find by structural similarity (matching attributes)."""
        query = MemoryQuery(
            memory_types=[MemoryType.EPISODIC],
            countries=[country],
            top_k=top_k * 2  # Get more to filter
        )
        
        memories = self.memory_store.search(query)
        
        # Calculate structural similarity scores
        results = []
        for memory in memories:
            if not isinstance(memory, EpisodicMemoryEntry):
                continue
            
            score = 0.0
            
            # Country match (base score)
            if memory.content.get('country') == country:
                score += 0.4
            
            # Parameter match
            if parameter and memory.content.get('agent_name', '').lower().find(parameter.lower()) >= 0:
                score += 0.3
            
            # Success match (prefer successful analyses)
            if memory.content.get('success', False):
                score += 0.2
            
            # Recency bonus
            days_old = (datetime.now() - memory.timestamp).days
            if days_old < 30:
                score += 0.1
            elif days_old < 90:
                score += 0.05
            
            results.append((memory, score))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _find_by_recency(
        self,
        country: str,
        parameter: Optional[str],
        top_k: int
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Find most recent analyses."""
        query = MemoryQuery(
            memory_types=[MemoryType.EPISODIC],
            countries=[country],
            top_k=top_k
        )
        
        memories = self.memory_store.search(query)
        
        # Score by recency
        results = []
        for memory in memories:
            if not isinstance(memory, EpisodicMemoryEntry):
                continue
            
            days_old = (datetime.now() - memory.timestamp).days
            # Exponential decay: score = e^(-days/30)
            import math
            score = math.exp(-days_old / 30)
            
            results.append((memory, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _find_by_frequency(
        self,
        country: str,
        parameter: Optional[str],
        top_k: int
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Find most frequently accessed analyses."""
        query = MemoryQuery(
            memory_types=[MemoryType.EPISODIC],
            countries=[country],
            top_k=top_k * 2
        )
        
        memories = self.memory_store.search(query)
        
        # Score by access count
        results = []
        max_access = max([m.metadata.access_count for m in memories]) if memories else 1
        
        for memory in memories:
            if not isinstance(memory, EpisodicMemoryEntry):
                continue
            
            # Normalize access count to 0-1
            score = memory.metadata.access_count / max_access if max_access > 0 else 0
            
            results.append((memory, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _find_by_hybrid(
        self,
        country: str,
        parameter: Optional[str],
        context: Optional[Dict[str, Any]],
        top_k: int
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Find using hybrid approach (combines multiple strategies)."""
        # Get candidates from different strategies
        similarity_results = self._find_by_similarity(country, parameter, context, top_k)
        recency_results = self._find_by_recency(country, parameter, top_k)
        frequency_results = self._find_by_frequency(country, parameter, top_k)
        
        # Combine scores with weights
        weights = {
            'similarity': 0.5,
            'recency': 0.3,
            'frequency': 0.2
        }
        
        # Build score map
        score_map: Dict[str, float] = {}
        
        for memory, score in similarity_results:
            score_map[memory.id] = score_map.get(memory.id, 0) + score * weights['similarity']
        
        for memory, score in recency_results:
            score_map[memory.id] = score_map.get(memory.id, 0) + score * weights['recency']
        
        for memory, score in frequency_results:
            score_map[memory.id] = score_map.get(memory.id, 0) + score * weights['frequency']
        
        # Get unique memories
        memory_map = {}
        for memory, _ in similarity_results + recency_results + frequency_results:
            memory_map[memory.id] = memory
        
        # Build final results
        results = [(memory_map[mem_id], score) for mem_id, score in score_map.items()]
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def _find_by_relevance(
        self,
        country: str,
        parameter: Optional[str],
        context: Optional[Dict[str, Any]],
        top_k: int
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Find by custom relevance scoring."""
        # Start with structural matching
        results = self._find_by_structure(country, parameter, top_k * 2)
        
        # Enhance with context matching if available
        if context:
            enhanced_results = []
            for memory, base_score in results:
                # Check context overlap
                context_match = 0.0
                mem_input = memory.content.get('input_data', {})
                
                for key, value in context.items():
                    if key in mem_input and mem_input[key] == value:
                        context_match += 1
                
                if context:
                    context_score = context_match / len(context)
                else:
                    context_score = 0
                
                # Combine scores
                final_score = base_score * 0.7 + context_score * 0.3
                enhanced_results.append((memory, final_score))
            
            enhanced_results.sort(key=lambda x: x[1], reverse=True)
            return enhanced_results[:top_k]
        
        return results[:top_k]
    
    def calculate_confidence(
        self,
        similar_memories: List[Tuple[BaseMemoryEntry, float]]
    ) -> ConfidenceLevel:
        """Calculate confidence level based on similar memories.
        
        Args:
            similar_memories: List of (memory, similarity_score) tuples
            
        Returns:
            Confidence level
        """
        if not similar_memories:
            return ConfidenceLevel.NONE
        
        # Average similarity score
        avg_similarity = sum(score for _, score in similar_memories) / len(similar_memories)
        
        if avg_similarity >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif avg_similarity >= 0.7:
            return ConfidenceLevel.HIGH
        elif avg_similarity >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif avg_similarity >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def get_common_patterns(
        self,
        memories: List[BaseMemoryEntry],
        min_frequency: int = 3
    ) -> List[Dict[str, Any]]:
        """Extract common patterns from a set of memories.
        
        Args:
            memories: List of memories to analyze
            min_frequency: Minimum times a pattern must appear
            
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        
        # Group by common attributes
        attribute_counts: Dict[str, Dict[Any, int]] = {}
        
        for memory in memories:
            if isinstance(memory, EpisodicMemoryEntry):
                # Track output patterns
                output = memory.content.get('output_data', {})
                
                for key, value in output.items():
                    if key not in attribute_counts:
                        attribute_counts[key] = {}
                    
                    # Convert to hashable type
                    val_str = str(value)
                    attribute_counts[key][val_str] = attribute_counts[key].get(val_str, 0) + 1
        
        # Extract frequent patterns
        for attribute, value_counts in attribute_counts.items():
            for value, count in value_counts.items():
                if count >= min_frequency:
                    patterns.append({
                        'attribute': attribute,
                        'value': value,
                        'frequency': count,
                        'confidence': count / len(memories)
                    })
        
        patterns.sort(key=lambda x: x['confidence'], reverse=True)
        return patterns
