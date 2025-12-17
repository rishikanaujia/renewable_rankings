#!/usr/bin/env python3
"""Demo script for testing the Country Stability Agent.

This script demonstrates:
1. Direct agent usage
2. Service layer usage
3. Score calculation based on ECR ratings
4. Comparison with Ambition agent

Run from project root:
    python scripts/demo_country_stability_agent.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import CountryStabilityAgent, analyze_country_stability
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
    agent = CountryStabilityAgent(mode=AgentMode.MOCK)
    
    # Test countries with different risk levels
    countries = [
        ("Germany", "Low Risk"),
        ("Brazil", "Moderate Risk"),
        ("India", "Moderate Risk"),
        ("Argentina", "High Risk")
    ]
    
    for country, expected_risk in countries:
        print(f"\n📍 {country} ({expected_risk})")
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
    result = analyze_country_stability("Brazil", "Q3 2024")
    
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
    result = agent_service.analyze_parameter("country_stability", "Germany", "Q3 2024")
    print(f"Germany Country Stability: {result.score}/10")
    print(f"Justification: {result.justification}")
    
    # Analyze subcategory (now has ambition + country_stability)
    print("\n📊 Analyzing subcategory (Regulation)...")
    subcat_result = agent_service.analyze_subcategory(
        "regulation",
        "USA",
        "Q3 2024"
    )
    print(f"USA Regulation: {subcat_result.score}/10")
    print(f"Parameters analyzed: {len(subcat_result.parameter_scores)}")
    for param_score in subcat_result.parameter_scores:
        print(f"  - {param_score.parameter_name}: {param_score.score}/10")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 4: Scoring Rubric Visualization")
    print("="*70)
    
    agent = CountryStabilityAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Country Stability:")
    print("(Note: Lower ECR = Higher Stability = Higher Score)")
    print("-" * 60)
    print(f"{'Score':<8} {'ECR Range':<20} {'Description'}")
    print("-" * 60)
    
    for level in rubric:
        max_ecr = level.get('max_ecr', 100.0)
        # Display very large numbers as infinity
        max_display = '∞' if max_ecr >= 100 else str(max_ecr)
        min_ecr = level.get('min_ecr', 0.0)
        score = level['score']
        description = level['description']
        
        print(
            f"{score:<8} "
            f"{min_ecr}-{max_display:<17} "
            f"{description}"
        )
    
    print("\n📊 Example Scores:")
    test_cases = [
        ("Switzerland", 0.5, "Extremely stable"),
        ("USA", 1.2, "Very stable"),
        ("Brazil", 2.3, "Stable"),
        ("India", 3.2, "Moderately stable"),
        ("Argentina", 5.8, "Moderate instability"),
        ("Nigeria", 6.2, "Unstable"),
    ]
    
    for name, ecr, description in test_cases:
        # Create mock data
        mock_data = {"ecr_rating": ecr, "risk_category": description}
        score = agent._calculate_score(mock_data, name, "Q3 2024")
        print(f"  {name:<20} ECR {ecr:>4.1f} → Score: {score}/10")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 5: All Mock Countries Comparison")
    print("="*70)
    
    agent = CountryStabilityAgent()
    
    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        ecr = agent.MOCK_DATA[country].get("ecr_rating", 0)
        results.append((country, result.score, ecr))
    
    # Sort by score descending (best stability first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'ECR Rating'}")
    print("-" * 60)
    
    for i, (country, score, ecr) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {score:<8.1f} {ecr:.1f}")


def demo_comparison_with_ambition():
    """Compare Country Stability with Ambition scores."""
    print("\n" + "="*70)
    print("DEMO 6: Comparison with Ambition Agent")
    print("="*70)
    
    from src.agents.parameter_agents import AmbitionAgent
    
    stability_agent = CountryStabilityAgent()
    ambition_agent = AmbitionAgent()
    
    countries = ["Brazil", "Germany", "India", "USA"]
    
    print("\nShowing how different factors affect overall ranking:")
    print("-" * 60)
    print(f"{'Country':<15} {'Ambition':<12} {'Stability':<12} {'Average'}")
    print("-" * 60)
    
    for country in countries:
        stability_result = stability_agent.analyze(country, "Q3 2024")
        ambition_result = ambition_agent.analyze(country, "Q3 2024")
        
        avg = (stability_result.score + ambition_result.score) / 2
        
        print(
            f"{country:<15} "
            f"{ambition_result.score:<12.1f} "
            f"{stability_result.score:<12.1f} "
            f"{avg:.1f}"
        )
    
    print("\nInsight: High ambition + high stability = best investment opportunity!")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("🚀 COUNTRY STABILITY AGENT DEMO")
    print("="*70)
    print("\nThis demo shows the Country Stability Agent in action.")
    print("The agent analyzes political and economic risk using ECR ratings.")
    print("\n")
    
    try:
        # Run demos
        demo_direct_agent_usage()
        demo_convenience_function()
        demo_service_layer()
        demo_scoring_rubric()
        demo_all_countries()
        demo_comparison_with_ambition()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review the agent code in src/agents/parameter_agents/country_stability_agent.py")
        print("2. Try modifying mock ECR ratings in MOCK_DATA dictionary")
        print("3. Implement the next parameter agent (e.g., Support Scheme)")
        print("4. Notice how regulation subcategory now uses TWO parameters!")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
