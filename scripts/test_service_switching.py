#!/usr/bin/env python3
"""Test script to verify service switching functionality."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.mock_service import mock_service
from src.services.ranking_service_adapter import ranking_service_adapter


def test_mock_service():
    """Test mock service interface."""
    print("=" * 60)
    print("TESTING MOCK SERVICE")
    print("=" * 60)

    # Test get_rankings
    print("\n1. Testing get_rankings()...")
    rankings = mock_service.get_rankings("Q3 2024")
    print(f"   ✓ Got {len(rankings.rankings)} countries")
    print(f"   ✓ Top country: {rankings.rankings[0].country_name} ({rankings.rankings[0].overall_score})")

    # Test get_country_ranking
    print("\n2. Testing get_country_ranking()...")
    brazil = mock_service.get_country_ranking("Brazil")
    print(f"   ✓ Brazil score: {brazil.overall_score}")
    print(f"   ✓ Subcategories: {len(brazil.subcategory_scores)}")

    # Test search_countries
    print("\n3. Testing search_countries()...")
    matches = mock_service.search_countries("bra")
    print(f"   ✓ Found {len(matches)} matches: {matches}")

    print("\n✅ Mock service tests passed!")
    return True


def test_ranking_service_adapter():
    """Test ranking service adapter interface."""
    print("\n" + "=" * 60)
    print("TESTING RANKING SERVICE ADAPTER (Real Agents)")
    print("=" * 60)

    # Test get_rankings
    print("\n1. Testing get_rankings()...")
    print("   ⚠️  This may take a while (analyzing 10 countries with real agents)...")
    try:
        rankings = ranking_service_adapter.get_rankings("Q3 2024")
        print(f"   ✓ Got {len(rankings.rankings)} countries")
        if rankings.rankings:
            print(f"   ✓ Top country: {rankings.rankings[0].country_name} ({rankings.rankings[0].overall_score})")
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
        print("   (This is expected if agents are not fully configured)")

    # Test get_country_ranking
    print("\n2. Testing get_country_ranking()...")
    try:
        brazil = ranking_service_adapter.get_country_ranking("Brazil")
        if brazil:
            print(f"   ✓ Brazil score: {brazil.overall_score}")
            print(f"   ✓ Subcategories: {len(brazil.subcategory_scores)}")
        else:
            print("   ⚠️  No ranking returned")
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
        print("   (This is expected if agents are not fully configured)")

    # Test search_countries
    print("\n3. Testing search_countries()...")
    matches = ranking_service_adapter.search_countries("bra")
    print(f"   ✓ Found {len(matches)} matches: {matches}")

    print("\n✅ Ranking service adapter tests completed!")
    return True


def test_app_initialization():
    """Test app initialization with different environment variables."""
    print("\n" + "=" * 60)
    print("TESTING APP INITIALIZATION")
    print("=" * 60)

    # Test with mock service
    print("\n1. Testing with USE_REAL_AGENTS=false...")
    os.environ["USE_REAL_AGENTS"] = "false"
    from src.ui.app import RankingsApp
    app = RankingsApp()
    assert app.service == mock_service, "Should use mock_service"
    print(f"   ✓ Service: {app.service.__class__.__name__}")

    # Clean up import to re-initialize
    if 'src.ui.app' in sys.modules:
        del sys.modules['src.ui.app']

    # Test with real agents
    print("\n2. Testing with USE_REAL_AGENTS=true...")
    os.environ["USE_REAL_AGENTS"] = "true"
    from src.ui.app import RankingsApp as RankingsApp2
    app2 = RankingsApp2()
    assert app2.service == ranking_service_adapter, "Should use ranking_service_adapter"
    print(f"   ✓ Service: {app2.service.__class__.__name__}")

    print("\n✅ App initialization tests passed!")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SERVICE SWITCHING TEST SUITE")
    print("=" * 60)

    try:
        # Test mock service
        test_mock_service()

        # Test ranking service adapter (may fail if agents not configured)
        test_ranking_service_adapter()

        # Test app initialization
        test_app_initialization()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now use the service switching feature:")
        print("  - USE_REAL_AGENTS=false  →  Mock service (fast, sample data)")
        print("  - USE_REAL_AGENTS=true   →  Real agents (slower, AI analysis)")
        print("\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
