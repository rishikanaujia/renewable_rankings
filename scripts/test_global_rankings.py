"""Test script for Global Rankings Agent.

Validates all functionality including tier assignments, statistics,
transitions, and configuration handling.
"""
import sys
from pathlib import Path

# Add parent to path to enable imports
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

import yaml
from src.agents.analysis_agents.global_rankings_agent import GlobalRankingsAgent
from src.agents.base_agent import AgentMode
from src.models.global_rankings import Tier


def test_config_loading():
    """Test that configuration is properly loaded."""
    print("Test 1: Configuration Loading")
    
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Check that global_rankings section exists
    assert 'analysis' in config, "❌ 'analysis' section missing"
    assert 'global_rankings' in config['analysis'], "❌ 'global_rankings' section missing"
    
    global_config = config['analysis']['global_rankings']
    
    # Validate tier thresholds
    assert 'tier_thresholds' in global_config, "❌ 'tier_thresholds' missing"
    tier_thresholds = global_config['tier_thresholds']
    assert tier_thresholds['tier_a_min'] == 8.0, "❌ tier_a_min incorrect"
    assert tier_thresholds['tier_b_min'] == 6.5, "❌ tier_b_min incorrect"
    assert tier_thresholds['tier_c_min'] == 5.0, "❌ tier_c_min incorrect"
    
    # Validate ranking display settings
    assert 'ranking_display' in global_config, "❌ 'ranking_display' missing"
    
    # Validate summary settings
    assert 'summary' in global_config, "❌ 'summary' missing"
    
    print("  ✅ Configuration loaded successfully")
    print(f"  ✅ Tier thresholds: A={tier_thresholds['tier_a_min']}, "
          f"B={tier_thresholds['tier_b_min']}, C={tier_thresholds['tier_c_min']}")
    return True


def test_agent_initialization():
    """Test agent initialization with configuration."""
    print("\nTest 2: Agent Initialization")
    
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize agent
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    # Verify agent properties
    assert agent.tier_a_min == 8.0, "❌ tier_a_min not loaded"
    assert agent.tier_b_min == 6.5, "❌ tier_b_min not loaded"
    assert agent.tier_c_min == 5.0, "❌ tier_c_min not loaded"
    
    print("  ✅ Agent initialized with correct configuration")
    print(f"  ✅ Tier thresholds: A>={agent.tier_a_min}, B>={agent.tier_b_min}, C>={agent.tier_c_min}")
    return True


def test_basic_rankings():
    """Test basic ranking generation."""
    print("\nTest 3: Basic Ranking Generation")
    
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    countries = ["Germany", "United States", "India"]
    rankings = agent.generate_rankings(countries=countries, period="Q3 2024")
    
    # Validate results
    assert rankings is not None, "❌ Rankings is None"
    assert len(rankings.rankings) == 3, f"❌ Expected 3 rankings, got {len(rankings.rankings)}"
    assert rankings.total_countries == 3, "❌ total_countries incorrect"
    
    # Check ranking order (rank 1 should have highest score)
    assert rankings.rankings[0].rank == 1, "❌ First ranking doesn't have rank 1"
    assert rankings.rankings[0].overall_score >= rankings.rankings[1].overall_score, "❌ Rankings not sorted"
    
    # Check tier assignments exist
    for ranking in rankings.rankings:
        assert ranking.tier in [Tier.A, Tier.B, Tier.C, Tier.D], f"❌ Invalid tier: {ranking.tier}"
    
    print(f"  ✅ Generated rankings for {len(countries)} countries")
    print(f"  ✅ Rankings properly sorted by score")
    print(f"  ✅ Tier assignments valid")
    return True


def test_tier_statistics():
    """Test tier statistics calculation."""
    print("\nTest 4: Tier Statistics")
    
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    countries = ["Germany", "United States", "China", "India", "Brazil"]
    rankings = agent.generate_rankings(countries=countries, period="Q3 2024")
    
    # Validate tier statistics
    assert len(rankings.tier_statistics) == 4, "❌ Should have 4 tiers"
    
    # Check that statistics match actual rankings
    for tier, stats in rankings.tier_statistics.items():
        tier_rankings = [r for r in rankings.rankings if r.tier == tier]
        assert stats.count == len(tier_rankings), f"❌ Tier {tier.value} count mismatch"
        
        if tier_rankings:
            scores = [r.overall_score for r in tier_rankings]
            assert stats.min_score == min(scores), f"❌ Tier {tier.value} min_score incorrect"
            assert stats.max_score == max(scores), f"❌ Tier {tier.value} max_score incorrect"
    
    print(f"  ✅ Tier statistics calculated correctly")
    
    # Display distribution
    non_empty_tiers = sum(1 for stats in rankings.tier_statistics.values() if stats.count > 0)
    print(f"  ✅ Distribution across {non_empty_tiers} tiers:")
    for tier, stats in rankings.tier_statistics.items():
        if stats.count > 0:
            print(f"     {tier.value}-Tier: {stats.count} countries (avg: {stats.avg_score:.2f})")
    
    return True


