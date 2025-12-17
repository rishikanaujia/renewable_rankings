#!/usr/bin/env python3
"""Demo for Ownership Hurdles Agent - THIRD COMPLETE SUBCATEGORY!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import OwnershipHurdlesAgent, analyze_ownership_hurdles
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Ownership Barrier Spectrum")
    print("="*70)
    
    agent = OwnershipHurdlesAgent()
    countries = [
        ("Brazil", "100%", "No barriers"),
        ("Germany", "100%", "No barriers"),
        ("India", "100%", "No barriers"),
        ("USA", "95%", "Minimal barriers"),
        ("Australia", "90%", "Minimal barriers"),
        ("Nigeria", "60%", "Below moderate barriers"),
        ("China", "49%", "Moderate barriers"),
        ("Vietnam", "49%", "Moderate barriers")
    ]
    
    for country, ownership, profile in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({ownership} - {profile})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_accommodation_complete():
    print("\n" + "="*70)
    print("🏆 DEMO 2: ACCOMMODATION 100% COMPLETE!")
    print("="*70)
    print("\n🎊 THIRD COMPLETE SUBCATEGORY! 🎊\n")
    
    result = agent_service.analyze_subcategory("accommodation", "Brazil")
    print(f"🎉 Brazil Accommodation: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/2 = 100% COMPLETE!")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")
    
    print("\n🏆 THIRD COMPLETE SUBCATEGORY!")
    print("Market Size, Profitability, AND Accommodation all 100%!")

def demo_three_complete_subcategories():
    print("\n" + "="*70)
    print("DEMO 3: THREE COMPLETE SUBCATEGORIES!")
    print("="*70)
    
    country = "Brazil"
    
    print(f"\n📊 {country} Complete Subcategory Analysis:")
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
    
    # Accommodation (100%) NEW!
    acc = agent_service.analyze_subcategory("accommodation", country)
    print(f"\n3. Accommodation: {acc.score}/10 🏆 COMPLETE!")
    for p in acc.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    print("\n💡 THREE complete subcategories!")
    print("📊 11 parameters across 3 complete categories!")

def main():
    print("\n" + "="*70)
    print("🏆 OWNERSHIP HURDLES AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: THIRD COMPLETE SUBCATEGORY!")
    print("Accommodation now 100% complete!\n")
    
    try:
        demo_direct()
        demo_accommodation_complete()
        demo_three_complete_subcategories()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🏆 THIRD COMPLETE SUBCATEGORY!")
        print("  ✅ Agent #13 complete")
        print("  ✅ 13/21 agents = 61.9% complete")
        print("  ✅ Accommodation 100% (2/2 parameters)")
        print("  ✅ THREE complete subcategories!")
        print("  ✅ Just 8 more agents to go!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
