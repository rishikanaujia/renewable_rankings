"""Demo and Test Suite for AmbitionExtractor

This file demonstrates and tests the AmbitionExtractor functionality.

Run modes:
    1. Mock mode (no API keys needed) - Tests basic functionality
    2. Real mode (requires API keys) - Tests with actual LLM

Usage:
    # Mock mode (default)
    python demo_ambition_extractor.py
    
    # Real mode with API key
    python demo_ambition_extractor.py --real --api-key YOUR_API_KEY
    
    # Or set environment variable
    export OPENAI_API_KEY=your_key
    python demo_ambition_extractor.py --real
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from ai_extraction_system import AmbitionExtractor

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
    "value": 80,
    "confidence": 0.95,
    "justification": "Germany has set legally binding targets under the Renewable Energy Sources Act (EEG 2023). The country aims for 80% renewable electricity by 2030 and 100% by 2035. This is supported by strong policy frameworks including feed-in tariffs, auction mechanisms, and renewable energy quotas. The target is part of Germany's broader climate neutrality goal for 2045.",
    "quotes": [
        "80% renewable electricity by 2030",
        "100% renewable electricity by 2035",
        "legally binding under EEG 2023"
    ],
    "metadata": {
        "target_year": "2030",
        "target_type": "electricity",
        "legal_status": "binding",
        "data_year": "2023",
        "source_reliability": "high"
    }
}
```"""
    
    def _brazil_response(self) -> str:
        """Mock response for Brazil."""
        return """```json
{
    "value": 45,
    "confidence": 0.85,
    "justification": "Brazil's National Energy Plan (PNE 2050) targets 45% renewable energy in the total energy mix by 2030, maintaining its strong position in renewable energy. The country has robust hydropower infrastructure (60% of electricity) and is rapidly expanding wind and solar capacity. The target aligns with Brazil's NDC commitments under the Paris Agreement.",
    "quotes": [
        "45% renewable energy by 2030",
        "PNE 2050 establishes long-term renewable targets",
        "NDC commitment includes renewable expansion"
    ],
    "metadata": {
        "target_year": "2030",
        "target_type": "total_energy",
        "legal_status": "aspirational",
        "data_year": "2023",
        "source_reliability": "high"
    }
}
```"""
    
    def _india_response(self) -> str:
        """Mock response for India."""
        return """```json
{
    "value": 50,
    "confidence": 0.90,
    "justification": "India has committed to achieving 50% cumulative electric power installed capacity from non-fossil fuel sources by 2030. This ambitious target is part of India's updated NDC and is backed by massive solar and wind capacity additions. The target includes 500 GW of renewable energy capacity by 2030. India is one of the fastest-growing renewable energy markets globally.",
    "quotes": [
        "50% non-fossil fuel capacity by 2030",
        "500 GW renewable capacity target",
        "Updated NDC commitment 2022"
    ],
    "metadata": {
        "target_year": "2030",
        "target_type": "capacity",
        "legal_status": "binding",
        "data_year": "2022",
        "source_reliability": "high"
    }
}
```"""
    
    def _generic_response(self) -> str:
        """Generic mock response."""
        return """```json
{
    "value": 30,
    "confidence": 0.70,
    "justification": "Based on available policy documents, the country has set a renewable energy target of approximately 30% by 2030. This represents a moderate ambition level compared to global averages. The target is part of the national energy strategy but specific implementation mechanisms are still being developed.",
    "quotes": [
        "30% renewable energy by 2030",
        "national energy strategy includes renewable targets"
    ],
    "metadata": {
        "target_year": "2030",
        "target_type": "total_energy",
        "legal_status": "aspirational",
        "data_year": "2023",
        "source_reliability": "medium"
    }
}
```"""


class MockBaseExtractor:
    """Mock base extractor for testing."""
    
    def __init__(self, parameter_name, llm_service, cache=None, config=None):
        self.parameter_name = parameter_name
        self.llm_service = llm_service
        self.cache = cache
        self.config = config or {}
        logger.info(f"Initialized extractor for parameter: {parameter_name}")


