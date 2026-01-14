# Memory System - Quick Reference

## Installation

```bash
pip install chromadb sentence-transformers
```

## Basic Setup

```python
from src.memory import MemoryManager
import yaml

# Load config
with open('config/memory.yaml') as f:
    config = yaml.safe_load(f)

# Initialize
memory = MemoryManager(config['memory'])
```

## Add Memory to Agent

```python
from src.memory import MemoryMixin

class MyAgent(BaseAgent, MemoryMixin):
    def __init__(self, mode, config, memory_manager):
        BaseAgent.__init__(self, "MyAgent", mode, config)
        MemoryMixin.init_memory(self, memory_manager)
```

## Record Analysis

```python
memory_id = memory.record_analysis(
    agent_name="CountryStability",
    country="Germany",
    period="Q3 2024",
    input_data={"gdp": 4.3},
    output_data={"score": 9.2, "justification": "..."},
    execution_time_ms=150.0
)
```

## Find Similar Cases

```python
from src.memory import RetrievalStrategy

similar = memory.get_similar_analyses(
    country="Germany",
    agent="CountryStability",
    top_k=5,
    strategy=RetrievalStrategy.HYBRID
)

for mem, similarity in similar:
    print(f"Score: {mem.content['output_data']['score']}, Similarity: {similarity:.2f}")
```

## Record Feedback

```python
from src.memory import FeedbackType

feedback_id = memory.record_feedback(
    feedback_type=FeedbackType.SCORE_ADJUSTMENT,
    original_analysis_id="abc123",
    expert_id="analyst_01",
    original_value=7.5,
    corrected_value=8.2,
    reasoning="Underestimated policy improvements"
)
```

## Get Score Suggestion

```python
suggestion = memory.suggest_score_adjustment(
    country="Germany",
    parameter="CountryStability",
    current_score=9.0
)

if suggestion:
    print(f"Suggested: {suggestion['suggested_score']:.2f}")
    print(f"Confidence: {suggestion['confidence']:.1%}")
```

## Recognize Patterns

```python
patterns = memory.recognize_patterns(
    pattern_type="scoring",
    country="Germany",
    agent="CountryStability"
)

for pattern in patterns:
    print(f"{pattern['pattern_type']}: {pattern['confidence']:.1%}")
```

## Store Knowledge

```python
memory.record_knowledge(
    subject="Germany",
    fact_type="policy",
    fact_content="New offshore wind auction system",
    source="Government announcement"
)
```

## Agent Memory Methods (via Mixin)

```python
# After adding MemoryMixin to agent:

# Check if enabled
agent.memory_enabled()

# Record analysis
agent.record_analysis(country, period, input_data, output_data, time_ms)

# Get similar cases
similar = agent.get_similar_cases(country, top_k=5)

# Get memory context
context = agent.get_memory_context(country, input_data)

# Get suggestion
suggestion = agent.suggest_score_from_memory(country, current_score)

# Record feedback
agent.record_expert_feedback(analysis_id, expert_id, ...)

# Get patterns
patterns = agent.get_patterns_for_context(country)

# Enhance justification
enhanced = agent.enhance_justification_with_memory(text, country, score)

# Get feedback summary
stats = agent.get_feedback_summary()
```

## Memory Types

| Type | Purpose | Example |
|------|---------|---------|
| **Episodic** | Analysis sessions | Country evaluation results |
| **Semantic** | Facts/knowledge | Policy changes, infrastructure |
| **Procedural** | Reasoning patterns | Scoring strategies, rules |
| **Feedback** | Expert corrections | Score adjustments, improvements |

## Retrieval Strategies

| Strategy | When to Use |
|----------|-------------|
| `SIMILARITY` | Find semantically similar cases |
| `TEMPORAL` | Get recent analyses |
| `FREQUENCY` | Find commonly accessed cases |
| `HYBRID` | Balanced approach (recommended) |
| `RELEVANCE` | Custom relevance scoring |

## Feedback Types

```python
FeedbackType.SCORE_ADJUSTMENT      # Score corrections
FeedbackType.REASONING_CORRECTION  # Logic improvements
FeedbackType.WEIGHT_MODIFICATION   # Weight changes
FeedbackType.NEW_INSIGHT          # New knowledge added
FeedbackType.VALIDATION           # Expert confirms
FeedbackType.REJECTION            # Expert rejects
```

## Configuration (config/memory.yaml)

```yaml
memory:
  enabled: true
  store_type: chromadb
  store_config:
    persist_directory: ./data/memory/chroma_db
    embedding_model: all-MiniLM-L6-v2
  retrieval:
    default_strategy: hybrid
    similarity_threshold: 0.75
    default_top_k: 5
  agent_integration:
    auto_record: true
    use_memory_suggestions: true
```

## Statistics

```python
stats = memory.get_memory_statistics()
print(f"Total memories: {stats['total_memories']}")
print(f"By type: {stats['by_type']}")
```

## Cleanup

```python
# Delete expired memories
deleted = memory.cleanup_expired_memories()

# Clear all (WARNING: destructive!)
memory.clear_all_memories()
```

## Memory-Aware Analysis (Full Integration)

```python
from src.memory import MemoryAwareAnalysisMixin

class SmartAgent(BaseAgent, MemoryAwareAnalysisMixin):
    def __init__(self, mode, config, memory_manager):
        BaseAgent.__init__(self, "Smart", mode, config)
        MemoryAwareAnalysisMixin.init_memory(self, memory_manager)
    
    def analyze(self, country, period, data):
        # Automatically records, suggests, and enhances!
        return self.analyze_with_memory(country, period, data)
```

## Common Patterns

### Pattern 1: Check Before Use
```python
if memory.is_enabled():
    memory.record_analysis(...)
```

### Pattern 2: Gradual Rollout
```python
# Start with one agent
class PilotAgent(BaseAgent, MemoryMixin):
    pass

# Monitor results, then expand to others
```

### Pattern 3: Expert in the Loop
```python
# Agent suggests, expert decides
suggestion = agent.suggest_score_from_memory(...)
if suggestion and suggestion['confidence'] >= 0.7:
    # Show suggestion to expert
    expert_decision = get_expert_input(suggestion)
    # Record feedback
    agent.record_expert_feedback(...)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not recording | Check `enabled: true` in config |
| No suggestions | Need 3+ similar cases |
| Slow retrieval | Reduce `top_k` or enable caching |
| Embedding errors | Check sentence-transformers installed |

## Performance Tips

1. Enable caching for frequent queries
2. Use `batch_size` for bulk operations
3. Set appropriate `ttl_days` for retention
4. Use separate collections at scale
5. Monitor and cleanup expired memories

## Quick Demo

```bash
python scripts/demo_memory_system.py
```

## Documentation

- Full guide: `docs/MEMORY_SYSTEM_GUIDE.md`
- Delivery summary: `MEMORY_SYSTEM_DELIVERY.md`
- Code: `src/memory/`

## Key Files

```
config/memory.yaml              # Configuration
src/memory/__init__.py          # Main imports
src/memory/integration/         # MemoryManager, Mixins
src/memory/learning/            # Similarity, Feedback, Patterns
src/memory/stores/              # ChromaDB store
scripts/demo_memory_system.py  # Full demo
```
