"""Memory mixin for adding memory capabilities to agents."""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from src.base.memory_entry import EpisodicMemoryEntry
from src.base.memory_types import (
    FeedbackType, RetrievalStrategy, DEFAULT_TOP_K_RETRIEVAL
)
from .memory_manager import MemoryManager
from ...core.logger import get_logger

logger = get_logger(__name__)


class MemoryMixin:
    """Mixin to add memory capabilities to any agent.
    
    Usage:
        class MyAgent(BaseAgent, MemoryMixin):
            def __init__(self, ...):
                BaseAgent.__init__(self, ...)
                MemoryMixin.init_memory(self, memory_manager)
    
    This mixin provides:
    - Automatic recording of analyses
    - Access to similar past cases
    - Feedback recording and retrieval
    - Pattern-based suggestions
    """
    
    def init_memory(
        self,
        memory_manager: Optional[MemoryManager] = None,
        auto_record: bool = True
    ):
        """Initialize memory capabilities.
        
        Args:
            memory_manager: Memory manager instance (creates default if None)
            auto_record: Automatically record all analyses
        """
        self._memory_manager = memory_manager
        self._memory_auto_record = auto_record
        
        if self._memory_manager is None:
            logger.debug(f"{self.__class__.__name__}: Memory manager not provided, using default")
            self._memory_manager = MemoryManager()
    
    def memory_enabled(self) -> bool:
        """Check if memory is enabled for this agent."""
        return (
            hasattr(self, '_memory_manager') and
            self._memory_manager is not None and
            self._memory_manager.is_enabled()
        )
    
    def record_analysis(
        self,
        country: str,
        period: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: float,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Optional[str]:
        """Record this analysis in memory.
        
        Args:
            country: Country analyzed
            period: Time period
            input_data: Input data
            output_data: Analysis results
            execution_time_ms: Execution time
            success: Whether analysis succeeded
            error_message: Error message if failed
            
        Returns:
            Memory ID if recorded, None otherwise
        """
        if not self.memory_enabled():
            return None
        
        # Get agent name from parameter_name or class name
        agent_name = getattr(self, 'parameter_name', self.__class__.__name__)
        
        # Create embedding text from output
        embedding_text = self._create_embedding_text(country, input_data, output_data)
        
        return self._memory_manager.record_analysis(
            agent_name=agent_name,
            country=country,
            period=period,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message,
            embedding_text=embedding_text
        )
    
    def get_similar_cases(
        self,
        country: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = DEFAULT_TOP_K_RETRIEVAL,
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    ) -> List[Tuple[EpisodicMemoryEntry, float]]:
        """Get similar past analyses.
        
        Args:
            country: Country to find cases for
            context: Optional context for matching
            top_k: Number of results
            strategy: Retrieval strategy
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        if not self.memory_enabled():
            return []
        
        agent_name = getattr(self, 'parameter_name', self.__class__.__name__)
        
        return self._memory_manager.get_similar_analyses(
            country=country,
            agent=agent_name,
            context=context,
            top_k=top_k,
            strategy=strategy
        )
    
    def get_memory_context(
        self,
        country: str,
        input_data: Optional[Dict[str, Any]] = None,
        max_memories: int = 5
    ) -> Dict[str, Any]:
        """Build context from relevant memories.
        
        Args:
            country: Country being analyzed
            input_data: Current input data
            max_memories: Maximum memories to include
            
        Returns:
            Context dictionary with relevant memories
        """
        if not self.memory_enabled():
            return {}
        
        # Get similar cases
        similar_cases = self.get_similar_cases(
            country=country,
            context=input_data,
            top_k=max_memories
        )
        
        if not similar_cases:
            return {}
        
        # Build context
        context = {
            'has_memory': True,
            'similar_cases_count': len(similar_cases),
            'cases': []
        }
        
        for memory, similarity in similar_cases:
            case = {
                'similarity': similarity,
                'period': memory.content.get('period'),
                'score': memory.content.get('output_data', {}).get('score'),
                'success': memory.content.get('success'),
                'timestamp': memory.timestamp.isoformat()
            }
            context['cases'].append(case)
        
        # Calculate confidence
        if similar_cases:
            avg_similarity = sum(s for _, s in similar_cases) / len(similar_cases)
            context['confidence'] = avg_similarity
        
        return context
    
    def suggest_score_from_memory(
        self,
        country: str,
        current_score: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get score suggestion based on memory.
        
        Args:
            country: Country being scored
            current_score: Current calculated score
            context: Optional context
            
        Returns:
            Suggestion dictionary or None
        """
        if not self.memory_enabled():
            return None
        
        agent_name = getattr(self, 'parameter_name', self.__class__.__name__)
        
        return self._memory_manager.suggest_score_adjustment(
            country=country,
            parameter=agent_name,
            current_score=current_score,
            context=context
        )
    
    def record_expert_feedback(
        self,
        analysis_id: str,
        expert_id: str,
        feedback_type: FeedbackType,
        original_value: Any,
        corrected_value: Any,
        reasoning: str,
        impact_scope: str = "specific"
    ) -> Optional[str]:
        """Record expert feedback on an analysis.
        
        Args:
            analysis_id: ID of original analysis
            expert_id: ID of expert
            feedback_type: Type of feedback
            original_value: Original value
            corrected_value: Corrected value
            reasoning: Expert reasoning
            impact_scope: Scope of impact
            
        Returns:
            Feedback memory ID
        """
        if not self.memory_enabled():
            return None
        
        return self._memory_manager.record_feedback(
            feedback_type=feedback_type,
            original_analysis_id=analysis_id,
            expert_id=expert_id,
            original_value=original_value,
            corrected_value=corrected_value,
            reasoning=reasoning,
            impact_scope=impact_scope
        )
    
    def get_patterns_for_context(
        self,
        country: Optional[str] = None,
        pattern_type: str = "scoring"
    ) -> List[Dict[str, Any]]:
        """Get recognized patterns for current context.
        
        Args:
            country: Optional country filter
            pattern_type: Type of patterns to get
            
        Returns:
            List of patterns
        """
        if not self.memory_enabled():
            return []
        
        agent_name = getattr(self, 'parameter_name', self.__class__.__name__)
        
        return self._memory_manager.recognize_patterns(
            pattern_type=pattern_type,
            country=country,
            agent=agent_name
        )
    
    def _create_embedding_text(
        self,
        country: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any]
    ) -> str:
        """Create text for embedding generation.
        
        Args:
            country: Country name
            input_data: Input data
            output_data: Output data
            
        Returns:
            Text for embedding
        """
        agent_name = getattr(self, 'parameter_name', self.__class__.__name__)
        
        # Build comprehensive text
        parts = [
            f"Agent: {agent_name}",
            f"Country: {country}",
        ]
        
        # Add key input attributes
        if input_data:
            parts.append(f"Inputs: {str(input_data)[:200]}")
        
        # Add output
        score = output_data.get('score')
        if score is not None:
            parts.append(f"Score: {score}")
        
        justification = output_data.get('justification')
        if justification:
            parts.append(f"Reasoning: {justification[:300]}")
        
        return " | ".join(parts)
    
    def enhance_justification_with_memory(
        self,
        base_justification: str,
        country: str,
        current_score: float
    ) -> str:
        """Enhance justification with insights from memory.
        
        Args:
            base_justification: Base justification text
            country: Country being analyzed
            current_score: Current score
            
        Returns:
            Enhanced justification
        """
        if not self.memory_enabled():
            return base_justification
        
        # Get similar cases
        similar = self.get_similar_cases(country, top_k=3)
        
        if not similar:
            return base_justification
        
        # Calculate statistics
        past_scores = [
            mem.content.get('output_data', {}).get('score')
            for mem, _ in similar
        ]
        past_scores = [s for s in past_scores if s is not None]
        
        if not past_scores:
            return base_justification
        
        avg_past_score = sum(past_scores) / len(past_scores)
        
        # Add historical context
        enhancement = f"\n\nHistorical context: Based on {len(similar)} similar analyses, "
        enhancement += f"the average score for {country} was {avg_past_score:.2f}. "
        
        if abs(current_score - avg_past_score) > 1.0:
            if current_score > avg_past_score:
                enhancement += f"The current score of {current_score:.2f} is notably higher than historical average, "
                enhancement += "suggesting improved conditions."
            else:
                enhancement += f"The current score of {current_score:.2f} is notably lower than historical average, "
                enhancement += "suggesting deteriorated conditions."
        else:
            enhancement += "The current score aligns with historical patterns."
        
        return base_justification + enhancement
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of feedback for this agent.
        
        Returns:
            Feedback statistics
        """
        if not self.memory_enabled():
            return {}
        
        agent_name = getattr(self, 'parameter_name', self.__class__.__name__)
        
        return self._memory_manager.get_feedback_statistics(agent=agent_name)


class MemoryAwareAnalysisMixin(MemoryMixin):
    """Extended mixin that automatically integrates memory into analysis workflow.
    
    Provides automatic memory recording and context enrichment.
    """
    
    def analyze_with_memory(
        self,
        country: str,
        period: str,
        input_data: Optional[Dict[str, Any]] = None,
        use_memory_suggestions: bool = True,
        enhance_with_context: bool = True
    ) -> Dict[str, Any]:
        """Perform analysis with memory integration.
        
        This method should be called instead of direct analyze() when
        memory integration is desired.
        
        Args:
            country: Country to analyze
            period: Time period
            input_data: Optional input data
            use_memory_suggestions: Use memory for score suggestions
            enhance_with_context: Enhance results with memory context
            
        Returns:
            Analysis result with memory enhancements
        """
        start_time = datetime.now()
        
        # Get memory context
        memory_context = {}
        if enhance_with_context:
            memory_context = self.get_memory_context(country, input_data)
        
        # Perform base analysis
        # Note: Assumes agent has analyze() method
        if hasattr(self, 'analyze'):
            result = self.analyze(country, period, input_data)
        else:
            raise NotImplementedError("Agent must implement analyze() method")
        
        # Apply memory suggestions if enabled
        if use_memory_suggestions and result.get('score') is not None:
            suggestion = self.suggest_score_from_memory(
                country=country,
                current_score=result['score'],
                context=input_data
            )
            
            if suggestion and suggestion['confidence'] >= 0.5:
                result['memory_suggestion'] = suggestion
                result['suggested_score'] = suggestion['suggested_score']
        
        # Enhance justification with memory context
        if enhance_with_context and result.get('justification'):
            result['justification'] = self.enhance_justification_with_memory(
                base_justification=result['justification'],
                country=country,
                current_score=result.get('score', 0)
            )
        
        # Add memory context to result
        if memory_context:
            result['memory_context'] = memory_context
        
        # Record analysis if auto-record is enabled
        if self._memory_auto_record:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            memory_id = self.record_analysis(
                country=country,
                period=period,
                input_data=input_data or {},
                output_data=result,
                execution_time_ms=execution_time,
                success=True
            )
            
            if memory_id:
                result['memory_id'] = memory_id
        
        return result
