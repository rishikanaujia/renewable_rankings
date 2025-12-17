#!/usr/bin/env python3
"""Demo for Ownership Consolidation Agent - FIFTH ACTIVE SUBCATEGORY!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import OwnershipConsolidationAgent, analyze_ownership_consolidation
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Market Concentration Spectrum")
    print("="*70)
    
    agent = OwnershipConsolidationAgent()
    countries = [
        ("Germany", "18%", "Very low", 8),
        ("USA", "22%", "Low", 7),
        ("India", "28%", "Low", 7),
        ("Australia", "25%", "Low", 7),
        ("Brazil", "35%", "Below moderate", 6),
        ("UK", "32%", "Below moderate", 6),
        ("South Africa", "38%", "Below moderate", 6),
        ("Spain", "45%", "Moderate", 5),
        ("Chile", "42%", "Moderate", 5),
        ("China", "55%", "Above moderate", 4),
        ("Vietnam", "62%", "High", 3),
        ("Nigeria", "75%", "Very high", 2),
        ("Indonesia", "82%", "Extreme monopoly", 1)
    ]
    
    for country, top3, category, expected in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({top3} by top 3 - {category})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_competition_started():
    print("\n" + "="*70)
    print("🚀 DEMO 2: COMPETITION & EASE 50% STARTED!")
    print("="*70)
    print("\n🎊 FIFTH ACTIVE SUBCATEGORY! 🎊\n")
    
    result = agent_service.analyze_subcategory("competition_ease", "Brazil")
    print(f"📊 Brazil Competition & Ease: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/2 = 50% started")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")
    
    print("\n🚀 FIFTH ACTIVE SUBCATEGORY!")
    print("Competition & Ease now active in the system!")

def demo_system_progress():
    print("\n" + "="*70)
    print("DEMO 3: OVERALL SYSTEM PROGRESS")
    print("="*70)
    
    print(f"\n📊 System Status:")
    print("  ✅ 16/21 agents = 76.2% complete")
    print("  ✅ 4 complete subcategories (100%)")
    print("  ✅ 1 new subcategory started (50%)")
    print("  ✅ Just 5 more agents to full system!")
    
    country = "Brazil"
    
    print(f"\n📊 {country} Analysis:")
    print("-" * 70)
    
    # Four complete subcategories
    reg = agent_service.analyze_subcategory("regulation", country)
    print(f"\nRegulation: {reg.score}/10 (100% COMPLETE 🏆)")
    
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"Market Size: {mkt.score}/10 (100% COMPLETE 🏆)")
    
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"Profitability: {prof.score}/10 (100% COMPLETE 🏆)")
    
    acc = agent_service.analyze_subcategory("accommodation", country)
    print(f"Accommodation: {acc.score}/10 (100% COMPLETE 🏆)")
    
    # New subcategory
    comp = agent_service.analyze_subcategory("competition_ease", country)
    print(f"Competition & Ease: {comp.score}/10 (50% started) 🚀")

def main():
    print("\n" + "="*70)
    print("🚀 OWNERSHIP CONSOLIDATION AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: FIFTH ACTIVE SUBCATEGORY!")
    print("Competition & Ease now started!\n")
    
    try:
        demo_direct()
        demo_competition_started()
        demo_system_progress()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🚀 FIFTH ACTIVE SUBCATEGORY!")
        print("  ✅ Agent #16 complete")
        print("  ✅ 16/21 agents = 76.2% complete")
        print("  ✅ Competition & Ease 50% (1/2 parameters)")
        print("  ✅ FOUR complete subcategories!")
        print("  ✅ Just 5 more to full system!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
