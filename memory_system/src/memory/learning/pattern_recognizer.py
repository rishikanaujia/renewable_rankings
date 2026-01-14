"""Pattern recognizer for learning from historical analyses."""
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict, Counter
from datetime import datetime

from src.core.logger import get_logger

from ..base.memory_store import MemoryStore
from ..base.memory_entry import (
    EpisodicMemoryEntry, ProceduralMemoryEntry,
    MemoryQuery, MemoryMetadata
)
from ..base.memory_types import (
    MemoryType, MemoryCategory
)

logger = get_logger(__name__)


class PatternRecognizer:
    """Recognize patterns from historical analyses.
    
    Identifies:
    - Scoring patterns (consistent scoring tendencies)
    - Reasoning patterns (common justification structures)
    - Decision patterns (how experts make judgments)
    - Temporal patterns (seasonal or time-based trends)
    """
    
    def __init__(
        self,
        memory_store: MemoryStore,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize pattern recognizer.
        
        Args:
            memory_store: Memory store to analyze
            config: Optional configuration
        """
        self.memory_store = memory_store
        self.config = config or {}
        
        # Pattern recognition thresholds
        self.min_pattern_occurrences = config.get('min_pattern_occurrences', 3)
        self.min_pattern_confidence = config.get('min_pattern_confidence', 0.6)
        
    def recognize_scoring_patterns(
        self,
        country: Optional[str] = None,
        parameter: Optional[str] = None,
        time_window_days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Recognize scoring patterns from historical analyses.
        
        Args:
            country: Optional country filter
            parameter: Optional parameter filter
            time_window_days: Optional time window to consider
            
        Returns:
            List of recognized patterns
        """
        # Get episodic memories
        query = MemoryQuery(
            memory_types=[MemoryType.EPISODIC],
            countries=[country] if country else None,
            agents=[parameter] if parameter else None
        )
        
        memories = self.memory_store.search(query)
        
        if not memories:
            return []
        
        # Filter by time window
        if time_window_days:
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=time_window_days)
            memories = [m for m in memories if m.timestamp >= cutoff]
        
        # Analyze score distributions
        patterns = []
        
        # Pattern 1: Score clustering
        score_clusters = self._find_score_clusters(memories)
        if score_clusters:
            patterns.append({
                'pattern_type': 'score_clustering',
                'description': 'Scores tend to cluster around specific values',
                'clusters': score_clusters,
                'confidence': self._calculate_cluster_confidence(score_clusters, len(memories))
            })
        
        # Pattern 2: Score-input correlations
        correlations = self._find_score_correlations(memories)
        if correlations:
            patterns.append({
                'pattern_type': 'score_correlation',
                'description': 'Scores correlate with specific input attributes',
                'correlations': correlations,
                'confidence': max(c['strength'] for c in correlations)
            })
        
        # Pattern 3: Consistent scoring ranges by context
        context_ranges = self._find_context_score_ranges(memories)
        if context_ranges:
            patterns.append({
                'pattern_type': 'context_ranges',
                'description': 'Specific contexts lead to consistent score ranges',
                'ranges': context_ranges,
                'confidence': self._calculate_range_confidence(context_ranges)
            })
        
        return patterns
    
    def _find_score_clusters(
        self,
        memories: List[EpisodicMemoryEntry]
    ) -> List[Dict[str, Any]]:
        """Find score clustering patterns."""
        scores = []
        for mem in memories:
            if isinstance(mem, EpisodicMemoryEntry):
                output = mem.content.get('output_data', {})
                score = output.get('score')
                if score is not None:
                    try:
                        scores.append(float(score))
                    except (TypeError, ValueError):
                        continue
        
        if len(scores) < self.min_pattern_occurrences:
            return []
        
        # Simple clustering: group scores into 0.5-point bins
        bins = defaultdict(list)
        for score in scores:
            bin_key = round(score * 2) / 2  # Round to nearest 0.5
            bins[bin_key].append(score)
        
        # Find bins with significant clustering
        clusters = []
        total_scores = len(scores)
        
        for bin_center, bin_scores in bins.items():
            if len(bin_scores) >= self.min_pattern_occurrences:
                clusters.append({
                    'center': bin_center,
                    'count': len(bin_scores),
                    'percentage': len(bin_scores) / total_scores,
                    'range': (min(bin_scores), max(bin_scores))
                })
        
        return sorted(clusters, key=lambda x: x['count'], reverse=True)
    
    def _calculate_cluster_confidence(
        self,
        clusters: List[Dict[str, Any]],
        total_scores: int
    ) -> float:
        """Calculate confidence in clustering pattern."""
        if not clusters or total_scores == 0:
            return 0.0
        
        # Confidence based on largest cluster
        largest_cluster = max(clusters, key=lambda x: x['count'])
        confidence = largest_cluster['count'] / total_scores
        
        return min(confidence * 1.5, 1.0)  # Boost but cap at 1.0
    
    def _find_score_correlations(
        self,
        memories: List[EpisodicMemoryEntry]
    ) -> List[Dict[str, Any]]:
        """Find correlations between inputs and scores."""
        # Collect input-score pairs
        input_scores: Dict[str, List[tuple[Any, float]]] = defaultdict(list)
        
        for mem in memories:
            if not isinstance(mem, EpisodicMemoryEntry):
                continue
            
            input_data = mem.content.get('input_data', {})
            output_data = mem.content.get('output_data', {})
            score = output_data.get('score')
            
            if score is None:
                continue
            
            try:
                score_float = float(score)
            except (TypeError, ValueError):
                continue
            
            # Track each input attribute
            for key, value in input_data.items():
                if isinstance(value, (int, float, bool, str)):
                    input_scores[key].append((value, score_float))
        
        # Calculate correlations
        correlations = []
        
        for input_key, pairs in input_scores.items():
            if len(pairs) < self.min_pattern_occurrences:
                continue
            
            # For categorical: average score per category
            if isinstance(pairs[0][0], str):
                category_scores: Dict[str, List[float]] = defaultdict(list)
                for value, score in pairs:
                    category_scores[value].append(score)
                
                # Find significant differences
                categories = [(cat, sum(scores)/len(scores), len(scores))
                             for cat, scores in category_scores.items()
                             if len(scores) >= 2]
                
                if len(categories) >= 2:
                    categories.sort(key=lambda x: x[1], reverse=True)
                    score_range = categories[0][1] - categories[-1][1]
                    
                    if score_range >= 1.0:  # Significant difference
                        correlations.append({
                            'input': input_key,
                            'type': 'categorical',
                            'categories': [
                                {'value': cat, 'avg_score': avg, 'count': cnt}
                                for cat, avg, cnt in categories
                            ],
                            'strength': min(score_range / 10.0, 1.0)
                        })
            
            # For numeric: correlation coefficient
            elif isinstance(pairs[0][0], (int, float)):
                values = [p[0] for p in pairs]
                scores = [p[1] for p in pairs]
                
                correlation = self._calculate_correlation(values, scores)
                
                if abs(correlation) >= 0.5:  # Moderate correlation
                    correlations.append({
                        'input': input_key,
                        'type': 'numeric',
                        'correlation': correlation,
                        'strength': abs(correlation),
                        'direction': 'positive' if correlation > 0 else 'negative'
                    })
        
        return sorted(correlations, key=lambda x: x['strength'], reverse=True)
    
    def _calculate_correlation(
        self,
        x_values: List[float],
        y_values: List[float]
    ) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        n = len(x_values)
        
        # Convert to float
        x = [float(v) for v in x_values]
        y = [float(v) for v in y_values]
        
        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        # Calculate correlation
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        
        x_variance = sum((x[i] - x_mean) ** 2 for i in range(n))
        y_variance = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        denominator = (x_variance * y_variance) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _find_context_score_ranges(
        self,
        memories: List[EpisodicMemoryEntry]
    ) -> List[Dict[str, Any]]:
        """Find consistent score ranges for specific contexts."""
        # Group by context attributes
        context_scores: Dict[str, List[float]] = defaultdict(list)
        
        for mem in memories:
            if not isinstance(mem, EpisodicMemoryEntry):
                continue
            
            # Build context key from relevant attributes
            context_parts = []
            
            country = mem.content.get('country')
            if country:
                context_parts.append(f"country:{country}")
            
            agent = mem.content.get('agent_name')
            if agent:
                context_parts.append(f"agent:{agent}")
            
            if not context_parts:
                continue
            
            context_key = "|".join(context_parts)
            
            # Get score
            output = mem.content.get('output_data', {})
            score = output.get('score')
            
            if score is not None:
                try:
                    context_scores[context_key].append(float(score))
                except (TypeError, ValueError):
                    continue
        
        # Find contexts with consistent ranges
        ranges = []
        
        for context, scores in context_scores.items():
            if len(scores) < self.min_pattern_occurrences:
                continue
            
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            std_dev = self._calculate_std(scores)
            
            # Consistent if std dev is low
            if std_dev < 1.5:
                ranges.append({
                    'context': context,
                    'count': len(scores),
                    'average': avg_score,
                    'range': (min_score, max_score),
                    'std_dev': std_dev,
                    'consistency': max(0, 1.0 - std_dev / 3.0)  # Lower std = higher consistency
                })
        
        return sorted(ranges, key=lambda x: x['consistency'], reverse=True)
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _calculate_range_confidence(
        self,
        ranges: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in range patterns."""
        if not ranges:
            return 0.0
        
        # Average consistency of top ranges
        top_ranges = ranges[:min(3, len(ranges))]
        avg_consistency = sum(r['consistency'] for r in top_ranges) / len(top_ranges)
        
        return avg_consistency
    
    def recognize_reasoning_patterns(
        self,
        agent: Optional[str] = None,
        country: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Recognize reasoning patterns from justifications.
        
        Args:
            agent: Optional agent filter
            country: Optional country filter
            
        Returns:
            List of reasoning patterns
        """
        query = MemoryQuery(
            memory_types=[MemoryType.EPISODIC],
            agents=[agent] if agent else None,
            countries=[country] if country else None
        )
        
        memories = self.memory_store.search(query)
        
        # Extract justifications
        justifications = []
        for mem in memories:
            if isinstance(mem, EpisodicMemoryEntry):
                output = mem.content.get('output_data', {})
                justification = output.get('justification')
                if justification:
                    justifications.append(justification)
        
        if len(justifications) < self.min_pattern_occurrences:
            return []
        
        # Find common phrases/structures
        patterns = self._extract_common_phrases(justifications)
        
        return patterns
    
    def _extract_common_phrases(
        self,
        texts: List[str]
    ) -> List[Dict[str, Any]]:
        """Extract common phrases from texts."""
        # Simple word frequency analysis
        word_freq = Counter()
        phrase_freq = Counter()
        
        for text in texts:
            # Words
            words = text.lower().split()
            word_freq.update(words)
            
            # Bigrams (2-word phrases)
            bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            phrase_freq.update(bigrams)
            
            # Trigrams (3-word phrases)
            trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
            phrase_freq.update(trigrams)
        
        # Filter and format patterns
        patterns = []
        
        # Common phrases
        for phrase, count in phrase_freq.most_common(10):
            if count >= self.min_pattern_occurrences:
                patterns.append({
                    'type': 'common_phrase',
                    'phrase': phrase,
                    'frequency': count,
                    'percentage': count / len(texts)
                })
        
        return patterns
    
    def create_procedural_memory(
        self,
        pattern: Dict[str, Any],
        pattern_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Create procedural memory from recognized pattern.
        
        Args:
            pattern: Recognized pattern
            pattern_type: Type of pattern
            context: Context where pattern applies
            
        Returns:
            ID of created procedural memory
        """
        confidence_score = pattern.get('confidence', 0.5)
        
        # Create action from pattern
        action = {
            'pattern_data': pattern,
            'recommendation': self._generate_recommendation(pattern, pattern_type)
        }
        
        procedural_mem = ProceduralMemoryEntry(
            pattern_name=f"{pattern_type}_{datetime.now().strftime('%Y%m%d')}",
            pattern_type=pattern_type,
            context=context,
            action=action,
            confidence_score=confidence_score,
            metadata=MemoryMetadata(source="pattern_recognizer")
        )
        
        mem_id = self.memory_store.store(procedural_mem)
        logger.info(f"Created procedural memory for {pattern_type} pattern")
        
        return mem_id
    
    def _generate_recommendation(
        self,
        pattern: Dict[str, Any],
        pattern_type: str
    ) -> str:
        """Generate action recommendation from pattern."""
        if pattern_type == 'score_clustering':
            clusters = pattern.get('clusters', [])
            if clusters:
                top_cluster = clusters[0]
                return f"Scores typically cluster around {top_cluster['center']} ({top_cluster['percentage']:.1%} of cases)"
        
        elif pattern_type == 'score_correlation':
            correlations = pattern.get('correlations', [])
            if correlations:
                top_corr = correlations[0]
                return f"Consider {top_corr['input']} strongly influences scores ({top_corr['direction']} correlation)"
        
        elif pattern_type == 'context_ranges':
            ranges = pattern.get('ranges', [])
            if ranges:
                top_range = ranges[0]
                return f"For {top_range['context']}, expect scores around {top_range['average']:.2f} ± {top_range['std_dev']:.2f}"
        
        return "Apply pattern to future analyses"
