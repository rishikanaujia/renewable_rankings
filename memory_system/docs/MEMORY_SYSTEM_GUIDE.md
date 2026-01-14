# Memory & Learning System Documentation

## Overview

The Memory & Learning system transforms the renewable energy rankings from a stateless calculator into an intelligent platform that learns from expert experience. It captures, stores, and applies knowledge from past analyses to improve future decision-making.

## Architecture

### Four-Layer Design

```
┌─────────────────────────────────────────────────────┐
│            Integration Layer                         │
│  (MemoryManager, MemoryMixin, MemoryAwareAnalysis) │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│            Learning Layer                            │
│  (SimilarityEngine, FeedbackProcessor, Patterns)    │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│            Store Layer                               │
│  (ChromaDB, Future: PostgreSQL, Redis)              │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│            Base Layer                                │
│  (Types, Entries, Queries, Abstract Interfaces)     │
└─────────────────────────────────────────────────────┘
```

## Memory Types

### 1. Episodic Memory
Stores specific analysis sessions and their results.

**Use cases:**
- Recording every country analysis
- Tracking parameter evaluations
- Building historical performance database

**Example:**
```python
memory = EpisodicMemoryEntry(
    agent_name="CountryStability",
    country="Germany",
    period="Q3 2024",
    input_data={"gdp": 4.3, "political_stability": 9.2},
    output_data={"score": 9.5, "justification": "..."},
    execution_time_ms=245.3
)
```

### 2. Semantic Memory
Stores facts and knowledge about countries/markets.

**Use cases:**
- Policy changes
- Infrastructure developments
- Market conditions
- Regulatory updates

**Example:**
```python
memory = SemanticMemoryEntry(
    subject="Germany",
    fact_type="policy",
    fact_content="Introduced new feed-in tariff for offshore wind",
    source="government_announcement",
    valid_from=datetime(2024, 1, 1)
)
```

### 3. Procedural Memory
Stores reasoning patterns and decision strategies.

**Use cases:**
- Scoring patterns (how experts typically score)
- Weighting rules
- Decision heuristics
- Evaluation strategies

**Example:**
```python
memory = ProceduralMemoryEntry(
    pattern_name="high_gdp_scoring",
    pattern_type="scoring_strategy",
    context={"gdp_growth": {"$gt": 3.0}},
    action={"boost_score": 0.5},
    confidence_score=0.85
)
```

### 4. Feedback Memory
Stores expert corrections and adjustments.

**Use cases:**
- Score adjustments
- Reasoning corrections
- Weight modifications
- New insights from experts

**Example:**
```python
memory = FeedbackMemoryEntry(
    feedback_type=FeedbackType.SCORE_ADJUSTMENT,
    original_analysis_id="abc123",
    expert_id="analyst_01",
    original_value=7.5,
    corrected_value=8.2,
    reasoning="Underestimated renewable penetration growth"
)
```

## Quick Start

### 1. Basic Setup

```python
from src.memory import MemoryManager
import yaml

# Load configuration
with open('config/memory.yaml') as f:
    config = yaml.safe_load(f)

# Initialize memory manager
memory_manager = MemoryManager(config['memory'])

# Check if enabled
print(f"Memory enabled: {memory_manager.is_enabled()}")
```

### 2. Adding Memory to an Agent

```python
from src.agents.base_agent import BaseParameterAgent
from src.memory import MemoryMixin

class CountryStabilityAgent(BaseParameterAgent, MemoryMixin):
    def __init__(self, mode, config, memory_manager):
        BaseParameterAgent.__init__(self, "Country Stability", mode, config)
        MemoryMixin.init_memory(self, memory_manager)
    
    def analyze(self, country, period, data=None):
        # Your existing analysis logic
        result = self._perform_analysis(country, period, data)
        
        # Record in memory (if auto_record is False)
        if not self._memory_auto_record:
            self.record_analysis(
                country=country,
                period=period,
                input_data=data or {},
                output_data=result,
                execution_time_ms=100.0
            )
        
        return result
```

### 3. Using Memory in Analysis

```python
# Get similar past cases
similar_cases = agent.get_similar_cases(
    country="Germany",
    top_k=5
)

for memory, similarity in similar_cases:
    print(f"Similarity: {similarity:.2f}")
    print(f"Past score: {memory.content['output_data']['score']}")

# Get memory-based context
context = agent.get_memory_context(
    country="Germany",
    max_memories=5
)

print(f"Found {context['similar_cases_count']} similar cases")
print(f"Confidence: {context['confidence']:.2f}")

# Get score suggestion
suggestion = agent.suggest_score_from_memory(
    country="Germany",
    current_score=7.5
)

if suggestion and suggestion['confidence'] >= 0.5:
    print(f"Suggested score: {suggestion['suggested_score']:.2f}")
    print(f"Adjustment: {suggestion['adjustment']:+.2f}")
```

