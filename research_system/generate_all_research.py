#!/usr/bin/env python3
"""Generate research documents for all parameters across multiple countries

This script generates a comprehensive research library by creating research documents
for every parameter-country combination. This provides a complete data foundation
for the agent system.

Cost Estimation:
- Per document: ~$0.04 (varies by parameter complexity)
- 18 parameters × 10 countries = 180 documents
- Estimated total cost: ~$7.20

Time Estimation:
- Per document: ~45 seconds
- Total time: ~2.25 hours (with parallel processing: ~45 minutes)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import time
import yaml
from typing import List, Dict, Any

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


# Configuration
DEFAULT_COUNTRIES = [
    "Brazil",
    "Germany",
    "United States",
    "China",
    "India",
    "United Kingdom",
    "Spain",
    "Australia",
    "Chile",
    "Vietnam"
]

DEFAULT_PERIOD = "Q4 2024"


def load_all_parameters() -> List[Dict[str, str]]:
    """Load all parameters from parameters.yaml.

    Returns:
        List of parameter dicts with name, key, and subcategory
    """
    config_path = project_root / "config" / "parameters.yaml"

    with open(config_path) as f:
        data = yaml.safe_load(f)

    parameters = []
    params_dict = data.get('parameters', {})

    for param_key, param_data in params_dict.items():
        if isinstance(param_data, dict):
            param_name = param_data.get('name', param_key.title().replace('_', ' '))
            parameters.append({
                'name': param_name,
                'key': param_key,
                'subcategory': param_data.get('subcategory', 'unknown')
            })

    return parameters


def print_header():
    """Print script header."""
    print("\n" + "=" * 80)
    print(" BATCH RESEARCH GENERATION: ALL PARAMETERS")
    print("=" * 80)
    print("\n📚 This script generates research documents for all parameters")
    print("   across multiple countries to create a comprehensive research library.\n")


def print_configuration(parameters: List[Dict], countries: List[str], period: str):
    """Print batch configuration."""
    print("=" * 80)
    print(" CONFIGURATION")
    print("=" * 80)
    print(f"\n📋 Parameters: {len(parameters)}")

    # Group by subcategory
    by_subcat = {}
    for p in parameters:
        subcat = p['subcategory']
        if subcat not in by_subcat:
            by_subcat[subcat] = []
        by_subcat[subcat].append(p['name'])

    for subcat, params in sorted(by_subcat.items()):
        print(f"   • {subcat}: {len(params)} parameters")
        for pname in params:
            print(f"      - {pname}")

    print(f"\n🌍 Countries: {len(countries)}")
    for i, country in enumerate(countries, 1):
        print(f"   {i:2d}. {country}")

    print(f"\n📅 Period: {period}")
    print(f"\n📊 Total Documents to Generate: {len(parameters)} × {len(countries)} = {len(parameters) * len(countries)}")

    # Cost estimation
    avg_cost_per_doc = 0.04
    total_cost = len(parameters) * len(countries) * avg_cost_per_doc
    print(f"\n💰 Estimated Cost: ${total_cost:.2f}")
    print(f"   (Average ${avg_cost_per_doc} per document)")

    # Time estimation
    avg_time_per_doc = 45  # seconds
    total_time_mins = (len(parameters) * len(countries) * avg_time_per_doc) / 60
    print(f"\n⏱️  Estimated Time: {total_time_mins:.1f} minutes ({total_time_mins/60:.1f} hours)")
    print(f"   (Average {avg_time_per_doc}s per document)\n")


def generate_batch(
    orchestrator: ResearchOrchestrator,
    parameters: List[Dict],
    countries: List[str],
    period: str,
    use_cache: bool = False,
    skip_existing: bool = True
) -> Dict[str, Any]:
    """Generate research for all parameter-country combinations.

    Args:
        orchestrator: Research orchestrator
        parameters: List of parameters to generate research for
        countries: List of countries
        period: Time period
        use_cache: Whether to use cached research (False = force new)
        skip_existing: Skip if research already exists

    Returns:
        Dictionary with results and statistics
    """
    total_count = len(parameters) * len(countries)
    results = {
        'successful': [],
        'failed': [],
        'skipped': [],
        'start_time': datetime.now(),
        'total_cost': 0.0,
        'total_tokens': 0
    }

    print("=" * 80)
    print(" BATCH GENERATION STARTED")
    print("=" * 80 + "\n")

    current = 0

    for param in parameters:
        param_name = param['name']
        param_key = param['key']
        subcat = param['subcategory']

        print(f"\n{'─' * 80}")
        print(f" 📌 PARAMETER: {param_name} ({subcat})")
        print(f"{'─' * 80}\n")

        for country in countries:
            current += 1

            print(f"[{current}/{total_count}] {country:20s} ", end="", flush=True)

            try:
                # Check if exists and skip_existing is True
                if skip_existing:
                    existing = orchestrator.research_store.load(param_name, country)
                    if existing and orchestrator.research_store.is_cache_valid(param_name, country):
                        print("⏭️  SKIPPED (exists)")
                        results['skipped'].append({
                            'parameter': param_name,
                            'country': country,
                            'version': existing.version
                        })
                        continue

                # Generate research
                start_time = time.time()
                doc = orchestrator.get_research(
                    parameter=param_name,
                    country=country,
                    period=period,
                    use_cache=use_cache
                )
                elapsed = time.time() - start_time

                # Get quality grade
                grade = doc.content.get('_validation', {}).get('grade', 'N/A')

                # Extract cost from metadata
                metadata = doc.content.get('_metadata', {})
                cost = metadata.get('cost_usd', 0.0)
                tokens = metadata.get('total_tokens', 0)

                results['total_cost'] += cost
                results['total_tokens'] += tokens

                print(f"✅ SUCCESS (v{doc.version}, Grade: {grade}, {elapsed:.1f}s, ${cost:.4f})")

                results['successful'].append({
                    'parameter': param_name,
                    'country': country,
                    'version': doc.version,
                    'grade': grade,
                    'elapsed': elapsed,
                    'cost': cost,
                    'tokens': tokens
                })

                # Small delay to avoid rate limits
                time.sleep(0.5)

            except Exception as e:
                print(f"❌ FAILED: {str(e)[:60]}")
                results['failed'].append({
                    'parameter': param_name,
                    'country': country,
                    'error': str(e)
                })

    results['end_time'] = datetime.now()
    results['duration'] = results['end_time'] - results['start_time']

    return results


def print_summary(results: Dict[str, Any]):
    """Print batch generation summary."""
    print("\n" + "=" * 80)
    print(" BATCH GENERATION COMPLETE")
    print("=" * 80 + "\n")

    successful = len(results['successful'])
    failed = len(results['failed'])
    skipped = len(results['skipped'])
    total = successful + failed + skipped

    print(f"📊 Results:")
    print(f"   ✅ Successful: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"   ❌ Failed:     {failed}/{total} ({failed/total*100:.1f}%)")
    print(f"   ⏭️  Skipped:    {skipped}/{total} ({skipped/total*100:.1f}%)")

    print(f"\n⏱️  Duration: {results['duration']}")

    if successful > 0:
        avg_time = sum(r['elapsed'] for r in results['successful']) / successful
        print(f"   Average time per document: {avg_time:.1f}s")

    print(f"\n💰 Cost:")
    print(f"   Total: ${results['total_cost']:.2f}")
    if successful > 0:
        print(f"   Average per document: ${results['total_cost']/successful:.4f}")

    print(f"\n🔢 Tokens:")
    print(f"   Total: {results['total_tokens']:,}")
    if successful > 0:
        print(f"   Average per document: {results['total_tokens']//successful:,}")

    # Quality grades distribution
    if successful > 0:
        print(f"\n📈 Quality Distribution:")
        grades = {}
        for r in results['successful']:
            grade = r['grade']
            grades[grade] = grades.get(grade, 0) + 1

        for grade in sorted(grades.keys()):
            count = grades[grade]
            print(f"   Grade {grade}: {count:3d} documents ({count/successful*100:.1f}%)")

    # Top 5 by parameter
    if successful > 0:
        print(f"\n📌 Top Parameters by Document Count:")
        param_counts = {}
        for r in results['successful']:
            param = r['parameter']
            param_counts[param] = param_counts.get(param, 0) + 1

        for param, count in sorted(param_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {param:30s} {count:2d} documents")

    # Failed items
    if failed > 0:
        print(f"\n❌ Failed Items:")
        for r in results['failed']:
            print(f"   • {r['parameter']:30s} - {r['country']:20s}")
            print(f"     Error: {r['error'][:60]}")

    print("\n" + "=" * 80)
    print(" Summary saved to: research_system/data/batch_generation_summary.txt")
    print("=" * 80 + "\n")


def save_summary_report(results: Dict[str, Any], parameters: List[Dict], countries: List[str]):
    """Save detailed summary report to file."""
    report_path = project_root / "research_system" / "data" / "batch_generation_summary.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write(" BATCH RESEARCH GENERATION SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {results['duration']}\n\n")

        f.write(f"Configuration:\n")
        f.write(f"  Parameters: {len(parameters)}\n")
        f.write(f"  Countries: {len(countries)}\n")
        f.write(f"  Total combinations: {len(parameters) * len(countries)}\n\n")

        successful = len(results['successful'])
        failed = len(results['failed'])
        skipped = len(results['skipped'])
        total = successful + failed + skipped

        f.write(f"Results:\n")
        f.write(f"  Successful: {successful}/{total} ({successful/total*100:.1f}%)\n")
        f.write(f"  Failed: {failed}/{total}\n")
        f.write(f"  Skipped: {skipped}/{total}\n\n")

        f.write(f"Cost: ${results['total_cost']:.2f}\n")
        f.write(f"Tokens: {results['total_tokens']:,}\n\n")

        f.write("Successful Documents:\n")
        f.write("-" * 80 + "\n")
        for r in results['successful']:
            f.write(f"{r['parameter']:30s} | {r['country']:20s} | v{r['version']} | Grade: {r['grade']} | ${r['cost']:.4f}\n")

        if failed > 0:
            f.write("\n\nFailed Documents:\n")
            f.write("-" * 80 + "\n")
            for r in results['failed']:
                f.write(f"{r['parameter']:30s} | {r['country']:20s} | Error: {r['error']}\n")

    print(f"✅ Detailed report saved to: {report_path}")


def main():
    """Main execution."""
    print_header()

    # Load configuration
    parameters = load_all_parameters()
    countries = DEFAULT_COUNTRIES
    period = DEFAULT_PERIOD

    print_configuration(parameters, countries, period)

    # Confirm before proceeding
    print("=" * 80)
    response = input("\n⚠️  This will generate research and incur API costs. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Batch generation cancelled by user.\n")
        return 1

    # Initialize orchestrator
    print("\n🔧 Initializing Research Orchestrator...")
    try:
        orchestrator = ResearchOrchestrator()
        print("✅ Orchestrator initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return 1

    # Generate batch
    try:
        results = generate_batch(
            orchestrator=orchestrator,
            parameters=parameters,
            countries=countries,
            period=period,
            use_cache=False,  # Force new generation
            skip_existing=True  # Skip if valid cache exists
        )

        # Print summary
        print_summary(results)

        # Save detailed report
        save_summary_report(results, parameters, countries)

        # Show LLM statistics
        print("\n" + "=" * 80)
        print(" LLM USAGE STATISTICS")
        print("=" * 80 + "\n")

        stats = orchestrator.research_agent.get_stats()
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"  • Prompt Tokens: {stats['prompt_tokens']:,}")
        print(f"  • Completion Tokens: {stats['completion_tokens']:,}")
        print(f"Total Cost: ${stats['total_cost_usd']:.2f}")
        if stats['total_requests'] > 0:
            print(f"Average Cost per Request: ${stats['total_cost_usd']/stats['total_requests']:.4f}")
            print(f"Average Latency: {stats['average_latency_ms']:.0f}ms")

        print("\n" + "=" * 80)
        print(" BATCH GENERATION COMPLETE ✅")
        print("=" * 80 + "\n")

        return 0 if len(results['failed']) == 0 else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Batch generation interrupted by user.")
        print("   Partial results may be saved.\n")
        return 1

    except Exception as e:
        print(f"\n\n❌ Batch generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
