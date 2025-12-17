#!/usr/bin/env python3
"""Demo script for Revenue Stream Stability Agent - Profitability 50%!"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import RevenueStreamStabilityAgent, analyze_revenue_stream_stability
from src.agents.agent_service import agent_service
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)

def demo_direct():
    print("\n" + "="*70)
    print("DEMO 1: Direct Agent Usage")
    print("="*70)
    
    agent = RevenueStreamStabilityAgent()
    countries = [("USA", "25y"), ("India", "25y"), ("Brazil", "20y"), ("UK", "15y"), ("Australia", "10y"), ("Nigeria", "5y")]
    
    for country, term in countries:
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        print(f"\n📍 {country} ({term} PPA)")
        print(f"Term: {data.get('ppa_term_years')}y | Score: {result.score}/10")

def demo_profitability_50():
    print("\n" + "="*70)
    print("🎊 DEMO 2: PROFITABILITY 50% COMPLETE!")
    print("="*70)
    
    result = agent_service.analyze_subcategory("profitability", "Brazil")
    print(f"\nBrazil Profitability: {result.score}/10")
    print(f"Parameters: {len(result.parameter_scores)}/4 = 50% complete!")
    for param in result.parameter_scores:
        print(f"  - {param.parameter_name}: {param.score}/10")

def main():
    print("\n" + "="*70)
    print("📊 REVENUE STREAM STABILITY AGENT DEMO")
    print("="*70)
    print("\n💪 MILESTONE: Profitability reaches 50% (2/4)!\n")
    
    try:
        demo_direct()
        demo_profitability_50()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n💪 PROFITABILITY 50%:")
        print("  ✅ Agent #8 complete")
        print("  ✅ Profitability 50% (2/4 parameters)")
        print("  ✅ 8 agents = 38.1% complete")
        print("\n")
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
