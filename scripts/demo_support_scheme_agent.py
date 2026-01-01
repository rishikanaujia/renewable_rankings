#!/usr/bin/env python3
"""Demo for Support Scheme Agent with RULE_BASED mode support.

📈 REGULATION 80% ADVANCED - Just 1 more parameter to complete!

This script demonstrates:
1. MOCK mode (using hardcoded support scheme assessments)
2. RULE_BASED mode (estimating from World Bank renewable energy data)
3. Comparison between MOCK and RULE_BASED modes
4. Support quality spectrum from Highly Mature to Minimal
5. Direct agent usage
6. Service layer usage
7. System progress tracking

Run from project root:
    python scripts/demo_support_scheme_agent.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    SupportSchemeAgent,
    analyze_support_scheme
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
    print("DEMO 1: MOCK Mode - Support Quality Spectrum")
    print("="*70)
    
    agent = SupportSchemeAgent(mode=AgentMode.MOCK)
    
    countries = [
        ("Germany", "Highly Mature", 10),
        ("China", "Highly Mature", 10),
        ("UK", "Highly Mature", 10),
        ("Saudi Arabia", "Strong but Not Scalable", 9),
        ("India", "Strong but Not Scalable", 9),
        ("Brazil", "Broad but Uneven", 8),
        ("USA", "Broad but Uneven", 8),
        ("Spain", "Solid but Uncertain", 7),
        ("Chile", "Developing", 6),
        ("South Africa", "Basic", 5),
        ("Vietnam", "Boom-Bust", 4),
        ("Mexico", "Forces Disadvantage", 3),
        ("Nigeria", "Emerging but Ineffective", 2)
    ]
    
    for country, category, expected_score in countries:
        print(f"\n🏴 {country} ({category})")
        print("-" * 60)
        
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        support_score = data.get("support_score", 0)
        stability = data.get("stability", "unknown")
        
        print(f"Support Score:  {support_score:.1f}/10")
        print(f"Category:       {category}")
        print(f"Stability:      {stability}")
        print(f"Final Score:    {result.score}/10")
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
    agent = SupportSchemeAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    # Test countries
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
    
    print("\n💡 Note: RULE_BASED mode estimates support quality from:")
    print("   - Renewable energy adoption % (World Bank)")
    print("   - GDP per capita (sophistication proxy)")
    print("   - Higher renewable adoption + higher GDP = Better support")


def demo_mock_vs_rule_based_comparison(data_service):
    """Compare MOCK vs RULE_BASED mode for same country."""
    print("\n" + "="*70)
    print("DEMO 3: MOCK vs RULE_BASED Mode Comparison")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping comparison.")
        return
    
    # Create both agents
    mock_agent = SupportSchemeAgent(mode=AgentMode.MOCK)
    rule_based_agent = SupportSchemeAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    countries = ["Germany", "Brazil", "USA"]
    
    print("\nComparing MOCK vs RULE_BASED support quality estimates:")
    print("-" * 80)
    print(f"{'Country':<15} {'MOCK Score':<15} {'MOCK Category':<25} {'Diff'}")
    print("-" * 80)
    
    for country in countries:
        mock_result = mock_agent.analyze(country, "Q3 2024")
        rule_based_result = rule_based_agent.analyze(country, "Q3 2024")
        
        # Get data from MOCK
        mock_data = mock_agent.MOCK_DATA.get(country, {})
        mock_support = mock_data.get('support_score', 0)
        mock_category = mock_data.get('category', 'Unknown')
        
        # Score difference
        diff = rule_based_result.score - mock_result.score
        diff_str = f"{diff:+.1f}" if diff != 0 else "Same"
        
        print(
            f"{country:<15} "
            f"{mock_support:<15.1f} "
            f"{mock_category:<25} "
            f"{diff_str}"
        )
    
    print("\n💡 Note:")
    print("   - MOCK: Detailed assessments of actual support mechanisms")
    print("   - RULE_BASED: Estimated from renewable adoption + GDP")
    print("   - Higher renewable penetration = Stronger support implied")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)
    
    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_support_scheme("Germany", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} for Germany: {result.score}/10")
    print(f"  Category: Highly Mature (world-class Energiewende)")
    
    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_support_scheme(
            "USA", 
            "Q3 2024", 
            mode=AgentMode.RULE_BASED, 
            data_service=data_service
        )
        print(f"  {result.parameter_name} for USA: {result.score}/10")
        print(f"  Estimated from renewable adoption + GDP")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 5: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # Single parameter
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("support_scheme", "Brazil", "Q3 2024")
    print(f"Brazil Support Scheme: {result.score}/10")
    print(f"Justification: {result.justification[:100]}...")


def demo_regulation_80_advanced():
    """📈 MILESTONE: Regulation 80% advanced!"""
    print("\n" + "="*70)
    print("📈 DEMO 6: REGULATION 80% ADVANCED - ALMOST COMPLETE!")
    print("="*70)
    
    print("\n🎉 MILESTONE ACHIEVED: Regulation well advanced!")
    print("Just 1 more parameter to complete!\n")
    
    result = agent_service.analyze_subcategory("regulation", "Brazil", "Q3 2024")
    
    print(f"Brazil Regulation: {result.score}/10")
    print(f"Parameters analyzed: {len(result.parameter_scores)}/5 (80%)\n")
    
    for i, param in enumerate(result.parameter_scores, 1):
        print(f"  {i}. {param.parameter_name}: {param.score}/10")
    
    print(f"\n💡 Regulation subcategory: 80% complete!")
    print(f"📈 Just 1 more parameter to 100%!")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 7: Scoring Rubric Visualization")
    print("="*70)
    
    agent = SupportSchemeAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Support Scheme:")
    print("(Note: Higher quality = Higher scores)")
    print("-" * 70)
    print(f"{'Score':<8} {'Category':<30} {'Description'}")
    print("-" * 70)
    
    for level in rubric:
        score = level['score']
        category = level.get('category', '')
        description = level['description']
        
        print(f"{score:<8} {category:<30} {description}")
    
    print("\n📊 Example Scores:")
    test_cases = [
        ("Germany", 10, "Highly Mature"),
        ("India", 9, "Strong but Not Scalable"),
        ("USA", 8, "Broad but Uneven"),
        ("Spain", 7, "Solid but Uncertain"),
        ("Chile", 6, "Developing"),
        ("South Africa", 5, "Basic"),
        ("Vietnam", 4, "Boom-Bust"),
        ("Mexico", 3, "Forces Disadvantage"),
        ("Nigeria", 2, "Emerging but Ineffective"),
    ]
    
    for name, support_score, category in test_cases:
        mock_data = {
            "support_score": support_score,
            "category": category
        }
        score = agent._calculate_score(mock_data, name, "Q3 2024")
        print(f"  {name:<20} {support_score:>3}/10 → Score: {score}/10 ({category})")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 8: All Mock Countries Comparison")
    print("="*70)
    
    agent = SupportSchemeAgent()
    
    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA[country]
        support_score = data.get("support_score", 0)
        category = data.get("category", "")
        stability = data.get("stability", "")
        results.append((country, result.score, support_score, category, stability))
    
    # Sort by support score descending (best first)
    results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'Support':<12} {'Category':<30} {'Stability'}")
    print("-" * 100)
    
    for i, (country, score, support_score, category, stability) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {score:<8.1f} {support_score:>10.1f} {category:<30} {stability}")
    
    print("\n💡 Key Insights:")
    print("  - Germany/China/UK: Score 10/10 (Highly Mature frameworks)")
    print("  - USA/Brazil: Score 8/10 (Broad but Uneven - regional variation)")
    print("  - Vietnam: Score 4/10 (Boom-Bust - policy instability)")
    print("  - Mexico: Score 3/10 (Forces Disadvantage - policy reversal)")
    print("  - Support scheme quality is critical for investment certainty!")


def demo_system_progress():
    """Show overall system progress."""
    print("\n" + "="*70)
    print("DEMO 9: OVERALL SYSTEM PROGRESS")
    print("="*70)
    
    print(f"\n📊 System Status:")
    print("  ✅ Agent #14 complete (SupportSchemeAgent)")
    print("  ✅ 14/21 agents = 66.7% complete")
    print("  ✅ THREE complete subcategories (100%)")
    print("  ✅ ONE well-advanced subcategory (80%)")
    print("  ✅ Just 7 more agents to full system!")
    
    country = "Brazil"
    
    print(f"\n📊 {country} Complete Analysis:")
    print("-" * 70)
    
    # Three complete subcategories
    print("\n🏆 COMPLETE SUBCATEGORIES:")
    
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"\n1. Market Size Fundamentals: {mkt.score}/10 (100% ✅)")
    for p in mkt.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"\n2. Profitability: {prof.score}/10 (100% ✅)")
    for p in prof.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    acc = agent_service.analyze_subcategory("accommodation", country)
    print(f"\n3. Accommodation: {acc.score}/10 (100% ✅)")
    for p in acc.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Well-advanced subcategory
    print("\n📈 WELL-ADVANCED SUBCATEGORY:")
    
    reg = agent_service.analyze_subcategory("regulation", country)
    print(f"\n4. Regulation: {reg.score}/10 (80% - 4/5 parameters)")
    for p in reg.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    print("\n💡 THREE complete + ONE advanced = Strong system foundation!")


def demo_support_insights():
    """Show support scheme insights."""
    print("\n" + "="*70)
    print("DEMO 10: Support Scheme Insights & Policy Quality")
    print("="*70)
    
    agent = SupportSchemeAgent()
    
    print("\n🏆 WORLD-CLASS SUPPORT (Score 10/10):")
    print("-" * 70)
    
    excellent = []
    good = []
    challenges = []
    
    for country, data in agent.MOCK_DATA.items():
        support_score = data.get("support_score", 0)
        category = data.get("category", "")
        stability = data.get("stability", "")
        
        if support_score >= 9:
            excellent.append((country, support_score, category, stability))
        elif support_score >= 6:
            good.append((country, support_score, category, stability))
        else:
            challenges.append((country, support_score, category, stability))
    
    excellent.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Country':<20} {'Score':<12} {'Category':<30} {'Stability'}")
    print("-" * 80)
    for country, support_score, category, stability in excellent:
        print(f"{country:<20} {support_score:>10.1f} {category:<30} {stability}")
    
    print(f"\n⚡ GOOD SUPPORT (6-9/10):")
    print("-" * 70)
    good.sort(key=lambda x: x[1], reverse=True)
    print(f"{'Country':<20} {'Score':<12} {'Category':<30} {'Stability'}")
    print("-" * 70)
    for country, support_score, category, stability in good:
        print(f"{country:<20} {support_score:>10.1f} {category:<30} {stability}")
    
    print("\n💡 Key Observations:")
    print("  - Excellent: Germany (EEG), China (massive FiTs), UK (CfD)")
    print("  - Good: USA (ITC/PTC), Brazil (auctions + net metering)")
    print("  - Challenges: Mexico (policy reversal), Nigeria (unimplemented FiT)")
    print("  - Support scheme quality determines investment certainty")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("📈 SUPPORT SCHEME AGENT DEMO - MOCK & RULE_BASED MODES")
    print("="*70)
    print("\n🎊 MILESTONE: REGULATION 80% ADVANCED!")
    print("Just one more parameter to complete the Regulation subcategory!")
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
        demo_regulation_80_advanced()  # 📈 MILESTONE DEMO!
        demo_scoring_rubric()
        demo_all_countries()
        demo_system_progress()
        demo_support_insights()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📈 REGULATION 80% ADVANCED - MAJOR PROGRESS!")
        print("  ✅ Agent #14 complete (SupportSchemeAgent)")
        print("  ✅ 14/21 agents = 66.7% complete")
        print("  ✅ Regulation 80% (4/5 parameters)")
        print("  ✅ THREE complete subcategories!")
        print("  ✅ Just 7 more agents to full system!")
        print("\nNext steps:")
        print("1. Test MOCK mode: Works immediately ✅")
        print("2. Test RULE_BASED mode: Estimates from World Bank ✅")
        print("3. Complete Regulation with 1 more agent!")
        print("\n💡 Support scheme quality drives investment certainty!")
        print("   Strong policies = Better project economics")
        print("\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
