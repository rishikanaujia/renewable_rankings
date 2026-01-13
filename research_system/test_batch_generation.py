#!/usr/bin/env python3
"""Test batch research generation with a small subset

This script tests the batch generation with just 3 parameters × 2 countries
to verify everything works before running the full batch.

Cost: ~$0.24 (6 documents × $0.04)
Time: ~4.5 minutes (6 documents × 45s)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
os.environ['LOG_LEVEL'] = 'INFO'

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from research_system import ResearchOrchestrator
from generate_all_research import (
    generate_batch,
    print_summary,
    save_summary_report
)


# Test configuration - small subset
TEST_PARAMETERS = [
    {'name': 'Ambition', 'key': 'ambition', 'subcategory': 'regulation'},
    {'name': 'Country Stability', 'key': 'country_stability', 'subcategory': 'regulation'},
    {'name': 'Expected Return', 'key': 'expected_return', 'subcategory': 'profitability'},
]

TEST_COUNTRIES = ["Brazil", "India"]
TEST_PERIOD = "Q4 2024"


def main():
    print("\n" + "=" * 80)
    print(" TEST BATCH GENERATION (Small Subset)")
    print("=" * 80)
    print("\n📋 Test Configuration:")
    print(f"   Parameters: {len(TEST_PARAMETERS)}")
    for p in TEST_PARAMETERS:
        print(f"      • {p['name']} ({p['subcategory']})")
    print(f"\n   Countries: {len(TEST_COUNTRIES)}")
    for c in TEST_COUNTRIES:
        print(f"      • {c}")
    print(f"\n   Total documents: {len(TEST_PARAMETERS)} × {len(TEST_COUNTRIES)} = {len(TEST_PARAMETERS) * len(TEST_COUNTRIES)}")
    print(f"   Estimated cost: ~${len(TEST_PARAMETERS) * len(TEST_COUNTRIES) * 0.04:.2f}")
    print(f"   Estimated time: ~{len(TEST_PARAMETERS) * len(TEST_COUNTRIES) * 45 / 60:.1f} minutes\n")

    response = input("⚠️  Continue with test generation? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Test cancelled by user.\n")
        return 1

    # Initialize orchestrator
    print("\n🔧 Initializing Research Orchestrator...")
    orchestrator = ResearchOrchestrator()
    print("✅ Orchestrator initialized\n")

    # Generate batch
    try:
        results = generate_batch(
            orchestrator=orchestrator,
            parameters=TEST_PARAMETERS,
            countries=TEST_COUNTRIES,
            period=TEST_PERIOD,
            use_cache=False,
            skip_existing=True
        )

        # Print summary
        print_summary(results)

        # Show stats
        print("\n" + "=" * 80)
        print(" LLM STATISTICS")
        print("=" * 80 + "\n")

        stats = orchestrator.research_agent.get_stats()
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"Total Cost: ${stats['total_cost_usd']:.2f}")

        print("\n" + "=" * 80)
        print(" TEST COMPLETE ✅")
        print("=" * 80)
        print("\n✅ If results look good, run: python research_system/generate_all_research.py\n")

        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
