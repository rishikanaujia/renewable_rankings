#!/usr/bin/env python3
"""Demo for Competitive Landscape Agent - FIFTH COMPLETE SUBCATEGORY!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import CompetitiveLandscapeAgent, analyze_competitive_landscape
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Market Entry Ease Spectrum")
    print("="*70)
    
    agent = CompetitiveLandscapeAgent()
    countries = [
        ("Germany", "Minimal barriers", 9),
        ("USA", "Very low barriers", 8),
        ("UK", "Very low barriers", 8),
        ("Australia", "Very low barriers", 8),
        ("Brazil", "Low barriers", 7),
        ("India", "Low barriers", 7),
        ("Chile", "Low barriers", 7),
        ("Spain", "Below moderate barriers", 6),
        ("South Africa", "Below moderate barriers", 6),
        ("Saudi Arabia", "Below moderate barriers", 6),
        ("China", "Moderate barriers", 5),
        ("Argentina", "Moderate barriers", 5),
        ("Vietnam", "Above moderate barriers", 4),
        ("Mexico", "High barriers", 3),
        ("Nigeria", "Very high barriers", 2),
        ("Indonesia", "Very high barriers", 2)
    ]
    
    for country, category, expected in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({category})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_competition_complete():
    print("\n" + "="*70)
    print("🏆 DEMO 2: COMPETITION & EASE 100% COMPLETE!")
    print("="*70)
    print("\n🎊 FIFTH COMPLETE SUBCATEGORY! 🎊\n")
    
    result = agent_service.analyze_subcategory("competition_ease", "Brazil")
    print(f"🎉 Brazil Competition & Ease: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/2 = 100% COMPLETE!")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")
    
    print("\n🏆 FIFTH COMPLETE SUBCATEGORY!")
    print("Regulation, Market Size, Profitability, Accommodation, AND Competition all 100%!")

def demo_five_complete_subcategories():
    print("\n" + "="*70)
    print("DEMO 3: FIVE COMPLETE SUBCATEGORIES!")
    print("="*70)
    
    country = "Brazil"
    
    print(f"\n📊 {country} Complete Subcategory Analysis:")
    print("-" * 70)
    
    # Five complete subcategories
    reg = agent_service.analyze_subcategory("regulation", country)
    print(f"\n1. Regulation: {reg.score}/10 🏆 COMPLETE")
    
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"2. Market Size: {mkt.score}/10 🏆 COMPLETE")
    
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"3. Profitability: {prof.score}/10 🏆 COMPLETE")
    
    acc = agent_service.analyze_subcategory("accommodation", country)
    print(f"4. Accommodation: {acc.score}/10 🏆 COMPLETE")
    
    # NEW complete subcategory
    comp = agent_service.analyze_subcategory("competition_ease", country)
    print(f"5. Competition & Ease: {comp.score}/10 🏆 COMPLETE (NEW!)")
    for p in comp.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    print("\n💡 FIVE complete subcategories!")
    print("📊 17 parameters across 5 complete categories!")

def main():
    print("\n" + "="*70)
    print("🏆 COMPETITIVE LANDSCAPE AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: FIFTH COMPLETE SUBCATEGORY!")
    print("Competition & Ease now 100% complete!\n")
    
    try:
        demo_direct()
        demo_competition_complete()
        demo_five_complete_subcategories()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🏆 FIFTH COMPLETE SUBCATEGORY!")
        print("  ✅ Agent #17 complete")
        print("  ✅ 17/21 agents = 80.95% complete")
        print("  ✅ Competition & Ease 100% (2/2 parameters)")
        print("  ✅ FIVE complete subcategories!")
        print("  ✅ Just 4 more to full system!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
