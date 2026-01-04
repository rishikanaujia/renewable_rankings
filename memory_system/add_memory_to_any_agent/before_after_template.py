"""
BEFORE/AFTER: Modifying CountryStabilityAgent to Add Memory
=============================================================

Apply these changes to: src/agents/parameter_agents/country_stability_agent.py
"""

# ==============================================================================
# CHANGE 1: Add import (line ~36)
# ==============================================================================

# BEFORE:
from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

# AFTER:
from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError
from ...memory import MemoryMixin  # <-- ADD THIS LINE


# ==============================================================================
# CHANGE 2: Modify class definition (line ~41)
# ==============================================================================

# BEFORE:
class CountryStabilityAgent(BaseParameterAgent):
    """Agent for analyzing country stability based on political/economic risk."""

# AFTER:
class CountryStabilityAgent(BaseParameterAgent, MemoryMixin):  # <-- ADD MemoryMixin
    """Agent for analyzing country stability based on political/economic risk."""


# ==============================================================================
# CHANGE 3: Modify __init__ method (line ~62)
# ==============================================================================

# BEFORE:
def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
    """Initialize Country Stability Agent."""
    super().__init__(
        parameter_name="Country Stability",
        mode=mode,
        config=config
    )
    
    # Load scoring rubric from config (NO HARDCODING!)
    self.scoring_rubric = self._load_scoring_rubric()
    
    logger.debug(f"Loaded scoring rubric with {len(self.scoring_rubric)} levels")

# AFTER:
def __init__(
    self, 
    mode: AgentMode = AgentMode.MOCK, 
    config: Dict[str, Any] = None,
    memory_manager=None  # <-- ADD THIS PARAMETER
):
    """Initialize Country Stability Agent."""
    super().__init__(
        parameter_name="Country Stability",
        mode=mode,
        config=config
    )
    
    # ADD THESE 3 LINES:
    if memory_manager:
        MemoryMixin.init_memory(self, memory_manager, auto_record=True)
        logger.info("Memory enabled for Country Stability Agent")
    
    # Load scoring rubric from config (NO HARDCODING!)
    self.scoring_rubric = self._load_scoring_rubric()
    
    logger.debug(f"Loaded scoring rubric with {len(self.scoring_rubric)} levels")


# ==============================================================================
# CHANGE 4: (Optional) Use memory features in analyze() method
# ==============================================================================

# In the analyze() method, you can optionally add memory features:

def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
    """Analyze country stability for a country."""
    try:
        # Your existing code...
        data = self._fetch_data(country, period)
        score = self._calculate_score(data)
        justification = self._generate_justification(score, data)
        
        # OPTIONAL: Add memory features
        if self.memory_enabled():
            # Get similar past cases
            similar = self.get_similar_cases(country, top_k=3)
            if similar:
                logger.debug(f"Found {len(similar)} similar analyses")
            
            # Get score suggestion
            suggestion = self.suggest_score_from_memory(country, score)
            if suggestion and suggestion['confidence'] >= 0.7:
                logger.info(f"Memory suggests score: {suggestion['suggested_score']:.2f}")
                # Optionally: use the suggestion to adjust the score
        
        # Create result
        result = ParameterScore(
            parameter_name=self.parameter_name,
            score=score,
            justification=justification,
            confidence=0.95,
            timestamp=datetime.now()
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


# ==============================================================================
# SUMMARY OF CHANGES
# ==============================================================================
"""
Total changes required:
1. Add 1 import line
2. Add MemoryMixin to class definition
3. Add memory_manager parameter to __init__
4. Add 3 lines to initialize memory

That's it! Only 5-6 lines of code changed.

The agent now automatically:
- Records all analyses in memory
- Can retrieve similar past cases
- Can get score suggestions
- Can record expert feedback
- Can recognize patterns

All existing functionality continues to work unchanged!
"""


# ==============================================================================
# USAGE EXAMPLE
# ==============================================================================
"""
In your main application:

from src.memory import MemoryManager
import yaml

# Initialize memory once
with open('config/memory.yaml') as f:
    config = yaml.safe_load(f)
memory = MemoryManager(config['memory'])

# Create agents with memory
agent = CountryStabilityAgent(
    mode=AgentMode.MOCK,
    memory_manager=memory  # <-- Pass memory manager
)

# Use normally
result = agent.analyze("Germany", "Q1 2024")

# Analysis is automatically recorded!
# Agent can now use memory features!
"""
