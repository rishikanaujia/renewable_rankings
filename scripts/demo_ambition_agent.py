#!/usr/bin/env python3
"""Demo script for testing the Ambition Agent.

This script demonstrates:
1. Direct agent usage
2. Service layer usage  
3. Score calculation
4. Result formatting

Run from project root:
    python scripts/demo_ambition_agent.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agents.parameter_agents import AmbitionAgent, analyze_ambition
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

# Setup logging
setup_logger(log_level="INFO")
logger = get_logger(__name__)


def demo_direct_agent_usage():
    """Demonstrate direct agent usage."""
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage")
    print("="*70)
    
    # Create agent
    agent = AmbitionAgent(mode=AgentMode.MOCK)
    
    # Test countries
    countries = ["Brazil", "Germany", "China", "India"]
    
    for country in countries:
        print(f"\n📍 {country}")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        
        # Display results
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification}")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Data Sources:   {', '.join(result.data_sources[:2])}...")


def demo_convenience_function():
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 2: Convenience Function")
    print("="*70)
    
    # Use convenience function
    result = analyze_ambition("Brazil", "Q3 2024")
    
    print(f"\n{result.parameter_name} Score for Brazil:")
    print(f"  Score: {result.score}/10")
    print(f"  {result.justification}")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 3: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # This is how the UI will use agents
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("ambition", "Germany", "Q3 2024")
    print(f"Germany Ambition: {result.score}/10")
    print(f"Justification: {result.justification}")
    
    # Analyze subcategory (currently only has ambition)
    print("\n📊 Analyzing subcategory...")
    subcat_result = agent_service.analyze_subcategory(
        "regulation",
        "USA",
        "Q3 2024"
    )
    print(f"USA Regulation: {subcat_result.score}/10")
    print(f"Parameters analyzed: {len(subcat_result.parameter_scores)}")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 4: Scoring Rubric Visualization")
    print("="*70)
    
    agent = AmbitionAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Ambition:")
    print("-" * 60)
    print(f"{'Score':<8} {'GW Range':<20} {'Description'}")
    print("-" * 60)
    
    for level in rubric:
        max_gw = level.get('max_gw', float('inf'))
        max_display = '∞' if max_gw == float('inf') else str(max_gw)
        min_gw = level.get('min_gw', 0)
        score = level['score']
        description = level['description']
        
        print(
            f"{score:<8} "
            f"{min_gw}-{max_display:<17} "
            f"{description}"
        )
    
    print("\n📊 Example Scores:")
    test_cases = [
        ("Small Island Nation", 2.5),
        ("Developing Country", 12.0),
        ("Medium-sized Economy", 27.0),
        ("Major Economy", 85.0),
        ("China", 600.0),
    ]
    
    for name, gw in test_cases:
        # Create mock data
        mock_data = {"total_gw": gw, "solar": gw*0.5, "onshore_wind": gw*0.4, "offshore_wind": gw*0.1}
        score = agent._calculate_score(mock_data, name, "Q3 2024")
        print(f"  {name:<25} {gw:>6.1f} GW → Score: {score}/10")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 5: All Mock Countries Comparison")
    print("="*70)
    
    agent = AmbitionAgent()
    
    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        gw = agent.MOCK_DATA[country].get("total_gw", 0)
        results.append((country, result.score, gw))
    
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'Target (GW)'}")
    print("-" * 60)
    
    for i, (country, score, gw) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {score:<8.1f} {gw:.1f}")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("🚀 AMBITION AGENT DEMO")
    print("="*70)
    print("\nThis demo shows the Ambition Agent in action.")
    print("The agent analyzes government renewable energy targets.")
    print("\n")
    
    try:
        # Run demos
        demo_direct_agent_usage()
        demo_convenience_function()
        demo_service_layer()
        demo_scoring_rubric()
        demo_all_countries()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review the agent code in src/agents/parameter_agents/ambition_agent.py")
        print("2. Try modifying mock data in MOCK_DATA dictionary")
        print("3. Implement the next parameter agent (e.g., Support Scheme)")
        print("4. Integrate with UI by updating mock_service.py")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
