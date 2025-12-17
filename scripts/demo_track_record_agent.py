#!/usr/bin/env python3
"""Demo for Track Record Agent - 50% MILESTONE REACHED!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import TrackRecordAgent, analyze_track_record
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage - Capacity Spectrum")
    print("="*70)
    
    agent = TrackRecordAgent()
    countries = [
        ("China", "758 GW", "Outstanding"),
        ("USA", "257 GW", "Outstanding"),
        ("India", "175 GW", "Outstanding"),
        ("Germany", "134 GW", "Outstanding"),
        ("Spain", "53 GW", "Excellent"),
        ("Brazil", "38.5 GW", "Very Good"),
        ("Chile", "11.5 GW", "Good"),
        ("Nigeria", "0.18 GW", "Minimal")
    ]
    
    for country, capacity, profile in countries:
        result = agent.analyze(country, "Q3 2024")
        print(f"\n📍 {country} ({capacity} - {profile})")
        print(f"Score: {result.score}/10 | Confidence: {result.confidence*100:.0f}%")

def demo_50_percent_milestone():
    print("\n" + "="*70)
    print("🎯 DEMO 2: 50% MILESTONE REACHED!")
    print("="*70)
    print("\n🎊 HALFWAY TO COMPLETION! 🎊\n")
    
    print("📊 System Status:")
    print("  ✅ 11/21 agents = 52.4% complete!")
    print("  ✅ 2 complete subcategories (100%)")
    print("  ✅ 1 well-advanced subcategory (60%)")
    print("  ✅ 3 active subcategories (50%)")
    
    result = agent_service.analyze_subcategory("regulation", "Brazil")
    print(f"\n📊 Brazil Regulation: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/5 = 60% complete")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")

def demo_system_progress():
    print("\n" + "="*70)
    print("DEMO 3: SYSTEM PROGRESS OVERVIEW")
    print("="*70)
    
    country = "Brazil"
    
    print(f"\n📊 {country} Analysis Across All Active Subcategories:")
    print("-" * 70)
    
    # Regulation (60%)
    reg = agent_service.analyze_subcategory("regulation", country)
    print(f"\n1. Regulation: {reg.score}/10 (60% complete)")
    for p in reg.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Market Size (100%)
    mkt = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"\n2. Market Size Fundamentals: {mkt.score}/10 (100% COMPLETE 🏆)")
    for p in mkt.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    # Profitability (100%)
    prof = agent_service.analyze_subcategory("profitability", country)
    print(f"\n3. Profitability: {prof.score}/10 (100% COMPLETE 🏆)")
    for p in prof.parameter_scores:
        print(f"   - {p.parameter_name}: {p.score}/10")
    
    print("\n💡 Three active subcategories spanning 11 agents!")

def main():
    print("\n" + "="*70)
    print("🎯 TRACK RECORD AGENT DEMO")
    print("="*70)
    print("\n🎊 MILESTONE: 50% OF ALL AGENTS COMPLETE!")
    print("Halfway to full system implementation!\n")
    
    try:
        demo_direct()
        demo_50_percent_milestone()
        demo_system_progress()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n🎯 50% MILESTONE REACHED!")
        print("  ✅ Agent #11 complete")
        print("  ✅ 11/21 agents = 52.4% complete")
        print("  ✅ Regulation 60% (3/5 parameters)")
        print("  ✅ 2 complete subcategories!")
        print("  ✅ Halfway to full system!")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
