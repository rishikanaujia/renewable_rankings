"""Demo and Test Suite for ExpectedReturnExtractor

This file demonstrates and tests the ExpectedReturnExtractor functionality.

Run modes:
    1. Mock mode (no API keys needed) - Tests basic functionality
    2. Real mode (requires API keys) - Tests with actual LLM

Usage:
    # Mock mode (default)
    python demo_expected_return_extractor.py

    # Real mode with API key
    python demo_expected_return_extractor.py --real --api-key YOUR_API_KEY

    # Or set environment variable
    export OPENAI_API_KEY=your_key
    python demo_expected_return_extractor.py --real
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path to import local ai_extraction_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_extraction_system import ExpectedReturnExtractor

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
    "value": 7,
    "confidence": 0.88,
    "justification": "Germany offers attractive but moderate returns for renewable energy projects. Typical solar PV projects achieve IRRs in the 7-9% range, while onshore wind projects see 8-10% IRRs. Recent auction clearing prices have been competitive at €52-58/MWh for solar and €60-65/MWh for wind. The market benefits from strong policy support, low-risk regulatory environment, and established project finance markets. However, returns are moderated by high development costs, strong competition, and mature market conditions. Overall, Germany provides good risk-adjusted returns with high bankability.",
    "quotes": [
        "Solar PV IRR: 7-9% typical range",
        "Onshore wind IRR: 8-10% for well-sited projects",
        "Recent auction clearing: €52-58/MWh solar",
        "Strong project finance market with competitive debt costs (3-4%)",
        "High bankability but competitive returns"
    ],
    "metadata": {
        "typical_irr": 8.0,
        "irr_range_min": 7.0,
        "irr_range_max": 10.0,
        "equity_return": 9.5,
        "debt_cost": 3.5,
        "ppa_price_solar": 55.0,
        "ppa_price_wind": 62.0,
        "technology": "solar and wind",
        "data_year": "2023"
    }
}
```"""

    def _brazil_response(self) -> str:
        """Mock response for Brazil."""
        return """```json
{
    "value": 9,
    "confidence": 0.90,
    "justification": "Brazil offers highly attractive returns for renewable energy projects, among the best globally. Solar PV projects achieve IRRs of 12-15%, while wind projects see 14-16% IRRs in the favorable Northeast region. The country's successful auction system has delivered competitive but profitable pricing - recent auctions cleared at R$106-118/MWh for solar and R$120-135/MWh for wind. Strong natural resources (excellent solar irradiation and wind speeds), established contractual frameworks with utilities/government, and growing corporate PPA market drive profitability. Currency risk is a consideration but manageable with proper hedging. Overall, Brazil provides excellent risk-adjusted returns.",
    "quotes": [
        "Solar PV IRR: 12-15% typical range",
        "Wind IRR: 14-16% in Northeast region",
        "Recent auction clearing: R$106-118/MWh solar, R$120-135/MWh wind",
        "Excellent natural resources boost capacity factors and returns",
        "Strong 20-year PPA contracts with government/utilities"
    ],
    "metadata": {
        "typical_irr": 13.5,
        "irr_range_min": 12.0,
        "irr_range_max": 16.0,
        "equity_return": 15.0,
        "debt_cost": 8.0,
        "ppa_price_solar": 112.0,
        "ppa_price_wind": 127.0,
        "technology": "solar and wind",
        "currency_risk": "moderate",
        "data_year": "2023"
    }
}
```"""

    def _generic_response(self) -> str:
        """Generic mock response."""
        return """```json
{
    "value": 6,
    "confidence": 0.75,
    "justification": "The country offers moderate returns for renewable energy projects. Typical project IRRs range from 8-11% depending on technology and location. Auction mechanisms are in place with recent clearing prices indicating reasonable profitability. The market shows adequate policy support and developing project finance capabilities. Returns are acceptable but not exceptional compared to global benchmarks.",
    "quotes": [
        "Project IRR range: 8-11%",
        "Moderate policy support in place",
        "Developing project finance market"
    ],
    "metadata": {
        "typical_irr": 9.5,
        "irr_range_min": 8.0,
        "irr_range_max": 11.0,
        "equity_return": 11.0,
        "debt_cost": 6.0,
        "technology": "solar and wind",
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
        Germany Renewable Energy Investment Analysis 2023

        Market Overview:
        Germany's renewable energy market is mature and highly competitive,
        offering stable but moderate returns for investors.

        Project Returns (IRR):
        - Solar PV: 7-9% typical range for utility-scale projects
        - Onshore Wind: 8-10% for well-sited projects
        - Offshore Wind: 9-11% for large-scale developments

        Recent Auction Results:
        - Solar PV: €52-58/MWh clearing prices (2023 rounds)
        - Onshore Wind: €60-65/MWh
        - Offshore Wind: €65-70/MWh

        Financing Conditions:
        - Debt cost: 3-4% for investment-grade projects
        - Equity expectations: 9-11% target returns
        - Typical leverage: 70-80% debt

        Market Characteristics:
        ✓ Strong regulatory framework (EEG 2023)
        ✓ Established project finance market
        ✓ Low country/regulatory risk
        ✓ High bankability
        ✗ High development costs
        ✗ Strong competition driving down returns
        ✗ Grid connection challenges in some regions

        Assessment: Good risk-adjusted returns (7-9 IRR range = Score 7-8/10)
        """,
        'metadata': {
            'source': 'BloombergNEF Germany Market Report',
            'date': '2023',
            'type': 'investment_analysis'
        }
    }
]

