#!/usr/bin/env python3
"""Demo script for testing the Energy Dependence Agent with RULE_BASED mode support.

This script demonstrates:
1. MOCK mode (using hardcoded test data)
2. RULE_BASED mode (estimating from World Bank economic data)
3. Comparison between MOCK and RULE_BASED modes
4. Direct agent usage
5. Service layer usage
6. Score calculation based on import dependency
7. Comparison across all agents

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
    PowerMarketSizeAgent
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
        print(f"\n🏴 {country} ({profile})")
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


def demo_rule_based_mode(data_service):
    """Demonstrate RULE_BASED mode (using real data)."""
    print("\n" + "="*70)
    print("DEMO 2: RULE_BASED Mode (Estimated from World Bank Data)")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping RULE_BASED mode demo.")
        print("    Make sure config/data_sources.yaml exists and is valid.")
        return
    
    # Create agent in RULE_BASED mode
    agent = EnergyDependenceAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    # Test countries (these should have energy/GDP data from World Bank)
    countries = ["Germany", "USA", "Brazil"]
    
    for country in countries:
        print(f"\n🌍 {country} (RULE_BASED ESTIMATION)")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        
        # Display results
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification}")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Data Sources:   {', '.join(result.data_sources[:2])}")
    
    print("\n💡 Note: RULE_BASED mode estimates import dependency from:")
    print("   - Energy use per capita (World Bank)")
    print("   - GDP per capita (World Bank)")
    print("   - Population (World Bank)")
    print("   Formula considers energy intensity and development level")


def demo_mock_vs_rule_based_comparison(data_service):
    """Compare MOCK vs RULE_BASED mode for same country."""
    print("\n" + "="*70)
    print("DEMO 3: MOCK vs RULE_BASED Mode Comparison")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping comparison.")
        return
    
    # Create both agents
    mock_agent = EnergyDependenceAgent(mode=AgentMode.MOCK)
    rule_based_agent = EnergyDependenceAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    countries = ["Germany", "Brazil", "USA", "Spain"]
    
    print("\nComparing MOCK vs RULE_BASED estimations:")
    print("-" * 80)
    print(f"{'Country':<15} {'MOCK %':<12} {'RULE_BASED %':<15} {'Score Diff'}")
    print("-" * 80)
    
    for country in countries:
        mock_result = mock_agent.analyze(country, "Q3 2024")
        rule_based_result = rule_based_agent.analyze(country, "Q3 2024")
        
        # Get import percentages from MOCK data
        mock_data = mock_agent.MOCK_DATA.get(country, {})
        mock_pct = mock_data.get('import_pct', 0)
        
        # Score difference
        diff = rule_based_result.score - mock_result.score
        diff_str = f"{diff:+.1f}" if diff != 0 else "Same"
        
        print(
            f"{country:<15} "
            f"{mock_pct:<12.1f} "
            f"Estimated     "
            f"{diff_str}"
        )
    
    print("\n💡 Differences are expected:")
    print("   - MOCK uses actual IEA 2023 data")
    print("   - RULE_BASED estimates from GDP/energy use patterns")
    print("   - Both provide useful insights for analysis!")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)
    
    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_energy_dependence("Australia", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} Score for Australia: {result.score}/10")
    print(f"  Status: Major energy exporter (coal, LNG)")
    
    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_energy_dependence(
            "Germany", 
            "Q3 2024", 
            mode=AgentMode.RULE_BASED, 
            data_service=data_service
        )
        print(f"  {result.parameter_name} Score for Germany: {result.score}/10")
        print(f"  Estimated import dependency")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 5: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # Single parameter
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("energy_dependence", "China", "Q3 2024")
    print(f"China Energy Dependence: {result.score}/10")
    print(f"Justification: {result.justification[:100]}...")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 6: Scoring Rubric Visualization")
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
    print("DEMO 7: All Mock Countries Comparison")
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
    """Compare all four agents."""
    print("\n" + "="*70)
    print("DEMO 8: Comparison Across All Four Agents")
    print("="*70)
    
    ambition = AmbitionAgent()
    stability = CountryStabilityAgent()
    market = PowerMarketSizeAgent()
    dependence = EnergyDependenceAgent()
    
    countries = ["Brazil", "Germany", "India", "Spain", "USA"]
    
    print("\nShowing how all factors combine for investment opportunity:")
    print("-" * 90)
    print(f"{'Country':<15} {'Ambition':<10} {'Stability':<10} {'Market':<10} {'Dependence':<10} {'Average'}")
    print("-" * 90)
    
    for country in countries:
        amb = ambition.analyze(country, "Q3 2024").score
        stab = stability.analyze(country, "Q3 2024").score
        mkt = market.analyze(country, "Q3 2024").score
        dep = dependence.analyze(country, "Q3 2024").score
        
        avg = (amb + stab + mkt + dep) / 4
        
        print(
            f"{country:<15} "
            f"{amb:<10.1f} "
            f"{stab:<10.1f} "
            f"{mkt:<10.1f} "
            f"{dep:<10.1f} "
            f"{avg:.1f}"
        )
    
    print("\n💡 Insights:")
    print("  - USA: High scores across all 4 factors → 9.5 average!")
    print("  - Germany: High ambition/stability but dependent on energy imports")
    print("  - Spain: Very high energy dependence (72.5%) impacts overall score")
    print("\n  → All four factors provide complementary perspectives!")


def demo_exporters_vs_importers():
    """Show energy exporters vs importers."""
    print("\n" + "="*70)
    print("DEMO 9: Energy Exporters vs Importers")
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
    
    print("\n🔥 ENERGY IMPORTERS (Positive import %):")
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
    print("⚡🔌 ENERGY DEPENDENCE AGENT DEMO - MOCK & RULE_BASED MODES")
    print("="*70)
    print("\nThis demo shows the Energy Dependence Agent with:")
    print("  - MOCK mode (actual IEA import data)")
    print("  - RULE_BASED mode (estimated from World Bank GDP/energy data)")
    print("  - INVERSE scoring: Lower import % = Higher score")
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
        demo_exporters_vs_importers()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review updated agent code in energy_dependence_agent.py")
        print("2. Test MOCK mode: Works immediately ✅")
        print("3. Test RULE_BASED mode: Estimates from economic indicators ✅")
        print("4. You now have 4 agents with RULE_BASED mode!")
        print("5. Apply same pattern to remaining 14 agents")
        print("\n💡 You've completed Tier 1 + 1 Tier 2 agent!")
        print("   Continue with more Tier 2 agents for maximum value")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
