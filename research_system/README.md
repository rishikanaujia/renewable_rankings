# Research System

An LLM-powered research generation system that creates comprehensive, versioned research documents for renewable energy investment parameters across different countries.

## Overview

The Research System automatically generates detailed research documents for each parameter-country combination, stores them with proper versioning, and makes them available for reuse by the AI extraction system and parameter agents.

### Key Features

- **Automated Research Generation**: LLM-powered comprehensive research for any parameter-country combination
- **Semantic Versioning**: Automatic versioning of research documents (1.0.0, 1.1.0, etc.)
- **Intelligent Caching**: 7-day cache TTL to avoid redundant LLM calls
- **Parameter-Specific Prompts**: Auto-generated prompts from `parameters.yaml`
- **Quality Validation**: Automatic quality scoring of research documents
- **Multiple Formats**: JSON and Markdown export
- **Cost Optimization**: Reuses cached research to minimize LLM costs
- **Langfuse Integration**: Optional observability for prompt tracking and cost analysis

## Architecture

```
research_system/
├── src/
│   ├── research_orchestrator.py    # High-level API coordinator
│   ├── research_agent.py            # LLM-powered research conductor
│   ├── prompt_generator.py          # Parameter-specific prompt generation
│   ├── version_manager.py           # Semantic versioning system
│   ├── extraction_adapter.py        # Bridge to AI extraction system
│   ├── langfuse_integration.py      # Optional observability
│   └── storage/
│       └── research_store.py        # Versioned document storage
├── config/
│   └── research_config.yaml         # System configuration
├── prompts/
│   ├── base_research_template.txt   # Base research template
│   └── generated/                   # Auto-generated parameter prompts
├── data/
│   └── research_documents/          # Versioned research storage
│       └── {parameter}/
│           └── {country}/
│               └── {version}/
│                   ├── research.json
│                   └── metadata.json
└── demo_research_system.py          # Demonstration script
```

## Installation

### Prerequisites

```bash
# Required: LangChain and LLM provider
pip install langchain langchain-openai langchain-anthropic

# Optional: For Langfuse observability
pip install langfuse

# Required: YAML support
pip install pyyaml
```

### Environment Variables

Add to your `.env` file:

```bash
# OpenAI (recommended)
OPENAI_API_KEY=your-openai-api-key

# Or Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional: Langfuse (for observability)
LANGFUSE_PUBLIC_KEY=your-public-key
LANGFUSE_SECRET_KEY=your-secret-key
```

## Quick Start

### Basic Usage

```python
from research_system import ResearchOrchestrator

# Initialize
orchestrator = ResearchOrchestrator()

# Generate research for a parameter-country combination
doc = orchestrator.get_research(
    parameter="Ambition",
    country="Germany",
    period="Q4 2024"
)

# Access research content
print(doc.content['overview'])
print(doc.content['key_metrics'])
print(doc.content['policy_framework'])

# Get version info
print(f"Version: {doc.version}")
print(f"Created: {doc.created_at}")
```

### Batch Generation

```python
# Generate research for multiple combinations
results = orchestrator.batch_generate_research(
    parameters=["Ambition", "Country Stability", "Track Record"],
    countries=["Germany", "Brazil", "India"],
    use_cache=True  # Use cached research if available
)

# Results is a dict: {"Ambition|Germany": doc, ...}
for key, doc in results.items():
    print(f"{key}: v{doc.version}")
```

### Cached Retrieval

```python
# Get cached research (fast, no LLM call)
doc = orchestrator.get_research(
    parameter="Ambition",
    country="Germany",
    use_cache=True  # Default
)

# Check cache status
is_valid = orchestrator.research_store.is_cache_valid("Ambition", "Germany")
print(f"Cache valid: {is_valid}")

# View version history
history = orchestrator.get_version_history("Ambition", "Germany")
for h in history:
    print(f"v{h['version']}: {h['created_at']}")
```

## Integration with AI Extraction System

The research system provides a lightweight adapter for the AI extraction system:

```python
from research_system.src.extraction_adapter import ResearchExtractionAdapter

# Initialize adapter
adapter = ResearchExtractionAdapter()

# Get research context for extraction
research = adapter.get_research_context(
    parameter="Ambition",
    country="Germany"
)

# Enhance extraction prompt with research
enhanced_prompt = adapter.enhance_extraction_prompt(
    base_prompt="Extract ambition metrics...",
    parameter="Ambition",
    country="Germany"
)

# Get specific cached values
metric = adapter.get_cached_value(
    parameter="Ambition",
    country="Germany",
    metric_name="renewable energy target"
)
```

