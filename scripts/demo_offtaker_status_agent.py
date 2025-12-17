#!/usr/bin/env python3
"""Demo script for Offtaker Status Agent - Profitability 75%!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import OfftakerStatusAgent, analyze_offtaker_status
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Credit Rating Spectrum")
    print("="*70)
    
    agent = OfftakerStatusAgent()
    countries = [
        ("Germany", "AAA", "Superior"),
        ("UK", "AA", "Excellent"),
        ("USA", "A", "Very Good"),
        ("Brazil", "BBB", "Good"),
        ("India", "BBB-", "Adequate"),
        ("Vietnam", "BB", "Moderate"),
        ("South Africa", "BB-", "Below Moderate"),
        ("Nigeria", "B", "Weak")
    ]
    
    for country, rating, profile in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({rating} - {profile})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_profitability_75():
    print("\n" + "="*70)
    print("🎊 DEMO 2: PROFITABILITY 75% COMPLETE!")
    print("="*70)
    
    result = agent_service.analyze_subcategory("profitability", "Brazil")
    print(f"\n🎉 Brazil Profitability: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/4 = 75% complete!")
    print("\nAll parameters:")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")
    
    print("\n💡 Only 1 more parameter to complete Profitability!")

def demo_multi_country():
    print("\n" + "="*70)
    print("DEMO 3: Profitability Comparison Across Countries")
    print("="*70)
    
    countries = ["Germany", "USA", "Brazil", "India"]
    
    print("\nComparing profitability across markets:")
    print("-" * 70)
    
    for country in countries:
        result = agent_service.analyze_subcategory("profitability", country)
        print(f"\n{country}: {result.score}/10")
        for param in result.parameter_scores:
            print(f"  - {param.parameter_name}: {param.score}/10")

def main():
    print("\n" + "="*70)
    print("🏅 OFFTAKER STATUS AGENT DEMO")
    print("="*70)
    print("\n🎯 MILESTONE: Profitability reaches 75% (3/4)!")
    print("Almost complete - just 1 more parameter!\n")
    
    try:
        demo_direct()
        demo_profitability_75()
        demo_multi_country()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🎯 PROFITABILITY 75%:")
        print("  ✅ Agent #9 complete")
        print("  ✅ Profitability 75% (3/4 parameters)")
        print("  ✅ 9 agents = 42.9% complete")
        print("  ✅ Only 1 more parameter to complete Profitability!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