### 4. Recording Feedback

```python
from src.memory import FeedbackType

# Expert adjusts a score
feedback_id = agent.record_expert_feedback(
    analysis_id="abc123",
    expert_id="analyst_01",
    feedback_type=FeedbackType.SCORE_ADJUSTMENT,
    original_value=7.5,
    corrected_value=8.2,
    reasoning="Underestimated recent policy improvements",
    impact_scope="category"  # Affects all similar analyses
)

# Get feedback statistics
stats = agent.get_feedback_summary()
print(f"Total feedback: {stats['total_feedback']}")
print(f"By type: {stats['by_type']}")
```

### 5. Pattern Recognition

```python
# Recognize scoring patterns
patterns = agent.get_patterns_for_context(
    country="Germany",
    pattern_type="scoring"
)

for pattern in patterns:
    print(f"Pattern: {pattern['pattern_type']}")
    print(f"Confidence: {pattern['confidence']:.2f}")
    print(f"Description: {pattern['description']}")
```

## Advanced Features

### Memory-Aware Analysis

Use the `MemoryAwareAnalysisMixin` for automatic integration:

```python
from src.memory import MemoryAwareAnalysisMixin

class SmartAgent(BaseParameterAgent, MemoryAwareAnalysisMixin):
    def __init__(self, mode, config, memory_manager):
        BaseParameterAgent.__init__(self, "Smart Agent", mode, config)
        MemoryAwareAnalysisMixin.init_memory(self, memory_manager)
    
    def analyze(self, country, period, data=None):
        # This automatically uses memory!
        return self.analyze_with_memory(
            country=country,
            period=period,
            input_data=data,
            use_memory_suggestions=True,
            enhance_with_context=True
        )
```

**Features:**
- Automatic memory recording
- Score suggestions applied
- Justifications enhanced with historical context
- Memory context added to results

### Semantic Knowledge Base

```python
# Record knowledge
memory_manager.record_knowledge(
    subject="Germany",
    fact_type="policy",
    fact_content="New offshore wind auction system introduced",
    source="BMWi_2024_announcement"
)

# Query knowledge
knowledge = memory_manager.get_knowledge_about(
    subject="Germany",
    fact_type="policy"
)

for fact in knowledge:
    print(fact.content['fact_content'])
```

### Learning from Feedback

```python
# Current configuration
current_config = {
    'country_stability_weight': 0.25,
    'track_record_weight': 0.20,
    # ... other weights
}

# Learn from feedback and update config
updated_config = memory_manager.learn_from_feedback(
    current_config=current_config,
    strategy=LearningStrategy.WEIGHT_ADAPTATION
)

# Apply updated configuration
agent.update_config(updated_config)
```

## Integration Patterns

### Pattern 1: Minimal Integration (Opt-in)

Agents work normally, memory is optional:

```python
class MyAgent(BaseParameterAgent):
    # No memory mixin, but can use memory manager directly
    def __init__(self, mode, config, memory_manager=None):
        super().__init__("MyAgent", mode, config)
        self.memory = memory_manager
    
    def analyze(self, country, period, data):
        result = self._calculate(country, data)
        
        # Optionally record
        if self.memory and self.memory.is_enabled():
            self.memory.record_analysis(...)
        
        return result
```

### Pattern 2: Mixin Integration (Recommended)

Add memory capabilities without changing core logic:

```python
class MyAgent(BaseParameterAgent, MemoryMixin):
    def __init__(self, mode, config, memory_manager):
        BaseParameterAgent.__init__(self, "MyAgent", mode, config)
        MemoryMixin.init_memory(self, memory_manager)
        # Agent works as before, but has memory methods available
```

### Pattern 3: Full Integration (Maximum Learning)

Memory drives the analysis:

```python
class MyAgent(BaseParameterAgent, MemoryAwareAnalysisMixin):
    def __init__(self, mode, config, memory_manager):
        BaseParameterAgent.__init__(self, "MyAgent", mode, config)
        MemoryAwareAnalysisMixin.init_memory(self, memory_manager, auto_record=True)
    
    def analyze(self, country, period, data):
        # Automatically uses memory throughout
        return self.analyze_with_memory(country, period, data)
```

