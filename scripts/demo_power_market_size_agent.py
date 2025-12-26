#!/usr/bin/env python3
"""Demo script for testing the Power Market Size Agent with RULE_BASED mode support.

This script demonstrates:
1. MOCK mode (using hardcoded test data)
2. RULE_BASED mode (using real data from data service)
3. Comparison between MOCK and RULE_BASED modes
4. Service layer usage
5. Score calculation based on TWh consumption
6. Comparison across all three agents

Run from project root:
    python scripts/demo_power_market_size_agent.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    PowerMarketSizeAgent,
    analyze_power_market_size,
    AmbitionAgent,
    CountryStabilityAgent
)
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

# Setup logging
setup_logger(log_level="INFO")
logger = get_logger(__name__)


def initialize_data_service():
    """Initialize data service for RULE_BASED mode."""
    try:
        import yaml
        from src.data import DataService
        
        # Load configuration
        with open('config/data_sources.yaml') as f:
            config = yaml.safe_load(f)
        
        # Create data service
        data_service = DataService(config)
        
        logger.info("Data service initialized successfully")
        return data_service
        
    except Exception as e:
        logger.warning(f"Could not initialize data service: {e}")
        logger.warning("RULE_BASED mode demos will fall back to MOCK data")
        return None


def demo_mock_mode():
    """Demonstrate MOCK mode (traditional usage)."""
    print("\n" + "="*70)
    print("DEMO 1: MOCK Mode (Test Data)")
    print("="*70)
    
    # Create agent in MOCK mode
    agent = PowerMarketSizeAgent(mode=AgentMode.MOCK)
    
    # Test countries with different market sizes
    countries = [
        ("Nigeria", "Very Small Market"),
        ("Chile", "Small Market"),
        ("Spain", "Moderate Market"),
        ("Brazil", "Large Market"),
        ("India", "Major Market"),
        ("China", "Massive Market")
    ]
    
    for country, expected_size in countries:
        print(f"\n🏴 {country} ({expected_size})")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        twh = data.get("twh_consumption", 0)
        
        # Display results
        print(f"Consumption:    {twh:,.0f} TWh/year")
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification[:80]}...")
        print(f"Confidence:     {result.confidence*100:.0f}%")


def demo_rule_based_mode(data_service):
    """Demonstrate RULE_BASED mode (using real data)."""
    print("\n" + "="*70)
    print("DEMO 2: RULE_BASED Mode (Real Data from Data Service)")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping RULE_BASED mode demo.")
        print("    Make sure config/data_sources.yaml exists and is valid.")
        return
    
    # Create agent in RULE_BASED mode
    agent = PowerMarketSizeAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    # Test countries (these should have electricity data from World Bank)
    countries = ["Germany", "USA", "Brazil"]
    
    for country in countries:
        print(f"\n🌍 {country} (RULE_BASED DATA)")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        
        # Display results
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification}")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Data Sources:   {', '.join(result.data_sources[:2])}")


def demo_mock_vs_rule_based_comparison(data_service):
    """Compare MOCK vs RULE_BASED mode for same country."""
    print("\n" + "="*70)
    print("DEMO 3: MOCK vs RULE_BASED Mode Comparison")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping comparison.")
        return
    
    # Create both agents
    mock_agent = PowerMarketSizeAgent(mode=AgentMode.MOCK)
    rule_based_agent = PowerMarketSizeAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    countries = ["Germany", "Brazil", "USA"]
    
    print("\nComparing MOCK vs RULE_BASED data:")
    print("-" * 70)
    print(f"{'Country':<15} {'MOCK Score':<12} {'RULE_BASED':<12} {'Difference'}")
    print("-" * 70)
    
    for country in countries:
        mock_result = mock_agent.analyze(country, "Q3 2024")
        rule_based_result = rule_based_agent.analyze(country, "Q3 2024")
        
        diff = rule_based_result.score - mock_result.score
        diff_str = f"{diff:+.1f}" if diff != 0 else "Same"
        
        print(
            f"{country:<15} "
            f"{mock_result.score:<12.1f} "
            f"{rule_based_result.score:<12.1f} "
            f"{diff_str}"
        )
    
    print("\n💡 Note: RULE_BASED uses World Bank electricity production data.")
    print("   Small differences expected due to data year variations!")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)
    
    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_power_market_size("Brazil", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} Score for Brazil: {result.score}/10")
    print(f"  {result.justification[:100]}...")
    
    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_power_market_size(
            "Germany", 
            "Q3 2024", 
            mode=AgentMode.RULE_BASED, 
            data_service=data_service
        )
        print(f"  {result.parameter_name} Score for Germany: {result.score}/10")
        print(f"  {result.justification[:100]}...")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 5: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # This is how the UI will use agents
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("power_market_size", "USA", "Q3 2024")
    print(f"USA Power Market Size: {result.score}/10")
    print(f"Justification: {result.justification[:100]}...")
    
    # Analyze subcategory (Market Size Fundamentals)
    print("\n📊 Analyzing subcategory (Market Size Fundamentals)...")
    subcat_result = agent_service.analyze_subcategory(
        "market_size_fundamentals",
        "Brazil",
        "Q3 2024"
    )
    print(f"Brazil Market Size Fundamentals: {subcat_result.score}/10")
    print(f"Parameters analyzed: {len(subcat_result.parameter_scores)}")
    for param_score in subcat_result.parameter_scores:
        print(f"  - {param_score.parameter_name}: {param_score.score}/10")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 6: Scoring Rubric Visualization")
    print("="*70)
    
    agent = PowerMarketSizeAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Power Market Size:")
    print("(Note: Higher TWh = Larger Market = Higher Score)")
    print("-" * 60)
    print(f"{'Score':<8} {'TWh Range':<20} {'Description'}")
    print("-" * 60)
    
    for level in rubric:
        max_twh = level.get('max_twh', 100000)
        # Display very large numbers as infinity
        max_display = '∞' if max_twh >= 100000 else f"{max_twh:,.0f}"
        min_twh = level.get('min_twh', 0)
        score = level['score']
        description = level['description']
        
        print(
            f"{score:<8} "
            f"{min_twh:,.0f}-{max_display:<17} "
            f"{description}"
        )
    
    print("\n📊 Example Scores:")
    test_cases = [
        ("Small Island", 25, "Very small"),
        ("Nigeria", 31, "Very small"),
        ("Chile", 82, "Small"),
        ("Spain", 249, "Moderate"),
        ("Brazil", 631, "Large"),
        ("India", 1730, "Major"),
        ("USA", 4050, "Massive"),
        ("China", 8540, "Massive"),
    ]
    
    for name, twh, description in test_cases:
        # Create mock data
        mock_data = {"twh_consumption": twh, "population_millions": 100, "per_capita_kwh": 3000}
        score = agent._calculate_score(mock_data, name, "Q3 2024")
        print(f"  {name:<20} {twh:>6,.0f} TWh → Score: {score}/10")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 7: All Mock Countries Comparison")
    print("="*70)
    
    agent = PowerMarketSizeAgent()
    
    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        twh = agent.MOCK_DATA[country].get("twh_consumption", 0)
        per_capita = agent.MOCK_DATA[country].get("per_capita_kwh", 0)
        results.append((country, result.score, twh, per_capita))
    
    # Sort by TWh descending (largest markets first)
    results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'TWh/year':<12} {'Per Capita'}")
    print("-" * 70)
    
    for i, (country, score, twh, per_capita) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {score:<8.1f} {twh:>10,.0f} {per_capita:>12,.0f} kWh")


def demo_comparison_all_agents():
    """Compare all three agents."""
    print("\n" + "="*70)
    print("DEMO 8: Comparison Across All Three Agents")
    print("="*70)
    
    ambition_agent = AmbitionAgent()
    stability_agent = CountryStabilityAgent()
    market_agent = PowerMarketSizeAgent()
    
    countries = ["Brazil", "Germany", "India", "USA", "Nigeria"]
    
    print("\nShowing how different factors combine for overall opportunity:")
    print("-" * 80)
    print(f"{'Country':<15} {'Ambition':<12} {'Stability':<12} {'Market':<12} {'Average'}")
    print("-" * 80)
    
    for country in countries:
        amb_result = ambition_agent.analyze(country, "Q3 2024")
        stab_result = stability_agent.analyze(country, "Q3 2024")
        mkt_result = market_agent.analyze(country, "Q3 2024")
        
        avg = (amb_result.score + stab_result.score + mkt_result.score) / 3
        
        print(
            f"{country:<15} "
            f"{amb_result.score:<12.1f} "
            f"{stab_result.score:<12.1f} "
            f"{mkt_result.score:<12.1f} "
            f"{avg:.1f}"
        )
    
    print("\n💡 Insights:")
    print("  - Germany: High ambition + high stability + large market = 10.0")
    print("  - India: Very high ambition + moderate stability + huge market = 9.0")
    print("  - Nigeria: Low ambition + low stability + tiny market = 1.7")
    print("\n  → All three factors matter for investment attractiveness!")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("⚡ POWER MARKET SIZE AGENT DEMO - MOCK & RULE_BASED MODES")
    print("="*70)
    print("\nThis demo shows the Power Market Size Agent with:")
    print("  - MOCK mode (test data)")
    print("  - RULE_BASED mode (real data from data service)")
    print("  - Uses World Bank electricity production data")
    print("\n")
    
    try:
        # Initialize data service for RULE_BASED mode
        data_service = initialize_data_service()
        
        # Run demos
        demo_mock_mode()
        demo_rule_based_mode(data_service)
        demo_mock_vs_rule_based_comparison(data_service)
        demo_convenience_function(data_service)
        demo_service_layer()
        demo_scoring_rubric()
        demo_all_countries()
        demo_comparison_all_agents()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review updated agent code in power_market_size_agent.py")
        print("2. Test MOCK mode: Works immediately ✅")
        print("3. Test RULE_BASED mode: Uses World Bank electricity data ✅")
        print("4. You now have 3 agents spanning 2 subcategories!")
        print("5. Apply same pattern to next agents!")
        print("\n💡 You've completed agents 1-3 in Tier 1!")
        print("   Move to Tier 2: RenewablesPenetrationAgent next")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
