#!/usr/bin/env python3
"""
Complete Working Example: Memory-Enabled Agent System

This shows the full integration from initialization to usage.
"""

import yaml
from datetime import datetime
from src.memory import MemoryManager, MemoryMixin, FeedbackType
from src.agents.base_agent import BaseParameterAgent, AgentMode
from src.models.parameter import ParameterScore


# ==============================================================================
# PART 1: Create Memory-Enabled Agent
# ==============================================================================

class CountryStabilityAgent(BaseParameterAgent, MemoryMixin):
    """Country Stability Agent with Memory."""
    
    MOCK_DATA = {
        "Germany": {"ecr_rating": 0.8},
        "USA": {"ecr_rating": 1.2},
        "India": {"ecr_rating": 3.2},
        "Brazil": {"ecr_rating": 2.3},
    }
    
    def __init__(self, mode=AgentMode.MOCK, config=None, memory_manager=None):
        # Initialize base agent
        BaseParameterAgent.__init__(self, "Country Stability", mode, config)
        
        # Initialize memory (if provided)
        if memory_manager:
            MemoryMixin.init_memory(self, memory_manager, auto_record=True)
    
    def _fetch_data(self, country, period):
        return self.MOCK_DATA.get(country, {"ecr_rating": 5.0})
    
    def _calculate_score(self, data):
        ecr = data["ecr_rating"]
        if ecr < 1.0: return 10.0
        elif ecr < 2.0: return 9.0
        elif ecr < 3.0: return 8.0
        elif ecr < 4.0: return 7.0
        else: return 6.0
    
    def _generate_justification(self, score, data):
        return f"ECR: {data['ecr_rating']:.1f}, Score: {score}/10"


# ==============================================================================
# PART 2: Initialize Memory System
# ==============================================================================

def setup_memory():
    """Initialize memory manager."""
    config = {
        'enabled': True,
        'store_type': 'chromadb',
        'store_config': {
            'persist_directory': './data/memory/production',
            'embedding_model': 'all-MiniLM-L6-v2'
        },
        'agent_integration': {
            'auto_record': True,
            'use_memory_suggestions': True
        }
    }
    return MemoryManager(config)


# ==============================================================================
# PART 3: Usage Examples
# ==============================================================================

def main():
    print("="*70)
    print("Memory-Enabled Agent System - Complete Example")
    print("="*70)
    
    # 1. Initialize memory
    print("\n1. Initializing memory system...")
    memory = setup_memory()
    print(f"   ✓ Memory enabled: {memory.is_enabled()}")
    
    # 2. Create agent WITH memory
    print("\n2. Creating agent with memory...")
    agent = CountryStabilityAgent(memory_manager=memory)
    print(f"   ✓ Agent created")
    print(f"   ✓ Memory enabled: {agent.memory_enabled()}")
    
    # 3. Run analyses (automatically recorded)
    print("\n3. Running analyses...")
    countries = ["Germany", "USA", "India", "Brazil"]
    for country in countries:
        result = agent.analyze(country, "Q1 2024")
        print(f"   ✓ {country}: {result.score}/10")
    
    # 4. Find similar cases
    print("\n4. Finding similar past cases for Germany...")
    similar = agent.get_similar_cases("Germany", top_k=3)
    for i, (mem, sim) in enumerate(similar, 1):
        score = mem.content['output_data']['score']
        print(f"   {i}. Score: {score}, Similarity: {sim:.2f}")
    
    # 5. Get memory statistics
    print("\n5. Memory statistics:")
    stats = memory.get_memory_statistics()
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   By type: {stats.get('by_type', {})}")
    
    # 6. Record expert feedback
    print("\n6. Recording expert feedback...")
    # Get first analysis ID from similar cases
    if similar:
        analysis_id = similar[0][0].id
        feedback_id = agent.record_expert_feedback(
            analysis_id=analysis_id,
            expert_id="analyst_01",
            feedback_type=FeedbackType.SCORE_ADJUSTMENT,
            original_value=9.0,
            corrected_value=9.5,
            reasoning="Underestimated recent stability improvements"
        )
        print(f"   ✓ Feedback recorded: {feedback_id[:8] if feedback_id else 'N/A'}")
    
    # 7. Get patterns
    print("\n7. Recognizing patterns...")
    patterns = agent.get_patterns_for_context("Germany", pattern_type="scoring")
    print(f"   Found {len(patterns)} patterns")
    for pattern in patterns[:2]:
        print(f"   - {pattern['pattern_type']}: {pattern.get('confidence', 0):.1%} confidence")
    
    # 8. Get score suggestion
    print("\n8. Getting score suggestion...")
    suggestion = agent.suggest_score_from_memory("Germany", current_score=9.0)
    if suggestion:
        print(f"   Current: {suggestion['current_score']:.1f}")
        print(f"   Suggested: {suggestion['suggested_score']:.1f}")
        print(f"   Confidence: {suggestion['confidence']:.1%}")
    else:
        print("   No suggestion available yet (need more data)")
    
    print("\n" + "="*70)
    print("✅ All features demonstrated successfully!")
    print("="*70)
    
    # Show what you can do
    print("\nWhat you can do now:")
    print("  • Analyses are automatically recorded")
    print("  • Find similar past cases")
    print("  • Get score suggestions from history")
    print("  • Record expert feedback")
    print("  • Recognize patterns automatically")
    print("  • System learns from corrections")


# ==============================================================================
# PART 4: Integration with Existing Application
# ==============================================================================

def integrate_with_existing_app():
    """
    Example of integrating memory into your existing application.
    
    In your main application file (e.g., run.py):
    """
    
    # At application startup
    memory_manager = setup_memory()
    
    # When creating agents (modify existing code)
    # BEFORE:
    # agent = CountryStabilityAgent(mode=AgentMode.MOCK)
    
    # AFTER:
    agent = CountryStabilityAgent(
        mode=AgentMode.MOCK,
        memory_manager=memory_manager  # <-- Add this
    )
    
    # Use agent normally - memory works automatically!
    result = agent.analyze("Germany", "Q1 2024")
    
    return agent


if __name__ == "__main__":
    main()
    
    # Or integrate with existing app
    # agent = integrate_with_existing_app()
