"""Demo and Test Suite for CountryStabilityExtractor

This file demonstrates and tests the CountryStabilityExtractor functionality.

Run modes:
    1. Mock mode (no API keys needed) - Tests basic functionality
    2. Real mode (requires API keys) - Tests with actual LLM

Usage:
    # Mock mode (default)
    python demo_country_stability_extractor.py

    # Real mode with API key
    python demo_country_stability_extractor.py --real --api-key YOUR_API_KEY

    # Or set environment variable
    export OPENAI_API_KEY=your_key
    python demo_country_stability_extractor.py --real
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path to import local ai_extraction_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_extraction_system import CountryStabilityExtractor

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
    "value": 9,
    "confidence": 0.95,
    "justification": "Germany demonstrates very high political and economic stability. As a core EU member with strong democratic institutions, Germany has exceptional political stability with peaceful transitions of power and consistent policy frameworks. Economic stability is very high with low inflation, strong fiscal discipline, and a robust economy. Institutional quality is excellent with transparent governance, low corruption (Transparency International CPI: 80/100), and strong rule of law. Policy continuity is very strong - renewable energy policies have remained stable across multiple governments.",
    "quotes": [
        "Stable democracy with strong institutions",
        "Low corruption index (80/100)",
        "Energiewende policy has cross-party support",
        "EU membership provides additional stability framework"
    ],
    "metadata": {
        "political_stability": "high",
        "economic_stability": "high",
        "policy_continuity": "high",
        "corruption_level": "low",
        "institutional_quality": "strong",
        "data_year": "2023"
    }
}
```"""

    def _brazil_response(self) -> str:
        """Mock response for Brazil."""
        return """```json
{
    "value": 6,
    "confidence": 0.85,
    "justification": "Brazil shows moderate political and economic stability with some volatility. Political stability is moderate - democratic institutions function but face periodic pressures. Economic stability is moderate with inflation challenges and fiscal concerns, though improving. Institutional quality is moderate with ongoing corruption challenges (Transparency International CPI: 38/100). However, renewable energy policy has shown remarkable continuity across different administrations.",
    "quotes": [
        "Democratic institutions functioning",
        "Renewable auction system stable across governments",
        "Moderate corruption challenges (CPI: 38/100)",
        "Economic volatility but improving fundamentals"
    ],
    "metadata": {
        "political_stability": "moderate",
        "economic_stability": "moderate",
        "policy_continuity": "moderate",
        "corruption_level": "moderate",
        "institutional_quality": "moderate",
        "data_year": "2023"
    }
}
```"""

    def _generic_response(self) -> str:
        """Generic mock response."""
        return """```json
{
    "value": 5,
    "confidence": 0.70,
    "justification": "The country demonstrates moderate political and economic stability. Political institutions function with some challenges. Economic stability is moderate with typical emerging market volatility. Institutional quality is developing with ongoing reforms.",
    "quotes": [
        "Moderate institutional stability",
        "Renewable energy policies in place",
        "Economic fundamentals adequate"
    ],
    "metadata": {
        "political_stability": "moderate",
        "economic_stability": "moderate",
        "policy_continuity": "moderate",
        "corruption_level": "moderate",
        "institutional_quality": "moderate",
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
        Germany Country Risk Assessment 2023

        Political Environment:
        Germany is a stable parliamentary democracy and a core member of the European Union.
        Political institutions are strong with transparent governance and regular peaceful
        transitions of power.

        Key Stability Indicators:
        - Democracy Index: 8.8/10 (Full Democracy)
        - Political Stability Index: 0.85 (World Bank)
        - Corruption Perceptions Index: 80/100 (Very Low Corruption)
        - Rule of Law Index: 0.92 (Very Strong)

        Economic Stability:
        - Largest economy in Europe
        - Low inflation environment (target 2%)
        - Strong fiscal discipline
        - Diversified industrial base

        Energy Policy Continuity:
        The Energiewende (energy transition) has been consistent policy across
        multiple governments since 2000.

        Assessment: Very high stability (9/10)
        """,
        'metadata': {
            'source': 'World Bank / IMF Country Report',
            'date': '2023',
            'type': 'country_risk'
        }
    }
]

SAMPLE_DOCS_BRAZIL = [
    {
        'content': """
        Brazil Country Risk and Investment Climate 2023

        Political Landscape:
        Brazil is a federal presidential democracy with functioning institutions.
        Democratic processes work though political landscape can be contentious.

        Stability Metrics:
        - Democracy Index: 6.9/10 (Flawed Democracy)
        - Political Stability Index: 0.15 (World Bank - Moderate)
        - Corruption Perceptions Index: 38/100 (Significant Challenges)
        - Rule of Law: 0.52 (Moderate)

        Economic Environment:
        - Emerging market volatility present
        - Inflation challenges but improving
        - Currency: Real (BRL) shows volatility
        - Fiscal challenges but reforms underway

        Renewable Energy Policy:
        Notable strength: Renewable energy auction system has remained stable
        across multiple administrations spanning 15+ years.

        Assessment: Moderate stability (6/10)
        """,
        'metadata': {
            'source': 'Country Risk Analysis',
            'date': '2023',
            'type': 'investment_climate'
        }
    }
]


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def run_extractor_demo(use_real_llm: bool = False, api_key: str = None):
    """Run demonstration of CountryStabilityExtractor."""

    print("=" * 80)
    print("COUNTRY STABILITY EXTRACTOR DEMO")
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
    print("Initializing CountryStabilityExtractor...")
    print("=" * 80)

    extractor = CountryStabilityExtractor(
        parameter_name="country_stability",
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
            'description': 'Very high stability (strong institutions)'
        },
        {
            'country': 'Brazil',
            'documents': SAMPLE_DOCS_BRAZIL,
            'description': 'Moderate stability (functioning democracy)'
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
            print(f"\n🔍 Extracting country stability data for {test_case['country']}...")
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
                print(f"\n📊 Stability Score: {result.data.value}/10")
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
                    'score': result.data.value,
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
        print(f"\n📊 Extracted Scores:")
        for r in results:
            if r.get('success'):
                print(f"   • {r['country']}: {r['score']}/10 (confidence: {r['confidence']:.1%})")

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
        description='Demo CountryStabilityExtractor'
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
