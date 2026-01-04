"""
STEP-BY-STEP: Add Memory to Your Existing Agents
==================================================

STEP 1: Modify your agent files
================================

For EACH agent you want to add memory to (e.g., country_stability_agent.py):

1. Add import at the top:
   from src.memory import MemoryMixin

2. Add MemoryMixin to class definition:
   BEFORE: class CountryStabilityAgent(BaseParameterAgent):
   AFTER:  class CountryStabilityAgent(BaseParameterAgent, MemoryMixin):

3. Add memory_manager parameter to __init__:
   BEFORE: def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
   AFTER:  def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None, memory_manager=None):

4. Initialize memory in __init__ (after super().__init__):
   super().__init__(parameter_name="Country Stability", mode=mode, config=config)
   
   # ADD THIS:
   if memory_manager:
       MemoryMixin.init_memory(self, memory_manager, auto_record=True)

THAT'S IT! The agent now has memory capabilities.


STEP 2: Initialize memory manager at application startup
=========================================================

In your main application file (e.g., run.py or main.py):

import yaml
from src.memory import MemoryManager

# Load memory config
with open('config/memory.yaml') as f:
    config = yaml.safe_load(f)

# Create memory manager (ONCE)
memory_manager = MemoryManager(config['memory'])

# Pass to agents when creating them
agent = CountryStabilityAgent(
    mode=AgentMode.MOCK,
    memory_manager=memory_manager  # <-- Add this
)


STEP 3: Use agents normally
============================

# Agents work exactly the same
result = agent.analyze("Germany", "Q1 2024")

# But now they automatically:
# - Record all analyses
# - Can retrieve similar past cases
# - Can get score suggestions
# - Can record expert feedback


STEP 4: (Optional) Use memory features explicitly
==================================================

If you want to use memory features in your code:

# Find similar past analyses
similar = agent.get_similar_cases("Germany", top_k=5)
for memory, similarity in similar:
    print(f"Past score: {memory.content['output_data']['score']}")
    print(f"Similarity: {similarity:.2f}")

# Get score suggestion
suggestion = agent.suggest_score_from_memory("Germany", current_score=8.5)
if suggestion:
    print(f"Suggested: {suggestion['suggested_score']}")

# Record expert feedback
agent.record_expert_feedback(
    analysis_id="abc123",
    expert_id="analyst_01",
    feedback_type=FeedbackType.SCORE_ADJUSTMENT,
    original_value=7.5,
    corrected_value=8.2,
    reasoning="Underestimated recent improvements"
)


EXAMPLE: Modified CountryStabilityAgent
========================================
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseParameterAgent, AgentMode
from src.memory import MemoryMixin  # 1. ADD THIS

class CountryStabilityAgent(BaseParameterAgent, MemoryMixin):  # 2. ADD MemoryMixin
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        memory_manager=None  # 3. ADD THIS PARAMETER
    ):
        super().__init__(
            parameter_name="Country Stability",
            mode=mode,
            config=config
        )
        
        # 4. ADD THIS
        if memory_manager:
            MemoryMixin.init_memory(self, memory_manager, auto_record=True)
        
        # ... rest of your existing code unchanged ...
        self.scoring_rubric = self._load_scoring_rubric()
    
    # ... all other methods unchanged ...


"""
MINIMAL CHANGES REQUIRED
=========================

To add memory to 18 agents:
1. Add 1 import line per file
2. Add MemoryMixin to 1 class definition per file  
3. Add 1 parameter to __init__ per file
4. Add 2 lines to initialize memory per file

Total: ~5 lines per agent × 18 agents = ~90 lines of code

Your existing code continues to work unchanged!
"""
