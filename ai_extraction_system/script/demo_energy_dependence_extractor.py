"""Demo and Test Suite for EnergyDependenceExtractor

This file demonstrates and tests the EnergyDependenceExtractor functionality.

Run modes:
    1. Mock mode (no API keys needed) - Tests basic functionality
    2. Real mode (requires API keys) - Tests with actual LLM

Usage:
    # Mock mode (default)
    python demo_energy_dependence_extractor.py

    # Real mode with API key
    python demo_energy_dependence_extractor.py --real --api-key YOUR_API_KEY

    # Or set environment variable
    export OPENAI_API_KEY=your_key
    python demo_energy_dependence_extractor.py --real
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path to import local ai_extraction_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_extraction_system import EnergyDependenceExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MOCK IMPLEMENTATIONS (for testing without API keys)
# ============================================================================

class MockLLMService:
    """Mock LLM service for testing without API calls."""

    def __init__(self, *args, **kwargs):
        self.model_name = kwargs.get('model_name', 'mock-model')
        logger.info("Initialized MockLLMService")

    def invoke(self, prompt: str) -> str:
        """Return mock LLM response based on prompt content."""
        logger.info(f"MockLLM invoked with prompt length: {len(prompt)}")

        # Detect country from prompt
        if 'Germany' in prompt:
            return self._germany_response()
        elif 'Brazil' in prompt:
            return self._brazil_response()
        else:
            return self._generic_response()

    def _germany_response(self) -> str:
        """Mock response for Germany."""
        return """```json
{
    "value": 65,
    "confidence": 0.90,
    "justification": "Germany has high energy import dependency at approximately 65% of total energy consumption. The country relies heavily on imports of natural gas (primarily from Russia, Norway), oil, and coal. Fossil fuels account for about 70% of energy consumption. However, Germany has strong energy security policies through EU integration, strategic reserves, and aggressive renewable energy targets under the Energiewende program. The diversification level is moderate with multiple import sources and growing renewable capacity.",
    "quotes": [
        "Energy import dependency: 65% of total consumption",
        "Primary import sources: Russia (gas), Norway (gas/oil), Netherlands (gas)",
        "Fossil fuel share: ~70% of energy mix",
        "Strong push for renewable energy independence through Energiewende",
        "Strategic gas reserves and LNG terminals under development"
    ],
    "metadata": {
        "fossil_fuel_share": 70.0,
        "primary_import_sources": ["Russia", "Norway", "Netherlands"],
        "energy_security_risk": "moderate",
        "diversification_level": "moderate",
        "renewable_share": 19.0,
        "data_year": "2023"
    }
}
```"""

    def _brazil_response(self) -> str:
        """Mock response for Brazil."""
        return """```json
{
    "value": 15,
    "confidence": 0.88,
    "justification": "Brazil has low energy import dependency at approximately 15% of total energy consumption, making it relatively energy independent. The country benefits from substantial domestic oil production (pre-salt reserves), extensive hydropower resources (60% of electricity), and significant biofuel production (ethanol from sugarcane). Fossil fuels account for about 55% of total energy consumption. Brazil's energy security is strong due to diversified domestic resources and minimal reliance on foreign energy imports.",
    "quotes": [
        "Energy import dependency: ~15% of total consumption",
        "Large domestic oil production from pre-salt reserves",
        "Hydropower provides 60% of electricity generation",
        "World leader in biofuels (ethanol)",
        "Energy security rated as strong due to domestic resources"
    ],
    "metadata": {
        "fossil_fuel_share": 55.0,
        "primary_import_sources": ["Argentina", "Bolivia"],
        "energy_security_risk": "low",
        "diversification_level": "high",
        "renewable_share": 45.0,
        "data_year": "2023"
    }
}
```"""

    def _generic_response(self) -> str:
        """Generic mock response."""
        return """```json
{
    "value": 40,
    "confidence": 0.75,
    "justification": "The country has moderate energy import dependency at approximately 40% of total energy consumption. Energy security policies are in place with some diversification of import sources. Fossil fuels dominate the energy mix with ongoing efforts to increase renewable energy capacity.",
    "quotes": [
        "Energy import dependency: ~40%",
        "Moderate fossil fuel reliance",
        "Developing renewable energy capacity"
    ],
    "metadata": {
        "fossil_fuel_share": 65.0,
        "primary_import_sources": ["Various"],
        "energy_security_risk": "moderate",
        "diversification_level": "moderate",
        "renewable_share": 20.0,
        "data_year": "2023"
    }
}
```"""


class MockExtractionCache:
    """Mock cache for testing."""

    def __init__(self, *args, **kwargs):
        self.cache = {}
        logger.info("Initialized MockExtractionCache")

    def get(self, key: str) -> Any:
        return self.cache.get(key)

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache, ignoring ttl in mock mode."""
        self.cache[key] = value


# ============================================================================
# SAMPLE DOCUMENTS (for testing)
# ============================================================================

SAMPLE_DOCS_GERMANY = [
    {
        'content': """
        Germany Energy Security Assessment 2023

        Import Dependency:
        Germany imports approximately 65% of its total energy consumption.
        Primary import sources:
        - Natural Gas: Russia (40%), Norway (30%), Netherlands (20%)
        - Oil: Russia, Norway, UK
        - Coal: Russia, USA, Australia

        Energy Mix:
        - Fossil Fuels: ~70% (declining)
        - Nuclear: Phasing out (completed 2023)
        - Renewables: 19% and growing rapidly
        - Hydropower: 3%

        Energy Security Strategy:
        Following the Ukraine crisis, Germany has accelerated:
        1. LNG terminal construction (5 terminals planned)
        2. Renewable energy expansion under Energiewende
        3. Gas pipeline diversification
        4. Strategic gas storage (90% target)
        5. Energy efficiency programs

        Assessment: High import dependency but strong mitigation strategies
        """,
        'metadata': {
            'source': 'German Federal Ministry for Economic Affairs and Energy',
            'date': '2023',
            'type': 'energy_security'
        }
    }
]