SAMPLE_DOCS_BRAZIL = [
    {
        'content': """
        Brazil Renewable Energy Investment Opportunity 2023

        Market Attractiveness:
        Brazil offers some of the most attractive renewable energy returns globally,
        combining excellent natural resources with supportive policy frameworks.

        Project Returns (IRR):
        - Solar PV: 12-15% typical range
        - Onshore Wind: 14-16% in favorable Northeast region
        - Hydro (small): 11-13%

        Recent Auction Results:
        - A-4 Auction 2023 Solar: R$106-118/MWh
        - A-4 Auction 2023 Wind: R$120-135/MWh
        - Long-term contracts: 20-year PPAs with government/utilities

        Natural Resource Quality:
        - Solar irradiation: 1,500-2,300 kWh/m²/year (world-class)
        - Wind speeds: 7-11 m/s average in Northeast (excellent)
        - Capacity factors: Solar 25-30%, Wind 40-55%

        Financing Structure:
        - BNDES financing available at subsidized rates
        - Commercial debt: 8-10% (local currency)
        - Equity requirements: 15-18% target returns
        - Typical leverage: 70-75% debt

        Risk Factors:
        - Currency volatility (Real vs USD/EUR)
        - Transmission constraints in some regions
        - Regulatory changes possible

        Assessment: Excellent returns (13-14% IRR = Score 9/10)
        High returns compensate for emerging market risks.
        """,
        'metadata': {
            'source': 'IRENA Brazil Investment Report',
            'date': '2023',
            'type': 'country_analysis'
        }
    }
]


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def run_extractor_demo(use_real_llm: bool = False, api_key: str = None):
    """Run demonstration of ExpectedReturnExtractor."""

    print("=" * 80)
    print("EXPECTED RETURN EXTRACTOR DEMO")
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
    print("Initializing ExpectedReturnExtractor...")
    print("=" * 80)

    extractor = ExpectedReturnExtractor(
        parameter_name="expected_return",
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
            'description': 'Moderate returns (7-9% IRR)'
        },
        {
            'country': 'Brazil',
            'documents': SAMPLE_DOCS_BRAZIL,
            'description': 'High returns (12-15% IRR)'
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
            print(f"\n🔍 Extracting expected return data for {test_case['country']}...")
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
                print(f"\n📊 Return Score: {result.data.value}/10")
                print(f"🎯 Confidence: {result.data.confidence:.1%}")
                print(f"\n💡 Justification:")
                print(f"   {result.data.justification[:250]}...")

                if hasattr(result.data, 'metadata') and result.data.metadata:
                    print(f"\n📋 Metadata:")
                    for key, value in result.data.metadata.items():
                        if key not in ['country', 'llm_model', 'extraction_method']:
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
        description='Demo ExpectedReturnExtractor'
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
