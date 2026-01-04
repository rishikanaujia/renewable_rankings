"""
QUICK REFERENCE: Add Memory to Any Agent
=========================================

Copy-paste these changes for ANY parameter agent.
"""
from src.agents.base_agent import BaseParameterAgent

from src import MemoryMixin, MemoryManager, FeedbackType
from src.memory.integration import memory_manager


# 1. ADD IMPORT (at top of file)

# 2. MODIFY CLASS DEFINITION
# Before: class YourAgent(BaseParameterAgent):
# After:
#class YourAgent(BaseParameterAgent, MemoryMixin):

# 3. MODIFY __init__ SIGNATURE
# Before: def __init__(self, mode=AgentMode.MOCK, config=None):
# After:
#def __init__(self, mode=AgentMode.MOCK, config=None, memory_manager=None):

# 4. INITIALIZE MEMORY (in __init__, after super().__init__)
#if memory_manager:
    #MemoryMixin.init_memory(self, memory_manager, auto_record=True)

# 5. USE IN APPLICATION
import yaml

# Setup (once at startup)
with open('config/memory.yaml') as f:
    config = yaml.safe_load(f)
memory = MemoryManager(config['memory'])

# Create agent with memory
#agent = YourAgent(memory_manager=memory)

# Use normally - memory works automatically!
result = agent.analyze("Germany", "Q1 2024")


# ==============================================================================
# MEMORY FEATURES AVAILABLE IN YOUR AGENT
# ==============================================================================

# Check if memory is enabled
if agent.memory_enabled():
    
    # Get similar past cases
    similar = agent.get_similar_cases("Germany", top_k=5)
    for memory, similarity in similar:
        print(f"Past score: {memory.content['output_data']['score']}")
    
    # Get memory context
    context = agent.get_memory_context("Germany")
    print(f"Similar cases: {context['similar_cases_count']}")
    
    # Get score suggestion
    suggestion = agent.suggest_score_from_memory("Germany", 8.5)
    if suggestion:
        print(f"Suggested: {suggestion['suggested_score']}")
    
    # Record expert feedback
    agent.record_expert_feedback(
        analysis_id="abc123",
        expert_id="analyst_01",
        feedback_type=FeedbackType.SCORE_ADJUSTMENT,
        original_value=7.5,
        corrected_value=8.2,
        reasoning="Improved conditions"
    )
    
    # Get patterns
    patterns = agent.get_patterns_for_context("Germany")
    
    # Get feedback summary
    stats = agent.get_feedback_summary()


# ==============================================================================
# APPLY TO ALL 18 AGENTS
# ==============================================================================
"""
Files to modify:
1. src/agents/parameter_agents/country_stability_agent.py
2. src/agents/parameter_agents/ambition_agent.py
3. src/agents/parameter_agents/competitive_landscape_agent.py
4. src/agents/parameter_agents/contract_terms_agent.py
5. src/agents/parameter_agents/energy_dependence_agent.py
6. src/agents/parameter_agents/expected_return_agent.py
7. src/agents/parameter_agents/long_term_interest_rates_agent.py
8. src/agents/parameter_agents/offtaker_status_agent.py
9. src/agents/parameter_agents/ownership_consolidation_agent.py
10. src/agents/parameter_agents/ownership_hurdles_agent.py
11. src/agents/parameter_agents/power_market_size_agent.py
12. src/agents/parameter_agents/renewables_penetration_agent.py
13. src/agents/parameter_agents/resource_availability_agent.py
14. src/agents/parameter_agents/revenue_stream_stability_agent.py
15. src/agents/parameter_agents/status_of_grid_agent.py
16. src/agents/parameter_agents/support_scheme_agent.py
17. src/agents/parameter_agents/system_modifiers_agent.py
18. src/agents/parameter_agents/track_record_agent.py

For EACH file:
- Add 1 import
- Modify 1 class definition
- Add 1 parameter to __init__
- Add 3 lines to initialize memory

Total: ~6 lines per file × 18 files = ~108 lines total
"""


# ==============================================================================
# BACKWARD COMPATIBILITY
# ==============================================================================
"""
Important: memory_manager parameter is OPTIONAL!

This works (with memory):
    agent = CountryStabilityAgent(memory_manager=memory)

This also works (without memory):
    agent = CountryStabilityAgent()  # No memory, agent works normally

Your existing code continues to work unchanged!
"""
