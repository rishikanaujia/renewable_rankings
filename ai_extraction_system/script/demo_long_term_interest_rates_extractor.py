"""Demo for LongTermInterestRatesExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import LongTermInterestRatesExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 9, "confidence": 0.88, "justification": "Germany has very low long-term interest rates with 10-year bund yields near 0-1%, providing excellent financing conditions for renewable projects.", "quotes": ["Bund yields below 1%"], "metadata": {"bond_yield_10y": 0.5, "financing_environment": "excellent"}}\n```'
        return '```json\n{"value": 6, "confidence": 0.75, "justification": "Moderate interest rates.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("LONG-TERM INTEREST RATES EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = LongTermInterestRatesExtractor("long_term_interest_rates", llm, cache)

    docs = [{'content': 'Germany 10-year bund yields: 0.5%, excellent financing conditions for renewables', 'metadata': {}}]
    result = extractor.extract('Germany', docs)

    if result.success:
        print(f"✅ SUCCESS: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
