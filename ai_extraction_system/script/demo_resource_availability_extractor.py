"""Demo for ResourceAvailabilityExtractor"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai_extraction_system import ResourceAvailabilityExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMService:
    def __init__(self, *args, **kwargs):
        self.model_name = 'mock-model'
    def invoke(self, prompt: str) -> str:
        if 'Chile' in prompt:
            return '```json\n{"value": 9, "confidence": 0.90, "justification": "Chile has world-class solar resources in the Atacama Desert with irradiance levels above 2500 kWh/m2/year and excellent wind resources in Patagonia.", "quotes": ["World-class solar and wind"], "metadata": {"solar_quality": "excellent", "wind_quality": "excellent"}}\n```'
        return '```json\n{"value": 6, "confidence": 0.75, "justification": "Moderate renewable resources.", "quotes": [], "metadata": {}}\n```'

class MockCache:
    def __init__(self, *args, **kwargs): self.cache = {}
    def get(self, key: str): return self.cache.get(key)
    def set(self, key: str, value, ttl=None): self.cache[key] = value

def main():
    print("RESOURCE AVAILABILITY EXTRACTOR DEMO")
    llm = MockLLMService()
    cache = MockCache()
    extractor = ResourceAvailabilityExtractor("resource_availability", llm, cache)

    docs = [{'content': 'Chile: Atacama Desert solar irradiance >2500 kWh/m2/year, world-class wind in Patagonia', 'metadata': {}}]
    result = extractor.extract('Chile', docs)

    if result.success:
        print(f"✅ SUCCESS: {result.data.value}/10, Confidence: {result.data.confidence:.1%}")
        return 0
    else:
        print(f"❌ FAILED: {result.error}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
