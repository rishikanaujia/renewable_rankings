"""Memory manager for high-level memory orchestration."""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from src.core.logger import get_logger

from ..base.memory_store import MemoryStore, MemoryStoreRegistry
from ..base.memory_entry import (
    EpisodicMemoryEntry, SemanticMemoryEntry,
    ProceduralMemoryEntry, FeedbackMemoryEntry,
    MemoryQuery, MemoryMetadata
)
from ..base.memory_types import (
    MemoryType, MemoryCategory, FeedbackType,
    RetrievalStrategy, LearningStrategy,
    DEFAULT_SIMILARITY_THRESHOLD, DEFAULT_TOP_K_RETRIEVAL
)
from ..learning.similarity_engine import SimilarityEngine
from ..learning.feedback_processor import FeedbackProcessor
from ..learning.pattern_recognizer import PatternRecognizer

logger = get_logger(__name__)


class MemoryManager:
    """High-level memory system manager.
    
    Coordinates all memory operations:
    - Storage and retrieval
    - Similarity search
    - Feedback processing
    - Pattern recognition
    - Learning from experience
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize memory manager.
        
        Args:
            config: Configuration dictionary with:
                - store_type: Type of memory store (default: 'chromadb')
                - store_config: Configuration for the store
                - learning_config: Configuration for learning
                - enabled: Whether memory is enabled (default: True)
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        
        if not self.enabled:
            logger.info("Memory system disabled by configuration")
            self.memory_store = None
            self.similarity_engine = None
            self.feedback_processor = None
            self.pattern_recognizer = None
            return
        
        # Initialize memory store
        store_type = self.config.get('store_type', 'chromadb')
        store_config = self.config.get('store_config', {})
        
        try:
            self.memory_store = MemoryStoreRegistry.create(store_type, store_config)
            self.memory_store.initialize()
            logger.info(f"Memory manager initialized with {store_type} store")
        except Exception as e:
            logger.error(f"Failed to initialize memory store: {e}")
            self.enabled = False
            return
        
        # Initialize learning components
        learning_config = self.config.get('learning_config', {})
        
        self.similarity_engine = SimilarityEngine(
            memory_store=self.memory_store,
            config=learning_config
        )
        
        self.feedback_processor = FeedbackProcessor(
            memory_store=self.memory_store,
            config=learning_config
        )
        
        self.pattern_recognizer = PatternRecognizer(
            memory_store=self.memory_store,
            config=learning_config
        )
    
    def is_enabled(self) -> bool:
        """Check if memory system is enabled."""
        return self.enabled
    
    # --- Episodic Memory Operations ---
    
    def record_analysis(
        self,
        agent_name: str,
        country: str,
        period: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
        embedding_text: Optional[str] = None
    ) -> Optional[str]:
        """Record an analysis session.
        
        Args:
            agent_name: Name of agent that performed analysis
            country: Country analyzed
            period: Time period
            input_data: Input data used
            output_data: Analysis output
            execution_time_ms: Execution time in milliseconds
            success: Whether analysis succeeded
            error_message: Error message if failed
            embedding_text: Optional text for embedding generation
            
        Returns:
            Memory ID if recorded, None if memory disabled
        """
        if not self.enabled:
            return None
        
        try:
            # Create episodic memory
            memory = EpisodicMemoryEntry(
                agent_name=agent_name,
                country=country,
                period=period,
                input_data=input_data,
                output_data=output_data,
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message,
                category=MemoryCategory.PARAMETER_ANALYSIS,
                metadata=MemoryMetadata(source=f"agent:{agent_name}")
            )
            
            # Generate embedding if text provided
            if embedding_text and self.similarity_engine:
                memory.embedding = self.similarity_engine.embed_text(embedding_text)
            
            # Store memory
            memory_id = self.memory_store.store(memory)
            logger.debug(f"Recorded analysis memory for {country} by {agent_name}")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to record analysis: {e}")
            return None
    
    def get_similar_analyses(
        self,
        country: str,
        agent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = DEFAULT_TOP_K_RETRIEVAL,
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Get similar past analyses.
        
        Args:
            country: Country to find analyses for
            agent: Optional agent filter
            context: Optional context for similarity
            top_k: Number of results
            strategy: Retrieval strategy
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        if not self.enabled or not self.similarity_engine:
            return []
        
        try:
            return self.similarity_engine.find_similar_analyses(
                country=country,
                parameter=agent,
                context=context,
                top_k=top_k,
                strategy=strategy
            )
        except Exception as e:
            logger.error(f"Failed to find similar analyses: {e}")
            return []
    
    # --- Semantic Memory Operations ---
    
    def record_knowledge(
        self,
        subject: str,
        fact_type: str,
        fact_content: str,
        source: str,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        embedding_text: Optional[str] = None
    ) -> Optional[str]:
        """Record a piece of knowledge about a country/market.
        
        Args:
            subject: Subject of knowledge (country, region, etc.)
            fact_type: Type of fact (policy, infrastructure, etc.)
            fact_content: The actual knowledge
            source: Source of knowledge
            valid_from: When this became valid
            valid_until: When this expires
            embedding_text: Optional text for embedding
            
        Returns:
            Memory ID if recorded, None if memory disabled
        """
        if not self.enabled:
            return None
        
        try:
            memory = SemanticMemoryEntry(
                subject=subject,
                fact_type=fact_type,
                fact_content=fact_content,
                source=source,
                valid_from=valid_from,
                valid_until=valid_until,
                metadata=MemoryMetadata(source=source)
            )
            
            # Generate embedding
            if embedding_text and self.similarity_engine:
                memory.embedding = self.similarity_engine.embed_text(embedding_text)
            elif self.similarity_engine:
                memory.embedding = self.similarity_engine.embed_text(fact_content)
            
            memory_id = self.memory_store.store(memory)
            logger.debug(f"Recorded knowledge about {subject}")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to record knowledge: {e}")
            return None
    
    def get_knowledge_about(
        self,
        subject: str,
        fact_type: Optional[str] = None,
        top_k: int = DEFAULT_TOP_K_RETRIEVAL
    ) -> List[SemanticMemoryEntry]:
        """Get knowledge about a subject.
        
        Args:
            subject: Subject to query
            fact_type: Optional fact type filter
            top_k: Number of results
            
        Returns:
            List of semantic memories
        """
        if not self.enabled:
            return []
        
        try:
            query = MemoryQuery(
                memory_types=[MemoryType.SEMANTIC],
                top_k=top_k
            )
            
            # Note: Would need to add subject filtering to MemoryQuery
            # For now, search and filter
            memories = self.memory_store.search(query)
            
            results = [
                m for m in memories
                if isinstance(m, SemanticMemoryEntry) and
                m.content.get('subject') == subject and
                (not fact_type or m.content.get('fact_type') == fact_type)
            ]
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to get knowledge: {e}")
            return []
    
    # --- Feedback Operations ---
    
    def record_feedback(
        self,
        feedback_type: FeedbackType,
        original_analysis_id: str,
        expert_id: str,
        original_value: Any,
        corrected_value: Any,
        reasoning: str,
        impact_scope: str = "specific"
    ) -> Optional[str]:
        """Record expert feedback.
        
        Args:
            feedback_type: Type of feedback
            original_analysis_id: ID of original analysis
            expert_id: ID of expert
            original_value: Original value
            corrected_value: Corrected value
            reasoning: Expert reasoning
            impact_scope: Scope of impact
            
        Returns:
            Feedback memory ID if recorded
        """
        if not self.enabled or not self.feedback_processor:
            return None
        
        try:
            return self.feedback_processor.record_feedback(
                feedback_type=feedback_type,
                original_analysis_id=original_analysis_id,
                expert_id=expert_id,
                original_value=original_value,
                corrected_value=corrected_value,
                reasoning=reasoning,
                impact_scope=impact_scope
            )
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return None
    
    def get_feedback_statistics(
        self,
        country: Optional[str] = None,
        agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get feedback statistics.
        
        Args:
            country: Optional country filter
            agent: Optional agent filter
            
        Returns:
            Statistics dictionary
        """
        if not self.enabled or not self.feedback_processor:
            return {}
        
        try:
            return self.feedback_processor.get_feedback_statistics(
                country=country,
                agent=agent
            )
        except Exception as e:
            logger.error(f"Failed to get feedback statistics: {e}")
            return {}
    
    def suggest_score_adjustment(
        self,
        country: str,
        parameter: str,
        current_score: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get score adjustment suggestion based on feedback.
        
        Args:
            country: Country being analyzed
            parameter: Parameter being scored
            current_score: Current score
            context: Optional context
            
        Returns:
            Adjustment suggestion or None
        """
        if not self.enabled or not self.feedback_processor:
            return None
        
        try:
            return self.feedback_processor.suggest_score_adjustment(
                country=country,
                parameter=parameter,
                current_score=current_score,
                context=context
            )
        except Exception as e:
            logger.error(f"Failed to suggest adjustment: {e}")
            return None
    
    # --- Pattern Recognition ---
    
    def recognize_patterns(
        self,
        pattern_type: str = "scoring",
        country: Optional[str] = None,
        agent: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Recognize patterns from historical data.
        
        Args:
            pattern_type: Type of pattern (scoring/reasoning)
            country: Optional country filter
            agent: Optional agent filter
            
        Returns:
            List of recognized patterns
        """
        if not self.enabled or not self.pattern_recognizer:
            return []
        
        try:
            if pattern_type == "scoring":
                return self.pattern_recognizer.recognize_scoring_patterns(
                    country=country,
                    parameter=agent
                )
            elif pattern_type == "reasoning":
                return self.pattern_recognizer.recognize_reasoning_patterns(
                    agent=agent,
                    country=country
                )
            else:
                logger.warning(f"Unknown pattern type: {pattern_type}")
                return []
        except Exception as e:
            logger.error(f"Failed to recognize patterns: {e}")
            return []
    
    # --- Learning ---
    
    def learn_from_feedback(
        self,
        current_config: Dict[str, Any],
        strategy: LearningStrategy = LearningStrategy.WEIGHT_ADAPTATION
    ) -> Dict[str, Any]:
        """Learn from feedback to update configuration.
        
        Args:
            current_config: Current configuration
            strategy: Learning strategy
            
        Returns:
            Updated configuration
        """
        if not self.enabled or not self.feedback_processor:
            return current_config
        
        try:
            return self.feedback_processor.apply_feedback_to_config(
                current_config=current_config,
                learning_strategy=strategy
            )
        except Exception as e:
            logger.error(f"Failed to learn from feedback: {e}")
            return current_config
    
    # --- Utility Operations ---
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get overall memory statistics."""
        if not self.enabled or not self.memory_store:
            return {'enabled': False}
        
        try:
            stats = self.memory_store.get_statistics()
            stats['enabled'] = True
            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'enabled': True, 'error': str(e)}
    
    def cleanup_expired_memories(self) -> int:
        """Clean up expired memories.
        
        Returns:
            Number of memories deleted
        """
        if not self.enabled or not self.memory_store:
            return 0
        
        try:
            return self.memory_store.delete_expired()
        except Exception as e:
            logger.error(f"Failed to cleanup memories: {e}")
            return 0
    
    def clear_all_memories(self) -> bool:
        """Clear all memories (WARNING: destructive!).
        
        Returns:
            True if successful
        """
        if not self.enabled or not self.memory_store:
            return False
        
        logger.warning("Clearing all memories - this is destructive!")
        
        try:
            return self.memory_store.clear_all()
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            return False
