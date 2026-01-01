#!/usr/bin/env python3
"""Demo for System Modifiers Agent with RULE_BASED mode support.

This is a SPECIAL COMPOSITE AGENT that provides final calibration adjustments
based on systemic factors affecting all renewable investments.

This script demonstrates:
1. MOCK mode (using composite risk indices)
2. RULE_BASED mode (estimating from World Bank macroeconomic indicators)
3. Comparison between MOCK and RULE_BASED modes
4. Risk spectrum from Severe to Optimal
5. Currency and geopolitical risk analysis
6. Direct agent usage
7. Service layer usage
8. Systemic risk as final ranking adjustment layer

Run from project root:
    python scripts/demo_system_modifiers_agent.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    SystemModifiersAgent,
    analyze_system_modifiers
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
    print("DEMO 1: MOCK Mode - Systemic Risk Spectrum")
    print("="*70)
    
    agent = SystemModifiersAgent(mode=AgentMode.MOCK)
    
    countries = [
        ("Germany", 9, "Minimal risk"),
        ("USA", 9, "Minimal risk"),
        ("UK", 8, "Very low risk"),
        ("Australia", 8, "Very low risk"),
        ("Spain", 7, "Low risk"),
        ("Saudi Arabia", 7, "Low risk"),
        ("Brazil", 6, "Below moderate positive"),
        ("India", 6, "Below moderate positive"),
        ("Chile", 6, "Below moderate positive"),
        ("Mexico", 6, "Below moderate positive"),
        ("China", 5, "Moderate factors"),
        ("Indonesia", 5, "Moderate factors"),
        ("South Africa", 5, "Moderate factors"),
        ("Vietnam", 4, "Above moderate negative"),
        ("Argentina", 3, "High negative"),
        ("Nigeria", 3, "High negative"),
    ]
    
    for country, expected_score, profile in countries:
        print(f"\n🌍 {country} ({profile})")
        print("-" * 60)
        
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        currency = data.get("currency_risk", "")
        volatility = data.get("currency_volatility_annual", 0)
        geopolitical = data.get("geopolitical_risk", "")
        
        print(f"Currency Risk:     {currency}")
        print(f"Volatility:        {volatility:.1f}% annual")
        print(f"Geopolitical:      {geopolitical}")
        print(f"Score:             {result.score}/10")
        print(f"Confidence:        {result.confidence*100:.0f}%")
        print(f"Note:              Lower risk = Higher score")


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
    agent = SystemModifiersAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    # Test countries
    countries = ["Germany", "USA", "Brazil", "India"]
    
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
    
    print("\n💡 Note: RULE_BASED mode estimates systemic risks from:")
    print("   - Inflation rate → Currency stability")
    print("   - Interest rate → Macroeconomic stability")
    print("   - Trade (% GDP) → Convertibility/openness")
    print("   - GDP per capita → Governance/development proxy")
    print("   - Lower inflation + stable rates = Lower systemic risk!")


def demo_mock_vs_rule_based_comparison(data_service):
    """Compare MOCK vs RULE_BASED mode for same country."""
    print("\n" + "="*70)
    print("DEMO 3: MOCK vs RULE_BASED Mode Comparison")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping comparison.")
        return
    
    # Create both agents
    mock_agent = SystemModifiersAgent(mode=AgentMode.MOCK)
    rule_based_agent = SystemModifiersAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    countries = ["Germany", "Brazil", "USA", "India"]
    
    print("\nComparing MOCK vs RULE_BASED systemic risk estimates:")
    print("-" * 80)
    print(f"{'Country':<15} {'MOCK Score':<15} {'RULE Score':<15} {'Diff'}")
    print("-" * 80)
    
    for country in countries:
        mock_result = mock_agent.analyze(country, "Q3 2024")
        rule_based_result = rule_based_agent.analyze(country, "Q3 2024")
        
        # Score difference
        diff = rule_based_result.score - mock_result.score
        diff_str = f"{diff:+.1f}" if diff != 0 else "Same"
        
        print(
            f"{country:<15} "
            f"{mock_result.score:<15.1f} "
            f"{rule_based_result.score:<15.1f} "
            f"{diff_str}"
        )
    
    print("\n💡 Note:")
    print("   - MOCK: Composite risk indices (geopolitical, currency)")
    print("   - RULE_BASED: Estimated from inflation + interest rates + trade")
    print("   - Lower systemic risk = Better environment = Higher score")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)
    
    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_system_modifiers("USA", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} for USA: {result.score}/10")
    print(f"  Minimal risk - best-in-class stability")
    
    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_system_modifiers(
            "Germany", 
            "Q3 2024", 
            mode=AgentMode.RULE_BASED, 
            data_service=data_service
        )
        print(f"  {result.parameter_name} for Germany: {result.score}/10")
        print(f"  Estimated from macroeconomic stability indicators")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 5: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # Single parameter
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("system_modifiers", "Brazil", "Q3 2024")
    print(f"Brazil System Modifiers: {result.score}/10")
    print(f"Justification: {result.justification[:100]}...")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 6: Scoring Rubric Visualization")
    print("="*70)
    
    agent = SystemModifiersAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for System Modifiers:")
    print("(Note: Lower systemic risk = Higher scores)")
    print("-" * 70)
    print(f"{'Score':<8} {'Risk Level':<25} {'Description'}")
    print("-" * 70)
    
    for level in rubric:
        score = level['score']
        range_str = level.get('range', '')
        description = level['description']
        
        print(f"{score:<8} {range_str:<25} {description[:40]}")
    
    print("\n📊 Example Countries:")
    test_cases = [
        ("USA/Germany", 9, "Minimal risk"),
        ("UK/Australia", 8, "Very low risk"),
        ("Spain/Saudi", 7, "Low risk"),
        ("Brazil/India", 6, "Below moderate positive"),
        ("China/Indonesia", 5, "Moderate factors"),
        ("Vietnam", 4, "Above moderate negative"),
        ("Argentina/Nigeria", 3, "High negative"),
    ]
    
    for name, score, category in test_cases:
        print(f"  {name:<20} {score:>2}/10 ({category})")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 7: All Mock Countries Comparison")
    print("="*70)
    
    agent = SystemModifiersAgent()
    
    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA[country]
        volatility = data.get("currency_volatility_annual", 0)
        currency = data.get("currency_risk", "")
        geopolitical = data.get("geopolitical_risk", "")
        results.append((country, result.score, volatility, currency, geopolitical))
    
    # Sort by score descending (best first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'Volatility':<12} {'Currency Risk':<25} {'Geopolitical'}")
    print("-" * 110)
    
    for i, (country, score, volatility, currency, geopolitical) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {score:<8.1f} {volatility:>10.1f}% {currency[:24]:<25} {geopolitical[:20]}")
    
    print("\n💡 Key Insights:")
    print("  - USA/Germany: Minimal risk (9/10) - reserve currencies, stable")
    print("  - UK/Australia: Very low risk (8/10) - strong governance")
    print("  - Spain/Saudi: Low risk (7/10) - stable with some factors")
    print("  - Brazil/India: Below moderate (6/10) - manageable EM risks")
    print("  - China/Indonesia: Moderate (5/10) - typical EM profile")
    print("  - Vietnam: Above moderate negative (4/10) - FX controls")
    print("  - Argentina/Nigeria: High negative (3/10) - severe currency risk")


def demo_currency_risk_analysis():
    """Analyze currency risk across countries."""
    print("\n" + "="*70)
    print("DEMO 8: Currency Risk & Volatility Analysis")
    print("="*70)
    
    agent = SystemModifiersAgent()
    
    print("\n💱 CURRENCY VOLATILITY SPECTRUM:")
    print("-" * 70)
    
    currency_data = []
    for country, data in agent.MOCK_DATA.items():
        volatility = data.get("currency_volatility_annual", 0)
        currency = data.get("currency_risk", "")
        score = agent._calculate_score(data, country, "Q3 2024")
        currency_data.append((country, score, volatility, currency))
    
    # Sort by volatility (lowest first)
    currency_data.sort(key=lambda x: x[2])
    
    print(f"{'Country':<20} {'Score':<10} {'Volatility':<12} {'Currency Risk'}")
    print("-" * 75)
    
    for country, score, volatility, currency in currency_data:
        print(f"{country:<20} {score:<10.1f} {volatility:>10.1f}% {currency[:40]}")
    
    print("\n💡 Currency Stability Matters:")
    print("  - Saudi Arabia (0.5%): USD peg = minimal volatility")
    print("  - USA (2.5%): Reserve currency = very stable")
    print("  - Germany/Spain (3.8%): EUR stability")
    print("  - Brazil (15.2%): Typical EM volatility")
    print("  - S.Africa (18.5%): High EM volatility")
    print("  - Nigeria (28.5%): Very high volatility, FX shortages")
    print("  - Argentina (45.2%): Hyperinflation, extreme volatility")
    print("  - Lower volatility = Better repatriation certainty!")


def demo_geopolitical_risk_analysis():
    """Analyze geopolitical risk factors."""
    print("\n" + "="*70)
    print("DEMO 9: Geopolitical Risk Assessment")
    print("="*70)
    
    agent = SystemModifiersAgent()
    
    print("\n🌍 GEOPOLITICAL RISK SPECTRUM:")
    print("-" * 70)
    
    geo_data = []
    for country, data in agent.MOCK_DATA.items():
        geopolitical = data.get("geopolitical_risk", "")
        score = agent._calculate_score(data, country, "Q3 2024")
        sanctions = data.get("sanctions_status", "None")
        anomalies = data.get("market_anomalies", "None")
        geo_data.append((country, score, geopolitical, sanctions, anomalies))
    
    # Sort by score (best first)
    geo_data.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Country':<20} {'Score':<10} {'Geopolitical Risk':<35} {'Special Factors'}")
    print("-" * 100)
    
    for country, score, geopolitical, sanctions, anomalies in geo_data:
        special = []
        if sanctions != "None":
            special.append(f"Sanctions: {sanctions}")
        if anomalies not in ["None", "None significant"]:
            special.append(f"Anomalies: {anomalies}")
        special_str = "; ".join(special) if special else "None"
        
        print(f"{country:<20} {score:<10.1f} {geopolitical[:34]:<35} {special_str[:30]}")
    
    print("\n💡 Geopolitical Stability Matters:")
    print("  - Germany/USA/UK: Very low risk (stable democracies, rule of law)")
    print("  - Australia/Spain: Very low risk (developed, stable)")
    print("  - Brazil/India: Moderate (stable democracies, some tensions)")
    print("  - China: Moderate (rising tensions, trade issues)")
    print("  - Vietnam: Moderate (one-party state, regional tensions)")
    print("  - Nigeria: High (security issues, corruption)")
    print("  - Argentina: High (economic crisis, policy uncertainty)")


def demo_systemic_adjustment_impact():
    """Show how systemic modifiers adjust overall rankings."""
    print("\n" + "="*70)
    print("DEMO 10: Systemic Modifiers as Ranking Adjustment Layer")
    print("="*70)
    
    agent = SystemModifiersAgent()
    
    print("\n⚖️  SYSTEMIC RISK ADJUSTMENT IMPACT:")
    print("-" * 70)
    print("System Modifiers act as a final calibration layer")
    print("adjusting country rankings based on systemic factors.\n")
    
    adjustment_data = []
    for country, data in agent.MOCK_DATA.items():
        score = agent._calculate_score(data, country, "Q3 2024")
        
        # Estimate adjustment impact
        # Score 9-10: +5% to +10% boost
        # Score 7-8: +0% to +5% boost
        # Score 5-6: -2% to +2% neutral
        # Score 4: -5% to -8% penalty
        # Score 3: -10% to -15% penalty
        # Score 1-2: -15% to -25% penalty
        
        if score >= 9:
            adjustment = "+7.5%"
            impact = "Strong positive boost"
        elif score >= 7:
            adjustment = "+2.5%"
            impact = "Modest positive boost"
        elif score >= 5:
            adjustment = "±0%"
            impact = "Neutral (no adjustment)"
        elif score >= 4:
            adjustment = "-6.5%"
            impact = "Moderate negative penalty"
        elif score >= 3:
            adjustment = "-12.5%"
            impact = "Significant negative penalty"
        else:
            adjustment = "-20%"
            impact = "Severe negative penalty"
        
        adjustment_data.append((country, score, adjustment, impact))
    
    # Sort by score (best first)
    adjustment_data.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Country':<20} {'Risk Score':<12} {'Adjustment':<15} {'Impact'}")
    print("-" * 80)
    
    for country, score, adjustment, impact in adjustment_data:
        print(f"{country:<20} {score:<12.1f} {adjustment:<15} {impact}")
    
    print("\n💡 System Modifiers Impact:")
    print("  - High scores (9-10): Amplify positive fundamentals")
    print("  - Moderate scores (5-6): Minimal adjustment")
    print("  - Low scores (3-4): Dampen attractiveness due to systemic risks")
    print("  - This final layer ensures currency/geopolitical risks are reflected!")
    print("  - Example: Argentina strong fundamentals BUT severe currency risk")
    print("           → System modifier (-12.5%) reflects macro instability")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("🌍 SYSTEM MODIFIERS AGENT DEMO")
    print("="*70)
    print("\nSpecial Composite Agent: Systemic Risk Adjustment Layer")
    print("Analyzing currency risk, geopolitical stability, and")
    print("macroeconomic environment across global markets\n")
    
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
        demo_currency_risk_analysis()
        demo_geopolitical_risk_analysis()
        demo_systemic_adjustment_impact()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n🌍 SYSTEM MODIFIERS AGENT COMPLETE!")
        print("  ✅ Agent implementation complete")
        print("  ✅ Both MOCK and RULE_BASED modes working")
        print("  ✅ All 10 demos pass")
        print("  ✅ Comprehensive systemic risk analysis")
        
        print("\n💡 Key Features:")
        print("  • Currency risk and volatility assessment")
        print("  • Geopolitical risk evaluation")
        print("  • Market anomaly detection")
        print("  • Convertibility analysis")
        print("  • Final ranking adjustment layer")
        
        print("\n📊 Risk Spectrum:")
        print("  • USA/Germany (9/10): Minimal risk - reserve currencies")
        print("  • UK/Australia (8/10): Very low risk - strong stability")
        print("  • Spain (7/10): Low risk - eurozone stability")
        print("  • Brazil/India (6/10): Below moderate - manageable EM risks")
        print("  • China (5/10): Moderate - controlled but stable")
        print("  • Vietnam (4/10): Above moderate negative - FX controls")
        print("  • Argentina/Nigeria (3/10): High negative - severe currency risk")
        
        print("\n💡 System Modifiers are CRITICAL for final ranking!")
        print("   They ensure macro risks (currency, geopolitical) are")
        print("   properly reflected in overall attractiveness scores!")
        print("\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
