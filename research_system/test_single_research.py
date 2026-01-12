#!/usr/bin/env python3
"""Test research generation for Germany - Ambition parameter"""

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
    print(" TESTING RESEARCH GENERATION: Ambition - Germany")
    print("=" * 80 + "\n")

    # Initialize orchestrator
    print("🔧 Initializing Research Orchestrator...")
    orchestrator = ResearchOrchestrator()

    parameter = "Ambition"
    country = "Germany"
    period = "Q4 2024"

    print(f"\n📋 Research Configuration:")
    print(f"   Parameter: {parameter}")
    print(f"   Country: {country}")
    print(f"   Period: {period}")
    print(f"\n⏳ Generating research... (this will take 30-60 seconds)\n")

    try:
        # Generate research (force new, don't use cache)
        doc = orchestrator.get_research(
            parameter=parameter,
            country=country,
            period=period,
            use_cache=False  # Force new research
        )

        print("\n" + "=" * 80)
        print(" RESEARCH GENERATION SUCCESSFUL!")
        print("=" * 80 + "\n")

        # Show metadata
        print(f"📄 Document Version: {doc.version}")
        print(f"📅 Created: {doc.created_at}")
        print(f"📊 Period: {doc.period}")

        content = doc.content

        # Show overview
        if 'overview' in content:
            print("\n" + "-" * 80)
            print("OVERVIEW:")
            print("-" * 80)
            overview = content['overview']
            print(overview[:800])
            if len(overview) > 800:
                print(f"\n... (truncated, full length: {len(overview)} characters)")
            print("-" * 80)

        # Show current status
        if 'current_status' in content:
            print("\nCURRENT STATUS:")
            print("-" * 80)
            status = content['current_status']
            print(status[:600])
            if len(status) > 600:
                print(f"\n... (truncated, full length: {len(status)} characters)")
            print("-" * 80)

        # Show key metrics
        if 'key_metrics' in content and content['key_metrics']:
            print("\nKEY METRICS:")
            print("-" * 80)
            metrics = content['key_metrics']
            if isinstance(metrics, list):
                for i, metric in enumerate(metrics[:10], 1):
                    if isinstance(metric, dict):
                        print(f"{i:2d}. {metric.get('metric', 'N/A')}")
                        print(f"    Value: {metric.get('value', 'N/A')} {metric.get('unit', '')}")
                        print(f"    Source: {metric.get('source', 'N/A')}")
                        print()
                if len(metrics) > 10:
                    print(f"... and {len(metrics) - 10} more metrics")
            print("-" * 80)

        # Show sources
        if 'sources' in content and content['sources']:
            print("\nSOURCES:")
            print("-" * 80)
            sources = content['sources']
            if isinstance(sources, list):
                for i, source in enumerate(sources[:5], 1):
                    if isinstance(source, dict):
                        print(f"{i}. {source.get('name', 'N/A')}")
                        if source.get('url'):
                            print(f"   {source['url']}")
                if len(sources) > 5:
                    print(f"... and {len(sources) - 5} more sources")
            print("-" * 80)

        # Show quality validation
        if '_validation' in content:
            validation = content['_validation']
            print("\nQUALITY ASSESSMENT:")
            print("-" * 80)
            print(f"Grade: {validation['grade']}")
            print(f"Overall Score: {validation['scores']['overall']:.2f}")
            print(f"  • Completeness: {validation['scores']['completeness']:.2f}")
            print(f"  • Data Quality: {validation['scores']['data_quality']:.2f}")
            print(f"  • Source Quality: {validation['scores']['source_quality']:.2f}")

            if validation.get('issues'):
                print(f"\nIssues Found:")
                for issue in validation['issues']:
                    print(f"  ⚠️  {issue}")
            else:
                print("\n✅ No quality issues found")
            print("-" * 80)

        # Show metadata
        if '_metadata' in content:
            metadata = content['_metadata']
            print("\nGENERATION METADATA:")
            print("-" * 80)
            print(f"Model: {metadata.get('llm_model', 'N/A')}")
            print(f"Execution Time: {metadata.get('execution_time_seconds', 0):.1f}s")
            print(f"Prompt Length: {metadata.get('prompt_length', 0):,} chars")
            print(f"Response Length: {metadata.get('response_length', 0):,} chars")
            print("-" * 80)

        # Show storage location
        version_path = orchestrator.research_store.version_manager.get_version_path(
            parameter, country, doc.version
        )
        print(f"\n💾 Stored at: {version_path}")

        # Test cached retrieval
        print("\n" + "=" * 80)
        print(" TESTING CACHED RETRIEVAL")
        print("=" * 80 + "\n")

        print("🔍 Retrieving from cache...")
        cached_doc = orchestrator.get_research(
            parameter=parameter,
            country=country,
            use_cache=True
        )

        print(f"✅ Retrieved cached version: {cached_doc.version}")
        print(f"   Cache is valid: {orchestrator.research_store.is_cache_valid(parameter, country)}")

        # Show agent statistics
        print("\n" + "=" * 80)
        print(" LLM USAGE STATISTICS")
        print("=" * 80 + "\n")

        stats = orchestrator.research_agent.get_stats()
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"  • Prompt Tokens: {stats['prompt_tokens']:,}")
        print(f"  • Completion Tokens: {stats['completion_tokens']:,}")
        print(f"Total Cost: ${stats['total_cost_usd']:.4f}")
        print(f"Average Latency: {stats['average_latency_ms']:.0f}ms")

        print("\n" + "=" * 80)
        print(" TEST COMPLETE - SUCCESS ✅")
        print("=" * 80 + "\n")
        return 0

    except Exception as e:
        print("\n" + "=" * 80)
        print(" TEST FAILED ❌")
        print("=" * 80 + "\n")
        print(f"Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
