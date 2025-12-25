"""Feedback processor for learning from expert corrections."""
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime

from ...base.memory_store import MemoryStore
from ...base.memory_entry import (
    FeedbackMemoryEntry, MemoryQuery, BaseMemoryEntry
)
from ...base.memory_types import (
    MemoryType, FeedbackType, LearningStrategy
)
from ...core.logger import get_logger

logger = get_logger(__name__)


class FeedbackProcessor:
    """Process expert feedback to improve future analyses.
    
    Learns from:
    - Score adjustments
    - Reasoning corrections
    - Weight modifications
    - New insights
    - Validations and rejections
    """
    
    def __init__(
        self,
        memory_store: MemoryStore,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize feedback processor.
        
        Args:
            memory_store: Memory store for storing/retrieving feedback
            config: Optional configuration
        """
        self.memory_store = memory_store
        self.config = config or {}
        
        # Learning parameters
        self.learning_rate = config.get('learning_rate', 0.1)
        self.min_feedback_count = config.get('min_feedback_count', 3)
        self.decay_factor = config.get('decay_factor', 0.95)  # For weighting recent feedback
        
    def record_feedback(
        self,
        feedback_type: FeedbackType,
        original_analysis_id: str,
        expert_id: str,
        original_value: Any,
        corrected_value: Any,
        reasoning: str,
        impact_scope: str = "specific",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record expert feedback.
        
        Args:
            feedback_type: Type of feedback
            original_analysis_id: ID of original analysis
            expert_id: ID of expert providing feedback
            original_value: Original value/analysis
            corrected_value: Corrected value
            reasoning: Expert's reasoning for correction
            impact_scope: Scope of impact (specific/category/global)
            metadata: Optional additional metadata
            
        Returns:
            ID of created feedback entry
        """
        from ..base.memory_entry import MemoryMetadata
        
        feedback = FeedbackMemoryEntry(
            feedback_type=feedback_type,
            original_analysis_id=original_analysis_id,
            expert_id=expert_id,
            original_value=original_value,
            corrected_value=corrected_value,
            reasoning=reasoning,
            impact_scope=impact_scope,
            metadata=MemoryMetadata(source=f"expert:{expert_id}")
        )
        
        # Add any additional metadata
        if metadata:
            feedback.content.update(metadata)
        
        feedback_id = self.memory_store.store(feedback)
        logger.info(
            f"Recorded {feedback_type.value} feedback from {expert_id} "
            f"for analysis {original_analysis_id}"
        )
        
        return feedback_id
    
    def get_feedback_for_analysis(
        self,
        analysis_id: str
    ) -> List[FeedbackMemoryEntry]:
        """Get all feedback for a specific analysis.
        
        Args:
            analysis_id: ID of analysis
            
        Returns:
            List of feedback entries
        """
        # Search for feedback targeting this analysis
        query = MemoryQuery(memory_types=[MemoryType.FEEDBACK])
        all_feedback = self.memory_store.search(query)
        
        relevant_feedback = [
            fb for fb in all_feedback
            if isinstance(fb, FeedbackMemoryEntry) and
            fb.content.get('original_analysis_id') == analysis_id
        ]
        
        return relevant_feedback
    
    def get_feedback_statistics(
        self,
        country: Optional[str] = None,
        agent: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None
    ) -> Dict[str, Any]:
        """Get statistics about feedback.
        
        Args:
            country: Optional country filter
            agent: Optional agent filter
            feedback_type: Optional feedback type filter
            
        Returns:
            Statistics dictionary
        """
        query = MemoryQuery(memory_types=[MemoryType.FEEDBACK])
        all_feedback = self.memory_store.search(query)
        
        # Filter
        if country:
            all_feedback = [
                fb for fb in all_feedback
                if fb.content.get('country') == country
            ]
        
        if agent:
            all_feedback = [
                fb for fb in all_feedback
                if fb.content.get('agent_name') == agent
            ]
        
        if feedback_type:
            all_feedback = [
                fb for fb in all_feedback
                if FeedbackType(fb.content.get('feedback_type')) == feedback_type
            ]
        
        # Calculate statistics
        stats = {
            'total_feedback': len(all_feedback),
            'by_type': defaultdict(int),
            'by_expert': defaultdict(int),
            'by_impact_scope': defaultdict(int),
            'average_correction_magnitude': 0.0
        }
        
        correction_magnitudes = []
        
        for fb in all_feedback:
            if not isinstance(fb, FeedbackMemoryEntry):
                continue
            
            fb_type = FeedbackType(fb.content.get('feedback_type'))
            stats['by_type'][fb_type.value] += 1
            stats['by_expert'][fb.content.get('expert_id')] += 1
            stats['by_impact_scope'][fb.content.get('impact_scope', 'specific')] += 1
            
            # Calculate correction magnitude for score adjustments
            if fb_type == FeedbackType.SCORE_ADJUSTMENT:
                try:
                    orig = float(fb.content.get('original_value', 0))
                    corr = float(fb.content.get('corrected_value', 0))
                    magnitude = abs(corr - orig)
                    correction_magnitudes.append(magnitude)
                except (TypeError, ValueError):
                    pass
        
        if correction_magnitudes:
            stats['average_correction_magnitude'] = sum(correction_magnitudes) / len(correction_magnitudes)
        
        return stats
    
    def extract_score_adjustment_patterns(
        self,
        country: Optional[str] = None,
        parameter: Optional[str] = None,
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """Extract patterns from score adjustment feedback.
        
        Args:
            country: Optional country filter
            parameter: Optional parameter filter
            min_occurrences: Minimum times a pattern must appear
            
        Returns:
            List of adjustment patterns
        """
        query = MemoryQuery(memory_types=[MemoryType.FEEDBACK])
        all_feedback = self.memory_store.search(query)
        
        # Filter for score adjustments
        adjustments = [
            fb for fb in all_feedback
            if isinstance(fb, FeedbackMemoryEntry) and
            FeedbackType(fb.content.get('feedback_type')) == FeedbackType.SCORE_ADJUSTMENT
        ]
        
        if country:
            adjustments = [fb for fb in adjustments if fb.content.get('country') == country]
        
        if parameter:
            adjustments = [fb for fb in adjustments if fb.content.get('parameter') == parameter]
        
        # Group by context and calculate patterns
        context_adjustments: Dict[str, List[float]] = defaultdict(list)
        
        for adj in adjustments:
            # Create context key from relevant attributes
            context_parts = []
            if adj.content.get('country'):
                context_parts.append(f"country:{adj.content['country']}")
            if adj.content.get('parameter'):
                context_parts.append(f"param:{adj.content['parameter']}")
            
            context_key = "|".join(context_parts) if context_parts else "general"
            
            try:
                orig = float(adj.content.get('original_value', 0))
                corr = float(adj.content.get('corrected_value', 0))
                adjustment = corr - orig
                context_adjustments[context_key].append(adjustment)
            except (TypeError, ValueError):
                continue
        
        # Extract patterns with sufficient occurrences
        patterns = []
        for context, adjustments_list in context_adjustments.items():
            if len(adjustments_list) >= min_occurrences:
                avg_adjustment = sum(adjustments_list) / len(adjustments_list)
                
                patterns.append({
                    'context': context,
                    'occurrences': len(adjustments_list),
                    'average_adjustment': avg_adjustment,
                    'min_adjustment': min(adjustments_list),
                    'max_adjustment': max(adjustments_list),
                    'std_deviation': self._calculate_std(adjustments_list),
                    'confidence': min(len(adjustments_list) / 10.0, 1.0)  # Cap at 10 occurrences
                })
        
        patterns.sort(key=lambda x: x['confidence'], reverse=True)
        return patterns
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def suggest_score_adjustment(
        self,
        country: str,
        parameter: str,
        current_score: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Suggest a score adjustment based on past feedback.
        
        Args:
            country: Country being analyzed
            parameter: Parameter being scored
            current_score: Current calculated score
            context: Optional additional context
            
        Returns:
            Adjustment suggestion or None if no pattern found
        """
        patterns = self.extract_score_adjustment_patterns(
            country=country,
            parameter=parameter,
            min_occurrences=self.min_feedback_count
        )
        
        if not patterns:
            return None
        
        # Use highest confidence pattern
        best_pattern = patterns[0]
        
        if best_pattern['confidence'] < 0.3:
            return None  # Not confident enough
        
        suggested_score = current_score + best_pattern['average_adjustment']
        
        # Clamp to valid range
        suggested_score = max(0.0, min(10.0, suggested_score))
        
        return {
            'current_score': current_score,
            'suggested_score': suggested_score,
            'adjustment': suggested_score - current_score,
            'confidence': best_pattern['confidence'],
            'based_on_occurrences': best_pattern['occurrences'],
            'reasoning': f"Based on {best_pattern['occurrences']} past adjustments with {best_pattern['confidence']:.1%} confidence"
        }
    
    def extract_reasoning_improvements(
        self,
        country: Optional[str] = None,
        agent: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract common reasoning improvements from feedback.
        
        Args:
            country: Optional country filter
            agent: Optional agent filter
            
        Returns:
            List of reasoning improvement patterns
        """
        query = MemoryQuery(memory_types=[MemoryType.FEEDBACK])
        all_feedback = self.memory_store.search(query)
        
        # Filter for reasoning corrections
        corrections = [
            fb for fb in all_feedback
            if isinstance(fb, FeedbackMemoryEntry) and
            FeedbackType(fb.content.get('feedback_type')) == FeedbackType.REASONING_CORRECTION
        ]
        
        if country:
            corrections = [fb for fb in corrections if fb.content.get('country') == country]
        
        if agent:
            corrections = [fb for fb in corrections if fb.content.get('agent_name') == agent]
        
        # Extract key themes from reasoning
        improvements = []
        for correction in corrections:
            reasoning = correction.content.get('reasoning', '')
            
            improvements.append({
                'original': correction.content.get('original_value'),
                'corrected': correction.content.get('corrected_value'),
                'reasoning': reasoning,
                'expert': correction.content.get('expert_id'),
                'timestamp': correction.timestamp.isoformat(),
                'impact_scope': correction.content.get('impact_scope')
            })
        
        return improvements
    
    def get_expert_consensus(
        self,
        analysis_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get expert consensus on an analysis.
        
        Args:
            analysis_id: ID of analysis
            
        Returns:
            Consensus information or None
        """
        feedback_list = self.get_feedback_for_analysis(analysis_id)
        
        if not feedback_list:
            return None
        
        validations = sum(
            1 for fb in feedback_list
            if FeedbackType(fb.content.get('feedback_type')) == FeedbackType.VALIDATION
        )
        
        rejections = sum(
            1 for fb in feedback_list
            if FeedbackType(fb.content.get('feedback_type')) == FeedbackType.REJECTION
        )
        
        total = len(feedback_list)
        
        return {
            'total_feedback': total,
            'validations': validations,
            'rejections': rejections,
            'adjustments': total - validations - rejections,
            'consensus_score': (validations - rejections) / total if total > 0 else 0,
            'needs_revision': rejections > validations
        }
    
    def apply_feedback_to_config(
        self,
        current_config: Dict[str, Any],
        learning_strategy: LearningStrategy = LearningStrategy.WEIGHT_ADAPTATION
    ) -> Dict[str, Any]:
        """Apply learned patterns to update configuration.
        
        Args:
            current_config: Current configuration
            learning_strategy: Strategy to use for learning
            
        Returns:
            Updated configuration
        """
        if learning_strategy == LearningStrategy.WEIGHT_ADAPTATION:
            return self._adapt_weights(current_config)
        elif learning_strategy == LearningStrategy.PATTERN_MATCHING:
            return self._apply_patterns(current_config)
        else:
            logger.warning(f"Learning strategy {learning_strategy} not yet implemented")
            return current_config
    
    def _adapt_weights(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt scoring weights based on feedback."""
        # Get weight modification feedback
        query = MemoryQuery(memory_types=[MemoryType.FEEDBACK])
        all_feedback = self.memory_store.search(query)
        
        weight_mods = [
            fb for fb in all_feedback
            if isinstance(fb, FeedbackMemoryEntry) and
            FeedbackType(fb.content.get('feedback_type')) == FeedbackType.WEIGHT_MODIFICATION
        ]
        
        if not weight_mods:
            return config
        
        # Extract weight changes
        weight_changes: Dict[str, List[float]] = defaultdict(list)
        
        for mod in weight_mods:
            param = mod.content.get('parameter')
            if not param:
                continue
            
            try:
                orig = float(mod.content.get('original_value', 0))
                corr = float(mod.content.get('corrected_value', 0))
                change = corr - orig
                weight_changes[param].append(change)
            except (TypeError, ValueError):
                continue
        
        # Apply average changes with learning rate
        new_config = config.copy()
        
        for param, changes in weight_changes.items():
            if len(changes) >= self.min_feedback_count:
                avg_change = sum(changes) / len(changes)
                adjusted_change = avg_change * self.learning_rate
                
                # Update config (path depends on structure)
                # This is simplified - real implementation would navigate config structure
                if param in new_config:
                    current_weight = new_config[param]
                    new_config[param] = max(0, current_weight + adjusted_change)
        
        return new_config
    
    def _apply_patterns(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learned patterns to configuration."""
        # This would implement pattern-based configuration updates
        # For now, return unchanged
        logger.info("Pattern application not yet implemented")
        return config
