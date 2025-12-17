#!/usr/bin/env python3
"""Demo script for testing the Resource Availability Agent.

This script demonstrates:
1. Direct agent usage
2. Service layer usage
3. Score calculation based on solar + wind resources
4. Comparison across all four agents

Run from project root:
    python scripts/demo_resource_availability_agent.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    ResourceAvailabilityAgent,
    analyze_resource_availability,
    AmbitionAgent,
    CountryStabilityAgent,
    PowerMarketSizeAgent
)
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
    agent = ResourceAvailabilityAgent(mode=AgentMode.MOCK)
    
    # Test countries with different resource profiles
    countries = [
        ("Germany", "Moderate Solar, Good Wind"),
        ("India", "Outstanding Solar, Good Wind"),
        ("Chile", "World-class Solar, Excellent Wind"),
        ("UK", "Low Solar, Excellent Wind"),
    ]
    
    for country, profile in countries:
        print(f"\n📍 {country} ({profile})")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        solar = data.get("solar_kwh_m2_day", 0)
        wind = data.get("wind_m_s", 0)
        
        # Display results
        print(f"Solar:          {solar:.1f} kWh/m²/day")
        print(f"Wind:           {wind:.1f} m/s")
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification}")
        print(f"Confidence:     {result.confidence*100:.0f}%")


def demo_convenience_function():
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 2: Convenience Function")
    print("="*70)
    
    # Use convenience function
    result = analyze_resource_availability("Chile", "Q3 2024")
    
    print(f"\n{result.parameter_name} Score for Chile:")
    print(f"  Score: {result.score}/10")
    print(f"  {result.justification}")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 3: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # Single parameter
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("resource_availability", "Australia", "Q3 2024")
    print(f"Australia Resource Availability: {result.score}/10")
    print(f"Justification: {result.justification}")
    
    # Analyze subcategory (Market Size Fundamentals now has 2 parameters!)
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
    
    print("\n💡 Market Size Fundamentals now combines:")
    print("   - Power Market Size (absolute TWh consumption)")
    print("   - Resource Availability (solar + wind quality)")
    print("   → More comprehensive market assessment!")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 4: Scoring Rubric Visualization")
    print("="*70)
    
    agent = ResourceAvailabilityAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Resource Availability:")
    print("(Note: Based on combined solar + wind score)")
    print("-" * 60)
    print(f"{'Score':<8} {'Combined Range':<20} {'Description'}")
    print("-" * 60)
    
    for level in rubric:
        max_combined = level.get('max_combined', 100.0)
        max_display = '∞' if max_combined >= 100 else f"{max_combined:.1f}"
        min_combined = level.get('min_combined', 0.0)
        score = level['score']
        description = level['description']
        
        print(
            f"{score:<8} "
            f"{min_combined:.1f}-{max_display:<17} "
            f"{description}"
        )
    
    print("\n📊 How Combined Score is Calculated:")
    print("  1. Normalize solar: (kWh/m²/day ÷ 2.5) × 10")
    print("  2. Normalize wind: (m/s ÷ 1.0) × 10")
    print("  3. Combined = (Solar × 0.5) + (Wind × 0.5)")
    
    print("\n📊 Example Calculations:")
    test_cases = [
        ("Germany", 3.0, 6.0, "Moderate solar, good wind"),
        ("India", 5.8, 6.0, "Outstanding solar, good wind"),
        ("Chile", 6.5, 8.5, "World-class solar, excellent wind"),
        ("UK", 2.5, 8.0, "Low solar, excellent offshore wind"),
    ]
    
    for name, solar, wind, description in test_cases:
        mock_data = {
            "solar_kwh_m2_day": solar,
            "wind_m_s": wind,
            "solar_quality": description,
            "wind_quality": description
        }
        combined = agent._calculate_combined_resource_score(mock_data, name)
        score = agent._calculate_score(combined, name, "Q3 2024")
        print(f"  {name:<15} Solar {solar:.1f}, Wind {wind:.1f} → Combined {combined:.1f} → Score: {score}/10")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 5: All Mock Countries Comparison")
    print("="*70)
    
    agent = ResourceAvailabilityAgent()
    
    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA[country]
        solar = data.get("solar_kwh_m2_day", 0)
        wind = data.get("wind_m_s", 0)
        combined = agent._calculate_combined_resource_score(data, country)
        results.append((country, result.score, solar, wind, combined))
    
    # Sort by score descending (best resources first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'Solar':<10} {'Wind':<10} {'Combined'}")
    print("-" * 75)
    
    for i, (country, score, solar, wind, combined) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {score:<8.1f} {solar:>8.1f} {wind:>8.1f} m/s {combined:>10.1f}")


def demo_comparison_all_agents():
    """Compare all four agents."""
    print("\n" + "="*70)
    print("DEMO 6: Comparison Across All Four Agents")
    print("="*70)
    
    ambition = AmbitionAgent()
    stability = CountryStabilityAgent()
    market = PowerMarketSizeAgent()
    resources = ResourceAvailabilityAgent()
    
    countries = ["Brazil", "Germany", "India", "Chile", "UK"]
    
    print("\nShowing how all factors combine for investment opportunity:")
    print("-" * 90)
    print(f"{'Country':<15} {'Ambition':<12} {'Stability':<12} {'Market':<12} {'Resources':<12} {'Average'}")
    print("-" * 90)
    
    for country in countries:
        amb = ambition.analyze(country, "Q3 2024").score
        stab = stability.analyze(country, "Q3 2024").score
        mkt = market.analyze(country, "Q3 2024").score
        res = resources.analyze(country, "Q3 2024").score
        
        avg = (amb + stab + mkt + res) / 4
        
        print(
            f"{country:<15} "
            f"{amb:<12.1f} "
            f"{stab:<12.1f} "
            f"{mkt:<12.1f} "
            f"{res:<12.1f} "
            f"{avg:.1f}"
        )
    
    print("\n💡 Insights:")
    print("  - Chile: Outstanding resources (10.0) despite smaller market (2.0)")
    print("  - UK: Excellent wind compensates for low solar → 8.0 resources")
    print("  - India: High scores across ambition, market, and resources → 8.8 avg")
    print("\n  → All four factors provide complementary perspectives!")


def demo_resource_breakdown():
    """Show solar vs wind resource breakdown."""
    print("\n" + "="*70)
    print("DEMO 7: Solar vs Wind Resource Breakdown")
    print("="*70)
    
    agent = ResourceAvailabilityAgent()
    
    print("\nCountries sorted by solar resources:")
    print("-" * 70)
    
    solar_results = []
    for country, data in agent.MOCK_DATA.items():
        solar = data.get("solar_kwh_m2_day", 0)
        solar_quality = data.get("solar_quality", "")
        solar_results.append((country, solar, solar_quality))
    
    solar_results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Country':<20} {'Solar (kWh/m²/day)':<25} {'Quality'}")
    print("-" * 70)
    for country, solar, quality in solar_results[:10]:
        print(f"{country:<20} {solar:>20.1f} {quality}")
    
    print("\nCountries sorted by wind resources:")
    print("-" * 70)
    
    wind_results = []
    for country, data in agent.MOCK_DATA.items():
        wind = data.get("wind_m_s", 0)
        wind_quality = data.get("wind_quality", "")
        wind_results.append((country, wind, wind_quality))
    
    wind_results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Country':<20} {'Wind Speed (m/s)':<25} {'Quality'}")
    print("-" * 70)
    for country, wind, quality in wind_results[:10]:
        print(f"{country:<20} {wind:>20.1f} {quality}")
    
    print("\n💡 Key Observations:")
    print("  - Chile has world-class BOTH solar (Atacama) and wind (Patagonia)")
    print("  - UK has low solar but excellent offshore wind → balanced score")
    print("  - Some countries excel in one resource type, others in both")
    print("\n  → Equal weighting (50/50) rewards balanced resource portfolios!")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("☀️💨 RESOURCE AVAILABILITY AGENT DEMO")
    print("="*70)
    print("\nThis demo shows the Resource Availability Agent in action.")
    print("The agent analyzes solar irradiation and wind speed resources.")
    print("\n")
    
    try:
        # Run demos
        demo_direct_agent_usage()
        demo_convenience_function()
        demo_service_layer()
        demo_scoring_rubric()
        demo_all_countries()
        demo_comparison_all_agents()
        demo_resource_breakdown()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review the agent code in src/agents/parameter_agents/resource_availability_agent.py")
        print("2. Try modifying mock solar/wind data in MOCK_DATA dictionary")
        print("3. Implement the next parameter agent (e.g., Expected Return)")
        print("4. Market Size Fundamentals subcategory now has 2 parameters!")
        print("5. You now have 4 agents spanning 2 subcategories!")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
