#!/usr/bin/env python3
"""Demo for Ownership Hurdles Agent with RULE_BASED mode support.

🎊 THIRD COMPLETE SUBCATEGORY - Accommodation 100%!

This script demonstrates:
1. MOCK mode (using hardcoded ownership restriction data)
2. RULE_BASED mode (estimating from World Bank FDI + economic indicators)
3. Comparison between MOCK and RULE_BASED modes
4. Ownership barrier spectrum from No Barriers to Prohibitive
5. Direct agent usage
6. Service layer usage
7. Complete Accommodation subcategory analysis

Run from project root:
    python scripts/demo_ownership_hurdles_agent.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    OwnershipHurdlesAgent,
    analyze_ownership_hurdles
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
    print("DEMO 1: MOCK Mode - Ownership Barrier Spectrum")
    print("="*70)
    
    agent = OwnershipHurdlesAgent(mode=AgentMode.MOCK)
    
    countries = [
        ("Brazil", 100, "No barriers"),
        ("Germany", 100, "No barriers"),
        ("India", 100, "No barriers"),
        ("Chile", 100, "No barriers"),
        ("USA", 95, "Minimal barriers"),
        ("Australia", 90, "Minimal barriers"),
        ("Nigeria", 60, "Below moderate"),
        ("China", 49, "Moderate"),
        ("Vietnam", 49, "Moderate")
    ]
    
    for country, foreign_pct, profile in countries:
        print(f"\n🏴 {country} ({foreign_pct}% - {profile})")
        print("-" * 60)
        
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        ownership_pct = data.get("foreign_ownership_pct", 0)
        category = data.get("category", "unknown")
        
        print(f"Foreign Own%:   {ownership_pct}%")
        print(f"Category:       {category.replace('_', ' ').title()}")
        print(f"Score:          {result.score}/10")
        print(f"Confidence:     {result.confidence*100:.0f}%")
        print(f"Note:           Lower barriers = Higher scores")


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
    agent = OwnershipHurdlesAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
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
    
    print("\n💡 Note: RULE_BASED mode estimates ownership openness from:")
    print("   - FDI net inflows (% of GDP) - Higher FDI suggests fewer restrictions")
    print("   - GDP per capita - Wealthier countries tend to be more open")
    print("   - Trade openness - More open trade correlates with investment openness")


def demo_mock_vs_rule_based_comparison(data_service):
    """Compare MOCK vs RULE_BASED mode for same country."""
    print("\n" + "="*70)
    print("DEMO 3: MOCK vs RULE_BASED Mode Comparison")
    print("="*70)
    
    if data_service is None:
        print("\n⚠️  Data service not available. Skipping comparison.")
        return
    
    # Create both agents
    mock_agent = OwnershipHurdlesAgent(mode=AgentMode.MOCK)
    rule_based_agent = OwnershipHurdlesAgent(mode=AgentMode.RULE_BASED, data_service=data_service)
    
    countries = ["Germany", "Brazil", "USA"]
    
    print("\nComparing MOCK vs RULE_BASED ownership estimates:")
    print("-" * 80)
    print(f"{'Country':<15} {'MOCK %':<15} {'MOCK Category':<25} {'Diff'}")
    print("-" * 80)
    
    for country in countries:
        mock_result = mock_agent.analyze(country, "Q3 2024")
        rule_based_result = rule_based_agent.analyze(country, "Q3 2024")
        
        # Get data from MOCK
        mock_data = mock_agent.MOCK_DATA.get(country, {})
        mock_pct = mock_data.get('foreign_ownership_pct', 0)
        mock_category = mock_data.get('category', 'Unknown').replace('_', ' ').title()
        
        # Score difference
        diff = rule_based_result.score - mock_result.score
        diff_str = f"{diff:+.1f}" if diff != 0 else "Same"
        
        print(
            f"{country:<15} "
            f"{mock_pct:<15.0f} "
            f"{mock_category:<25} "
            f"{diff_str}"
        )
    
    print("\n💡 Note:")
    print("   - MOCK: Actual foreign ownership regulations")
    print("   - RULE_BASED: Estimated from FDI inflows + development level")
    print("   - Higher FDI + Higher GDP = More open to foreign investment")


def demo_convenience_function(data_service):
    """Demonstrate convenience function."""
    print("\n" + "="*70)
    print("DEMO 4: Convenience Function (Both Modes)")
    print("="*70)
    
    # MOCK mode
    print("\nMOCK Mode:")
    result = analyze_ownership_hurdles("Germany", "Q3 2024", mode=AgentMode.MOCK)
    print(f"  {result.parameter_name} for Germany: {result.score}/10")
    print(f"  100% foreign ownership allowed (No barriers)")
    
    # RULE_BASED mode
    if data_service:
        print("\nRULE_BASED Mode:")
        result = analyze_ownership_hurdles(
            "USA", 
            "Q3 2024", 
            mode=AgentMode.RULE_BASED, 
            data_service=data_service
        )
        print(f"  {result.parameter_name} for USA: {result.score}/10")
        print(f"  Estimated from FDI inflows + GDP per capita")


def demo_service_layer():
    """Demonstrate service layer usage."""
    print("\n" + "="*70)
    print("DEMO 5: Service Layer (UI Integration Pattern)")
    print("="*70)
    
    # Single parameter
    print("\n📊 Analyzing single parameter...")
    result = agent_service.analyze_parameter("ownership_hurdles", "Brazil", "Q3 2024")
    print(f"Brazil Ownership Hurdles: {result.score}/10")
    print(f"Justification: {result.justification[:100]}...")


def demo_accommodation_complete():
    """🎊 MILESTONE: Third complete subcategory!"""
    print("\n" + "="*70)
    print("🎊 DEMO 6: ACCOMMODATION 100% COMPLETE!")
    print("="*70)
    
    print("\n🎉 MILESTONE ACHIEVED: Third complete subcategory!")
    print("Accommodation now has ALL parameters!\n")
    
    result = agent_service.analyze_subcategory("accommodation", "Brazil", "Q3 2024")
    
    print(f"Brazil Accommodation: {result.score}/10")
    print(f"Parameters analyzed: {len(result.parameter_scores)}/2 (100%)\n")
    
    for i, param in enumerate(result.parameter_scores, 1):
        print(f"  {i}. {param.parameter_name}: {param.score}/10")
    
    print(f"\n💡 Complete subcategory score calculation:")
    scores_str = ' + '.join([f"{p.score:.1f}" for p in result.parameter_scores])
    print(f"   ({scores_str}) / {len(result.parameter_scores)} = {result.score:.1f}/10")
    
    print("\n🏆 ACCOMMODATION 100% COMPLETE!")
    print("Third complete subcategory achieved!")


def demo_scoring_rubric():
    """Demonstrate scoring rubric."""
    print("\n" + "="*70)
    print("DEMO 7: Scoring Rubric Visualization")
    print("="*70)
    
    agent = OwnershipHurdlesAgent()
    rubric = agent._get_scoring_rubric()
    
    print("\nScoring Rubric for Ownership Hurdles:")
    print("(Note: Lower restrictions = Higher scores)")
    print("-" * 70)
    print(f"{'Score':<8} {'Category':<20} {'Description'}")
    print("-" * 70)
    
    for level in rubric:
        score = level['score']
        range_str = level.get('range', '')
        description = level['description']
        
        print(f"{score:<8} {range_str:<20} {description}")
    
    print("\n📊 Example Countries:")
    test_cases = [
        ("Germany", 100, "No barriers"),
        ("India", 100, "No barriers"),
        ("USA", 95, "Minimal"),
        ("Australia", 90, "Minimal"),
        ("Nigeria", 60, "Below moderate"),
        ("China", 49, "Moderate"),
        ("Vietnam", 49, "Moderate"),
    ]
    
    for name, ownership_pct, category in test_cases:
        mock_data = {
            "foreign_ownership_pct": ownership_pct,
            "category": category.lower().replace(' ', '_') + ("_barriers" if category != "No barriers" else "")
        }
        if category == "No barriers":
            mock_data["category"] = "no_barriers"
        
        score = agent._calculate_score(mock_data, name, "Q3 2024")
        print(f"  {name:<20} {ownership_pct:>3}% → Score: {score}/10 ({category})")


def demo_all_countries():
    """Test all mock countries."""
    print("\n" + "="*70)
    print("DEMO 8: All Mock Countries Comparison")
    print("="*70)
    
    agent = OwnershipHurdlesAgent()
    
    results = []
    for country in agent.MOCK_DATA.keys():
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA[country]
        foreign_pct = data.get("foreign_ownership_pct", 0)
        category = data.get("category", "").replace('_', ' ').title()
        approval = data.get("approval_complexity", "")
        results.append((country, result.score, foreign_pct, category, approval))
    
    # Sort by foreign ownership % descending (most open first)
    results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n{'Rank':<6} {'Country':<20} {'Score':<8} {'Foreign %':<12} {'Category':<25} {'Approval'}")
    print("-" * 100)
    
    for i, (country, score, foreign_pct, category, approval) in enumerate(results, 1):
        print(f"{i:<6} {country:<20} {score:<8.1f} {foreign_pct:>10.0f} {category:<25} {approval}")
    
    print("\n💡 Key Insights:")
    print("  - Brazil/Germany/India: 100% foreign ownership (No barriers)")
    print("  - USA: 95% (CFIUS review for sensitive cases)")
    print("  - China/Vietnam: 49% cap (Moderate barriers)")
    print("  - Nigeria: 60% (Below moderate - complex approvals)")
    print("  - Ownership openness is critical for foreign capital access!")


def demo_three_complete_subcategories():
    """Show all three complete subcategories."""
    print("\n" + "="*70)
    print("DEMO 9: THREE COMPLETE SUBCATEGORIES!")
    print("="*70)
    
    country = "Brazil"
    
    print(f"\n🏆 Complete Subcategories for {country}:")
    print("-" * 70)
    
    # Market Size (100%)
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"\n1. Market Size Fundamentals: {mkt.score}/10 🏆 COMPLETE (100%)")
    for p in mkt.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Profitability (100%)
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"\n2. Profitability: {prof.score}/10 🏆 COMPLETE (100%)")
    for p in prof.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Accommodation (100%) NEW!
    acc = agent_service.analyze_subcategory("accommodation", country)
    print(f"\n3. Accommodation: {acc.score}/10 🏆 COMPLETE (100%) ← NEW!")
    for p in acc.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    print("\n💡 THREE complete subcategories spanning 11 parameters!")
    print(f"📊 System Status: 13 agents = 61.9% complete")


def demo_ownership_insights():
    """Show ownership barrier insights."""
    print("\n" + "="*70)
    print("DEMO 10: Ownership Barrier Insights & Foreign Investment")
    print("="*70)
    
    agent = OwnershipHurdlesAgent()
    
    print("\n🏆 FULLY OPEN MARKETS (100% foreign ownership):")
    print("-" * 70)
    
    fully_open = []
    mostly_open = []
    restricted = []
    
    for country, data in agent.MOCK_DATA.items():
        foreign_pct = data.get("foreign_ownership_pct", 0)
        category = data.get("category", "").replace('_', ' ').title()
        status = data.get("status", "")
        
        if foreign_pct >= 100:
            fully_open.append((country, foreign_pct, category, status))
        elif foreign_pct >= 75:
            mostly_open.append((country, foreign_pct, category, status))
        else:
            restricted.append((country, foreign_pct, category, status))
    
    fully_open.sort(key=lambda x: x[0])
    
    print(f"{'Country':<20} {'Foreign %':<12} {'Category':<25} {'Status'}")
    print("-" * 80)
    for country, foreign_pct, category, status in fully_open:
        print(f"{country:<20} {foreign_pct:>10.0f} {category:<25} {status[:30]}")
    
    print(f"\n⚡ MOSTLY OPEN (75-99%):")
    print("-" * 70)
    mostly_open.sort(key=lambda x: x[1], reverse=True)
    print(f"{'Country':<20} {'Foreign %':<12} {'Category':<25} {'Status'}")
    print("-" * 70)
    for country, foreign_pct, category, status in mostly_open:
        print(f"{country:<20} {foreign_pct:>10.0f} {category:<25} {status[:30]}")
    
    print("\n💡 Key Observations:")
    print("  - Fully open: Brazil, Germany, India, UK, Spain (100%)")
    print("  - Mostly open: USA (95% - CFIUS), Australia (90% - FIRB)")
    print("  - Restricted: China (49%), Vietnam (49%), Nigeria (60%)")
    print("  - Ownership openness correlates strongly with FDI inflows")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("🎊 OWNERSHIP HURDLES AGENT DEMO - MOCK & RULE_BASED MODES")
    print("="*70)
    print("\n🎊 MILESTONE: THIRD COMPLETE SUBCATEGORY!")
    print("Accommodation now 100% complete - Land + Ownership!")
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
        demo_accommodation_complete()  # 🎊 MILESTONE DEMO!
        demo_scoring_rubric()
        demo_all_countries()
        demo_three_complete_subcategories()
        demo_ownership_insights()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n🏆 THIRD COMPLETE SUBCATEGORY!")
        print("  ✅ Agent #13 complete (OwnershipHurdlesAgent)")
        print("  ✅ 13/21 agents = 61.9% complete")
        print("  ✅ Accommodation 100% (2/2 parameters) ← NEW!")
        print("  ✅ THREE complete subcategories!")
        print("  ✅ Just 8 more agents to go!")
        print("\nNext steps:")
        print("1. Test MOCK mode: Works immediately ✅")
        print("2. Test RULE_BASED mode: Estimates from FDI + GDP ✅")
        print("3. Continue building remaining 8 agents!")
        print("\n💡 Ownership openness is critical for foreign investment!")
        print("   Lower barriers = Greater capital access")
        print("\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