class MockExtractedData:
    """Mock extracted data structure."""
    
    def __init__(self, **kwargs):
        self.parameter_name = kwargs.get('parameter_name')
        self.value = kwargs.get('value')
        self.confidence = kwargs.get('confidence')
        self.confidence_level = kwargs.get('confidence_level', 'medium')
        self.justification = kwargs.get('justification')
        self.sources = kwargs.get('sources', [])
        self.extracted_quotes = kwargs.get('extracted_quotes', [])
        self.metadata = kwargs.get('metadata', {})
        self.extraction_timestamp = datetime.now()


class MockExtractionResult:
    """Mock extraction result."""
    
    def __init__(self, success, data=None, error=None):
        self.success = success
        self.data = data
        self.error = error
        self.cached = False
        self.extraction_duration_ms = 0.0


class MockPromptTemplates:
    """Mock prompt templates."""
    
    AMBITION_TEMPLATE = """Extract renewable energy targets for {country}..."""
    
    @staticmethod
    def format_template(template, parameter_name, country, documents, **kwargs):
        return template.format(country=country, **kwargs)





# ============================================================================
# TEST DATA
# ============================================================================

SAMPLE_DOCUMENTS = {
    'germany': [{
        'content': """
        Germany's Renewable Energy Sources Act (EEG 2023)
        
        Germany has set ambitious and legally binding renewable energy targets:
        - 80% of electricity from renewable sources by 2030
        - 100% renewable electricity by 2035
        - Climate neutrality by 2045
        
        The targets are supported by comprehensive policy instruments including:
        - Feed-in tariffs for small-scale generators
        - Technology-specific auctions for large-scale projects
        - Renewable energy quotas for energy suppliers
        - Grid expansion and modernization programs
        
        Germany's Energiewende (energy transition) is one of the most comprehensive
        renewable energy policies globally, with over €500 billion invested since 2000.
        """,
        'metadata': {
            'source': 'German Federal Ministry for Economic Affairs and Energy',
            'url': 'https://www.bmwi.de/eeg2023',
            'year': 2023,
            'type': 'policy_document'
        }
    }],
    
    'brazil': [{
        'content': """
        Brazil National Energy Plan (PNE 2050)
        
        Brazil maintains its position as a renewable energy leader with the following targets:
        - 45% of total energy consumption from renewable sources by 2030
        - Expansion of wind capacity to 35 GW by 2030
        - Solar capacity target of 25 GW by 2030
        - Continued dominance of hydropower (currently 60% of electricity)
        
        The plan aligns with Brazil's NDC commitments under the Paris Agreement
        and builds on the country's natural advantages in renewable resources.
        
        Brazil's renewable energy auction system has been highly successful,
        achieving some of the world's lowest prices for wind and solar energy.
        """,
        'metadata': {
            'source': 'Brazilian Ministry of Mines and Energy',
            'url': 'https://www.gov.br/mme/pt-br/pne2050',
            'year': 2023,
            'type': 'national_plan'
        }
    }],
    
    'india': [{
        'content': """
        India's Updated NDC and Renewable Energy Commitments
        
        India has announced one of the world's most ambitious renewable energy programs:
        - 50% cumulative electric power installed capacity from non-fossil fuel sources by 2030
        - 500 GW of renewable energy capacity by 2030
        - Reduce emissions intensity of GDP by 45% by 2030 (from 2005 levels)
        - Achieve net-zero emissions by 2070
        
        Current achievements:
        - 175 GW of renewable capacity already installed
        - World's 4th largest renewable energy capacity
        - Fastest growing renewable energy market
        
        Key policies supporting these targets:
        - National Solar Mission
        - Production-Linked Incentive scheme for solar manufacturing
        - Green Energy Corridors for grid integration
        - Renewable Purchase Obligations for utilities
        """,
        'metadata': {
            'source': 'Ministry of New and Renewable Energy (MNRE)',
            'url': 'https://mnre.gov.in/',
            'year': 2022,
            'type': 'ndc_submission'
        }
    }]
}


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_basic_functionality():
    """Test 1: Basic extraction functionality."""
    print("\n" + "="*70)
    print("TEST 1: Basic Extraction Functionality")
    print("="*70)
    
    try:
        # Initialize mock LLM service
        llm_service = MockLLMService()
        
        # Create extractor
        extractor = AmbitionExtractor(
            parameter_name="ambition",
            llm_service=llm_service
        )
        
        print("✅ AmbitionExtractor initialized successfully")
        
        # Test with Germany
        print("\n📊 Testing extraction for Germany...")
        result = extractor.extract(
            country='Germany',
            documents=SAMPLE_DOCUMENTS['germany']
        )
        
        if result.success:
            print(f"✅ Extraction successful!")
            print(f"   Target: {result.data.value}%")
            print(f"   Confidence: {result.data.confidence:.2f}")
            print(f"   Target Year: {result.data.metadata.get('target_year')}")
            print(f"   Legal Status: {result.data.metadata.get('legal_status')}")
            print(f"   Justification: {result.data.justification[:100]}...")
        else:
            print(f"❌ Extraction failed: {result.error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_countries():
    """Test 2: Extraction for multiple countries."""
    print("\n" + "="*70)
    print("TEST 2: Multiple Country Extraction")
    print("="*70)
    
    try:
        llm_service = MockLLMService()
        extractor = AmbitionExtractor(
            parameter_name="ambition",
            llm_service=llm_service
        )
        
        countries = ['Germany', 'Brazil', 'India']
        results = {}
        
        for country in countries:
            print(f"\n📊 Extracting for {country}...")
            
            docs = SAMPLE_DOCUMENTS.get(country.lower(), [{
                'content': f'Sample policy document for {country}',
                'metadata': {'source': 'Test'}
            }])
            
            result = extractor.extract(country=country, documents=docs)
            results[country] = result
            
            if result.success:
                print(f"   ✅ Target: {result.data.value}%")
                print(f"   ✅ Confidence: {result.data.confidence:.2f}")
            else:
                print(f"   ❌ Failed: {result.error}")
        
        # Summary
        print("\n" + "-"*70)
        print("SUMMARY:")
        print("-"*70)
        for country, result in results.items():
            status = "✅" if result.success else "❌"
            value = f"{result.data.value}%" if result.success else "N/A"
            conf = f"{result.data.confidence:.2f}" if result.success else "N/A"
            print(f"{status} {country:15s} | Target: {value:6s} | Confidence: {conf}")
        
        return all(r.success for r in results.values())
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test 3: Data validation."""
    print("\n" + "="*70)
    print("TEST 3: Data Validation")
    print("="*70)
    
    try:
        llm_service = MockLLMService()
        extractor = AmbitionExtractor(
            parameter_name="ambition",
            llm_service=llm_service
        )
        
        # Test cases
        test_cases = [
            {
                'name': 'Valid data',
                'data': {
                    'normalized_value': 80,
                    'confidence': 0.95,
                    'justification': 'This is a valid justification with sufficient length.',
                    'metadata': {'target_year': '2030'}
                },
                'expected': True
            },
            {
                'name': 'Target too high',
                'data': {
                    'normalized_value': 200,
                    'confidence': 0.95,
                    'justification': 'Valid justification here.',
                    'metadata': {}
                },
                'expected': False
            },
            {
                'name': 'Confidence out of range',
                'data': {
                    'normalized_value': 80,
                    'confidence': 1.5,
                    'justification': 'Valid justification here.',
                    'metadata': {}
                },
                'expected': False
            },
            {
                'name': 'Justification too short',
                'data': {
                    'normalized_value': 80,
                    'confidence': 0.95,
                    'justification': 'Too short',
                    'metadata': {}
                },
                'expected': False
            }
        ]
        
        all_passed = True
        for test in test_cases:
            is_valid, error = extractor._validate_extracted_data(test['data'], 'Test')
            passed = (is_valid == test['expected'])
            
            status = "✅" if passed else "❌"
            print(f"{status} {test['name']:30s} | Valid: {is_valid:5} | Expected: {test['expected']}")
            
            if not passed:
                all_passed = False
            
            if error and not test['expected']:
                print(f"   Error: {error}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_value_normalization():
    """Test 4: Value normalization."""
    print("\n" + "="*70)
    print("TEST 4: Value Normalization")
    print("="*70)
    
    try:
        llm_service = MockLLMService()
        extractor = AmbitionExtractor(
            parameter_name="ambition",
            llm_service=llm_service
        )
        
        test_cases = [
            (80, 80.0),
            (80.5, 80.5),
            ("80", 80.0),
            ("80%", 80.0),
            ("80.5%", 80.5),
            ("  80  ", 80.0),
            ("Target: 80%", 80.0),
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            result = extractor._normalize_target_value(input_val)
            passed = (result == expected)
            
            status = "✅" if passed else "❌"
            print(f"{status} {str(input_val):20s} → {result:6.1f} (expected: {expected:.1f})")
            
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_json_extraction():
    """Test 5: JSON extraction from various formats."""
    print("\n" + "="*70)
    print("TEST 5: JSON Extraction from LLM Responses")
    print("="*70)
    
    try:
        llm_service = MockLLMService()
        extractor = AmbitionExtractor(
            parameter_name="ambition",
            llm_service=llm_service
        )
        
        # Test cases
        test_responses = [
            {
                'name': 'Markdown code block',
                'response': '''```json
{"value": 80, "confidence": 0.95, "justification": "Test"}
```''',
                'should_parse': True
            },
            {
                'name': 'Plain JSON',
                'response': '{"value": 80, "confidence": 0.95, "justification": "Test"}',
                'should_parse': True
            },
            {
                'name': 'JSON with text',
                'response': 'Here is the result: {"value": 80, "confidence": 0.95, "justification": "Test"} as requested.',
                'should_parse': True
            }
        ]
        
        all_passed = True
        for test in test_responses:
            try:
                result = extractor._extract_json_from_response(test['response'])
                passed = test['should_parse'] and isinstance(result, dict)
                status = "✅" if passed else "❌"
                print(f"{status} {test['name']:25s} | Parsed: {isinstance(result, dict)}")
            except Exception as e:
                passed = not test['should_parse']
                status = "✅" if passed else "❌"
                print(f"{status} {test['name']:25s} | Failed: {str(e)[:30]}")
                if test['should_parse']:
                    all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_with_real_api(api_key=None):
    """Test 6: Real API integration (requires API key)."""
    print("\n" + "="*70)
    print("TEST 6: Real API Integration")
    print("="*70)

    
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  Skipping - No API key provided")
        print("   Set OPENAI_API_KEY environment variable or pass --api-key")
        return None
    
    try:
        from ai_extraction_system.llm_service import LLMService, LLMConfig, LLMProvider
        
        print("🔄 Initializing real LLM service...")
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model_name='claude-3-sonnet-20240229',
            temperature=0.1,
            max_tokens=2000
        )
        
        llm_service = LLMService(config)
        print("✅ LLM service initialized")
        
        extractor = AmbitionExtractor(
            parameter_name="ambition",
            llm_service=llm_service
        )
        
        print("\n📊 Testing with real API for Germany...")
        result = extractor.extract(
            country='Germany',
            documents=SAMPLE_DOCUMENTS['germany']
        )
        
        if result.success:
            print(f"✅ Real API extraction successful!")
            print(f"   Target: {result.data.value}%")
            print(f"   Confidence: {result.data.confidence:.2f}")
            print(f"   Justification: {result.data.justification[:200]}...")
            return True
        else:
            print(f"❌ Extraction failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Real API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    """Run all tests and demos."""
    print("\n" + "="*70)
    print("AMBITION EXTRACTOR - DEMO AND TEST SUITE")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Demo Ambition Extractor')
    parser.add_argument('--real', action='store_true', help='Use real API')
    parser.add_argument('--api-key', type=str, help='API key for real mode')
    args = parser.parse_args()
    
    # Run tests
    results = {}
    
    results['basic'] = test_basic_functionality()
    results['multiple'] = test_multiple_countries()
    results['validation'] = test_validation()
    results['normalization'] = test_value_normalization()
    results['json'] = test_json_extraction()
    
    if args.real:
        results['real_api'] = test_with_real_api(args.api_key)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️ "
            status_text = "SKIPPED"
        elif result:
            status = "✅"
            status_text = "PASSED"
        else:
            status = "❌"
            status_text = "FAILED"
        
        print(f"{status} {test_name.upper():20s} | {status_text}")
    
    # Overall result
    passed_tests = sum(1 for r in results.values() if r is True)
    total_tests = sum(1 for r in results.values() if r is not None)
    
    print("\n" + "="*70)
    print(f"OVERALL: {passed_tests}/{total_tests} tests passed")
    print("="*70)
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! AmbitionExtractor is working correctly!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
