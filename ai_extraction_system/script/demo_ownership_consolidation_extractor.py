"""Demo for OwnershipConsolidationExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import OwnershipConsolidationExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 8, "confidence": 0.85, "justification": "Germany has a highly competitive renewable energy market with very diverse ownership. Top 3 owners control only 18% of market share, with over 100 significant players including cooperatives, municipalities, and private investors. Low consolidation enables market entry and innovation.", "quotes": ["Low consolidation", "100+ players"], "metadata": {"top3_share_pct": 18, "hhi": 450, "num_players": 100}}\n```'
        elif 'China' in prompt:
            return '```json\n{"value": 4, "confidence": 0.80, "justification": "China has moderately high consolidation with top 3 state-owned enterprises controlling 55% of renewable capacity. Market dominated by State Power Investment Corp, China Three Gorges, and China Huaneng, with about 50 significant players total.", "quotes": ["State-owned dominance"], "metadata": {"top3_share_pct": 55, "hhi": 1800, "num_players": 50}}\n```'
        return '```json\n{"value": 5, "confidence": 0.75, "justification": "Moderate consolidation.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("OWNERSHIP CONSOLIDATION EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = OwnershipConsolidationExtractor("ownership_consolidation", llm, cache)

    # Test 1: Germany (low consolidation)
    print("\nTest 1: Germany")
    docs = [{'content': 'Germany: Top 3 owners (RWE, EnBW, E.ON) control 18% market share. Over 100 significant players. HHI of 450. Highly competitive market.', 'metadata': {}}]
    result = extractor.extract('Germany', docs)
    if result.success:
        print(f"✅ Germany: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
    else:
        print(f"❌ Germany FAILED: {result.error}")
        return 1

    # Test 2: China (high consolidation)
    print("\nTest 2: China")
    docs = [{'content': 'China: Top 3 SOEs control 55% of renewable capacity. Market dominated by state-owned enterprises. About 50 significant players.', 'metadata': {}}]
    result = extractor.extract('China', docs)
    if result.success:
        print(f"✅ China: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ China FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
