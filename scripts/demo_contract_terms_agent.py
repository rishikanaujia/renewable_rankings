#!/usr/bin/env python3
"""Demo for Contract Terms Agent - FOURTH COMPLETE SUBCATEGORY!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import ContractTermsAgent, analyze_contract_terms
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Contract Quality Spectrum")
    print("="*70)
    
    agent = ContractTermsAgent()
    countries = [
        ("Germany", "Best-in-class", 10),
        ("UK", "Best-in-class", 10),
        ("Saudi Arabia", "Excellent", 9),
        ("USA", "Excellent", 9),
        ("Brazil", "Very good", 8),
        ("Australia", "Very good", 8),
        ("Chile", "Very good", 8),
        ("South Africa", "Good", 7),
        ("China", "Good", 7),
        ("India", "Above adequate", 6),
        ("Spain", "Adequate", 5),
        ("Vietnam", "Below adequate", 4),
        ("Nigeria", "Very poor", 2)
    ]
    
    for country, category, expected in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({category})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_regulation_complete():
    print("\n" + "="*70)
    print("🏆 DEMO 2: REGULATION 100% COMPLETE!")
    print("="*70)
    print("\n🎊 FOURTH COMPLETE SUBCATEGORY! 🎊\n")
    
    result = agent_service.analyze_subcategory("regulation", "Brazil")
    print(f"🎉 Brazil Regulation: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/5 = 100% COMPLETE!")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")
    
    print("\n🏆 FOURTH COMPLETE SUBCATEGORY!")
    print("Regulation, Market Size, Profitability, AND Accommodation all 100%!")

def demo_four_complete_subcategories():
    print("\n" + "="*70)
    print("DEMO 3: FOUR COMPLETE SUBCATEGORIES!")
    print("="*70)
    
    country = "Brazil"
    
    print(f"\n📊 {country} Complete Subcategory Analysis:")
    print("-" * 70)
    
    # Regulation (100%) NEW!
    reg = agent_service.analyze_subcategory("regulation", country)
    print(f"\n1. Regulation: {reg.score}/10 🏆 COMPLETE!")
    for p in reg.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Market Size (100%)
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"\n2. Market Size Fundamentals: {mkt.score}/10 🏆 COMPLETE")
    for p in mkt.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Profitability (100%)
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"\n3. Profitability: {prof.score}/10 🏆 COMPLETE")
    for p in prof.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Accommodation (100%)
    acc = agent_service.analyze_subcategory("accommodation", country)
    print(f"\n4. Accommodation: {acc.score}/10 🏆 COMPLETE")
    for p in acc.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    print("\n💡 FOUR complete subcategories!")
    print("📊 15 parameters across 4 complete categories!")

def main():
    print("\n" + "="*70)
    print("🏆 CONTRACT TERMS AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: FOURTH COMPLETE SUBCATEGORY!")
    print("Regulation now 100% complete!\n")
    
    try:
        demo_direct()
        demo_regulation_complete()
        demo_four_complete_subcategories()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🏆 FOURTH COMPLETE SUBCATEGORY!")
        print("  ✅ Agent #15 complete")
        print("  ✅ 15/21 agents = 71.4% complete")
        print("  ✅ Regulation 100% (5/5 parameters)")
        print("  ✅ FOUR complete subcategories!")
        print("  ✅ Just 6 more agents to go!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
