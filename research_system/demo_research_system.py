#!/usr/bin/env python3
"""Demo Script for Research System

Demonstrates the complete research system functionality:
1. Generate prompts for all parameters
2. Conduct research for specific parameter-country combinations
3. Store and version research documents
4. Retrieve cached research
5. View statistics and history
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
os.environ['LOG_LEVEL'] = 'INFO'

from research_system import ResearchOrchestrator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def demo_prompt_generation():
    """Demo 1: Generate parameter-specific prompts."""
    print_section("DEMO 1: Parameter Prompt Generation")

    orchestrator = ResearchOrchestrator()

    print("📝 Generating prompts for all parameters from parameters.yaml...\n")

    prompts = orchestrator.generate_all_prompts()

    print(f"✅ Generated {len(prompts)} parameter-specific prompts\n")

    # Show a sample prompt
    if prompts:
        sample_param = list(prompts.keys())[0]
        print(f"Sample prompt for '{sample_param}':")
        print("-" * 80)
        sample_prompt = prompts[sample_param]
        # Show first 500 characters
        print(sample_prompt[:500])
        print(f"\n... (truncated, full length: {len(sample_prompt)} chars)")
        print("-" * 80)

    print(f"\n💾 Prompts saved to: research_system/prompts/generated/\n")


def demo_single_research():
    """Demo 2: Conduct research for a single parameter-country combination."""
    print_section("DEMO 2: Single Parameter Research")

    orchestrator = ResearchOrchestrator()

    parameter = "Ambition"
    country = "Germany"
    period = "Q4 2024"

    print(f"🔬 Conducting research for:")
    print(f"   Parameter: {parameter}")
    print(f"   Country: {country}")
    print(f"   Period: {period}\n")

    print("⏳ This will take 30-60 seconds (LLM generation)...\n")

    try:
        # Generate research
        doc = orchestrator.get_research(
            parameter=parameter,
            country=country,
            period=period,
            use_cache=False  # Force new research for demo
        )

        print("✅ Research completed!\n")

        # Display results
        content = doc.content

        print(f"📄 Research Document v{doc.version}")
        print(f"   Created: {doc.created_at}")
        print(f"   Research Date: {content.get('research_date', 'N/A')}\n")

        # Show overview
        if 'overview' in content:
            print("OVERVIEW:")
            print("-" * 80)
            overview = content['overview']
            # Show first 400 chars
            print(overview[:400])
            if len(overview) > 400:
                print(f"\n... (truncated, full length: {len(overview)} chars)")
            print("-" * 80)

        # Show key metrics
        if 'key_metrics' in content and content['key_metrics']:
            print("\nKEY METRICS:")
            metrics = content['key_metrics']
            if isinstance(metrics, list):
                for i, metric in enumerate(metrics[:5], 1):
                    if isinstance(metric, dict):
                        print(f"   {i}. {metric.get('metric', 'N/A')}: "
                              f"{metric.get('value', 'N/A')} {metric.get('unit', '')}")
                if len(metrics) > 5:
                    print(f"   ... and {len(metrics) - 5} more")

        # Show quality validation
        if '_validation' in content:
            validation = content['_validation']
            print(f"\nQUALITY SCORE: {validation['grade']} "
                  f"(Overall: {validation['scores']['overall']:.2f})")
            print(f"   Completeness: {validation['scores']['completeness']:.2f}")
            print(f"   Data Quality: {validation['scores']['data_quality']:.2f}")
            print(f"   Source Quality: {validation['scores']['source_quality']:.2f}")

        # Show where it's stored
        print(f"\n💾 Stored at:")
        print(f"   {orchestrator.research_store.get_version_path(parameter, country, doc.version)}")

    except Exception as e:
        print(f"❌ Research failed: {e}")
        import traceback
        traceback.print_exc()


def demo_cached_retrieval():
    """Demo 3: Retrieve cached research."""
    print_section("DEMO 3: Cached Research Retrieval")

    orchestrator = ResearchOrchestrator()

    parameter = "Ambition"
    country = "Germany"

    print(f"📂 Retrieving cached research for {parameter}/{country}...\n")

    # Check if research exists
    if orchestrator.research_store.exists(parameter, country):
        doc = orchestrator.get_research(
            parameter=parameter,
            country=country,
            use_cache=True  # Use cache
        )

        print(f"✅ Retrieved cached research v{doc.version}")
        print(f"   Created: {doc.created_at}")

        # Check if cache is valid
        is_valid = orchestrator.research_store.is_cache_valid(parameter, country)
        print(f"   Cache Valid: {'Yes ✓' if is_valid else 'No (expired)'}")

        # Show version history
        history = orchestrator.get_version_history(parameter, country)
        print(f"\n📜 Version History ({len(history)} versions):")
        for h in history[:5]:
            print(f"   • v{h['version']}: {h['created_at']} - {h.get('change_description', 'N/A')}")

    else:
        print(f"⚠️  No cached research found for {parameter}/{country}")
        print("   Run Demo 2 first to generate research.")


def demo_batch_research():
    """Demo 4: Batch research generation."""
    print_section("DEMO 4: Batch Research Generation")

    orchestrator = ResearchOrchestrator()

    parameters = ["Ambition", "Country Stability"]
    countries = ["Brazil", "India"]

    print(f"🔬 Generating research for:")
    print(f"   Parameters: {', '.join(parameters)}")
    print(f"   Countries: {', '.join(countries)}")
    print(f"   Total: {len(parameters)} × {len(countries)} = {len(parameters) * len(countries)} documents\n")

    print("⚠️  WARNING: This will make multiple LLM calls and may take several minutes!")
    print("   For demo purposes, we'll just show the setup.\n")

    # Uncomment to actually run batch generation:
    # print("⏳ Starting batch generation...\n")
    # results = orchestrator.batch_generate_research(
    #     parameters=parameters,
    #     countries=countries,
    #     use_cache=True  # Use cache if available
    # )
    #
    # print(f"\n✅ Batch complete: {len(results)} documents generated/retrieved")

    print("💡 To run batch generation, uncomment the code in this function.")


def demo_statistics():
    """Demo 5: View system statistics."""
    print_section("DEMO 5: System Statistics")

    orchestrator = ResearchOrchestrator()

    print("📊 Fetching system statistics...\n")

    stats = orchestrator.get_statistics()

    # Storage statistics
    storage = stats['storage']
    print("STORAGE:")
    print(f"   Total Documents: {storage['total_documents']}")
    print(f"   Unique Parameters: {storage['unique_parameters']}")
    print(f"   Unique Countries: {storage['unique_countries']}")
    print(f"   Total Size: {storage['total_size_mb']} MB")

    if storage['parameters']:
        print("\n   Documents by Parameter:")
        for param, count in sorted(storage['parameters'].items(), key=lambda x: x[1], reverse=True):
            print(f"      • {param}: {count}")

    if storage['countries']:
        print("\n   Documents by Country:")
        for country, count in sorted(storage['countries'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      • {country}: {count}")

    # Agent statistics
    agent = stats['agent']
    print(f"\nAGENT (LLM Usage):")
    print(f"   Total Requests: {agent['total_requests']}")
    print(f"   Successful: {agent['successful_requests']}")
    print(f"   Failed: {agent['failed_requests']}")
    print(f"   Total Tokens: {agent['total_tokens']:,}")
    print(f"   Total Cost: ${agent['total_cost_usd']:.4f}")
    print(f"   Avg Latency: {agent['average_latency_ms']:.0f}ms")

    # Cache info
    cache = stats['cache']
    print(f"\nCACHE:")
    print(f"   Enabled: {cache['enabled']}")
    print(f"   TTL: {cache['ttl_seconds']} seconds ({cache['ttl_seconds'] / 86400:.1f} days)")


def demo_search():
    """Demo 6: Search research documents."""
    print_section("DEMO 6: Search Research Documents")

    orchestrator = ResearchOrchestrator()

    print("🔍 Searching available research...\n")

    # Get all research
    all_research = orchestrator.get_available_research()

    if all_research:
        print(f"Found {len(all_research)} research documents:\n")

        for i, item in enumerate(all_research[:10], 1):
            print(f"{i:2d}. {item['parameter']:20s} | {item['country']:20s} | v{item['version']}")

        if len(all_research) > 10:
            print(f"    ... and {len(all_research) - 10} more")

        # Search by parameter
        print("\n🔍 Searching for 'Ambition' parameter:")
        ambition_research = orchestrator.search_research(parameter="Ambition")
        print(f"   Found {len(ambition_research)} countries with Ambition research")
        for item in ambition_research[:5]:
            print(f"      • {item['country']}")

    else:
        print("⚠️  No research documents found yet.")
        print("   Run Demo 2 or Demo 4 to generate research first.")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print(" RESEARCH SYSTEM DEMONSTRATION")
    print("=" * 80)
    print(f"\n📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project: {project_root}\n")

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  WARNING: No API key found in environment!")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        print("   Research generation will fail without API key.\n")
    else:
        print("✅ API key found in environment\n")

    # Run demos
    try:
        demo_prompt_generation()

        # Uncomment to run full research demos (requires API key and time):
        # demo_single_research()
        # demo_cached_retrieval()
        # demo_batch_research()

        demo_statistics()
        demo_search()

        print_section("DEMO COMPLETE")

        print("✅ All demos completed successfully!\n")

        print("NEXT STEPS:")
        print("1. Uncomment demo_single_research() to generate actual research")
        print("2. Try batch generation with demo_batch_research()")
        print("3. Integrate research system with your agents\n")

        print("INTEGRATION EXAMPLE:")
        print("-" * 80)
        print("""
from research_system import ResearchOrchestrator

# In your agent
orchestrator = ResearchOrchestrator()

# Get research for analysis
research = orchestrator.get_research("Ambition", "Germany")
print(research.content['overview'])
print(research.content['key_metrics'])
        """)
        print("-" * 80)

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
