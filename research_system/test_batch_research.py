#!/usr/bin/env python3
"""Test batch research generation for multiple countries"""

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

def main():
    print("\n" + "=" * 80)
    print(" BATCH RESEARCH GENERATION: Ambition Parameter")
    print("=" * 80 + "\n")

    # Initialize orchestrator
    print("🔧 Initializing Research Orchestrator...")
    orchestrator = ResearchOrchestrator()

    parameter = "Ambition"
    countries = ["Brazil", "India", "China"]
    period = "Q4 2024"

    print(f"\n📋 Batch Configuration:")
    print(f"   Parameter: {parameter}")
    print(f"   Countries: {', '.join(countries)}")
    print(f"   Period: {period}")
    print(f"   Total: {len(countries)} research documents")
    print(f"\n⏳ Generating research... (this will take 2-3 minutes)\n")

    results = {}

    for i, country in enumerate(countries, 1):
        print("\n" + "-" * 80)
        print(f" [{i}/{len(countries)}] Generating: {country}")
        print("-" * 80 + "\n")

        try:
            # Generate research (force new)
            doc = orchestrator.get_research(
                parameter=parameter,
                country=country,
                period=period,
                use_cache=False
            )

            results[country] = {
                'success': True,
                'doc': doc,
                'version': doc.version,
                'metrics_count': len(doc.content.get('key_metrics', [])),
                'grade': doc.content.get('_validation', {}).get('grade', 'N/A')
            }

            # Show summary
            print(f"✅ {country} - SUCCESS")
            print(f"   Version: {doc.version}")
            print(f"   Metrics: {results[country]['metrics_count']}")
            print(f"   Quality: {results[country]['grade']}")

            # Show key metrics
            metrics = doc.content.get('key_metrics', [])
            if metrics:
                total_gw = 0
                print(f"\n   Key Targets:")
                for metric in metrics[:3]:
                    if isinstance(metric, dict):
                        value = metric.get('value', '0')
                        try:
                            total_gw += float(value)
                        except:
                            pass
                        print(f"      • {metric.get('metric', 'N/A')}: {value} {metric.get('unit', '')}")

                if total_gw > 0:
                    print(f"\n   📊 Total Capacity: {total_gw:.1f} GW")

                    # Determine score based on rubric
                    if total_gw >= 40:
                        score = 10
                        desc = "World-class"
                    elif total_gw >= 35:
                        score = 9
                        desc = "Extremely high"
                    elif total_gw >= 30:
                        score = 8
                        desc = "Very high"
                    elif total_gw >= 25:
                        score = 7
                        desc = "High"
                    elif total_gw >= 20:
                        score = 6
                        desc = "Above moderate"
                    elif total_gw >= 15:
                        score = 5
                        desc = "Moderate"
                    elif total_gw >= 10:
                        score = 4
                        desc = "Below moderate"
                    elif total_gw >= 5:
                        score = 3
                        desc = "Low"
                    elif total_gw >= 3:
                        score = 2
                        desc = "Very low"
                    else:
                        score = 1
                        desc = "Minimal"

                    print(f"   🎯 Ambition Score: {score}/10 ({desc} targets)")

        except Exception as e:
            print(f"❌ {country} - FAILED: {e}")
            results[country] = {
                'success': False,
                'error': str(e)
            }

    # Summary
    print("\n" + "=" * 80)
    print(" BATCH GENERATION COMPLETE")
    print("=" * 80 + "\n")

    successful = [c for c, r in results.items() if r['success']]
    failed = [c for c, r in results.items() if not r['success']]

    print(f"✅ Successful: {len(successful)}/{len(countries)}")
    if successful:
        for country in successful:
            r = results[country]
            print(f"   • {country:15s} v{r['version']} - Grade: {r['grade']}")

    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(countries)}")
        for country in failed:
            print(f"   • {country:15s} - {results[country]['error']}")

    # LLM Statistics
    print("\n" + "-" * 80)
    print(" LLM USAGE STATISTICS")
    print("-" * 80 + "\n")

    stats = orchestrator.research_agent.get_stats()
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Total Tokens: {stats['total_tokens']:,}")
    print(f"  • Prompt Tokens: {stats['prompt_tokens']:,}")
    print(f"  • Completion Tokens: {stats['completion_tokens']:,}")
    print(f"Total Cost: ${stats['total_cost_usd']:.4f}")
    print(f"Avg Cost per Document: ${stats['total_cost_usd']/stats['total_requests']:.4f}")

    # Storage info
    print("\n" + "-" * 80)
    print(" STORAGE INFO")
    print("-" * 80 + "\n")

    all_research = orchestrator.get_available_research()
    print(f"Total Research Documents: {len(all_research)}")
    print(f"\nAmbition Parameter Coverage:")
    ambition_research = orchestrator.search_research(parameter="Ambition")
    for item in ambition_research:
        print(f"   • {item['country']:15s} v{item['version']}")

    print("\n" + "=" * 80)
    print(" TEST COMPLETE")
    print("=" * 80 + "\n")

    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
