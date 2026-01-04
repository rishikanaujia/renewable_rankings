"""Memory type definitions and enums for the memory system."""
from enum import Enum
from typing import List


class MemoryType(str, Enum):
    """Types of memory in the system."""
    EPISODIC = "episodic"          # Specific analysis sessions/events
    SEMANTIC = "semantic"          # Facts, knowledge about countries/markets
    PROCEDURAL = "procedural"      # Reasoning patterns, strategies
    FEEDBACK = "feedback"          # Expert corrections and adjustments
    

class MemoryCategory(str, Enum):
    """Categories for organizing memory entries."""
    COUNTRY_ANALYSIS = "country_analysis"
    PARAMETER_ANALYSIS = "parameter_analysis"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    GLOBAL_RANKINGS = "global_rankings"
    EXPERT_REASONING = "expert_reasoning"
    MARKET_KNOWLEDGE = "market_knowledge"
    SCORING_PATTERN = "scoring_pattern"
    USER_CORRECTION = "user_correction"
    

class FeedbackType(str, Enum):
    """Types of expert feedback."""
    SCORE_ADJUSTMENT = "score_adjustment"      # Expert adjusts a score
    REASONING_CORRECTION = "reasoning_correction"  # Expert corrects reasoning
    WEIGHT_MODIFICATION = "weight_modification"    # Expert changes weights
    NEW_INSIGHT = "new_insight"                    # Expert adds new knowledge
    VALIDATION = "validation"                       # Expert confirms analysis
    REJECTION = "rejection"                         # Expert rejects analysis
    

class ConfidenceLevel(str, Enum):
    """Confidence levels for memory-based predictions."""
    VERY_HIGH = "very_high"  # 90-100% similar cases
    HIGH = "high"            # 70-89% similar cases
    MEDIUM = "medium"        # 50-69% similar cases
    LOW = "low"              # 30-49% similar cases
    VERY_LOW = "very_low"    # <30% similar cases
    NONE = "none"            # No similar cases found
    

class RetrievalStrategy(str, Enum):
    """Strategies for retrieving relevant memories."""
    SIMILARITY = "similarity"          # Vector similarity search
    TEMPORAL = "temporal"              # Time-based retrieval
    FREQUENCY = "frequency"            # Most frequently accessed
    RECENCY = "recency"               # Most recently accessed
    HYBRID = "hybrid"                 # Combination of strategies
    RELEVANCE = "relevance"           # Custom relevance scoring
    

class LearningStrategy(str, Enum):
    """Strategies for learning from feedback."""
    PATTERN_MATCHING = "pattern_matching"      # Learn similar patterns
    WEIGHT_ADAPTATION = "weight_adaptation"    # Adjust scoring weights
    RULE_EXTRACTION = "rule_extraction"        # Extract decision rules
    CASE_BASED = "case_based"                 # Case-based reasoning
    ENSEMBLE = "ensemble"                     # Combine strategies


# Constants for memory configuration
DEFAULT_SIMILARITY_THRESHOLD = 0.75
DEFAULT_TOP_K_RETRIEVAL = 5
DEFAULT_MEMORY_TTL_DAYS = 365  # 1 year default retention
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_CONTEXT_MEMORIES = 10  # Maximum memories to include in agent context
