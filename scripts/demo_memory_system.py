"""Comprehensive demonstration of the Memory & Learning system.

This script demonstrates:
1. Memory system initialization
2. Recording analyses (episodic memory)
3. Storing knowledge (semantic memory)
4. Recording feedback
5. Pattern recognition
6. Similarity search
7. Score suggestions from memory
8. Agent integration
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from datetime import datetime
from typing import Dict, Any
from src import (
    MemoryManager,
    MemoryMixin,
    MemoryType,
    FeedbackType,
    RetrievalStrategy
)
from src.agents.base_agent import BaseParameterAgent, AgentMode


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_1_initialization():
    """Demo 1: Initialize memory system."""
    print_section("Demo 1: Memory System Initialization")
    
    # Create configuration
    config = {
        'enabled': True,
        'store_type': 'chromadb',
        'store_config': {
            'persist_directory': './data/memory/demo',
            'embedding_model': 'all-MiniLM-L6-v2',
            'collection_name': 'demo_memory'
        },
        'learning_config': {
            'learning_rate': 0.1,
            'min_feedback_count': 2,
            'min_pattern_occurrences': 2
        }
    }
    
    # Initialize memory manager
    print("Initializing memory manager...")
    memory_manager = MemoryManager(config)
    
    print(f"✓ Memory system initialized")
    print(f"✓ Enabled: {memory_manager.is_enabled()}")
    print(f"✓ Store type: {config['store_type']}")
    print(f"✓ Persist directory: {config['store_config']['persist_directory']}")
    
    return memory_manager


def demo_2_episodic_memory(memory_manager: MemoryManager):
    """Demo 2: Recording analyses in episodic memory."""
    print_section("Demo 2: Recording Analyses (Episodic Memory)")
    
    # Record several analyses
    countries = ["Germany", "United States", "China", "Germany", "India"]
    periods = ["Q1 2024", "Q1 2024", "Q1 2024", "Q2 2024", "Q1 2024"]
    scores = [9.2, 8.5, 7.8, 9.4, 6.5]
    
    print("Recording multiple analyses...")
    
    for country, period, score in zip(countries, periods, scores):
        memory_id = memory_manager.record_analysis(
            agent_name="CountryStability",
            country=country,
            period=period,
            input_data={
                "gdp_growth": 2.5 if country == "Germany" else 3.0,
                "political_stability": 9.0 if country == "Germany" else 7.5
            },
            output_data={
                "score": score,
                "justification": f"Analysis for {country} in {period}"
            },
            execution_time_ms=150.0,
            success=True
        )
        print(f"  ✓ Recorded: {country} ({period}) - Score: {score:.1f} - ID: {memory_id[:8]}")
    
    # Get statistics
    stats = memory_manager.get_memory_statistics()
    print(f"\n📊 Memory Statistics:")
    print(f"  Total memories: {stats['total_memories']}")
    print(f"  By type: {stats.get('by_type', {})}")


def demo_3_semantic_memory(memory_manager: MemoryManager):
    """Demo 3: Storing knowledge in semantic memory."""
    print_section("Demo 3: Storing Knowledge (Semantic Memory)")
    
    knowledge_items = [
        {
            'subject': 'Germany',
            'fact_type': 'policy',
            'fact_content': 'Introduced new offshore wind auction system',
            'source': 'BMWi 2024'
        },
        {
            'subject': 'Germany',
            'fact_type': 'infrastructure',
            'fact_content': 'Completed North Sea grid expansion',
            'source': 'Grid operator report'
        },
        {
            'subject': 'United States',
            'fact_type': 'policy',
            'fact_content': 'Extended ITC for solar projects',
            'source': 'IRA 2024'
        }
    ]
    
    print("Recording knowledge items...")
    
    for item in knowledge_items:
        memory_id = memory_manager.record_knowledge(**item)
        print(f"  ✓ {item['subject']}: {item['fact_content'][:50]}... - ID: {memory_id[:8]}")
    
    # Query knowledge
    print(f"\n🔍 Querying knowledge about Germany:")
    knowledge = memory_manager.get_knowledge_about("Germany")
    for fact in knowledge:
        content = fact.content
        print(f"  - [{content['fact_type']}] {content['fact_content']}")
        print(f"    Source: {content['source']}")


def demo_4_similarity_search(memory_manager: MemoryManager):
    """Demo 4: Finding similar analyses."""
    print_section("Demo 4: Similarity Search")
    
    # Find similar analyses for Germany
    print("Finding similar analyses for Germany...")
    
    similar = memory_manager.get_similar_analyses(
        country="Germany",
        agent="CountryStability",
        top_k=3,
        strategy=RetrievalStrategy.HYBRID
    )
    
    if similar:
        print(f"\n✓ Found {len(similar)} similar cases:")
        for i, (memory, similarity) in enumerate(similar, 1):
            content = memory.content
            output = content.get('output_data', {})
            print(f"\n  {i}. Similarity: {similarity:.2f}")
            print(f"     Period: {content.get('period')}")
            print(f"     Score: {output.get('score')}")
            print(f"     Timestamp: {memory.timestamp.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("  No similar cases found")


def demo_5_feedback_recording(memory_manager: MemoryManager):
    """Demo 5: Recording expert feedback."""
    print_section("Demo 5: Expert Feedback Recording")
    
    # Simulate expert feedback
    print("Recording expert feedback...")
    
    # Score adjustment
    feedback_id_1 = memory_manager.record_feedback(
        feedback_type=FeedbackType.SCORE_ADJUSTMENT,
        original_analysis_id="dummy_id_1",
        expert_id="analyst_01",
        original_value=9.2,
        corrected_value=9.5,
        reasoning="Underestimated recent grid improvements",
        impact_scope="category"
    )
    print(f"  ✓ Score adjustment feedback recorded - ID: {feedback_id_1[:8]}")
    
    # Reasoning correction
    feedback_id_2 = memory_manager.record_feedback(
        feedback_type=FeedbackType.REASONING_CORRECTION,
        original_analysis_id="dummy_id_2",
        expert_id="analyst_02",
        original_value="Basic justification",
        corrected_value="Enhanced justification with policy context",
        reasoning="Need to mention new policy framework",
        impact_scope="specific"
    )
    print(f"  ✓ Reasoning correction feedback recorded - ID: {feedback_id_2[:8]}")
    
    # Get feedback statistics
    print(f"\n📊 Feedback Statistics:")
    stats = memory_manager.get_feedback_statistics(country="Germany")
    print(f"  Total feedback: {stats.get('total_feedback', 0)}")
    print(f"  By type: {dict(stats.get('by_type', {}))}")
    print(f"  By expert: {dict(stats.get('by_expert', {}))}")


def demo_6_pattern_recognition(memory_manager: MemoryManager):
    """Demo 6: Recognizing patterns from historical data."""
    print_section("Demo 6: Pattern Recognition")
    
    print("Recognizing scoring patterns for Germany...")
    
    patterns = memory_manager.recognize_patterns(
        pattern_type="scoring",
        country="Germany",
        agent="CountryStability"
    )
    
    if patterns:
        print(f"\n✓ Found {len(patterns)} patterns:")
        for i, pattern in enumerate(patterns, 1):
            print(f"\n  {i}. Pattern: {pattern['pattern_type']}")
            print(f"     Confidence: {pattern['confidence']:.2f}")
            print(f"     Description: {pattern['description']}")
            
            # Show pattern details
            if 'clusters' in pattern:
                print(f"     Clusters: {len(pattern['clusters'])}")
                for cluster in pattern['clusters'][:2]:
                    print(f"       - Center: {cluster['center']}, Count: {cluster['count']}")
    else:
        print("  No patterns found (need more data)")


def demo_7_score_suggestions(memory_manager: MemoryManager):
    """Demo 7: Getting score suggestions from memory."""
    print_section("Demo 7: Score Suggestions from Memory")
    
    print("Getting score suggestion for Germany...")
    
    suggestion = memory_manager.suggest_score_adjustment(
        country="Germany",
        parameter="CountryStability",
        current_score=9.0
    )
    
    if suggestion:
        print(f"\n✓ Memory-based suggestion:")
        print(f"  Current score: {suggestion['current_score']:.2f}")
        print(f"  Suggested score: {suggestion['suggested_score']:.2f}")
        print(f"  Adjustment: {suggestion['adjustment']:+.2f}")
        print(f"  Confidence: {suggestion['confidence']:.2%}")
        print(f"  Based on: {suggestion['based_on_occurrences']} past adjustments")
        print(f"  Reasoning: {suggestion['reasoning']}")
    else:
        print("  No suggestion available (insufficient data)")


def demo_8_agent_integration(memory_manager: MemoryManager):
    """Demo 8: Integrating memory with an agent."""
    print_section("Demo 8: Agent Integration with Memory")
    
    # Create a memory-aware agent
    class DemoAgent(BaseParameterAgent, MemoryMixin):
        def __init__(self, mode, config, memory_manager):
            BaseParameterAgent.__init__(self, "Demo Agent", mode, config)
            MemoryMixin.init_memory(self, memory_manager, auto_record=True)
        
        def _fetch_data(self, country: str, period: str) -> Dict[str, Any]:
            """Fetch data for analysis (mock implementation)."""
            return {"test_data": True}
        
        def _calculate_score(self, data: Dict[str, Any]) -> float:
            """Calculate score (mock implementation)."""
            return 8.0
        
        def _generate_justification(self, score: float, data: Dict[str, Any]) -> str:
            """Generate justification (mock implementation)."""
            return f"Mock justification for score {score}"
        
        def analyze(self, country, period, data=None):
            """Simple analysis with memory integration."""
            # Simulate calculation
            base_score = 8.0
            
            # Get memory context
            context = self.get_memory_context(country, data)
            
            result = {
                'score': base_score,
                'justification': f"Base analysis for {country}",
                'period': period
            }
            
            # Get suggestion from memory
            if context.get('has_memory'):
                suggestion = self.suggest_score_from_memory(country, base_score, data)
                if suggestion and suggestion['confidence'] >= 0.3:
                    result['memory_suggestion'] = suggestion
                    result['score'] = suggestion['suggested_score']
                    result['justification'] += f"\n\nMemory-adjusted score based on {len(context['cases'])} similar cases."
            
            # Record analysis
            self.record_analysis(
                country=country,
                period=period,
                input_data=data or {},
                output_data=result,
                execution_time_ms=100.0
            )
            
            return result
    
    # Create agent
    print("Creating memory-aware agent...")
    agent = DemoAgent(
        mode=AgentMode.MOCK,
        config={},
        memory_manager=memory_manager
    )
    print("✓ Agent created with memory capabilities")
    
    # Run analysis
    print(f"\nRunning analysis for Germany...")
    result = agent.analyze("Germany", "Q3 2024", {"test": True})
    
    print(f"\n📊 Analysis Result:")
    print(f"  Score: {result['score']:.2f}")
    print(f"  Justification: {result['justification']}")
    if 'memory_suggestion' in result:
        print(f"  Memory adjustment: {result['memory_suggestion']['adjustment']:+.2f}")
    
    # Check agent memory methods
    print(f"\n🔍 Agent Memory Methods:")
    print(f"  ✓ memory_enabled(): {agent.memory_enabled()}")
    print(f"  ✓ get_similar_cases() available")
    print(f"  ✓ get_memory_context() available")
    print(f"  ✓ suggest_score_from_memory() available")
    print(f"  ✓ record_expert_feedback() available")


def demo_9_statistics(memory_manager: MemoryManager):
    """Demo 9: Memory system statistics."""
    print_section("Demo 9: Memory System Statistics")
    
    stats = memory_manager.get_memory_statistics()
    
    print("📊 Overall Statistics:")
    print(f"  Enabled: {stats['enabled']}")
    print(f"  Total memories: {stats.get('total_memories', 0)}")
    
    if stats.get('by_type'):
        print(f"\n  By memory type:")
        for mem_type, count in stats['by_type'].items():
            print(f"    - {mem_type}: {count}")
    
    if stats.get('by_category'):
        print(f"\n  By category:")
        for category, count in stats['by_category'].items():
            print(f"    - {category}: {count}")
    
    print(f"\n  Collections: {stats.get('collections', 0)}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("  RENEWABLE ENERGY RANKINGS - MEMORY & LEARNING SYSTEM DEMO")
    print("="*70)
    
    try:
        # Demo 1: Initialize
        memory_manager = demo_1_initialization()
        
        # Demo 2: Episodic Memory
        demo_2_episodic_memory(memory_manager)
        
        # Demo 3: Semantic Memory
        demo_3_semantic_memory(memory_manager)
        
        # Demo 4: Similarity Search
        demo_4_similarity_search(memory_manager)
        
        # Demo 5: Feedback Recording
        demo_5_feedback_recording(memory_manager)
        
        # Demo 6: Pattern Recognition
        demo_6_pattern_recognition(memory_manager)
        
        # Demo 7: Score Suggestions
        demo_7_score_suggestions(memory_manager)
        
        # Demo 8: Agent Integration
        demo_8_agent_integration(memory_manager)
        
        # Demo 9: Statistics
        demo_9_statistics(memory_manager)
        
        # Summary
        print_section("Summary")
        print("✅ All demos completed successfully!")
        print("\nThe memory system is now ready for production use.")
        print("\nNext steps:")
        print("  1. Integrate memory with your existing agents")
        print("  2. Configure memory settings in config/memory.yaml")
        print("  3. Start recording analyses to build historical database")
        print("  4. Collect expert feedback to enable learning")
        print("  5. Monitor patterns and suggestions")
        print("\nSee docs/MEMORY_SYSTEM_GUIDE.md for detailed documentation.")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
