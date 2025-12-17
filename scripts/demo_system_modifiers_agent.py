#!/usr/bin/env python3
"""Demo for System Modifiers Agent - SIXTH ACTIVE SUBCATEGORY!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import SystemModifiersAgent, analyze_system_modifiers
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Systemic Risk Spectrum")
    print("="*70)
    
    agent = SystemModifiersAgent()
    countries = [
        ("Germany", "Minimal risk", 9),
        ("USA", "Minimal risk", 9),
        ("UK", "Very low risk", 8),
        ("Australia", "Very low risk", 8),
        ("Saudi Arabia", "Low risk", 7),
        ("Spain", "Low risk", 7),
        ("Brazil", "Below moderate positive", 6),
        ("India", "Below moderate positive", 6),
        ("Chile", "Below moderate positive", 6),
        ("China", "Moderate factors", 5),
        ("South Africa", "Moderate factors", 5),
        ("Mexico", "Moderate factors", 5),
        ("Indonesia", "Moderate factors", 5),
        ("Vietnam", "Above moderate negative", 4),
        ("Argentina", "Very high negative", 2),
        ("Nigeria", "Very high negative", 2)
    ]
    
    for country, category, expected in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({category})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_system_started():
    print("\n" + "="*70)
    print("🎊 DEMO 2: SYSTEM MODIFIERS 100% STARTED!")
    print("="*70)
    print("\n🎊 SIXTH ACTIVE SUBCATEGORY! 🎊\n")
    print("(Single composite parameter - already 100%!)\n")
    
    result = agent_service.analyze_subcategory("system_modifiers", "Brazil")
    print(f"📊 Brazil System Modifiers: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/1 = 100% (composite)")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")
    
    print("\n🎊 ALL SIX SUBCATEGORIES NOW ACTIVE!")
    print("System Modifiers is a composite parameter - complete in one agent!")

def demo_all_subcategories():
    print("\n" + "="*70)
    print("DEMO 3: ALL SIX SUBCATEGORIES ACTIVE!")
    print("="*70)
    
    country = "Brazil"
    
    print(f"\n📊 {country} ALL Subcategory Analysis:")
    print("-" * 70)
    
    # All six subcategories
    reg = agent_service.analyze_subcategory("regulation", country)
    print(f"\n1. Regulation: {reg.score}/10 (5/5) 🏆 COMPLETE")
    
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"2. Market Size: {mkt.score}/10 (4/4) 🏆 COMPLETE")
    
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"3. Profitability: {prof.score}/10 (4/4) 🏆 COMPLETE")
    
    acc = agent_service.analyze_subcategory("accommodation", country)
    print(f"4. Accommodation: {acc.score}/10 (2/2) 🏆 COMPLETE")
    
    comp = agent_service.analyze_subcategory("competition_ease", country)
    print(f"5. Competition & Ease: {comp.score}/10 (2/2) 🏆 COMPLETE")
    
    # NEW subcategory
    sys_mod = agent_service.analyze_subcategory("system_modifiers", country)
    print(f"6. System Modifiers: {sys_mod.score}/10 (1/1) 🎊 ACTIVE (NEW!)")
    for p in sys_mod.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    print("\n💡 ALL SIX SUBCATEGORIES ACTIVE!")
    print("📊 18 parameters across 6 active categories!")

def main():
    print("\n" + "="*70)
    print("🎊 SYSTEM MODIFIERS AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: SIXTH ACTIVE SUBCATEGORY!")
    print("All subcategories now active!\n")
    
    try:
        demo_direct()
        demo_system_started()
        demo_all_subcategories()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🎊 SIXTH ACTIVE SUBCATEGORY!")
        print("  ✅ Agent #18 complete")
        print("  ✅ 18/21 agents = 85.7% complete")
        print("  ✅ System Modifiers active")
        print("  ✅ ALL SIX SUBCATEGORIES ACTIVE!")
        print("  ✅ Just 3 more to full system!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