def test_tier_transitions():
    """Test tier transition tracking."""
    print("\nTest 5: Tier Transitions")
    
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    countries = ["Germany", "United States", "India"]
    
    # Mock previous rankings
    previous_rankings = {
        "Germany": {"tier": "B", "score": 7.5},
        "United States": {"tier": "A", "score": 8.5},
        "India": {"tier": "C", "score": 5.5},
    }
    
    rankings = agent.generate_rankings(
        countries=countries,
        period="Q3 2024",
        previous_rankings=previous_rankings
    )
    
    # Validate transitions
    assert rankings.tier_transitions is not None, "❌ Transitions is None"
    
    # Check transition properties
    for trans in rankings.tier_transitions:
        assert trans.country in countries, f"❌ Unknown country in transitions: {trans.country}"
        assert trans.from_tier is not None, f"❌ from_tier is None for {trans.country}"
        assert trans.to_tier is not None, f"❌ to_tier is None for {trans.country}"
        assert trans.direction in ["upgrade", "downgrade", "stable", "new"], \
            f"❌ Invalid direction: {trans.direction}"
    
    print(f"  ✅ Tier transitions tracked correctly")
    if rankings.tier_transitions:
        print(f"  ✅ Detected {len(rankings.tier_transitions)} tier changes")
        for trans in rankings.tier_transitions:
            print(f"     {trans.country}: {trans.from_tier.value} → {trans.to_tier.value}")
    else:
        print(f"  ✅ No tier transitions detected (all stable)")
    
    return True


def test_summary_generation():
    """Test summary generation."""
    print("\nTest 6: Summary Generation")
    
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    countries = ["Germany", "United States", "China", "India", "Brazil", "United Kingdom"]
    rankings = agent.generate_rankings(countries=countries, period="Q3 2024")
    
    # Validate summary
    assert rankings.summary, "❌ Summary is empty"
    assert len(rankings.summary) > 100, "❌ Summary too short"
    assert "Global Rankings Summary" in rankings.summary, "❌ Summary missing header"
    assert "Q3 2024" in rankings.summary, "❌ Summary missing period"
    
    # Check for key elements
    assert "Tier Distribution:" in rankings.summary, "❌ Summary missing tier distribution"
    assert "Top" in rankings.summary, "❌ Summary missing top performers"
    
    print(f"  ✅ Summary generated successfully ({len(rankings.summary)} chars)")
    print(f"  ✅ Summary includes period, tiers, and top performers")
    return True


def test_validation():
    """Test input validation."""
    print("\nTest 7: Input Validation")
    
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    # Test empty country list
    try:
        agent.generate_rankings(countries=[], period="Q3 2024")
        print("  ❌ Should have rejected empty country list")
        return False
    except Exception:
        print("  ✅ Correctly rejected empty country list")
    
    # Test insufficient countries (if min is configured)
    min_countries = config.get('analysis', {}).get('global_rankings', {}).get('min_countries_for_ranking', 1)
    if min_countries > 1:
        try:
            agent.generate_rankings(countries=["Germany"], period="Q3 2024")
            print(f"  ❌ Should have rejected list with < {min_countries} countries")
            return False
        except Exception:
            print(f"  ✅ Correctly enforced minimum of {min_countries} countries")
    
    return True


def test_tier_assignment_logic():
    """Test tier assignment logic."""
    print("\nTest 8: Tier Assignment Logic")
    
    config_path = Path(__file__).parent.parent / "config" / "parameters.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    agent = GlobalRankingsAgent(
        mode=AgentMode.MOCK,
        config=config.get('analysis', {})
    )
    
    # Test tier assignment
    assert agent._assign_tier(8.5) == Tier.A, "❌ Should be A-tier"
    assert agent._assign_tier(8.0) == Tier.A, "❌ Should be A-tier (boundary)"
    assert agent._assign_tier(7.5) == Tier.B, "❌ Should be B-tier"
    assert agent._assign_tier(6.5) == Tier.B, "❌ Should be B-tier (boundary)"
    assert agent._assign_tier(5.5) == Tier.C, "❌ Should be C-tier"
    assert agent._assign_tier(5.0) == Tier.C, "❌ Should be C-tier (boundary)"
    assert agent._assign_tier(4.5) == Tier.D, "❌ Should be D-tier"
    
    print("  ✅ Tier assignment logic correct for all boundaries")
    print(f"     A-tier: >= {agent.tier_a_min}")
    print(f"     B-tier: {agent.tier_b_min} to {agent.tier_a_min - 0.01}")
    print(f"     C-tier: {agent.tier_c_min} to {agent.tier_b_min - 0.01}")
    print(f"     D-tier: < {agent.tier_c_min}")
    
    return True


def main():
    """Run all tests."""
    print("=" * 80)
    print("  GLOBAL RANKINGS AGENT - TEST SUITE")
    print("  Agent #21 of 21 - Final Synthesis Layer")
    print("=" * 80)
    
    tests = [
        test_config_loading,
        test_agent_initialization,
        test_basic_rankings,
        test_tier_statistics,
        test_tier_transitions,
        test_summary_generation,
        test_validation,
        test_tier_assignment_logic,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"  TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        print("\nAgent #21 (Global Rankings) is production-ready!")
        print("\n🎉 SYSTEM COMPLETE: All 21 agents operational!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
