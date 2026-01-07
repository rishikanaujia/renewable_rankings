"""Demo for TrackRecordExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import TrackRecordExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Germany' in prompt:
            return '```json\n{"value": 9, "confidence": 0.90, "justification": "Germany has excellent track record with 130+ GW renewable capacity deployed.", "quotes": ["130 GW installed"], "metadata": {"capacity_gw": 130}}\n```'
        return '```json\n{"value": 7, "confidence": 0.80, "justification": "Good track record.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("TRACK RECORD EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = TrackRecordExtractor("track_record", llm, cache)
    
    docs = [{'content': 'Germany: 130 GW renewable capacity', 'metadata': {}}]
    result = extractor.extract('Germany', docs)
    
    if result.success:
        print(f"✅ SUCCESS: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