## Integration with Parameter Agents

Add research capability to your parameter agents:

```python
from research_system import ResearchOrchestrator

class EnhancedAmbitionAgent(AmbitionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.research_orchestrator = ResearchOrchestrator()

    def _fetch_data(self, country: str, period: str, **kwargs):
        # Try to get research first
        try:
            research_doc = self.research_orchestrator.get_research(
                parameter="Ambition",
                country=country,
                period=period,
                use_cache=True
            )

            # Extract metrics from research
            metrics = research_doc.content.get('key_metrics', [])
            # Use metrics for analysis...

        except Exception as e:
            logger.warning(f"Research not available, using fallback: {e}")
            # Fall back to original data fetching
            return super()._fetch_data(country, period, **kwargs)
```

## Research Document Structure

Each research document contains:

```json
{
  "parameter": "Ambition",
  "country": "Germany",
  "period": "Q4 2024",
  "research_date": "2024-01-07",

  "overview": "Comprehensive overview...",
  "current_status": "Current state analysis...",
  "historical_trends": "Historical evolution...",
  "policy_framework": "Legal and regulatory framework...",

  "key_metrics": [
    {
      "metric": "Renewable energy target",
      "value": "80",
      "unit": "%",
      "source": "German Energy Act 2023",
      "date": "2023-12-01"
    }
  ],

  "challenges": "Main barriers...",
  "opportunities": "Growth drivers...",
  "future_outlook": "Projections...",

  "sources": [
    {
      "name": "German Federal Ministry",
      "url": "https://...",
      "access_date": "2024-01-07"
    }
  ],

  "confidence": 0.85,
  "completeness_score": 0.92,

  "_validation": {
    "scores": {"overall": 0.88},
    "grade": "B",
    "issues": []
  }
}
```

## Configuration

Edit `research_system/config/research_config.yaml`:

```yaml
llm:
  provider: openai  # openai or anthropic
  model_name: gpt-4-turbo-preview
  temperature: 0.3
  max_tokens: 8000

research:
  depth: comprehensive  # quick, standard, comprehensive, exhaustive
  sources:
    - web_search
    - policy_databases
    - government_sites

storage:
  versioning:
    strategy: semantic  # semantic or timestamp
    keep_versions: 5

cache:
  enabled: true
  ttl: 604800  # 7 days

langfuse:
  enabled: false  # Set true to enable
```

## Prompt Customization

### Generate Parameter-Specific Prompts

```python
from research_system.src.prompt_generator import PromptGenerator

generator = PromptGenerator()

# Generate all prompts from parameters.yaml
prompts = generator.generate_all_prompts()

# Prompts saved to: research_system/prompts/generated/
```

### Customize Base Template

Edit `research_system/prompts/base_research_template.txt` to change:
- Research structure
- Output format
- Instructions
- Required sections

## CLI Usage

```bash
# Run demo
python research_system/demo_research_system.py

# Generate research for specific parameter-country
python -c "
from research_system import ResearchOrchestrator
orc = ResearchOrchestrator()
doc = orc.get_research('Ambition', 'Germany')
print(doc.content['overview'])
"
```

## Statistics and Monitoring

```python
# Get system statistics
stats = orchestrator.get_statistics()

print(f"Total documents: {stats['storage']['total_documents']}")
print(f"Total cost: ${stats['agent']['total_cost_usd']:.2f}")
print(f"Average latency: {stats['agent']['average_latency_ms']:.0f}ms")

# Search research
all_research = orchestrator.get_available_research()
ambition_research = orchestrator.search_research(parameter="Ambition")
germany_research = orchestrator.search_research(country="Germany")
```

## Version Management

```python
# Get version history
history = orchestrator.get_version_history("Ambition", "Germany")

# Cleanup old versions (keep last 5)
cleanup_stats = orchestrator.cleanup_old_versions(keep_count=5)
print(f"Deleted {cleanup_stats['total_deleted']} old versions")

# Load specific version
doc = orchestrator.research_store.load("Ambition", "Germany", version="1.2.0")
```

## Export Research

