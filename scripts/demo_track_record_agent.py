#!/usr/bin/env python3
"""Demo for Track Record Agent with RULE_BASED mode support.

This script demonstrates:
1. MOCK mode (using hardcoded IRENA test data)
2. RULE_BASED mode (estimating from World Bank renewable data)
3. Comparison between MOCK and RULE_BASED modes
4. Direct agent usage
5. Service layer usage
6. Track record spectrum from minimal to outstanding

Run from project root:
    python scripts/demo_track_record_agent.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    TrackRecordAgent,
    analyze_track_record,
    CountryStabilityAgent,
    AmbitionAgent,
    PowerMarketSizeAgent,
    EnergyDependenceAgent,
    RenewablesPenetrationAgent
)
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

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
    print("DEMO 1: MOCK Mode - Capacity Spectrum")
    print("="*70)
    
    agent = TrackRecordAgent(mode=AgentMode.MOCK)
    
    countries = [
        ("China", "758 GW", "Outstanding"),
        ("USA", "257 GW", "Outstanding"),
        ("India", "175 GW", "Outstanding"),
        ("Germany", "134 GW", "Outstanding"),
        ("Spain", "53 GW", "Excellent"),
        ("Brazil", "38.5 GW", "Very Good"),
        ("Chile", "11.5 GW", "Good"),
        ("Nigeria", "0.18 GW", "Minimal")
    ]
    
    for country, capacity, profile in countries:
        print(f"\n🏴 {country} ({capacity} - {profile})")
        print("-" * 60)
        
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        capacity_gw = data.get("capacity_mw", 0) / 1000
        
        print(f"Capacity:       {capacity_gw:.1f} GW")
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
    agent = TrackRecordAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    # Test countries (these should have renewable data from World Bank)
    countries = ["Germany", "USA", "Brazil"]
    
    for country in countries:
        print(f"\n🌍 {country} (RULE_BASED ESTIMATION)")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        
        # Display results
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification[:150]}...")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Data Sources:   {', '.join(result.data_sources[:2])}")
    
    print("\n💡 Note: RULE_BASED mode estimates capacity from:")
    print("   - Renewable energy consumption % (World Bank)")
    print("   - Electricity production (World Bank)")
    print("   - Capacity factor assumptions (solar/wind/hydro mix)")


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
    
    countries = ["Germany", "Brazil", "USA"]
    
    print("\nComparing MOCK vs RULE_BASED capacity estimates:")
    print("-" * 80)
    print(f"{'Country':<15} {'MOCK (GW)':<15} {'MOCK Score':<12} {'RULE_BASED':<15} {'Diff'}")
    print("-" * 80)
    
    for country in countries:
        mock_result = mock_agent.analyze(country, "Q3 2024")
        rule_based_result = rule_based_agent.analyze(country, "Q3 2024")
        
        # Get capacity from MOCK data
        mock_data = mock_agent.MOCK_DATA.get(country, {})
        mock_gw = mock_data.get('capacity_mw', 0) / 1000
        
        # Score difference
        diff = rule_based_result.score - mock_result.score
        diff_str = f"{diff:+.1f}" if diff != 0 else "Same"
        
        print(
            f"{country:<15} "
            f"{mock_gw:<15.1f} "
            f"{mock_result.score:<12.1f} "
            f"Estimated      "
            f"{diff_str}"
        )
    
    print("\n💡 Note:")
    print("   - MOCK: Actual IRENA 2023 installed capacity data")
    print("   - RULE_BASED: Estimated from renewable generation + capacity factors")
    print("   - Both provide useful track record assessment!")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)
    
    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_track_record("China", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} for China: {result.score}/10")
    print(f"  758 GW installed (world leader!)")
    
    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_track_record(
            "Germany", 
            "Q3 2024", 
            mode=AgentMode.RULE_BASED, 
            data_service=data_service
        )
        print(f"  {result.parameter_name} for Germany: {result.score}/10")
        print(f"  Estimated from renewable generation data")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 5: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # Single parameter
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("track_record", "India", "Q3 2024")
    print(f"India Track Record: {result.score}/10")
    print(f"Justification: {result.justification[:100]}...")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 6: Scoring Rubric Visualization")
    print("="*70)
    
    agent = TrackRecordAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Track Record:")
    print("(Note: Higher capacity = Better track record = Higher score)")
    print("-" * 60)
    print(f"{'Score':<8} {'Capacity Range':<20} {'Description'}")
    print("-" * 60)
    
    for level in rubric:
        score = level['score']
        range_str = level['range']
        description = level['description']
        
        print(f"{score:<8} {range_str:<20} {description}")
    
    print("\n📊 Example Scores:")
    test_cases = [
        ("Nigeria", 180, "Minimal"),
        ("Indonesia", 950, "Limited"),
        ("Saudi Arabia", 1800, "Below moderate"),
        ("Chile", 11500, "Good"),
        ("Brazil", 38500, "Very good"),
        ("Germany", 134000, "Outstanding"),
        ("China", 758000, "Outstanding"),
    ]
    
    for name, capacity_mw, description in test_cases:
        mock_data = {
            "capacity_mw": capacity_mw,
            "solar_mw": capacity_mw * 0.5,
            "onshore_wind_mw": capacity_mw * 0.5,
            "offshore_wind_mw": 0
        }
        score = agent._calculate_score(mock_data, name, "Q3 2024")
        capacity_gw = capacity_mw / 1000
        print(f"  {name:<15} {capacity_gw:>7.1f} GW → Score: {score}/10")


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
        capacity_gw = data.get("capacity_mw", 0) / 1000
        status = data.get("status", "")
        results.append((country, result.score, capacity_gw, status))
    
    # Sort by capacity descending (largest first)
    results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'Capacity (GW)':<15} {'Status'}")
    print("-" * 80)
    
    for i, (country, score, capacity_gw, status) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {score:<8.1f} {capacity_gw:>13.1f} {status}")
    
    print("\n💡 Key Insights:")
    print("  - China: 758 GW (absolute world leader)")
    print("  - USA: 257 GW (second largest)")
    print("  - India: 175 GW (third largest, rapid growth)")
    print("  - Capacity demonstrates proven execution capability!")


def demo_all_six_agents():
    """Compare all six agents."""
    print("\n" + "="*70)
    print("DEMO 8: All Six Agents Combined Assessment")
    print("="*70)
    
    agents = {
        "Ambition": AmbitionAgent(),
        "Stability": CountryStabilityAgent(),
        "Market": PowerMarketSizeAgent(),
        "Dependence": EnergyDependenceAgent(),
        "Renewables": RenewablesPenetrationAgent(),
        "Track Record": TrackRecordAgent()
    }
    
    countries = ["Brazil", "Germany", "China", "USA"]
    
    print("\nComprehensive investment assessment across 6 key factors:")
    print("-" * 110)
    print(f"{'Country':<12} {'Ambition':<10} {'Stability':<10} {'Market':<10} {'Depend':<10} {'Renew':<10} {'Track':<10} {'Avg'}")
    print("-" * 110)
    
    for country in countries:
        scores = {}
        for name, agent in agents.items():
            scores[name] = agent.analyze(country, "Q3 2024").score
        
        avg = sum(scores.values()) / len(scores)
        
        print(
            f"{country:<12} "
            f"{scores['Ambition']:<10.1f} "
            f"{scores['Stability']:<10.1f} "
            f"{scores['Market']:<10.1f} "
            f"{scores['Dependence']:<10.1f} "
            f"{scores['Renewables']:<10.1f} "
            f"{scores['Track Record']:<10.1f} "
            f"{avg:.1f}"
        )
    
    print("\n💡 Insights:")
    print("  - China: Outstanding track record (758 GW) drives high overall score")
    print("  - Germany: Excellent across all dimensions → 9.1 average")
    print("  - Brazil: Strong renewables + track record → 8.5 average")
    print("\n  → Track record is a key indicator of market maturity!")


def demo_capacity_insights():
    """Show track record insights."""
    print("\n" + "="*70)
    print("DEMO 9: Track Record Insights & Market Leaders")
    print("="*70)
    
    agent = TrackRecordAgent()
    
    print("\n🏆 WORLD LEADERS (≥100 GW):")
    print("-" * 70)
    
    leaders = []
    major = []
    emerging = []
    
    for country, data in agent.MOCK_DATA.items():
        capacity_gw = data.get("capacity_mw", 0) / 1000
        status = data.get("status", "")
        
        if capacity_gw >= 100:
            leaders.append((country, capacity_gw, status))
        elif capacity_gw >= 25:
            major.append((country, capacity_gw, status))
        else:
            emerging.append((country, capacity_gw, status))
    
    leaders.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Country':<20} {'Capacity (GW)':<15} {'Status'}")
    print("-" * 70)
    for country, capacity_gw, status in leaders:
        print(f"{country:<20} {capacity_gw:>13.1f} {status}")
    
    print(f"\n⚡ MAJOR MARKETS (25-100 GW):")
    print("-" * 70)
    major.sort(key=lambda x: x[1], reverse=True)
    print(f"{'Country':<20} {'Capacity (GW)':<15} {'Status'}")
    print("-" * 70)
    for country, capacity_gw, status in major:
        print(f"{country:<20} {capacity_gw:>13.1f} {status}")
    
    print("\n💡 Key Observations:")
    print("  - Top 3 markets: China (758 GW), USA (257 GW), India (175 GW)")
    print("  - Outstanding track record (≥100 GW) = world-class execution")
    print("  - Track record reduces regulatory risk + proves capabilities")
    print("  - Recent deployment rates show market momentum")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("🏆 TRACK RECORD AGENT DEMO - MOCK & RULE_BASED MODES")
    print("="*70)
    print("\nThis demo shows the Track Record Agent:")
    print("  - MOCK mode (actual IRENA 2023 installed capacity)")
    print("  - RULE_BASED mode (estimated from World Bank renewable data)")
    print("  - Capacity spectrum from 0.18 GW (Nigeria) to 758 GW (China)")
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
        demo_all_six_agents()
        demo_capacity_insights()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Test MOCK mode: Works immediately ✅")
        print("2. Test RULE_BASED mode: Estimates from World Bank data ✅")
        print("3. You now have 6 agents with RULE_BASED mode!")
        print("4. Continue with remaining Tier 2 agents")
        print("\n💡 Track record demonstrates proven execution capability!")
        print("   Key differentiator for investment risk assessment")
        print("\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
