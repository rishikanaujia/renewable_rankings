"""Demo for StatusOfGridExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import StatusOfGridExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 8, "confidence": 0.85, "justification": "Germany has a reliable grid infrastructure with low curtailment rates (<2%) and strong transmission capacity, supporting high renewable penetration.", "quotes": ["Low curtailment <2%"], "metadata": {"grid_reliability": "high", "curtailment_rate": 1.5}}\n```'
        elif 'China' in prompt:
            return '```json\n{"value": 6, "confidence": 0.80, "justification": "China has moderate grid quality with some curtailment issues in wind-rich regions, but improving transmission infrastructure.", "quotes": ["Improving transmission"], "metadata": {"grid_reliability": "moderate", "curtailment_rate": 5.0}}\n```'
        return '```json\n{"value": 5, "confidence": 0.75, "justification": "Moderate grid quality.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("STATUS OF GRID EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = StatusOfGridExtractor("status_of_grid", llm, cache)

    # Test 1: Germany (good grid)
    print("\nTest 1: Germany")
    docs = [{'content': 'Germany: Reliable grid, curtailment <2%, strong transmission capacity', 'metadata': {}}]
    result = extractor.extract('Germany', docs)
    if result.success:
        print(f"✅ Germany: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
    else:
        print(f"❌ Germany FAILED: {result.error}")
        return 1

    # Test 2: China (moderate grid)
    print("\nTest 2: China")
    docs = [{'content': 'China: Moderate grid, some curtailment in wind regions, improving transmission', 'metadata': {}}]
    result = extractor.extract('China', docs)
    if result.success:
        print(f"✅ China: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ China FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
