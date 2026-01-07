"""Demo for SystemModifiersExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import SystemModifiersExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 9, "confidence": 0.90, "justification": "Germany has excellent systemic stability with minimal risk factors. Very low currency risk (EUR stability in eurozone), very low geopolitical risk (EU, NATO member), full convertibility, no sanctions, and low currency volatility (3.8% annual). Optimal investment environment.", "quotes": ["Excellent stability", "Minimal risk"], "metadata": {"currency_volatility": 3.8, "geopolitical_risk": "Very Low", "sanctions": "None"}}\n```'
        elif 'Brazil' in prompt:
            return '```json\n{"value": 6, "confidence": 0.80, "justification": "Brazil has below moderate positive systemic conditions. Moderate currency risk with BRL volatility around 15% annually, but manageable. Low to moderate geopolitical risk as stable democracy. Full convertibility with some capital controls. No sanctions or major market anomalies.", "quotes": ["Manageable risks"], "metadata": {"currency_volatility": 15.2, "geopolitical_risk": "Low-Moderate", "sanctions": "None"}}\n```'
        return '```json\n{"value": 7, "confidence": 0.75, "justification": "Low systemic risk.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("SYSTEM MODIFIERS EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = SystemModifiersExtractor("system_modifiers", llm, cache)

    # Test 1: Germany (minimal risk)
    print("\nTest 1: Germany")
    docs = [{'content': 'Germany: EUR stability in eurozone, 3.8% annual currency volatility. Very low geopolitical risk (EU, NATO). Full convertibility, no sanctions.', 'metadata': {}}]
    result = extractor.extract('Germany', docs)
    if result.success:
        print(f"✅ Germany: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
    else:
        print(f"❌ Germany FAILED: {result.error}")
        return 1

    # Test 2: Brazil (moderate risk)
    print("\nTest 2: Brazil")
    docs = [{'content': 'Brazil: BRL volatility ~15% annually. Stable democracy. Full convertibility with some capital controls. No sanctions.', 'metadata': {}}]
    result = extractor.extract('Brazil', docs)
    if result.success:
        print(f"✅ Brazil: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ Brazil FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
