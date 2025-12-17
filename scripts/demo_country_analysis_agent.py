#!/usr/bin/env python3
"""Demo for Country Analysis Agent - FIRST SYNTHESIS AGENT!"""
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
        print(f"🔍 Confidence: {result.confidence*100:.0f}%")
        
        print(f"\n📊 Subcategory Breakdown:")
        for subcat in result.subcategory_scores:
            weighted_pct = subcat.weight * 100
            print(f"  {subcat.name:.<35} {subcat.score:>4.1f}/10  "
                  f"(weight: {weighted_pct:>4.0f}%, weighted score: {subcat.weighted_score:>4.2f})")
        
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
    print("DEMO 2: Score Calculation Transparency")
    print("="*70)
    
    agent = CountryAnalysisAgent()
    result = agent.analyze("Brazil", "Q3 2024")
    
    print(f"\n🎯 {result.country} - Weighted Score Calculation")
    print("="*70)
    
    print(f"\nSubcategory Weights (sum to 100%):")
    total_weight = sum(s.weight for s in result.subcategory_scores)
    print(f"  Total Weight: {total_weight*100:.0f}%")
    
    print(f"\nDetailed Calculation:")
    total_weighted = 0.0
    for subcat in result.subcategory_scores:
        print(f"\n  {subcat.name}:")
        print(f"    Raw Score:      {subcat.score:.2f}/10")
        print(f"    Weight:         {subcat.weight*100:.0f}%")
        print(f"    Weighted Score: {subcat.score:.2f} × {subcat.weight:.2f} = {subcat.weighted_score:.2f}")
        total_weighted += subcat.weighted_score
    
    print(f"\n{'─'*70}")
    print(f"  Total Weighted Score: {total_weighted:.2f}/10")
    print(f"  Final Overall Score:  {result.overall_score:.2f}/10")
    print(f"{'─'*70}")

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

def main():
    print("\n" + "="*70)
    print("🎯 COUNTRY ANALYSIS AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: FIRST SYNTHESIS AGENT!")
    print("Aggregates all 18 parameters into country profiles!\n")
    
    try:
        demo_single_country()
        demo_score_breakdown()
        demo_comparative_view()
        demo_strength_weakness_analysis()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🎯 FIRST SYNTHESIS AGENT!")
        print("  ✅ Agent #19 complete")
        print("  ✅ 19/21 agents = 90.5% complete")
        print("  ✅ Country-level analysis working")
        print("  ✅ All 18 parameters synthesized")
        print("  ✅ Just 2 more to full system!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
