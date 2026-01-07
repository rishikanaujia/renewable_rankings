"""Demo for RevenueStreamStabilityExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import RevenueStreamStabilityExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 9, "confidence": 0.88, "justification": "Germany has very stable revenue streams with government-backed feed-in tariffs and strong contract enforcement, providing excellent revenue predictability.", "quotes": ["Government-backed FiT"], "metadata": {"contract_stability": "high", "merchant_exposure": "minimal"}}\n```'
        return '```json\n{"value": 6, "confidence": 0.75, "justification": "Moderate revenue stability.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("REVENUE STREAM STABILITY EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = RevenueStreamStabilityExtractor("revenue_stream_stability", llm, cache)

    docs = [{'content': 'Germany: Government-backed FiT, strong contract enforcement, minimal merchant exposure', 'metadata': {}}]
    result = extractor.extract('Germany', docs)

    if result.success:
        print(f"✅ SUCCESS: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
