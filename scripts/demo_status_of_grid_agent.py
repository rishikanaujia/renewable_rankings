#!/usr/bin/env python3
"""Demo for Status of Grid Agent - FOURTH SUBCATEGORY STARTED!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import StatusOfGridAgent, analyze_status_of_grid
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Grid Quality Spectrum")
    print("="*70)
    
    agent = StatusOfGridAgent()
    countries = [
        ("Germany", "9.2", "Excellent"),
        ("UK", "8.8", "Excellent"),
        ("China", "8.2", "Very Good"),
        ("USA", "7.8", "Very Good"),
        ("Spain", "7.5", "Very Good"),
        ("Brazil", "6.5", "Good"),
        ("India", "5.8", "Above Adequate"),
        ("South Africa", "4.8", "Adequate"),
        ("Nigeria", "2.5", "Significant Constraints")
    ]
    
    for country, grid_score, profile in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({grid_score}/10 - {profile})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_accommodation_started():
    print("\n" + "="*70)
    print("🎊 DEMO 2: ACCOMMODATION SUBCATEGORY STARTED!")
    print("="*70)
    print("\n🚀 FOURTH ACTIVE SUBCATEGORY! 🚀\n")
    
    result = agent_service.analyze_subcategory("accommodation", "Brazil")
    print(f"🎉 Brazil Accommodation: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/2 = 50% complete")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")
    
    print("\n🎊 NEW SUBCATEGORY ACTIVE!")
    print("Fourth active subcategory in the system!")

def demo_four_subcategories():
    print("\n" + "="*70)
    print("DEMO 3: FOUR ACTIVE SUBCATEGORIES!")
    print("="*70)
    
    country = "Brazil"
    
    print(f"\n📊 {country} Analysis Across All Four Active Subcategories:")
    print("-" * 70)
    
    # Regulation (60%)
    reg = agent_service.analyze_subcategory("regulation", country)
    print(f"\n1. Regulation: {reg.score}/10 (60% complete)")
    print(f"   {len(reg.parameter_scores)}/5 parameters")
    
    # Market Size (100%)
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"\n2. Market Size Fundamentals: {mkt.score}/10 (100% COMPLETE 🏆)")
    print(f"   {len(mkt.parameter_scores)}/4 parameters")
    
    # Profitability (100%)
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"\n3. Profitability: {prof.score}/10 (100% COMPLETE 🏆)")
    print(f"   {len(prof.parameter_scores)}/4 parameters")
    
    # Accommodation (50%) NEW!
    acc = agent_service.analyze_subcategory("accommodation", country)
    print(f"\n4. Accommodation: {acc.score}/10 (50% complete) 🆕")
    print(f"   {len(acc.parameter_scores)}/2 parameters")
    
    print("\n💡 Four active subcategories spanning 12 agents!")

def main():
    print("\n" + "="*70)
    print("🚀 STATUS OF GRID AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: FOURTH SUBCATEGORY STARTED!")
    print("Accommodation subcategory now active!\n")
    
    try:
        demo_direct()
        demo_accommodation_started()
        demo_four_subcategories()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🚀 FOURTH SUBCATEGORY STARTED!")
        print("  ✅ Agent #12 complete")
        print("  ✅ 12/21 agents = 57.1% complete")
        print("  ✅ Accommodation 50% (1/2 parameters)")
        print("  ✅ 4 active subcategories!")
        print("  ✅ 2 complete subcategories!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
