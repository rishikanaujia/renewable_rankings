#!/usr/bin/env python3
"""Demo script for Comparative Analysis Agent - SECOND SYNTHESIS AGENT!

This demonstrates the Comparative Analysis Agent (Level IV synthesis agent) that:
- Compares multiple countries side-by-side
- Identifies best/worst performers by subcategory
- Analyzes competitive landscapes
- Generates comparative rankings

ACTUAL STRUCTURE (from Implementation Guide):
Total: 18 parameter agents across 6 subcategories

Features demonstrated:
1. Multi-country comparison
2. Subcategory performance comparison  
3. Best/worst performer identification
4. Competitive landscape analysis
5. Side-by-side rankings
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from src.agents.analysis_agents import ComparativeAnalysisAgent, compare_countries
from src.agents.base_agent import AgentMode
from src.core.logger import setup_logger

# Setup logging
logger = setup_logger()


def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    print(f"\n{char * 70}")
    print(text)
    print(f"{char * 70}")


def print_country_comparison(comparison):
    """Print a single country comparison."""
    print(f"\n#{comparison.rank}. {comparison.country}")
    print(f"    Overall Score: {comparison.overall_score:.2f}/10")
    print(f"    Strengths: {comparison.strengths_count} | Weaknesses: {comparison.weaknesses_count}")
    print(f"    Top Subcategories:")
    
    # Sort subcategories by score
    sorted_subcats = sorted(
        comparison.subcategory_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    for name, score in sorted_subcats:
        print(f"      - {name}: {score:.1f}/10")


def print_subcategory_comparison(subcat):
    """Print subcategory comparison."""
    print(f"\n📊 {subcat.name}")
    print(f"   Weight: {subcat.weight:.1%} | Average: {subcat.average_score:.1f}/10")
    print(f"   Best:  {subcat.best_country} ({subcat.best_score:.1f})")
    print(f"   Worst: {subcat.worst_country} ({subcat.worst_score:.1f})")
    print(f"   Range: {subcat.best_score - subcat.worst_score:.1f} points")


def demo_basic_comparison():
    """Demo 1: Basic multi-country comparison."""
    print_header("DEMO 1: Basic Multi-Country Comparison (3 Countries)")
    
    agent = ComparativeAnalysisAgent(mode=AgentMode.MOCK)
    result = agent.compare(
        countries=["Germany", "USA", "Brazil"],
        period="Q3 2024"
    )
    
    print(f"\n📋 Comparing {len(result.countries)} countries:")
    print(f"   {', '.join(result.countries)}")
    print(f"\n💡 Summary:")
    print(f"   {result.summary}")
    
    print(f"\n🏆 Country Rankings:")
    for comp in result.country_comparisons:
        print_country_comparison(comp)
    
    print("\n" + "-" * 70)


def demo_subcategory_analysis():
    """Demo 2: Detailed subcategory comparison."""
    print_header("DEMO 2: Subcategory Performance Comparison (6 Subcategories)")
    
    result = compare_countries(
        countries=["Germany", "USA", "Brazil", "China"],
        period="Q3 2024"
    )
    
    print(f"\n🔍 Analyzing 6 subcategories across {len(result.countries)} countries")
    print(f"   Total: 18 parameter agents")
    
    print(f"\n📊 Subcategory Details:")
    for subcat in result.subcategory_comparisons:
        print_subcategory_comparison(subcat)
    
    print("\n" + "-" * 70)


def demo_large_comparison():
    """Demo 3: Large-scale comparison (6 countries)."""
    print_header("DEMO 3: Large-Scale Comparison (6 Countries)")
    
    countries = ["Germany", "USA", "Brazil", "China", "India", "Nigeria"]
    
    agent = ComparativeAnalysisAgent(mode=AgentMode.MOCK)
    result = agent.compare(countries=countries, period="Q3 2024")
    
    print(f"\n📊 Comprehensive Comparison: {len(countries)} Countries")
    
    # Rankings table
    print(f"\n{'Rank':<6} {'Country':<15} {'Score':<8} {'💪':<4} {'⚠️':<4}")
    print("-" * 40)
    for comp in result.country_comparisons:
        print(
            f"{comp.rank:<6} {comp.country:<15} "
            f"{comp.overall_score:<8.2f} "
            f"{comp.strengths_count:<4} {comp.weaknesses_count:<4}"
        )
    
    # Score distribution
    scores = [c.overall_score for c in result.country_comparisons]
    print(f"\n📈 Score Distribution:")
    print(f"   Highest: {max(scores):.2f} ({result.country_comparisons[0].country})")
    print(f"   Lowest:  {min(scores):.2f} ({result.country_comparisons[-1].country})")
    print(f"   Range:   {max(scores) - min(scores):.2f} points")
    print(f"   Average: {sum(scores) / len(scores):.2f}")
    
    print("\n" + "-" * 70)


def demo_competitive_landscape():
    """Demo 4: Competitive landscape analysis."""
    print_header("DEMO 4: Competitive Landscape Analysis")
    
    result = compare_countries(
        countries=["Germany", "USA", "Brazil", "China", "India"],
        period="Q3 2024"
    )
    
    print(f"\n🎯 Identifying Competitive Dynamics Across 6 Subcategories")
    
    # Find most/least competitive subcategories
    subcat_ranges = [
        (s.name, max(s.country_scores.values()) - min(s.country_scores.values()))
        for s in result.subcategory_comparisons
    ]
    subcat_ranges.sort(key=lambda x: x[1])
    
    print(f"\n🤝 Most Competitive Subcategories (smallest gaps):")
    for name, range_val in subcat_ranges[:3]:
        print(f"   • {name}: {range_val:.1f} point range")
    
    print(f"\n⚔️  Least Competitive Subcategories (largest gaps):")
    for name, range_val in subcat_ranges[-3:]:
        print(f"   • {name}: {range_val:.1f} point range")
    
    # Country dominance
    print(f"\n👑 Subcategory Leadership:")
    leadership = {}
    for subcat in result.subcategory_comparisons:
        leader = subcat.best_country
        leadership[leader] = leadership.get(leader, 0) + 1
    
    for country, count in sorted(leadership.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {country}: Leads in {count}/6 subcategories")
    
    print("\n" + "-" * 70)


def demo_visual_comparison():
    """Demo 5: Visual comparison matrix."""
    print_header("DEMO 5: Visual Comparison Matrix (6 Subcategories)")
    
    result = compare_countries(
        countries=["Germany", "USA", "Brazil"],
        period="Q3 2024"
    )
    
    print(f"\n📊 Side-by-Side Comparison Matrix")
    print(f"\n{'Subcategory':<30} | {'Germany':<10} | {'USA':<10} | {'Brazil':<10}")
    print("-" * 70)
    
    for subcat in result.subcategory_comparisons:
        row = f"{subcat.name[:29]:<30}"
        for country in result.countries:
            score = subcat.country_scores.get(country, 0)
            # Add indicator for best/worst
            indicator = ""
            if country == subcat.best_country:
                indicator = "🥇"
            elif country == subcat.worst_country:
                indicator = "⚠️"
            row += f" | {score:>4.1f}/10 {indicator:<3}"
        print(row)
    
    print("-" * 70)
    print(f"{'OVERALL':<30}", end="")
    for comp in result.country_comparisons:
        print(f" | {comp.overall_score:>4.1f}/10    ", end="")
    print()
    
    print("\n💡 Indicators: 🥇 = Best in subcategory, ⚠️ = Needs improvement")
    
    print("\n" + "-" * 70)


def demo_system_architecture():
    """Demo 6: System architecture context."""
    print_header("DEMO 6: Multi-Agent System Architecture")
    
    print(f"\n🏗️  COMPLETE SYSTEM ARCHITECTURE:")
    print("="*70)
    
    print(f"\n  Level V:   GlobalRankingsAgent (global analysis)")
    print(f"             ↓")
    print(f"  Level IV:  ComparativeAnalysisAgent ← THIS DEMO")
    print(f"             ↓")
    print(f"  Level III: CountryAnalysisAgent (individual profiles)")
    print(f"             ↓")
    print(f"  Level II:  6 Subcategories")
    print(f"             ├─ Regulation (5 params, 22.5%)")
    print(f"             ├─ Profitability (4 params, 22.5%)")
    print(f"             ├─ Accommodation (2 params, 17.5%)")
    print(f"             ├─ Market Size & Fundamentals (4 params, 12.5%)")
    print(f"             ├─ Competition & Ease (2 params, 12.5%)")
    print(f"             └─ System Modifiers (1 composite, 7.5%)")
    print(f"             ↓")
    print(f"  Level I:   18 Parameter Agents")
    
    print(f"\n✅ SYSTEM STATUS:")
    print(f"  • 18 Parameter Agents: COMPLETE ✓")
    print(f"  • 6 Subcategories: COMPLETE ✓")
    print(f"  • Country Analysis: COMPLETE ✓")
    print(f"  • Comparative Analysis: COMPLETE ✓ (this demo)")
    print(f"  • Global Rankings: Available")


def main():
    """Run all demos."""
    print_header("🎯 COMPARATIVE ANALYSIS AGENT DEMO", "=")
    print("\n🎊 MILESTONE: SECOND SYNTHESIS AGENT!")
    print("Compares multiple countries across all investment dimensions!")
    print("\nArchitecture: Level IV synthesis agent")
    print("Structure: 18 parameters → 6 subcategories → Country comparisons\n")
    
    # Run all demos
    demo_basic_comparison()
    demo_subcategory_analysis()
    demo_large_comparison()
    demo_competitive_landscape()
    demo_visual_comparison()
    demo_system_architecture()
    
    print_header("✅ ALL DEMOS COMPLETED!", "=")
    print("\n🎯 COMPARATIVE ANALYSIS AGENT (LEVEL IV):")
    print("  ✅ Second synthesis agent complete")
    print("  ✅ Multi-country comparison working")
    print("  ✅ 6 subcategory analysis")
    print("  ✅ Competitive landscape analysis")
    print("  ✅ Uses CountryAnalysisAgent (Level III)")
    print("  ✅ Aggregates 18 parameters")
    print("  ✅ Ready for global rankings!")
    print()


if __name__ == "__main__":
    main()
