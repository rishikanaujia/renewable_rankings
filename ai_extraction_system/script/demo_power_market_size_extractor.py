"""Demo for PowerMarketSizeExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import PowerMarketSizeExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 8, "confidence": 0.90, "justification": "Germany has a large power market with ~500 TWh annual electricity consumption, providing substantial opportunity for renewable energy deployment.", "quotes": ["500 TWh annual consumption"], "metadata": {"consumption_twh": 500, "market_size": "large"}}\n```'
        return '```json\n{"value": 5, "confidence": 0.75, "justification": "Moderate market size.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("POWER MARKET SIZE EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = PowerMarketSizeExtractor("power_market_size", llm, cache)

    docs = [{'content': 'Germany annual electricity consumption: ~500 TWh, one of largest markets in Europe', 'metadata': {}}]
    result = extractor.extract('Germany', docs)

    if result.success:
        print(f"✅ SUCCESS: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
