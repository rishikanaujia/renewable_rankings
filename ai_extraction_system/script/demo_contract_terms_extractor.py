"""Demo and Test Suite for ContractTermsExtractor

This file demonstrates and tests the ContractTermsExtractor functionality.

Run modes:
    1. Mock mode (no API keys needed) - Tests basic functionality
    2. Real mode (requires API keys) - Tests with actual LLM

Usage:
    # Mock mode (default)
    python demo_contract_terms_extractor.py

    # Real mode with API key
    python demo_contract_terms_extractor.py --real --api-key YOUR_API_KEY

    # Or set environment variable
    export OPENAI_API_KEY=your_key
    python demo_contract_terms_extractor.py --real
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path to import local ai_extraction_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_extraction_system import ContractTermsExtractor

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
        elif 'India' in prompt:
            return self._india_response()
        else:
            return self._generic_response()

    def _germany_response(self) -> str:
        """Mock response for Germany."""
        return """```json
{
    "value": 10,
    "confidence": 0.95,
    "justification": "Germany's renewable energy contract framework under the EEG (Renewable Energy Sources Act) represents the gold standard globally. The EEG provides standardized, government-backed contracts with optimal risk allocation - developers face minimal project risk due to feed-in tariff guarantees. Contract enforceability is excellent under German and EU legal frameworks. Currency risk is minimal with EUR stability. The framework has decades of proven track record with exceptional bankability - projects routinely secure non-recourse financing at favorable terms. Risk allocation is optimal with government bearing most policy and market risks.",
    "quotes": [
        "EEG provides standardized feed-in tariff contracts",
        "Government-backed payment guarantees",
        "Decades of proven track record",
        "Gold standard for project finance bankability"
    ],
    "metadata": {
        "ppa_framework": "EEG (Feed-in/auction) and corporate PPAs",
        "standardization": "very_high",
        "risk_allocation": "optimal",
        "enforceability": "excellent",
        "currency_risk": "minimal",
        "termination_protections": "excellent",
        "bankability": "exceptional",
        "data_year": "2023"
    }
}
```"""

    def _brazil_response(self) -> str:
        """Mock response for Brazil."""
        return """```json
{
    "value": 8,
    "confidence": 0.88,
    "justification": "Brazil's CCEAR (regulated auctions) and bilateral PPA framework demonstrates very good contract quality. The auction system provides standardized contracts with balanced risk allocation between parties. The legal framework is strong with established arbitration mechanisms. Payment security is provided through CCEE (power trading chamber). Currency risk is moderate due to BRL volatility but hedging mechanisms exist. The framework has extensive project finance track record with high bankability - international lenders actively finance Brazilian renewable projects. Contracts have been tested and enforced successfully.",
    "quotes": [
        "CCEAR standardized auction contracts",
        "Balanced risk allocation framework",
        "Strong legal enforceability with arbitration",
        "Extensive project finance track record"
    ],
    "metadata": {
        "ppa_framework": "CCEAR (regulated) and bilateral (merchant)",
        "standardization": "high",
        "risk_allocation": "balanced",
        "enforceability": "strong",
        "currency_risk": "moderate",
        "termination_protections": "strong",
        "bankability": "very_high",
        "data_year": "2023"
    }
}
```"""

    def _india_response(self) -> str:
        """Mock response for India."""
        return """```json
{
    "value": 6,
    "confidence": 0.82,
    "justification": "India's PPA framework shows adequate to good quality with ongoing improvements. Contracts are increasingly standardized especially for SECI (Solar Energy Corporation of India) auctions. Risk allocation has improved with payment security mechanisms being strengthened. However, challenges remain with some state utilities' payment delays. Enforceability is moderate - while legal framework exists, resolution can be slow. Currency risk is present but manageable. The framework demonstrates adequate bankability - projects can secure financing but may require credit enhancements. Recent reforms are improving contract quality.",
    "quotes": [
        "SECI standard auction contracts improving",
        "Payment security mechanisms being strengthened",
        "Bankable with credit enhancements",
        "Legal framework exists but enforcement can be slow"
    ],
    "metadata": {
        "ppa_framework": "SECI auctions and state-level PPAs",
        "standardization": "moderate",
        "risk_allocation": "improving",
        "enforceability": "moderate",
        "currency_risk": "moderate",
        "termination_protections": "moderate",
        "bankability": "adequate",
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
    "justification": "The country's renewable energy contract framework shows adequate quality with standard industry practices. PPAs exist but may lack full standardization. Risk allocation is balanced though some gaps may exist in coverage. Legal enforceability is present but may face practical challenges. The framework demonstrates adequate bankability for well-structured projects, though financing may require additional credit support or guarantees.",
    "quotes": [
        "PPA framework exists with standard terms",
        "Legal framework provides enforceability",
        "Bankability adequate for structured projects"
    ],
    "metadata": {
        "ppa_framework": "Standard PPAs",
        "standardization": "moderate",
        "risk_allocation": "balanced",
        "enforceability": "moderate",
        "currency_risk": "moderate",
        "bankability": "adequate",
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
        Germany's Renewable Energy Contract Framework - EEG 2023

        The Renewable Energy Sources Act (EEG) provides the legal framework
        for renewable energy contracts in Germany.

        Key Contract Features:

        1. Standardization:
        - Highly standardized contract templates
        - Clear terms and conditions under EEG framework
        - Transparent pricing mechanisms (feed-in tariffs or auctions)

        2. Risk Allocation:
        - Government bears market price risk through feed-in guarantees
        - Grid operators obligated to connect and purchase
        - Developers face minimal volume and price risk

        3. Payment Security:
        - Government-backed payment obligations
        - Direct payment from transmission system operators
        - No counterparty credit risk

        4. Legal Framework:
        - Strong enforceability under German civil law
        - EU regulatory framework provides additional security
        - Established dispute resolution mechanisms

        5. Bankability:
        - Gold standard for project finance globally
        - Non-recourse financing readily available
        - Lowest cost of capital in renewable energy sector
        - Decades of proven track record

        Currency and Political Risk:
        - EUR stability provides currency certainty
        - Minimal political risk within EU framework
        - Long-term policy stability demonstrated

        Assessment: World-class contract framework (10/10)
        """,
        'metadata': {
            'source': 'German Federal Ministry',
            'date': '2023',
            'type': 'legal_framework'
        }
    }
]

SAMPLE_DOCS_BRAZIL = [
    {
        'content': """
        Brazil's Renewable Energy Contract Framework - CCEAR System

        Brazil's electricity auction system (CCEAR) provides the primary
        framework for renewable energy contracts.

        Contract Types:
        1. Regulated Market: CCEAR contracts from auctions
        2. Free Market: Bilateral PPAs between parties

        CCEAR Contract Features:

        Standardization:
        - Highly standardized auction contracts
        - Clear terms set by ANEEL (regulatory authority)
        - Proven template with extensive track record

        Risk Allocation:
        - Balanced allocation between developer and distributor
        - Volume risk shared through indexing mechanisms
        - Price certainty through long-term fixed prices

        Payment Security:
        - CCEE (trading chamber) provides clearing
        - Distributor payment guarantees
        - Established collection mechanisms

        Legal Enforceability:
        - Strong Brazilian legal framework
        - Commercial arbitration available
        - Successful enforcement history

        Bankability Assessment:
        - Very high bankability (8/10)
        - Extensive international project finance participation
        - Major development banks and commercial lenders active
        - Standard non-recourse financing available

        Challenges:
        - BRL currency volatility (hedging available)
        - Regulatory changes require monitoring
        - Some payment delays in stressed utilities

        Overall: Very good contract framework with proven track record
        """,
        'metadata': {
            'source': 'CCEE/ANEEL Reports',
            'date': '2023',
            'type': 'regulatory_framework'
        }
    }
]


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def run_extractor_demo(use_real_llm: bool = False, api_key: str = None):
    """Run demonstration of ContractTermsExtractor."""

    print("=" * 80)
    print("CONTRACT TERMS EXTRACTOR DEMO")
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
    print("Initializing ContractTermsExtractor...")
    print("=" * 80)

    extractor = ContractTermsExtractor(
        parameter_name="contract_terms",
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
            'description': 'Gold standard contracts (EEG framework)'
        },
        {
            'country': 'Brazil',
            'documents': SAMPLE_DOCS_BRAZIL,
            'description': 'Very good contracts (CCEAR system)'
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
            print(f"\n🔍 Extracting contract terms data for {test_case['country']}...")
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
                print(f"\n📊 Contract Quality Score: {result.data.value}/10")
                print(f"🎯 Confidence: {result.data.confidence:.1%}")
                print(f"\n💡 Justification:")
                print(f"   {result.data.justification[:300]}...")

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
        description='Demo ContractTermsExtractor'
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