```python
# Export as JSON
json_output = orchestrator.export_research(
    parameter="Ambition",
    country="Germany",
    format='json'
)

# Export as Markdown
markdown = orchestrator.export_research(
    parameter="Ambition",
    country="Germany",
    format='markdown'
)

# Save to file
with open('research_report.md', 'w') as f:
    f.write(markdown)
```

## Langfuse Observability (Optional)

Enable detailed tracking of prompts, generations, and costs:

```yaml
# research_config.yaml
langfuse:
  enabled: true
  track_prompts: true
  track_generations: true
  track_costs: true
```

```bash
# Set environment variables
export LANGFUSE_PUBLIC_KEY=your-key
export LANGFUSE_SECRET_KEY=your-secret
```

Access dashboard at: https://cloud.langfuse.com

## Cost Optimization

The research system minimizes costs through:

1. **Intelligent Caching**: 7-day TTL prevents redundant research
2. **Version Reuse**: Loads existing research instead of regenerating
3. **Batch Operations**: Efficient batch processing for multiple documents
4. **Quality Validation**: Ensures research quality before storage
5. **Selective Generation**: Only generates new research when needed

### Cost Estimates

Approximate costs per research document (using GPT-4):
- Single research: $0.20 - $0.50
- Cached retrieval: $0.00
- Batch of 10: $2.00 - $5.00

## Best Practices

### 1. Use Cache Effectively

```python
# Always use cache for repeated access
doc = orchestrator.get_research("Ambition", "Germany", use_cache=True)

# Force new research only when needed
doc = orchestrator.get_research("Ambition", "Germany", use_cache=False)
```

### 2. Batch Generate Strategically

```python
# Pre-generate research for common countries
common_countries = ["Germany", "United States", "China", "Brazil", "India"]
all_params = orchestrator.prompt_generator.list_parameters()

results = orchestrator.batch_generate_research(
    parameters=all_params,
    countries=common_countries,
    use_cache=True
)
```

### 3. Monitor Quality

```python
doc = orchestrator.get_research("Ambition", "Germany")
validation = doc.content.get('_validation', {})

if validation.get('grade', 'F') < 'C':
    logger.warning(f"Low quality research: {validation['grade']}")
    # Consider regenerating or manual review
```

### 4. Regular Cleanup

```python
# Schedule weekly cleanup
cleanup_stats = orchestrator.cleanup_old_versions(keep_count=5)
```

## Troubleshooting

### Issue: "No API key found"
**Solution**: Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`

### Issue: "Research quality too low"
**Solution**:
- Increase `max_tokens` in config
- Use more powerful model (gpt-4-turbo-preview)
- Add additional context to research prompt

### Issue: "Slow generation"
**Solution**:
- Use cache whenever possible
- Consider using faster model for bulk generation
- Enable batch processing

### Issue: "Storage growing too large"
**Solution**:
- Run regular cleanup with `cleanup_old_versions()`
- Reduce `keep_versions` in config
- Delete unused parameter-country combinations

## Examples

See `demo_research_system.py` for comprehensive examples:

```bash
python research_system/demo_research_system.py
```

## API Reference

### ResearchOrchestrator

Main entry point for research system.

**Methods:**
- `get_research(parameter, country, period=None, use_cache=True)`
- `batch_generate_research(parameters, countries, period=None, use_cache=True)`
- `get_available_research()`
- `search_research(parameter=None, country=None)`
- `get_version_history(parameter, country)`
- `cleanup_old_versions(keep_count=5)`
- `get_statistics()`
- `export_research(parameter, country, version=None, format='json')`

### ResearchAgent

LLM-powered research conductor.

**Methods:**
- `conduct_research(parameter, country, period=None, additional_context=None)`
- `batch_research(parameter_country_pairs, period=None)`
- `validate_research_quality(research_data)`

### ResearchStore

Versioned document storage.

**Methods:**
- `save(parameter, country, period, content, change_type, change_description=None)`
- `load(parameter, country, version=None)`
- `exists(parameter, country, version=None)`
- `is_cache_valid(parameter, country, version=None)`
- `list_all_research()`
- `search_by_parameter(parameter)`
- `search_by_country(country)`

## Contributing

To extend the research system:

1. **Add new research sections**: Edit `base_research_template.txt`
2. **Customize prompts**: Modify `PromptGenerator._format_description()`
3. **Add data sources**: Update research agent's source integration
4. **Enhance validation**: Extend `validate_research_quality()`

## License

Part of the Renewable Rankings project.

## Support

For issues or questions, see the main project README or open an issue.
