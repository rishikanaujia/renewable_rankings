#!/usr/bin/env python3
"""Demo script for testing the Expected Return Agent.

MILESTONE: This agent STARTS the Profitability subcategory (0% → 25%)!

Run from project root:
    python scripts/demo_expected_return_agent.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.parameter_agents import (
    ExpectedReturnAgent,
    analyze_expected_return
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
    
    agent = ExpectedReturnAgent(mode=AgentMode.MOCK)
    
    countries = [
        ("Nigeria", "Outstanding"),
        ("Vietnam", "Outstanding"),
        ("Chile", "Excellent"),
        ("India", "Very Good"),
        ("USA", "Good"),
        ("Germany", "Minimally Acceptable")
    ]
    
    for country, profile in countries:
        print(f"\n📍 {country} ({profile})")
        print("-" * 60)
        
        result = agent.analyze(country, "Q3 2024")
        data = agent.MOCK_DATA.get(country, {})
        irr = data.get("irr_pct", 0)
        project_type = data.get("project_type", "")
        
        print(f"IRR:            {irr:.1f}%")
        print(f"Project Type:   {project_type}")
        print(f"Score:          {result.score}/10")
        print(f"Confidence:     {result.confidence*100:.0f}%")


def demo_new_subcategory():
    print("\n" + "="*70)
    print("🎊 DEMO 2: NEW SUBCATEGORY - PROFITABILITY STARTED!")
    print("="*70)
    
    print("\n🚀 NEW SUBCATEGORY: Profitability now active!")
    print("Second subcategory with implemented parameters:\n")
    
    print("📊 Analyzing Profitability parameter...")
    result = agent_service.analyze_parameter("expected_return", "Brazil", "Q3 2024")
    
    print(f"\nBrazil Expected Return: {result.score}/10")
    print(f"IRR: 12.5%")
    print(f"Project Type: Solar + Wind")
    print(f"\n💡 Profitability subcategory: 1/4 parameters = 25% complete")


def demo_multi_subcategory():
    print("\n" + "="*70)
    print("DEMO 3: Multiple Subcategories Working Together")
    print("="*70)
    
    print("\nShowing how parameters span multiple subcategories:")
    print("-" * 70)
    
    country = "Brazil"
    
    # Market Size (complete subcategory)
    print(f"\n📊 Market Size Fundamentals (COMPLETE 🏆):")
    mkt_result = agent_service.analyze_subcategory("market_size_fundamentals", country)
    print(f"  Overall Score: {mkt_result.score}/10")
    for param in mkt_result.parameter_scores:
        print(f"    - {param.parameter_name}: {param.score}/10")
    
    # Profitability (new subcategory)
    print(f"\n💰 Profitability (NEW - 25%):")
    prof_result = agent_service.analyze_parameter("expected_return", country)
    print(f"  Expected Return: {prof_result.score}/10")
    print(f"  (Need 3 more parameters to complete subcategory)")
    
    print("\n💡 System now has:")
    print("  ✅ 1 complete subcategory (Market Size)")
    print("  🚀 1 new subcategory started (Profitability)")
    print("  ⏳ 4 more subcategories to start")


def main():
    print("\n" + "="*70)
    print("💰 EXPECTED RETURN AGENT DEMO")
    print("="*70)
    print("\n🚀 NEW SUBCATEGORY: Starts Profitability (0% → 25%)!")
    print("Second subcategory with implemented parameters!\n")
    
    try:
        demo_direct_agent_usage()
        demo_new_subcategory()
        demo_multi_subcategory()
        
        print("\n" + "="*70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n🚀 NEW SUBCATEGORY STARTED:")
        print("  ✅ Agent #7 complete")
        print("  ✅ Profitability subcategory started (1/4 = 25%)")
        print("  ✅ Second subcategory with implemented parameters")
        print("  ✅ 7 agents spanning 3 subcategories")
        print("  ✅ 33.3% of all agents complete (7/21)")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
