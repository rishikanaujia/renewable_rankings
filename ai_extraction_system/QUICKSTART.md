# 🚀 QUICK START GUIDE

## Installation (5 minutes)

### Step 1: Extract the Archive

```bash
# Extract the zip file
unzip ai_extraction_system.zip

# Navigate to the directory
cd ai_extraction_system
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# OR install as a package
pip install -e .
```

### Step 3: Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Minimum required: ANTHROPIC_API_KEY or OPENAI_API_KEY
```

## Quick Test (2 minutes)

### Test 1: LLM Service

```python
from ai_extraction_system.llm_service import LLMService, LLMConfig, LLMProvider

# Initialize LLM
config = LLMConfig(
    provider=LLMProvider.ANTHROPIC,
    model_name='claude-3-sonnet-20240229',
    temperature=0.1
)

llm = LLMService(config)
response = llm.invoke("What is 2+2?")
print(response)  # Should contain "4"
```

### Test 2: Extraction Adapter

```python
from ai_extraction_system import AIExtractionAdapter

# Initialize adapter
adapter = AIExtractionAdapter()

# Test extraction with sample document
documents = [{
    'content': 'Germany aims for 80% renewable electricity by 2030.',
    'metadata': {'source': 'Test Document'}
}]

result = adapter.extract_parameter(
    parameter_name='ambition',
    country='Germany',
    period='Q3 2024',
    documents=documents
)

print(f"Target: {result['value']}%")
print(f"Confidence: {result['confidence']:.2f}")
```

## Integration with Existing Agents (10 minutes)

### Add AI_POWERED Mode to Your Agent

In your parameter agent's `_fetch_data()` method, add:

```python
elif self.mode == AgentMode.AI_POWERED:
    try:
        from ai_extraction_system import AIExtractionAdapter
        
        adapter = AIExtractionAdapter(
            llm_config=self.config.get('llm_config'),
            cache_config=self.config.get('cache_config')
        )
        
        return adapter.extract_parameter(
            parameter_name='ambition',  # Change to your parameter
            country=country,
            period=period,
            documents=kwargs.get('documents'),
            document_urls=kwargs.get('document_urls')
        )
    except Exception as e:
        logger.error(f"AI extraction failed: {e}")
        # Fallback to RULE_BASED mode
        self.mode = AgentMode.RULE_BASED
        return self._fetch_data(country, period, **kwargs)
```

### Test Your Agent

```python
from your_agents import AmbitionAgent
from ai_extraction_system.base_extractor import AgentMode

# Create agent in AI_POWERED mode
agent = AmbitionAgent(
    mode=AgentMode.AI_POWERED,
    config={
        'llm_config': {
            'provider': 'anthropic',
            'model_name': 'claude-3-sonnet-20240229'
        }
    }
)

# Analyze
result = agent.analyze(country='Germany', period='Q3 2024')
print(f"Score: {result.score}")
print(f"Confidence: {result.confidence}")
```

## Project Structure

```
ai_extraction_system/
├── __init__.py                 # Package initialization
├── base_extractor.py           # Abstract base class
├── llm_service.py              # LangChain LLM wrapper
├── ai_extraction_adapter.py   # Integration adapter
│
├── extractors/                 # Parameter extractors
│   ├── __init__.py
│   └── ambition_extractor.py   # Example extractor
│
├── processors/                 # Document processing
│   ├── __init__.py
│   └── document_processor.py   # PDF/HTML/web
│
├── prompts/                    # Prompt templates
│   ├── __init__.py
│   └── prompt_templates.py     # All templates
│
├── cache/                      # Caching system
│   ├── __init__.py
│   └── extraction_cache.py     # Cache implementation
│
├── validators/                 # Data validation
│   ├── __init__.py
│   └── data_validator.py       # Validators
│
├── requirements.txt            # Dependencies
├── setup.py                    # Package setup
├── .env.example               # Config template
├── README.md                   # Full documentation
└── INTEGRATION_EXAMPLE.py     # Integration examples
```

## Next Steps

1. **Read README.md** - Complete system documentation
2. **See INTEGRATION_EXAMPLE.py** - Detailed integration examples
3. **Implement more extractors** - Use templates provided
4. **Test with real data** - Validate on your documents
5. **Deploy to production** - Monitor costs and performance

## Common Issues

### Issue: ImportError

**Solution:** Make sure you're importing from the package:
```python
from ai_extraction_system import AIExtractionAdapter  # Correct
# not: from ai_extraction_adapter import ...
```

### Issue: API Key Not Found

**Solution:** Check your .env file:
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
```

### Issue: Module Not Found

**Solution:** Install in development mode:
```bash
pip install -e .
```

## Support

- **Documentation:** See README.md
- **Examples:** See INTEGRATION_EXAMPLE.py
- **Issues:** Check error logs for details

## Cost Estimation

- **Per extraction:** ~$0.015 (1.5 cents)
- **With caching (80% hit rate):** ~$0.003 average
- **Monthly (18 params × 1000 countries):** ~$54 with caching

Happy extracting! 🎉
