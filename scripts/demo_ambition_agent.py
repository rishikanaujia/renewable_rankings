#!/usr/bin/env python3
"""Demo script for testing the Ambition Agent with RULE_BASED mode support.

This script demonstrates:
1. MOCK mode (using hardcoded test data)
2. RULE_BASED mode (using real data from data service)
3. Comparison between MOCK and RULE_BASED modes
4. Service layer usage
5. Score calculation

Run from project root:
    python scripts/demo_ambition_agent.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import AmbitionAgent, analyze_ambition
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
    agent = AmbitionAgent(mode=AgentMode.MOCK)
    
    # Test countries
    countries = ["Brazil", "Germany", "China", "India"]
    
    for country in countries:
        print(f"\n🏴 {country}")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        
        # Display results
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification}")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Data Sources:   {', '.join(result.data_sources[:2])}...")


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
    agent = AmbitionAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    # Test countries (these should have GDP data from World Bank)
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
        print(f"Data Sources:   {', '.join(result.data_sources)}")


def demo_mock_vs_rule_based_comparison(data_service):
    """Compare MOCK vs RULE_BASED mode for same country."""
    print("\n" + "="*70)
    print("DEMO 3: MOCK vs RULE_BASED Mode Comparison")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping comparison.")
        return
    
    # Create both agents
    mock_agent = AmbitionAgent(mode=AgentMode.MOCK)
    rule_based_agent = AmbitionAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
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
    
    print("\n💡 Note: RULE_BASED uses GDP growth as proxy for renewable ambition.")
    print("   In production, use actual renewable target data from NDCs!")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)
    
    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_ambition("Brazil", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} Score for Brazil: {result.score}/10")
    print(f"  {result.justification}")
    
    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_ambition(
            "Germany", 
            "Q3 2024", 
            mode=AgentMode.RULE_BASED, 
            data_service=data_service
        )
        print(f"  {result.parameter_name} Score for Germany: {result.score}/10")
        print(f"  {result.justification}")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 5: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # This is how the UI will use agents
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("ambition", "Germany", "Q3 2024")
    print(f"Germany Ambition: {result.score}/10")
    print(f"Justification: {result.justification}")
    
    # Analyze subcategory (currently only has ambition)
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
    print("DEMO 6: Scoring Rubric Visualization")
    print("="*70)
    
    agent = AmbitionAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Ambition:")
    print("-" * 60)
    print(f"{'Score':<8} {'GW Range':<20} {'Description'}")
    print("-" * 60)
    
    for level in rubric:
        max_gw = level.get('max_gw', 10000)
        # Display very large numbers as infinity
        max_display = '∞' if max_gw >= 10000 else str(max_gw)
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
    print("DEMO 7: All Mock Countries Comparison")
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


def demo_data_service_status(data_service):
    """Show data service status and available data."""
    print("\n" + "="*70)
    print("DEMO 8: Data Service Status")
    print("="*70)
    
    if data_service is None:
        print("\n❌ Data service not initialized")
        print("   To enable RULE_BASED mode:")
        print("   1. Ensure config/data_sources.yaml exists")
        print("   2. World Bank API will provide GDP growth data")
        print("   3. Add renewable target CSV files for real target data")
        return
    
    try:
        status = data_service.get_status()
        
        print("\n✅ Data Service Active")
        print(f"   Providers: {len(status['providers'])}")
        print(f"   Indicators: {status['total_indicators']}")
        print(f"   Countries: {status['total_countries']}")
        
        print("\n📊 Available for Ambition Analysis:")
        print("   - GDP growth data (World Bank) ✅ (used as proxy)")
        print("   - Renewable target data: Add CSV files!")
        print("\n💡 To add real renewable targets:")
        print("   1. Create: data/files/renewable_target_Germany.csv")
        print("   2. Format: date,value,quality,unit")
        print("   3. Update agent to use 'renewable_target' indicator")
        
    except Exception as e:
        print(f"\n⚠️  Error getting data service status: {e}")


def demo_integration_pattern():
    """Show integration pattern for future agents."""
    print("\n" + "="*70)
    print("DEMO 9: Integration Pattern (For Next Agent)")
    print("="*70)
    
    print("\nYou just saw the pattern! Here's what changed:")
    print("-" * 70)
    print("""
1. Added data_service parameter to __init__:
   def __init__(self, mode, config, data_service=None):
       self.data_service = data_service

2. Updated _fetch_data for RULE_BASED mode:
   elif self.mode == AgentMode.RULE_BASED:
       # Fetch from data service
       value = self.data_service.get_value(country, 'indicator')
       return {'metric': value, 'source': 'rule_based'}

3. Added fallback method:
   def _fetch_data_mock_fallback(self, country):
       return self.MOCK_DATA.get(country, defaults)

That's it! Same pattern for all remaining 16 agents.
    """)


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("🚀 AMBITION AGENT DEMO - MOCK & RULE_BASED MODES")
    print("="*70)
    print("\nThis demo shows the Ambition Agent with:")
    print("  - MOCK mode (test data)")
    print("  - RULE_BASED mode (real data from data service)")
    print("  - GDP growth as proxy for renewable ambition")
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
        demo_data_service_status(data_service)
        demo_integration_pattern()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review updated agent code in ambition_agent.py")
        print("2. Test MOCK mode: Works immediately ✅")
        print("3. Test RULE_BASED mode: Uses GDP growth proxy ✅")
        print("4. Add real renewable target CSV files for production")
        print("5. Apply same pattern to PowerMarketSizeAgent next!")
        print("\n💡 Pro tip: RULE_BASED mode uses GDP growth as proxy")
        print("   In production, replace with actual renewable target data!")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
