"""Demo for OfftakerStatusExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import OfftakerStatusExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 9, "confidence": 0.92, "justification": "German utilities are highly creditworthy with strong payment history.", "quotes": ["Investment grade ratings"], "metadata": {"creditworthiness": "high"}}\n```'
        return '```json\n{"value": 6, "confidence": 0.75, "justification": "Moderate offtaker quality.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("OFFTAKER STATUS EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = OfftakerStatusExtractor("offtaker_status", llm, cache)
    
    docs = [{'content': 'German utilities: investment grade ratings, strong payment history', 'metadata': {}}]
    result = extractor.extract('Germany', docs)
    
    if result.success:
        print(f"✅ SUCCESS: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
