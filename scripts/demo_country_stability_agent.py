#!/usr/bin/env python3
"""Demo script for testing the Country Stability Agent with REAL data integration.

This script demonstrates:
1. MOCK mode (using hardcoded test data)
2. RULE_BASED mode (using rule-based data from data service)
3. Comparison between MOCK and RULE_BASED modes
4. Service layer usage
5. Score calculation based on ECR ratings

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
    agent = CountryStabilityAgent(mode=AgentMode.MOCK)
    
    # Test countries with different risk levels
    countries = [
        ("Germany", "Low Risk"),
        ("Brazil", "Moderate Risk"),
        ("India", "Moderate Risk"),
        ("Argentina", "High Risk")
    ]
    
    for country, expected_risk in countries:
        print(f"\n🏴 {country} ({expected_risk})")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        
        # Display results
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification}")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Data Sources:   {', '.join(result.data_sources[:2])}...")


def demo_real_mode(data_service):
    """Demonstrate RULE_BASED mode (using rule-based data)."""
    print("\n" + "="*70)
    print("DEMO 2: RULE_BASED Mode (Real Data from Data Service)")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping RULE_BASED mode demo.")
        print("    Make sure config/data_sources.yaml exists and is valid.")
        return
    
    # Create agent in RULE_BASED mode
    agent = CountryStabilityAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    # Test countries (these should have ECR data in data/files/)
    countries = ["Germany", "USA"]
    
    for country in countries:
        print(f"\n🌍 {country} (REAL DATA)")
        print("-" * 60)
        
        # Analyze
        result = agent.analyze(country, "Q3 2024")
        
        # Display results
        print(f"Score:          {result.score}/10")
        print(f"Justification:  {result.justification}")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Data Sources:   {', '.join(result.data_sources)}")


def demo_mock_vs_real_comparison(data_service):
    """Compare MOCK vs RULE_BASED mode for same country."""
    print("\n" + "="*70)
    print("DEMO 3: MOCK vs RULE_BASED Mode Comparison")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping comparison.")
        return
    
    # Create both agents
    mock_agent = CountryStabilityAgent(mode=AgentMode.MOCK)
    real_agent = CountryStabilityAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    countries = ["Germany", "USA"]
    
    print("\nComparing MOCK vs REAL data:")
    print("-" * 70)
    print(f"{'Country':<15} {'MOCK Score':<12} {'REAL Score':<12} {'Difference'}")
    print("-" * 70)
    
    for country in countries:
        mock_result = mock_agent.analyze(country, "Q3 2024")
        real_result = real_agent.analyze(country, "Q3 2024")
        
        diff = real_result.score - mock_result.score
        diff_str = f"{diff:+.1f}" if diff != 0 else "Same"
        
        print(
            f"{country:<15} "
            f"{mock_result.score:<12.1f} "
            f"{real_result.score:<12.1f} "
            f"{diff_str}"
        )
    
    print("\n💡 Insight: REAL and MOCK data should match if CSV files match MOCK_DATA!")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)
    
    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_country_stability("Brazil", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} Score for Brazil: {result.score}/10")
    print(f"  {result.justification}")
    
    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_country_stability(
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
    print("DEMO 6: Scoring Rubric Visualization")
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
    print("DEMO 7: All Mock Countries Comparison")
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


def demo_data_service_status(data_service):
    """Show data service status."""
    print("\n" + "="*70)
    print("DEMO 8: Data Service Status")
    print("="*70)
    
    if data_service is None:
        print("\n❌ Data service not initialized")
        print("   To enable RULE_BASED mode:")
        print("   1. Ensure config/data_sources.yaml exists")
        print("   2. Add ECR data files to data/files/")
        print("   3. Format: ecr_CountryName.csv")
        return
    
    try:
        status = data_service.get_status()
        
        print("\n✅ Data Service Active")
        print(f"   Providers: {len(status['providers'])}")
        print(f"   Indicators: {status['total_indicators']}")
        print(f"   Countries: {status['total_countries']}")
        
        # Show available ECR data
        print("\n📊 Available ECR Data:")
        countries = data_service.get_available_countries()
        
        # Try to get ECR data for each country
        ecr_countries = []
        for country in countries:
            value = data_service.get_value(country, 'ecr', default=None)
            if value is not None:
                ecr_countries.append((country, value))
        
        if ecr_countries:
            print(f"   Found ECR data for {len(ecr_countries)} countries:")
            for country, value in ecr_countries[:10]:  # Show first 10
                print(f"   - {country}: {value}")
        else:
            print("   No ECR data found")
            print("   Add CSV files to data/files/ with format: ecr_CountryName.csv")
        
    except Exception as e:
        print(f"\n⚠️  Error getting data service status: {e}")


def demo_integration_guide():
    """Show integration guide for other agents."""
    print("\n" + "="*70)
    print("DEMO 9: Integration Guide for Other Agents")
    print("="*70)
    
    print("\nTo add RULE_BASED mode to other agents, follow this pattern:")
    print("-" * 70)
    print("""
1. Add data_service parameter to __init__:

   def __init__(self, mode=AgentMode.MOCK, config=None, data_service=None):
       super().__init__("Agent Name", mode, config)
       self.data_service = data_service

2. Update _fetch_data method:

   def _fetch_data(self, country, period, **kwargs):
       if self.mode == AgentMode.MOCK:
           return self.MOCK_DATA.get(country, {})
       
       elif self.mode == AgentMode.RULE_BASED:
           if self.data_service is None:
               return self._fetch_data_mock_fallback(country)
           
           # Fetch rule-based data
           data = {}
           data['your_indicator'] = self.data_service.get_value(
               country, 'indicator_name', default=0.0
           )
           return data

3. Initialize with data service:

   data_service = initialize_data_service()
   agent = YourAgent(mode=AgentMode.RULE_BASED, data_service=data_service)

That's it! Your agent now supports both MOCK and RULE_BASED modes.
    """)


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("🚀 COUNTRY STABILITY AGENT DEMO - MOCK & RULE_BASED MODES")
    print("="*70)
    print("\nThis demo shows the Country Stability Agent with:")
    print("  - MOCK mode (test data)")
    print("  - RULE_BASED mode (rule-based data from data service)")
    print("  - Comparison between modes")
    print("\n")
    
    try:
        # Initialize data service for RULE_BASED mode
        data_service = initialize_data_service()
        
        # Run demos
        demo_mock_mode()
        demo_real_mode(data_service)
        demo_mock_vs_real_comparison(data_service)
        demo_convenience_function(data_service)
        demo_service_layer()
        demo_scoring_rubric()
        demo_all_countries()
        demo_data_service_status(data_service)
        demo_integration_guide()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Review updated agent code in country_stability_agent.py")
        print("2. Test MOCK mode: Works immediately ✅")
        print("3. Test RULE_BASED mode: Add ECR CSV files to data/files/")
        print("4. Apply same pattern to other 17 agents")
        print("5. Notice backward compatibility: MOCK mode unchanged!")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
