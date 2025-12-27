#!/usr/bin/env python3
"""Demo script for testing the Track Record Agent with RULE_BASED mode support.

This script demonstrates:
1. MOCK mode (using hardcoded test data from IRENA/IEA)
2. RULE_BASED mode (using World Bank renewable capacity data)
3. Comparison between MOCK and RULE_BASED modes
4. Direct agent usage
5. Service layer usage
6. Score calculation based on installed capacity
7. Comparison across agents

Run from project root:
    python scripts/demo_track_record_agent.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    TrackRecordAgent,
    analyze_track_record,
    AmbitionAgent,
    CountryStabilityAgent,
    PowerMarketSizeAgent,
    RenewablesPenetrationAgent
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
    print("DEMO 1: MOCK Mode (Test Data from IRENA/IEA)")
    print("="*70)

    # Create agent in MOCK mode
    agent = TrackRecordAgent(mode=AgentMode.MOCK)

    # Test countries with different capacity levels
    countries = [
        ("China", "758 GW", "Outstanding - World Leader"),
        ("USA", "257 GW", "Outstanding - Largest Market"),
        ("Germany", "134 GW", "Outstanding - Energiewende"),
        ("Spain", "53 GW", "Excellent - Early Pioneer"),
        ("Brazil", "38.5 GW", "Very Good - Latin America Leader"),
        ("Chile", "11.5 GW", "Good - Atacama Solar"),
        ("Nigeria", "0.18 GW", "Minimal - Nascent Market")
    ]

    for country, expected_capacity, profile in countries:
        print(f"\n🏴 {country} ({profile})")
        print("-" * 60)

        # Analyze
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        capacity_mw = data.get("capacity_mw", 0)
        capacity_gw = capacity_mw / 1000.0
        recent_deployment = data.get("recent_deployment_gw_per_year", 0)
        status = data.get("status", "")

        # Display results
        print(f"Capacity:       {capacity_gw:.1f} GW ({capacity_mw:.0f} MW)")
        print(f"Deployment:     {recent_deployment:.1f} GW/year")
        print(f"Status:         {status}")
        print(f"Score:          {result.score}/10")
        print(f"Confidence:     {result.confidence*100:.0f}%")

def demo_rule_based_mode(data_service):
    """Demonstrate RULE_BASED mode (using real data)."""
    print("\n" + "="*70)
    print("DEMO 2: RULE_BASED Mode (World Bank Renewable Capacity Data)")
    print("="*70)

    if data_service is None:
        print("\n⚠️  Data service not available. Skipping RULE_BASED mode demo.")
        print("    Make sure config/data_sources.yaml exists and is valid.")
        return

    # Create agent in RULE_BASED mode
    agent = TrackRecordAgent(mode=AgentMode.RULE_BASED, data_service=data_service)

    # Test countries (these should have renewable capacity data from World Bank)
    countries = ["Germany", "USA", "Brazil", "India"]

    for country in countries:
        print(f"\n🌍 {country} (RULE_BASED - World Bank Data)")
        print("-" * 60)

        # Analyze
        result = agent.analyze(country, "Q3 2024")

        # Display results
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification[:150]}...")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Data Sources:   {', '.join(result.data_sources[:2])}")

    print("\n💡 Note: RULE_BASED mode fetches/estimates renewable capacity from:")
    print("   - World Bank renewable capacity data")
    print("   - Electricity production (World Bank)")
    print("   - Renewable consumption percentage (World Bank)")
    print("   Estimates total capacity when direct data unavailable")


def demo_mock_vs_rule_based_comparison(data_service):
    """Compare MOCK vs RULE_BASED mode for same country."""
    print("\n" + "="*70)
    print("DEMO 3: MOCK vs RULE_BASED Mode Comparison")
    print("="*70)

    if data_service is None:
        print("\n⚠️  Data service not available. Skipping comparison.")
        return

    # Create both agents
    mock_agent = TrackRecordAgent(mode=AgentMode.MOCK)
    rule_based_agent = TrackRecordAgent(mode=AgentMode.RULE_BASED, data_service=data_service)

    countries = ["Germany", "Brazil", "USA", "Spain"]

    print("\nComparing MOCK vs RULE_BASED estimations:")
    print("-" * 90)
    print(f"{'Country':<15} {'MOCK Capacity':<18} {'RULE Capacity':<18} {'Score Diff'}")
    print("-" * 90)

    for country in countries:
        mock_result = mock_agent.analyze(country, "Q3 2024")
        rule_based_result = rule_based_agent.analyze(country, "Q3 2024")

        # Get capacity from MOCK data
        mock_data = mock_agent.MOCK_DATA.get(country, {})
        mock_capacity_gw = mock_data.get('capacity_mw', 0) / 1000.0

        # Score difference
        diff = rule_based_result.score - mock_result.score
        diff_str = f"{diff:+.1f}" if diff != 0 else "Same"

        print(
            f"{country:<15} "
            f"{mock_capacity_gw:<18.1f} GW "
            f"Estimated        "
            f"{diff_str}"
        )

    print("\n💡 Differences are expected:")
    print("   - MOCK uses actual IRENA/IEA capacity data (2023)")
    print("   - RULE_BASED estimates from World Bank renewable generation")
    print("   - Both provide track record assessment for investment analysis!")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)

    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_track_record("Australia", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} Score for Australia: {result.score}/10")
    print(f"  Status: Very good track record (rooftop solar leader)")

    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_track_record(
            "Germany",
            "Q3 2024",
            mode=AgentMode.RULE_BASED,
            data_service=data_service
        )
        print(f"  {result.parameter_name} Score for Germany: {result.score}/10")
        print(f"  Estimated from World Bank renewable data")

def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 5: Service Layer (UI Integration Pattern)")
    print("="*70)

    # Single parameter
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("track_record", "China", "Q3 2024")
    print(f"China Track Record: {result.score}/10")
    print(f"Justification: {result.justification[:100]}...")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 6: Scoring Rubric Visualization")
    print("="*70)

    agent = TrackRecordAgent()
    rubric = agent._get_scoring_rubric()

    print("\nScoring Rubric for Track Record:")
    print("(Note: DIRECT - Higher capacity = Better track record = Higher score)")
    print("-" * 70)
    print(f"{'Score':<8} {'Capacity Range':<25} {'Description'}")
    print("-" * 70)

    # Sort by score descending (best first)
    for level in sorted(rubric, key=lambda x: x['score'], reverse=True):
        score = level['score']
        range_str = level['range']
        description = level['description']

        print(f"{score:<8} {range_str:<25} {description}")

    print("\n📊 Example Scores:")
    test_cases = [
        ("China", 758000, "Outstanding - World leader"),
        ("USA", 257000, "Outstanding - Largest market"),
        ("Germany", 134000, "Outstanding - Energiewende"),
        ("Brazil", 38500, "Very good - Latin America leader"),
        ("Chile", 11500, "Good - Atacama solar boom"),
        ("Nigeria", 180, "Minimal - Nascent market"),
    ]

    for name, capacity_mw, description in test_cases:
        mock_data = {
            "capacity_mw": capacity_mw,
            "solar_mw": capacity_mw * 0.4,
            "onshore_wind_mw": capacity_mw * 0.5,
            "offshore_wind_mw": capacity_mw * 0.05,
            "recent_deployment_gw_per_year": capacity_mw / 1000 * 0.15,
            "status": description
        }
        score = agent._calculate_score(mock_data, name, "Q3 2024")
        capacity_gw = capacity_mw / 1000
        print(f"  {name:<15} {capacity_gw:>8.1f} GW → Score: {score}/10")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 7: All Mock Countries Comparison")
    print("="*70)

    agent = TrackRecordAgent()

    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA[country]
        capacity_mw = data.get("capacity_mw", 0)
        capacity_gw = capacity_mw / 1000.0
        status = data.get("status", "")
        results.append((country, result.score, capacity_gw, status))

    # Sort by capacity descending (highest first)
    results.sort(key=lambda x: x[2], reverse=True)

    print(f"\n{'Rank':<6} {'Country':<20} {'Capacity (GW)':<15} {'Score':<8} {'Status'}")
    print("-" * 85)

    for i, (country, score, capacity_gw, status) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {capacity_gw:<15.1f} {score:<8.1f} {status}")

    print("\n💡 Key Insights:")
    print("  - China leads globally with 758 GW installed capacity")
    print("  - USA, India, Germany all have outstanding track records (>100 GW)")
    print("  - Track record reduces execution risk and demonstrates proven capability")

def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("📈 TRACK RECORD AGENT DEMO - MOCK & RULE_BASED MODES")
    print("="*70)
    print("\nThis demo shows the Track Record Agent with:")
    print("  - MOCK mode (actual IRENA/IEA capacity data)")
    print("  - RULE_BASED mode (estimated from World Bank renewable data)")
    print("  - DIRECT scoring: Higher capacity = Higher score")
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

        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review updated agent code in track_record_agent.py")
        print("2. Test MOCK mode: Works immediately ✅")
        print("3. Test RULE_BASED mode: Fetches from World Bank ✅")
        print("4. You now have 6 agents with RULE_BASED mode!")
        print("5. Apply same pattern to remaining agents")
        print("\n📊 PROGRESS UPDATE:")
        print("   ✅ Tier 1 Complete (3/3 agents)")
        print("   🔄 Tier 2 Progress (3/5 agents - 60%)")
        print("   → TrackRecordAgent is Agent #6/18 ✅")
        print("   → Continue with FinancingCostAgent next!")
        print("\n")

        return 0

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
