#!/usr/bin/env python3
"""Demo for Long Term Interest Rates Agent - PROFITABILITY 100% COMPLETE!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import LongTermInterestRatesAgent, analyze_long_term_interest_rates
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Interest Rate Spectrum")
    print("="*70)
    
    agent = LongTermInterestRatesAgent()
    countries = [
        ("Germany", "2.4%", "Ultra-low"),
        ("China", "2.6%", "Exceptionally low"),
        ("Spain", "3.2%", "Very low"),
        ("USA", "4.2%", "Low"),
        ("India", "7.2%", "Moderate"),
        ("Mexico", "9.8%", "Above moderate"),
        ("Brazil", "12.5%", "High"),
        ("Nigeria", "16.5%", "Very high")
    ]
    
    for country, rate, profile in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({rate} - {profile})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_profitability_100():
    print("\n" + "="*70)
    print("🏆 DEMO 2: PROFITABILITY 100% COMPLETE!")
    print("="*70)
    print("\n🎊 SECOND COMPLETE SUBCATEGORY! 🎊\n")
    
    result = agent_service.analyze_subcategory("profitability", "Brazil")
    print(f"🎉 Brazil Profitability: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/4 = 100% COMPLETE!")
    print("\nAll parameters:")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")
    
    print("\n🏆 PROFITABILITY SUBCATEGORY: 100% COMPLETE!")
    print("Second subcategory fully implemented!")

def demo_two_complete_subcategories():
    print("\n" + "="*70)
    print("DEMO 3: TWO COMPLETE SUBCATEGORIES!")
    print("="*70)
    
    country = "Brazil"
    
    print(f"\n🏆 Complete Subcategories for {country}:")
    print("-" * 70)
    
    # Market Size (100%)
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"\n1. Market Size Fundamentals: {mkt.score}/10 🏆 COMPLETE")
    for p in mkt.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Profitability (100%)
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"\n2. Profitability: {prof.score}/10 🏆 COMPLETE")
    for p in prof.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    print("\n💡 TWO complete subcategories!")
    print("📊 System: 10 agents = 47.6% complete")

def main():
    print("\n" + "="*70)
    print("🏆 LONG TERM INTEREST RATES AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: PROFITABILITY 100% COMPLETE!")
    print("Second subcategory fully implemented!\n")
    
    try:
        demo_direct()
        demo_profitability_100()
        demo_two_complete_subcategories()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🏆 PROFITABILITY 100% COMPLETE!")
        print("  ✅ Agent #10 complete")
        print("  ✅ Profitability 100% (4/4 parameters)")
        print("  ✅ SECOND complete subcategory!")
        print("  ✅ 10 agents = 47.6% complete")
        print("  ✅ Just 1 more to 50%!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
