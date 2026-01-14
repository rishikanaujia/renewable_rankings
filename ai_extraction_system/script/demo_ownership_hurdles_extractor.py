"""Demo for OwnershipHurdlesExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import OwnershipHurdlesExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 10, "confidence": 0.90, "justification": "Germany allows 100% foreign ownership in renewable energy with no restrictions. Full EU single market access, no local content requirements, and standard approval processes. Excellent market access for international investors.", "quotes": ["100% foreign ownership", "No restrictions"], "metadata": {"foreign_ownership_pct": 100, "approval_complexity": "Standard", "local_content_req": "None"}}\n```'
        elif 'China' in prompt:
            return '```json\n{"value": 5, "confidence": 0.75, "justification": "China has moderate ownership barriers with 49% foreign ownership cap in many renewable projects. Multiple approval requirements from NDRC and MOFCOM. Significant local content requirements and extensive investment screening.", "quotes": ["49% cap", "Local content requirements"], "metadata": {"foreign_ownership_pct": 49, "approval_complexity": "High", "local_content_req": "Significant"}}\n```'
        return '```json\n{"value": 7, "confidence": 0.75, "justification": "Low ownership hurdles.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("OWNERSHIP HURDLES EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = OwnershipHurdlesExtractor("ownership_hurdles", llm, cache)

    # Test 1: Germany (no barriers)
    print("\nTest 1: Germany")
    docs = [{'content': 'Germany: 100% foreign ownership allowed. EU single market. No local content requirements. Standard approval process.', 'metadata': {}}]
    result = extractor.extract('Germany', docs)
    if result.success:
        print(f"✅ Germany: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
    else:
        print(f"❌ Germany FAILED: {result.error}")
        return 1

    # Test 2: China (moderate barriers)
    print("\nTest 2: China")
    docs = [{'content': 'China: 49% foreign ownership cap. Multiple approval requirements. Significant local content requirements.', 'metadata': {}}]
    result = extractor.extract('China', docs)
    if result.success:
        print(f"✅ China: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ China FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
