"""Demo for RenewablesPenetrationExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import RenewablesPenetrationExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 6, "confidence": 0.85, "justification": "Germany has ~45% renewables penetration, indicating moderate remaining opportunity for further renewable deployment.", "quotes": ["45% renewables share"], "metadata": {"penetration_pct": 45, "opportunity": "moderate"}}\n```'
        elif 'Saudi Arabia' in prompt:
            return '```json\n{"value": 10, "confidence": 0.90, "justification": "Saudi Arabia has <5% renewables penetration, indicating excellent opportunity for renewable energy expansion.", "quotes": ["<5% renewables"], "metadata": {"penetration_pct": 2, "opportunity": "excellent"}}\n```'
        return '```json\n{"value": 5, "confidence": 0.75, "justification": "Moderate penetration.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("RENEWABLES PENETRATION EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = RenewablesPenetrationExtractor("renewables_penetration", llm, cache)

    # Test 1: Germany (moderate penetration)
    print("\nTest 1: Germany")
    docs = [{'content': 'Germany renewables share: 45% of electricity generation', 'metadata': {}}]
    result = extractor.extract('Germany', docs)
    if result.success:
        print(f"✅ Germany: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
    else:
        print(f"❌ Germany FAILED: {result.error}")
        return 1

    # Test 2: Saudi Arabia (very low penetration = high opportunity)
    print("\nTest 2: Saudi Arabia")
    docs = [{'content': 'Saudi Arabia renewables: <5% of power mix, massive opportunity', 'metadata': {}}]
    result = extractor.extract('Saudi Arabia', docs)
    if result.success:
        print(f"✅ Saudi Arabia: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ Saudi Arabia FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
