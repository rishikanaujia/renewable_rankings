#!/usr/bin/env python3
"""Demo script for testing the Energy Dependence Agent.

This script demonstrates:
1. Direct agent usage
2. Service layer usage
3. Score calculation based on import dependency
4. Comparison across all five agents
5. Market Size Fundamentals now has 3 parameters!

Run from project root:
    python scripts/demo_energy_dependence_agent.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    EnergyDependenceAgent,
    analyze_energy_dependence,
    AmbitionAgent,
    CountryStabilityAgent,
    PowerMarketSizeAgent,
    ResourceAvailabilityAgent
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
    agent = EnergyDependenceAgent(mode=AgentMode.MOCK)
    
    # Test countries with different import dependencies
    countries = [
        ("USA", "Energy Independent"),
        ("Brazil", "Near Independent"),
        ("India", "Moderate-Low Dependence"),
        ("Germany", "High Dependence"),
        ("Spain", "Very High Dependence")
    ]
    
    for country, profile in countries:
        print(f"\n📍 {country} ({profile})")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        import_pct = data.get("import_pct", 0)
        status = data.get("status", "")
        
        # Display results
        print(f"Import %:       {import_pct:.1f}%")
        print(f"Status:         {status}")
        print(f"Score:          {result.score}/10")
        print(f"Confidence:     {result.confidence*100:.0f}%")


def demo_convenience_function():
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 2: Convenience Function")
    print("="*70)
    
    # Use convenience function
    result = analyze_energy_dependence("Australia", "Q3 2024")
    
    print(f"\n{result.parameter_name} Score for Australia:")
    print(f"  Score: {result.score}/10")
    print(f"  Status: Major energy exporter (coal, LNG)")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 3: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # Single parameter
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("energy_dependence", "China", "Q3 2024")
    print(f"China Energy Dependence: {result.score}/10")
    print(f"Justification: {result.justification[:150]}...")
    
    # Analyze subcategory (Market Size Fundamentals now has 3 parameters!)
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
    print("   - Energy Dependence (import reliance)")
    print("   → Even more comprehensive market assessment!")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 4: Scoring Rubric Visualization")
    print("="*70)
    
    agent = EnergyDependenceAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Energy Dependence:")
    print("(Note: INVERSE - Lower imports = Better = Higher score)")
    print("-" * 60)
    print(f"{'Score':<8} {'Import Range':<20} {'Description'}")
    print("-" * 60)
    
    # Sort by score descending (best first)
    for level in sorted(rubric, key=lambda x: x['score'], reverse=True):
        score = level['score']
        range_str = level['range']
        description = level['description']
        
        print(f"{score:<8} {range_str:<20} {description}")
    
    print("\n📊 Example Scores:")
    test_cases = [
        ("USA", 3.2, "Energy independent"),
        ("Brazil", 8.5, "Near independent"),
        ("China", 22.5, "Low dependence"),
        ("Germany", 63.5, "High dependence"),
        ("Spain", 72.5, "Very high dependence"),
    ]
    
    for name, import_pct, description in test_cases:
        mock_data = {
            "import_pct": import_pct,
            "production_mtoe": 100,
            "consumption_mtoe": 100 + import_pct,
            "status": description
        }
        score = agent._calculate_score(mock_data, name, "Q3 2024")
        print(f"  {name:<15} {import_pct:>5.1f}% imports → Score: {score}/10")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 5: All Mock Countries Comparison")
    print("="*70)
    
    agent = EnergyDependenceAgent()
    
    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA[country]
        import_pct = data.get("import_pct", 0)
        status = data.get("status", "")
        results.append((country, result.score, import_pct, status))
    
    # Sort by score descending (best energy security first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'Import %':<12} {'Status'}")
    print("-" * 75)
    
    for i, (country, score, import_pct, status) in enumerate(results, 1):
        # Format negative as "Net Exporter"
        if import_pct < 0:
            import_str = f"{import_pct:>10.1f}% (Exporter)"
        else:
            import_str = f"{import_pct:>10.1f}%"
        print(f"{i:<6} {country:<20} {score:<8.1f} {import_str:<12} {status}")
    
    print("\n💡 Key Insight:")
    print("  - Net exporters (Australia, Nigeria, South Africa) score 10/10")
    print("  - Energy independent countries (USA, Brazil) score 10/10")
    print("  - Import-dependent countries score lower based on dependency level")


def demo_comparison_all_agents():
    """Compare all five agents."""
    print("\n" + "="*70)
    print("DEMO 6: Comparison Across All Five Agents")
    print("="*70)
    
    ambition = AmbitionAgent()
    stability = CountryStabilityAgent()
    market = PowerMarketSizeAgent()
    resources = ResourceAvailabilityAgent()
    dependence = EnergyDependenceAgent()
    
    countries = ["Brazil", "Germany", "India", "Spain", "USA"]
    
    print("\nShowing how all factors combine for investment opportunity:")
    print("-" * 100)
    print(f"{'Country':<15} {'Ambition':<10} {'Stability':<10} {'Market':<10} {'Resources':<10} {'Dependence':<10} {'Average'}")
    print("-" * 100)
    
    for country in countries:
        amb = ambition.analyze(country, "Q3 2024").score
        stab = stability.analyze(country, "Q3 2024").score
        mkt = market.analyze(country, "Q3 2024").score
        res = resources.analyze(country, "Q3 2024").score
        dep = dependence.analyze(country, "Q3 2024").score
        
        avg = (amb + stab + mkt + res + dep) / 5
        
        print(
            f"{country:<15} "
            f"{amb:<10.1f} "
            f"{stab:<10.1f} "
            f"{mkt:<10.1f} "
            f"{res:<10.1f} "
            f"{dep:<10.1f} "
            f"{avg:.1f}"
        )
    
    print("\n💡 Insights:")
    print("  - USA: High scores across all 5 factors → 9.4 average!")
    print("  - Germany: High ambition/stability but dependent on energy imports")
    print("  - Spain: Very high energy dependence (72.5%) impacts overall score")
    print("\n  → All five factors provide complementary perspectives!")


def demo_exporters_vs_importers():
    """Show energy exporters vs importers."""
    print("\n" + "="*70)
    print("DEMO 7: Energy Exporters vs Importers")
    print("="*70)
    
    agent = EnergyDependenceAgent()
    
    print("\n🔋 ENERGY EXPORTERS (Negative import %):")
    print("-" * 70)
    
    exporters = []
    importers = []
    
    for country, data in agent.MOCK_DATA.items():
        import_pct = data.get("import_pct", 0)
        if import_pct < 0:
            exporters.append((country, import_pct, data))
        else:
            importers.append((country, import_pct, data))
    
    exporters.sort(key=lambda x: x[1])  # Most negative first
    
    print(f"{'Country':<20} {'Net Export %':<15} {'Status'}")
    print("-" * 70)
    for country, import_pct, data in exporters:
        export_pct = abs(import_pct)
        status = data.get("status", "")
        print(f"{country:<20} {export_pct:>13.1f}% {status}")
    
    print("\n📥 ENERGY IMPORTERS (Positive import %):")
    print("-" * 70)
    
    importers.sort(key=lambda x: x[1])  # Lowest dependency first
    
    print(f"{'Country':<20} {'Import %':<15} {'Score':<8} {'Status'}")
    print("-" * 70)
    for country, import_pct, data in importers:
        result = agent.analyze(country, "Q3 2024")
        status = data.get("status", "")
        print(f"{country:<20} {import_pct:>13.1f}% {result.score:<8.1f} {status}")
    
    print("\n💡 Key Observations:")
    print("  - Energy exporters have strategic advantage for renewable investment")
    print("  - High import dependence creates urgency for renewable development")
    print("  - Energy independence = better investment climate + energy security")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("⚡🔌 ENERGY DEPENDENCE AGENT DEMO")
    print("="*70)
    print("\nThis demo shows the Energy Dependence Agent in action.")
    print("The agent analyzes import dependency to assess energy security.")
    print("\n")
    
    try:
        # Run demos
        demo_direct_agent_usage()
        demo_convenience_function()
        demo_service_layer()
        demo_scoring_rubric()
        demo_all_countries()
        demo_comparison_all_agents()
        demo_exporters_vs_importers()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review the agent code in src/agents/parameter_agents/energy_dependence_agent.py")
        print("2. Try modifying mock import % data in MOCK_DATA dictionary")
        print("3. Implement the next parameter agent (e.g., Renewables Penetration or Expected Return)")
        print("4. Market Size Fundamentals subcategory now has 3 parameters (75% complete)!")
        print("5. You now have 5 agents spanning 2 subcategories!")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
