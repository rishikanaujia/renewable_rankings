"""Demo script for Global Rankings Agent.

This script demonstrates the complete functionality of the Global Rankings Agent,
including tier assignments, statistics, and transitions.
"""
import sys
from pathlib import Path

# Add parent to path to enable imports
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

import yaml
from src.agents.analysis_agents.global_rankings_agent import GlobalRankingsAgent
from src.agents.base_agent import AgentMode


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def demo_basic_rankings():
    """Demo basic global rankings functionality."""
    print_section("DEMO 1: Basic Global Rankings")
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize agent
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    # Generate rankings for a set of countries
    countries = [
        "Germany",
        "United States",
        "China",
        "India",
        "Brazil",
        "United Kingdom",
        "Japan",
        "Australia"
    ]
    
    print(f"Generating global rankings for {len(countries)} countries...")
    rankings = agent.generate_rankings(
        countries=countries,
        period="Q3 2024"
    )
    
    # Display results
    print(f"\n{rankings.summary}\n")
    
    print("Detailed Rankings:")
    for ranking in rankings.rankings:
        print(f"  #{ranking.rank:2d}: {ranking.country:20s} "
              f"Score: {ranking.overall_score:.2f}  "
              f"Tier: {ranking.tier.value}")
    
    # Display tier statistics
    print("\n\nTier Statistics:")
    for tier, stats in rankings.tier_statistics.items():
        if stats.count > 0:
            print(f"\n{tier.value}-Tier:")
            print(f"  Countries: {stats.count}")
            print(f"  Average Score: {stats.avg_score:.2f}")
            print(f"  Score Range: {stats.min_score:.2f} - {stats.max_score:.2f}")
            print(f"  Members: {', '.join(stats.countries)}")


def demo_tier_transitions():
    """Demo tier transition tracking."""
    print_section("DEMO 2: Tier Transitions")
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize agent
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    countries = ["Germany", "United States", "China", "India", "Brazil"]
    
    # Generate current rankings
    print("Generating Q3 2024 rankings...")
    current = agent.generate_rankings(
        countries=countries,
        period="Q3 2024"
    )
    
    # Create mock previous period data
    previous_rankings = {
        "Germany": {"tier": "A", "score": 8.3},
        "United States": {"tier": "A", "score": 8.6},
        "China": {"tier": "B", "score": 7.1},
        "India": {"tier": "C", "score": 5.8},
        "Brazil": {"tier": "C", "score": 5.3},
    }
    
    # Generate rankings with transition tracking
    print("Generating Q4 2024 rankings with transition tracking...")
    updated = agent.generate_rankings(
        countries=countries,
        period="Q4 2024",
        previous_rankings=previous_rankings
    )
    
    # Display transitions
    if updated.tier_transitions:
        print("\nTier Transitions:")
        for trans in updated.tier_transitions:
            direction_icon = "⬆️" if trans.direction == "upgrade" else "⬇️"
            print(f"  {direction_icon} {trans.country}: "
                  f"{trans.from_tier.value}-tier → {trans.to_tier.value}-tier "
                  f"({trans.from_score:.2f} → {trans.to_score:.2f})")
    else:
        print("\nNo tier transitions detected.")
    
    # Show current tier distribution
    print("\nCurrent Tier Distribution:")
    for tier, stats in updated.tier_statistics.items():
        if stats.count > 0:
            print(f"  {tier.value}-Tier: {stats.count} countries")


def demo_large_scale_rankings():
    """Demo rankings with larger country set."""
    print_section("DEMO 3: Large-Scale Rankings")
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize agent
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    # Larger set of countries
    countries = [
        # Americas
        "United States", "Canada", "Brazil", "Mexico", "Chile", "Argentina",
        # Europe
        "Germany", "United Kingdom", "France", "Spain", "Italy", "Netherlands",
        "Sweden", "Norway", "Denmark", "Poland",
        # Asia
        "China", "Japan", "India", "South Korea", "Singapore", "Thailand",
        "Vietnam", "Indonesia",
        # Oceania
        "Australia", "New Zealand",
        # Africa
        "South Africa", "Morocco", "Kenya",
        # Middle East
        "UAE", "Saudi Arabia"
    ]
    
    print(f"Generating rankings for {len(countries)} countries...")
    rankings = agent.generate_rankings(
        countries=countries,
        period="Q3 2024"
    )
    
    # Show tier distribution
    print("\nTier Distribution:")
    for tier in ["A", "B", "C", "D"]:
        tier_obj = getattr(rankings.tier_statistics, tier, None)
        if tier_obj:
            stats = rankings.tier_statistics[tier_obj]
            print(f"  {tier}-Tier: {stats.count} countries ({stats.count/len(countries)*100:.1f}%)")
    
    # Show top 10
    print("\nTop 10 Countries:")
    for ranking in rankings.rankings[:10]:
        print(f"  #{ranking.rank:2d}: {ranking.country:20s} "
              f"{ranking.overall_score:.2f} ({ranking.tier.value})")
    
    # Show tier averages
    print("\nTier Averages:")
    for tier, stats in rankings.tier_statistics.items():
        if stats.count > 0:
            print(f"  {tier.value}-Tier: {stats.avg_score:.2f} (n={stats.count})")


def demo_tier_boundaries():
    """Demo tier boundary analysis."""
    print_section("DEMO 4: Tier Boundary Analysis")
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize agent
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    print(f"Tier Thresholds:")
    print(f"  A-Tier: >= {agent.tier_a_min}")
    print(f"  B-Tier: {agent.tier_b_min} - {agent.tier_a_min - 0.01}")
    print(f"  C-Tier: {agent.tier_c_min} - {agent.tier_b_min - 0.01}")
    print(f"  D-Tier: < {agent.tier_c_min}")
    
    countries = ["Germany", "United States", "India", "Brazil", "China"]
    rankings = agent.generate_rankings(countries=countries, period="Q3 2024")
    
    print("\nCountries Near Tier Boundaries:")
    for ranking in rankings.rankings:
        score = ranking.overall_score
        tier = ranking.tier.value
        
        # Check distance to boundaries
        if tier == "A" and score < agent.tier_a_min + 0.5:
            print(f"  {ranking.country}: {score:.2f} (A-tier, "
                  f"{score - agent.tier_a_min:.2f} above B-tier boundary)")
        elif tier == "B":
            dist_to_a = agent.tier_a_min - score
            dist_to_c = score - agent.tier_b_min
            closer = "A" if dist_to_a < dist_to_c else "C"
            print(f"  {ranking.country}: {score:.2f} (B-tier, "
                  f"closer to {closer}-tier)")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  GLOBAL RANKINGS AGENT - DEMONSTRATION")
    print("  Agent #21 of 21 - Final Synthesis Layer")
    print("=" * 80)
    
    try:
        demo_basic_rankings()
        demo_tier_transitions()
        demo_large_scale_rankings()
        demo_tier_boundaries()
        
        print_section("DEMONSTRATION COMPLETE")
        print("✅ All demos executed successfully!")
        print("\nAgent #21 (Global Rankings) is now fully operational.")
        print("\n🎉 CONGRATULATIONS! All 21 agents are now complete!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
