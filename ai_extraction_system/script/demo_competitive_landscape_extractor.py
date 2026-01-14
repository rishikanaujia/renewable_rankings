"""Demo and Test Suite for CompetitiveLandscapeExtractor

This file demonstrates and tests the CompetitiveLandscapeExtractor functionality.

Run modes:
    1. Mock mode (no API keys needed) - Tests basic functionality
    2. Real mode (requires API keys) - Tests with actual LLM

Usage:
    # Mock mode (default)
    python demo_competitive_landscape_extractor.py

    # Real mode with API key
    python demo_competitive_landscape_extractor.py --real --api-key YOUR_API_KEY

    # Or set environment variable
    export OPENAI_API_KEY=your_key
    python demo_competitive_landscape_extractor.py --real
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path to import local ai_extraction_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_extraction_system import CompetitiveLandscapeExtractor

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
        elif 'China' in prompt:
            return self._china_response()
        else:
            return self._generic_response()

    def _germany_response(self) -> str:
        """Mock response for Germany."""
        return """```json
{
    "value": 9,
    "confidence": 0.95,
    "justification": "Germany has one of the most open and competitive renewable energy markets globally. The market features minimal barriers to entry with streamlined EEG (Renewable Energy Act) processes, clear regulatory frameworks, and transparent grid connection rules. Licensing complexity is low with well-established procedures, permitting typically takes 6 months, and grid connection is highly efficient with mature infrastructure. The market shows very high competitive intensity with thousands of participants including utilities, IPPs, and community energy projects.",
    "quotes": [
        "Streamlined EEG regulatory process",
        "Transparent grid connection rules under BNetzA oversight",
        "Thousands of active market participants including cooperatives",
        "Clear and stable licensing requirements"
    ],
    "metadata": {
        "licensing_complexity": "low",
        "permitting_timeline_months": 6,
        "grid_connection_ease": "high",
        "market_openness": "very_high",
        "competitive_intensity": "very_high",
        "entry_examples": "Thousands of small and medium players, community projects, international developers",
        "data_year": "2023"
    }
}
```"""

    def _brazil_response(self) -> str:
        """Mock response for Brazil."""
        return """```json
{
    "value": 7,
    "confidence": 0.88,
    "justification": "Brazil maintains an open renewable energy market with low barriers to entry, primarily organized through competitive auction systems. The regulatory framework is clear under ANEEL oversight, with moderate licensing complexity. Permitting timelines average 12 months, and grid connection processes are improving. The market demonstrates high competitive intensity with strong participation from both domestic and international developers. The auction system ensures transparent market entry opportunities.",
    "quotes": [
        "Competitive auction-based system under ANEEL",
        "Open to international and domestic players",
        "High participation in renewable energy auctions",
        "Clear regulatory framework with moderate bureaucracy"
    ],
    "metadata": {
        "licensing_complexity": "moderate",
        "permitting_timeline_months": 12,
        "grid_connection_ease": "moderate",
        "market_openness": "high",
        "competitive_intensity": "high",
        "entry_examples": "Strong IPP participation, international developers active in auctions",
        "data_year": "2023"
    }
}
```"""

    def _china_response(self) -> str:
        """Mock response for China."""
        return """```json
{
    "value": 5,
    "confidence": 0.82,
    "justification": "China's renewable energy market has moderate barriers to entry with preference for state-owned enterprises (SOEs) and joint venture requirements for foreign investors. Licensing complexity is moderate to high requiring multiple government approvals. Permitting timelines average 18 months. Grid connection is controlled by state grid companies. While the market is large and growing, competitive intensity is moderate as SOEs dominate. Private and foreign players can participate but face additional regulatory hurdles.",
    "quotes": [
        "Preference for state-owned enterprises in project allocation",
        "Joint venture requirements for foreign developers",
        "State grid control over connections",
        "Multiple approval levels required for project development"
    ],
    "metadata": {
        "licensing_complexity": "high",
        "permitting_timeline_months": 18,
        "grid_connection_ease": "moderate",
        "market_openness": "moderate",
        "competitive_intensity": "moderate",
        "entry_examples": "Primarily SOEs, some private players, limited foreign participation",
        "data_year": "2023"
    }
}
```"""

    def _generic_response(self) -> str:
        """Generic mock response."""
        return """```json
{
    "value": 6,
    "confidence": 0.70,
    "justification": "The country's renewable energy market shows moderate openness with some regulatory barriers to entry. Licensing requirements are established but can involve bureaucratic processes. Permitting timelines vary between 9-15 months depending on project type and location. Grid connection procedures exist but may lack full transparency. The market shows moderate competitive intensity with a mix of established utilities and newer independent developers.",
    "quotes": [
        "Established but sometimes complex licensing procedures",
        "Moderate permitting timelines",
        "Growing but not fully mature competitive market"
    ],
    "metadata": {
        "licensing_complexity": "moderate",
        "permitting_timeline_months": 12,
        "grid_connection_ease": "moderate",
        "market_openness": "moderate",
        "competitive_intensity": "moderate",
        "entry_examples": "Mix of utilities and independent developers",
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
        Germany's Renewable Energy Market Access Report 2023

        Market Entry and Regulatory Framework:

        The German renewable energy market is governed by the Renewable Energy
        Sources Act (EEG 2023) and overseen by the Federal Network Agency (BNetzA).

        Key Features:
        - Streamlined licensing procedures under EEG framework
        - Transparent auction system for capacity allocation
        - Clear grid connection rules and timelines
        - Non-discriminatory market access for all developers

        Licensing and Permitting:
        - Building permits: Typically 4-6 months for wind/solar
        - Grid connection applications: Processed within 8 weeks
        - Environmental assessments: Standardized procedures

        Market Characteristics:
        - Over 1,500 energy cooperatives
        - Mix of utilities, IPPs, and community projects
        - Strong competition in all renewable segments
        - International developers welcome

        Barriers Assessment: Minimal - Germany ranks among the most
        open renewable energy markets globally.
        """,
        'metadata': {
            'source': 'German Federal Ministry for Economic Affairs and Climate Action',
            'date': '2023',
            'type': 'regulatory_framework'
        }
    },
    {
        'content': """
        BNetzA Grid Connection Report 2023

        Grid Connection Statistics:
        - Average connection approval time: 6 weeks
        - Standard connection processes established
        - Clear cost allocation rules
        - Transparent queue management

        The German grid connection framework is considered world-class
        with clear rules, fair treatment, and efficient processing.
        """,
        'metadata': {
            'source': 'Bundesnetzagentur (BNetzA)',
            'date': '2023',
            'type': 'grid_connection'
        }
    }
]

SAMPLE_DOCS_BRAZIL = [
    {
        'content': """
        Brazilian Renewable Energy Market Analysis 2023

        Regulatory Authority: ANEEL (National Electric Energy Agency)

        Market Structure:
        - Competitive auction-based system
        - Open to domestic and international participants
        - Long-term power purchase agreements through auctions

        Entry Requirements:
        - Company registration in Brazil
        - Environmental licenses (9-15 months typical)
        - Grid connection agreements with ONS
        - Participation in CCEE (power trading chamber)

        Market Openness:
        Brazil's renewable auctions have attracted significant international
        participation. Major global developers operate successfully in Brazil.

        Competitive Intensity:
        Recent auctions show strong competition with 2-3x oversubscription.
        Mix of local and international developers.

        Assessment: Low to moderate barriers - auction system provides
        transparent market access though bureaucracy can be challenging.
        """,
        'metadata': {
            'source': 'ANEEL Market Report',
            'date': '2023',
            'type': 'market_analysis'
        }
    }
]


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def run_extractor_demo(use_real_llm: bool = False, api_key: str = None):
    """Run demonstration of CompetitiveLandscapeExtractor."""

    print("=" * 80)
    print("COMPETITIVE LANDSCAPE EXTRACTOR DEMO")
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
    print("Initializing CompetitiveLandscapeExtractor...")
    print("=" * 80)

    extractor = CompetitiveLandscapeExtractor(
        parameter_name="competitive_landscape",
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
            'description': 'Highly open market with minimal barriers'
        },
        {
            'country': 'Brazil',
            'documents': SAMPLE_DOCS_BRAZIL,
            'description': 'Open auction-based market'
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
            print(f"\n🔍 Extracting competitive landscape data for {test_case['country']}...")
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
                print(f"\n📊 Market Openness Score: {result.data.value}/10")
                print(f"🎯 Confidence: {result.data.confidence:.1%}")
                print(f"\n💡 Justification:")
                print(f"   {result.data.justification}")

                if hasattr(result.data, 'quotes') and result.data.quotes:
                    print(f"\n📝 Key Quotes:")
                    for quote in result.data.quotes[:3]:
                        print(f"   • {quote}")

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
        description='Demo CompetitiveLandscapeExtractor'
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
