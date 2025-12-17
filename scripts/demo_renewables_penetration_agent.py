#!/usr/bin/env python3
"""Demo script for testing the Renewables Penetration Agent.

MILESTONE: This agent COMPLETES the Market Size Fundamentals subcategory (100%)!

Run from project root:
    python scripts/demo_renewables_penetration_agent.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    RenewablesPenetrationAgent,
    analyze_renewables_penetration,
    AmbitionAgent, CountryStabilityAgent,
    PowerMarketSizeAgent, ResourceAvailabilityAgent, EnergyDependenceAgent
)
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)


def demo_direct_agent_usage():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage")
    print("="*70)
    
    agent = RenewablesPenetrationAgent(mode=AgentMode.MOCK)
    
    countries = [
        ("Norway", "World-Leading"),
        ("Brazil", "World-Leading"),
        ("Spain", "Very High"),
        ("Germany", "High"),
        ("USA", "Moderate"),
        ("South Africa", "Low")
    ]
    
    for country, profile in countries:
        print(f"\n📍 {country} ({profile})")
        print("-" * 60)
        
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        renewables_pct = data.get("renewables_pct", 0)
        dominant = data.get("dominant_source", "")
        
        print(f"Renewables:     {renewables_pct:.1f}%")
        print(f"Dominant:       {dominant}")
        print(f"Score:          {result.score}/10")
        print(f"Confidence:     {result.confidence*100:.0f}%")


def demo_complete_subcategory():
    print("\n" + "="*70)
    print("🎊 DEMO 2: COMPLETE SUBCATEGORY - MARKET SIZE FUNDAMENTALS 100%!")
    print("="*70)
    
    print("\n🎉 MILESTONE ACHIEVED: First complete subcategory!")
    print("Market Size Fundamentals now has ALL 4 parameters:\n")
    
    result = agent_service.analyze_subcategory("market_size_fundamentals", "Brazil", "Q3 2024")
    
    print(f"Brazil Market Size Fundamentals: {result.score}/10")
    print(f"Parameters analyzed: {len(result.parameter_scores)}\n")
    
    for i, param in enumerate(result.parameter_scores, 1):
        print(f"  {i}. {param.parameter_name}: {param.score}/10")
    
    print(f"\n💡 Complete subcategory score: ({' + '.join([str(p.score) for p in result.parameter_scores])}) / 4 = {result.score:.1f}/10")
    print("\n🏆 Market Size Fundamentals: 4/4 parameters = 100% COMPLETE!")


def demo_all_six_agents():
    print("\n" + "="*70)
    print("DEMO 3: All Six Agents Combined")
    print("="*70)
    
    agents = {
        "Ambition": AmbitionAgent(),
        "Stability": CountryStabilityAgent(),
        "Market": PowerMarketSizeAgent(),
        "Resources": ResourceAvailabilityAgent(),
        "Dependence": EnergyDependenceAgent(),
        "Renewables": RenewablesPenetrationAgent()
    }
    
    countries = ["Brazil", "Germany", "Spain", "USA"]
    
    print("\nShowing comprehensive investment assessment:")
    print("-" * 110)
    print(f"{'Country':<12} {'Ambition':<10} {'Stability':<10} {'Market':<10} {'Resources':<10} {'Dependence':<10} {'Renewables':<10} {'Avg'}")
    print("-" * 110)
    
    for country in countries:
        scores = {}
        for name, agent in agents.items():
            scores[name] = agent.analyze(country, "Q3 2024").score
        
        avg = sum(scores.values()) / len(scores)
        
        print(
            f"{country:<12} "
            f"{scores['Ambition']:<10.1f} "
            f"{scores['Stability']:<10.1f} "
            f"{scores['Market']:<10.1f} "
            f"{scores['Resources']:<10.1f} "
            f"{scores['Dependence']:<10.1f} "
            f"{scores['Renewables']:<10.1f} "
            f"{avg:.1f}"
        )


def main():
    print("\n" + "="*70)
    print("🌱 RENEWABLES PENETRATION AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: Completes Market Size Fundamentals (100%)!")
    print("First complete subcategory with all 4 parameters!\n")
    
    try:
        demo_direct_agent_usage()
        demo_complete_subcategory()
        demo_all_six_agents()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n🏆 MILESTONE ACHIEVED:")
        print("  ✅ Agent #6 complete")
        print("  ✅ Market Size Fundamentals 100% complete (4/4 parameters)")
        print("  ✅ First complete subcategory!")
        print("  ✅ 6 agents spanning 2 subcategories")
        print("  ✅ 28.6% of all agents complete (6/21)")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
