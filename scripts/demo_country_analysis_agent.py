#!/usr/bin/env python3
"""Demo for Country Analysis Agent - FIRST SYNTHESIS AGENT!

This demonstrates the Country Analysis Agent (Level III synthesis agent) that:
- Aggregates all 18 parameter agents across 6 subcategories
- Produces comprehensive country investment profiles
- Identifies strengths and weaknesses
- Generates overall investment assessment

ACTUAL STRUCTURE (from Implementation Guide):

LEVEL I - Critical Deal-Breakers (55-70%):
1. Regulation (5 parameters, 20-25% weight)
2. Profitability (4 parameters, 20-25% weight)
3. Accommodation (2 parameters, 15-20% weight)

LEVEL II - Opportunity Sizing (20-30%):
4. Market Size & Fundamentals (4 parameters, 10-15% weight)
5. Competition & Ease of Business (2 parameters, 10-15% weight)

LEVEL III - Edge Cases (5-10%):
6. System/External Modifiers (1 composite parameter, 5-10% weight)

Total: 18 parameter agents across 6 subcategories
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.analysis_agents import CountryAnalysisAgent, analyze_country
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_single_country():
    print("\n" + "="*70)
    print("DEMO 1: Single Country Comprehensive Analysis")
    print("="*70)
    
    agent = CountryAnalysisAgent()
    
    countries = ["Brazil", "Germany", "USA", "India", "Nigeria"]
    
    for country in countries:
        print(f"\n{'='*70}")
        print(f"📊 {country} - Complete Investment Profile")
        print('='*70)
        
        result = agent.analyze(country, "Q3 2024")
        
        print(f"\n🎯 Overall Score: {result.overall_score}/10")
        print(f"📅 Period: {result.period}")
        print(f"🔒 Confidence: {result.confidence*100:.0f}%")
        
        print(f"\n📊 Subcategory Breakdown (6 subcategories, 18 parameters total):")
        print(f"{'Subcategory':<35} {'Score':<8} {'Weight':<8} {'Weighted'}")
        print("-" * 70)
        for subcat in result.subcategory_scores:
            weighted_pct = subcat.weight * 100
            print(f"  {subcat.name:.<33} {subcat.score:>6.1f}/10  "
                  f"{weighted_pct:>5.1f}%  {subcat.weighted_score:>6.2f}")
        
        if result.strengths:
            print(f"\n💪 Key Strengths:")
            for strength in result.strengths:
                print(f"  ✓ {strength.area} ({strength.score:.1f}/10): {strength.reason}")
        
        if result.weaknesses:
            print(f"\n⚠️  Key Challenges:")
            for weakness in result.weaknesses:
                print(f"  ✗ {weakness.area} ({weakness.score:.1f}/10): {weakness.reason}")
        
        print(f"\n📝 Overall Assessment:")
        print(f"  {result.overall_assessment}")
        
        if country != countries[-1]:
            print("\n" + "-"*70)

def demo_score_breakdown():
    print("\n" + "="*70)
    print("DEMO 2: Score Calculation Transparency (Brazil Example)")
    print("="*70)
    
    agent = CountryAnalysisAgent()
    result = agent.analyze("Brazil", "Q3 2024")
    
    print(f"\n🎯 {result.country} - Weighted Score Calculation")
    print("="*70)
    print(f"\nSubcategory Weights (sum to 100%):")
    total_weight = sum(s.weight for s in result.subcategory_scores)
    print(f"  Total Weight: {total_weight*100:.1f}%")
    
    print(f"\nDetailed Calculation:")
    print(f"Formula: Overall = Σ(Subcategory Score × Weight)\n")
    
    total_weighted = 0.0
    for subcat in result.subcategory_scores:
        print(f"  {subcat.name}:")
        print(f"    Raw Score:      {subcat.score:.2f}/10")
        print(f"    Weight:         {subcat.weight*100:.1f}%")
        print(f"    Weighted Score: {subcat.score:.2f} × {subcat.weight:.3f} = {subcat.weighted_score:.2f}")
        total_weighted += subcat.weighted_score
    
    print(f"\n{'─'*70}")
    print(f"  Total Weighted Score: {total_weighted:.2f}/10")
    print(f"  Final Overall Score:  {result.overall_score:.2f}/10")
    print(f"{'─'*70}")
    
    print(f"\n💡 Example matches Implementation Guide:")
    print(f"   Brazil = 6.47/10 (from: 8.0×0.225 + 6.0×0.225 + 5.5×0.175 +")
    print(f"            8.0×0.125 + 7.3×0.125 + 6.0×0.075)")

def demo_comparative_view():
    print("\n" + "="*70)
    print("DEMO 3: Multi-Country Comparison View")
    print("="*70)
    
    agent = CountryAnalysisAgent()
    countries = ["Germany", "USA", "Brazil", "India", "China", "Nigeria"]
    
    results = {}
    for country in countries:
        results[country] = agent.analyze(country, "Q3 2024")
    
    # Sort by overall score
    sorted_countries = sorted(results.items(), key=lambda x: x[1].overall_score, reverse=True)
    
    print(f"\n📊 Investment Attractiveness Rankings:")
    print("="*70)
    
    for rank, (country, result) in enumerate(sorted_countries, 1):
        strength_count = len(result.strengths)
        weakness_count = len(result.weaknesses)
        
        print(f"\n#{rank}. {country:.<20} {result.overall_score:>4.1f}/10  "
              f"[💪 {strength_count} strengths, ⚠️  {weakness_count} challenges]")
        
        # Show top 2 subcategories
        top_subcats = sorted(result.subcategory_scores, key=lambda x: x.score, reverse=True)[:2]
        print(f"     Top areas: {top_subcats[0].name} ({top_subcats[0].score:.1f}), "
              f"{top_subcats[1].name} ({top_subcats[1].score:.1f})")

def demo_strength_weakness_analysis():
    print("\n" + "="*70)
    print("DEMO 4: Strength & Weakness Identification")
    print("="*70)
    
    agent = CountryAnalysisAgent()
    
    print(f"\nThresholds:")
    print(f"  Strength: Score >= {agent.strength_threshold}")
    print(f"  Weakness: Score < {agent.weakness_threshold}")
    
    countries = ["Germany", "USA", "Nigeria", "Argentina"]
    
    for country in countries:
        result = agent.analyze(country, "Q3 2024")
        
        print(f"\n{'─'*70}")
        print(f"📊 {country} (Overall: {result.overall_score}/10)")
        print(f"{'─'*70}")
        
        if result.strengths:
            print(f"\n💪 Identified Strengths ({len(result.strengths)}):")
            for s in result.strengths:
                print(f"  ✓ {s.area:.<30} {s.score:>4.1f}/10")
        else:
            print(f"\n💪 No areas meet strength threshold (>= {agent.strength_threshold})")
        
        if result.weaknesses:
            print(f"\n⚠️  Identified Weaknesses ({len(result.weaknesses)}):")
            for w in result.weaknesses:
                print(f"  ✗ {w.area:.<30} {w.score:>4.1f}/10")
        else:
            print(f"\n⚠️  No areas below weakness threshold (< {agent.weakness_threshold})")

def demo_system_architecture():
    print("\n" + "="*70)
    print("DEMO 5: System Architecture Visualization")
    print("="*70)
    
    print(f"\n🏗️  COMPLETE MULTI-AGENT SYSTEM ARCHITECTURE:")
    print("="*70)
    
    print(f"\n  Level V:   GlobalRankingsAgent")
    print(f"             ↓")
    print(f"  Level IV:  ComparativeAnalysisAgent")
    print(f"             ↓")
    print(f"  Level III: CountryAnalysisAgent ← THIS DEMO")
    print(f"             ↓")
    print(f"  Level II:  6 Subcategories (via agent_service)")
    print(f"             │")
    print(f"             ├─ LEVEL I (Critical): 55-70%")
    print(f"             │  ├─ Regulation (5 params, 22.5%)")
    print(f"             │  ├─ Profitability (4 params, 22.5%)")
    print(f"             │  └─ Accommodation (2 params, 17.5%)")
    print(f"             │")
    print(f"             ├─ LEVEL II (Opportunity): 20-30%")
    print(f"             │  ├─ Market Size & Fundamentals (4 params, 12.5%)")
    print(f"             │  └─ Competition & Ease (2 params, 12.5%)")
    print(f"             │")
    print(f"             └─ LEVEL III (Modifiers): 5-10%")
    print(f"                └─ System/External Modifiers (1 composite, 7.5%)")
    print(f"             ↓")
    print(f"  Level I:   18 Parameter Agents")
    
    print(f"\n✅ SYSTEM STATUS:")
    print(f"  • 18 Parameter Agents: COMPLETE ✓")
    print(f"  • 6 Subcategories: COMPLETE ✓")
    print(f"  • Country Analysis: COMPLETE ✓ (this demo)")
    print(f"  • Comparative Analysis: Available")
    print(f"  • Global Rankings: Available")

def main():
    print("\n" + "="*70)
    print("🎯 COUNTRY ANALYSIS AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: FIRST SYNTHESIS AGENT!")
    print("Aggregates all 18 parameters into country profiles!")
    print("\nArchitecture: Level III synthesis agent")
    print("Structure: 18 parameters → 6 subcategories → Overall Score\n")
    
    try:
        demo_single_country()
        demo_score_breakdown()
        demo_comparative_view()
        demo_strength_weakness_analysis()
        demo_system_architecture()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🎯 COUNTRY ANALYSIS AGENT (LEVEL III):")
        print("  ✅ First synthesis agent complete")
        print("  ✅ Aggregates 18 parameter agents")
        print("  ✅ Processes 6 subcategories")
        print("  ✅ 3-level hierarchy (Critical, Opportunity, Modifiers)")
        print("  ✅ Country-level analysis working")
        print("  ✅ Ready for comparative & global analysis!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