SAMPLE_DOCS_BRAZIL = [
    {
        'content': """
        Brazil Energy Independence Report 2023

        Import Dependency:
        Brazil has low energy import dependency at approximately 15% of
        total energy consumption, making it one of the most energy-independent
        large economies.

        Domestic Energy Resources:
        - Pre-Salt Oil Production: 2.8 million barrels/day (world's 8th largest producer)
        - Hydropower: 60% of electricity generation
        - Biofuels: World's 2nd largest ethanol producer
        - Natural Gas: Increasing domestic production

        Energy Mix:
        - Fossil Fuels: 55% (oil, gas, coal)
        - Hydropower: 30%
        - Biofuels: 15%
        - Other Renewables: Growing (wind, solar)

        Energy Security:
        Brazil's energy security is rated as STRONG:
        - Minimal reliance on energy imports
        - Diversified domestic resources
        - Large renewable energy base
        - Strategic position in South American energy market

        Limited imports mainly consist of:
        - Natural Gas from Bolivia and Argentina
        - Some refined petroleum products

        Assessment: Very low import dependency, strong energy independence
        """,
        'metadata': {
            'source': 'Brazilian Ministry of Mines and Energy',
            'date': '2023',
            'type': 'energy_independence'
        }
    }
]


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def run_extractor_demo(use_real_llm: bool = False, api_key: str = None):
    """Run demonstration of EnergyDependenceExtractor."""

    print("=" * 80)
    print("ENERGY DEPENDENCE EXTRACTOR DEMO")
    print("=" * 80)
    print()

    # Initialize LLM service
    if use_real_llm:
        print("🔄 Using REAL LLM service (will make API calls)")
        try:
            from ai_extraction_system.llm_service import LLMService
            llm_service = LLMService(api_key=api_key)
        except Exception as e:
            print(f"❌ Failed to initialize real LLM service: {e}")
            print("   Falling back to mock mode")
            llm_service = MockLLMService()
    else:
        print("🎭 Using MOCK LLM service (no API calls)")
        llm_service = MockLLMService()

    # Initialize cache
    cache = MockExtractionCache()

    # Initialize extractor
    print("\n" + "=" * 80)
    print("Initializing EnergyDependenceExtractor...")
    print("=" * 80)

    extractor = EnergyDependenceExtractor(
        parameter_name="energy_dependence",
        llm_service=llm_service,
        cache=cache
    )

    print(f"✅ Extractor initialized")
    print(f"   Parameter: {extractor.parameter_name}")

    # Test cases
    test_cases = [
        {
            'country': 'Germany',
            'documents': SAMPLE_DOCS_GERMANY,
            'description': 'High import dependency (65%)'
        },
        {
            'country': 'Brazil',
            'documents': SAMPLE_DOCS_BRAZIL,
            'description': 'Low import dependency (15%)'
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print("\n" + "=" * 80)
        print(f"TEST CASE {i}: {test_case['country']}")
        print(f"Expected: {test_case['description']}")
        print("=" * 80)

        try:
            # Extract data
            print(f"\n🔍 Extracting energy dependence data for {test_case['country']}...")
            result = extractor.extract(
                country=test_case['country'],
                documents=test_case['documents']
            )

            # Display results
            print(f"\n{'=' * 80}")
            print(f"EXTRACTION RESULTS - {test_case['country']}")
            print(f"{'=' * 80}")

            if result.success:
                print(f"✅ Status: SUCCESS")
                print(f"\n📊 Import Dependency: {result.data.value}%")
                print(f"🎯 Confidence: {result.data.confidence:.1%}")
                print(f"\n💡 Justification:")
                print(f"   {result.data.justification[:250]}...")

                if hasattr(result.data, 'metadata') and result.data.metadata:
                    print(f"\n📋 Metadata:")
                    for key, value in result.data.metadata.items():
                        if key != 'country':
                            print(f"   • {key}: {value}")

                results.append({
                    'country': test_case['country'],
                    'success': True,
                    'dependency': result.data.value,
                    'confidence': result.data.confidence
                })
            else:
                print(f"❌ Status: FAILED")
                print(f"   Error: {result.error}")
                results.append({
                    'country': test_case['country'],
                    'success': False,
                    'error': result.error
                })

        except Exception as e:
            print(f"\n❌ Exception during extraction: {e}")
            logger.exception("Extraction failed")
            results.append({
                'country': test_case['country'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print("\n" + "=" * 80)
    print("DEMO SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r.get('success'))
    print(f"\n✅ Successful extractions: {successful}/{len(results)}")

    if successful > 0:
        print(f"\n📊 Extracted Dependencies:")
        for r in results:
            if r.get('success'):
                print(f"   • {r['country']}: {r['dependency']}% (confidence: {r['confidence']:.1%})")

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)

    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Demo EnergyDependenceExtractor'
    )
    parser.add_argument(
        '--real',
        action='store_true',
        help='Use real LLM instead of mock'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='API key for LLM service'
    )

    args = parser.parse_args()

    # Get API key from args or environment
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')

    if args.real and not api_key:
        print("⚠️  Warning: --real specified but no API key provided")
        print("   Set OPENAI_API_KEY environment variable or use --api-key")
        print("   Falling back to mock mode\n")
        args.real = False

    # Run demo
    try:
        results = run_extractor_demo(
            use_real_llm=args.real,
            api_key=api_key
        )

        # Exit with appropriate code
        all_success = all(r.get('success') for r in results)
        sys.exit(0 if all_success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        logger.exception("Demo failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