## Configuration

### Memory Configuration File

Located at `config/memory.yaml`:

```yaml
memory:
  enabled: true
  store_type: chromadb
  store_config:
    persist_directory: ./data/memory/chroma_db
    embedding_model: all-MiniLM-L6-v2
  learning_config:
    learning_rate: 0.1
    min_feedback_count: 3
  retrieval:
    default_strategy: hybrid
    similarity_threshold: 0.75
  agent_integration:
    auto_record: true
    use_memory_suggestions: true
```

### Environment-Specific Configs

```yaml
# Development
development:
  memory:
    enabled: true
    learning_config:
      min_feedback_count: 2  # Lower threshold for testing

# Production
production:
  memory:
    enabled: true
    store_config:
      persist_directory: /var/data/memory
      use_separate_collections: true
    retention:
      default_ttl_days: 730

# Testing (memory disabled)
testing:
  memory:
    enabled: false
```

## Retrieval Strategies

### 1. Similarity (Vector-based)
Uses embedding similarity to find semantically similar cases.

**Best for:** Finding cases with similar reasoning/justification.

```python
cases = agent.get_similar_cases(
    country="Germany",
    strategy=RetrievalStrategy.SIMILARITY
)
```

### 2. Temporal (Time-based)
Prioritizes recent analyses.

**Best for:** Getting latest insights, tracking trends over time.

```python
cases = agent.get_similar_cases(
    country="Germany",
    strategy=RetrievalStrategy.TEMPORAL
)
```

### 3. Frequency
Retrieves most frequently accessed analyses.

**Best for:** Finding commonly referenced "canonical" cases.

```python
cases = agent.get_similar_cases(
    country="Germany",
    strategy=RetrievalStrategy.FREQUENCY
)
```

### 4. Hybrid (Default)
Combines similarity, recency, and frequency with configurable weights.

**Best for:** Most use cases, balanced approach.

```python
cases = agent.get_similar_cases(
    country="Germany",
    strategy=RetrievalStrategy.HYBRID
)
```

## Performance Considerations

### Storage
- ChromaDB stores data locally (default: `./data/memory/chroma_db`)
- Disk usage grows with analyses (~1-2 KB per analysis)
- Embeddings add ~384 floats per entry (all-MiniLM-L6-v2)

### Computation
- Embedding generation: ~10-50ms per text
- Similarity search: <10ms for thousands of entries
- Pattern recognition: 100-500ms depending on data size

### Optimization Tips

1. **Batch Operations**: Use `store_batch()` for bulk recording
2. **Caching**: Enable caching for frequently accessed memories
3. **Cleanup**: Run periodic cleanup of expired memories
4. **Separate Collections**: For large deployments, use separate collections per memory type

## Troubleshooting

### Memory Not Recording

**Check:**
1. Is memory enabled? `memory_manager.is_enabled()`
2. Is auto_record set? Check agent initialization
3. Any errors in logs? Check `logs/memory.log`

### Low Confidence Suggestions

**Causes:**
- Insufficient historical data (need 3+ similar cases)
- High variability in past scores
- Different context from past analyses

**Solutions:**
- Record more analyses
- Provide more specific context
- Adjust `min_pattern_confidence` in config

### Slow Retrieval

**Optimizations:**
- Reduce `top_k` parameter
- Use more specific filters
- Enable caching
- Consider separate collections

## Best Practices

1. **Start Simple**: Use basic memory recording first, add learning later
2. **Monitor Feedback**: Track feedback statistics to ensure quality
3. **Review Patterns**: Periodically review recognized patterns
4. **Balance Automation**: Don't over-rely on suggestions, keep expert in loop
5. **Clean Data**: Remove bad analyses, they pollute the memory
6. **Version Memories**: Tag memories with model version for tracking
7. **Document Sources**: Always attribute knowledge to sources
8. **Test Learning**: Test learning updates in dev before production

## API Reference

See individual module documentation:
- `src/memory/base/` - Core types and interfaces
- `src/memory/stores/` - Storage implementations
- `src/memory/learning/` - Learning components
- `src/memory/integration/` - Agent integration

## Examples

See `scripts/demo_memory_system.py` for comprehensive examples.

## Future Enhancements

Planned features:
- PostgreSQL store for structured queries
- Redis store for high-speed caching
- Multi-agent collaborative learning
- Automatic weight tuning
- Explainable AI integration
- Memory visualization dashboard
- A/B testing framework for learning strategies
