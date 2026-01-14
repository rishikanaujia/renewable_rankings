# Memory & Learning System - Installation Guide

## Package Contents

This package contains the complete Memory & Learning system for the Renewable Energy Rankings platform.

### Files Included

```
memory_system/
├── src/memory/                          # Core memory system code
│   ├── base/                           # Base types and interfaces
│   │   ├── __init__.py
│   │   ├── memory_types.py            # Enums and type definitions
│   │   ├── memory_entry.py            # Data models for all memory types
│   │   └── memory_store.py            # Abstract storage interface
│   ├── stores/                         # Storage implementations
│   │   ├── __init__.py
│   │   └── chromadb_store.py          # ChromaDB vector database
│   ├── learning/                       # Learning components
│   │   ├── __init__.py
│   │   ├── similarity_engine.py       # Find similar cases
│   │   ├── feedback_processor.py      # Learn from feedback
│   │   └── pattern_recognizer.py      # Extract patterns
│   └── integration/                    # Agent integration
│       ├── __init__.py
│       ├── memory_manager.py          # High-level API
│       └── memory_mixin.py            # Agent mixins
├── config/memory.yaml                  # Configuration file
├── docs/MEMORY_SYSTEM_GUIDE.md        # Complete user guide
├── scripts/demo_memory_system.py      # Demonstration script
├── MEMORY_SYSTEM_DELIVERY.md          # Technical summary
├── MEMORY_QUICK_REFERENCE.md          # Quick reference
└── requirements.txt                    # Updated dependencies
```

### Code Statistics

- **Total Lines of Code**: ~3,280 lines
- **Documentation**: ~1,800 lines
- **Configuration**: ~120 lines
- **Python Files**: 14 modules
- **Zero Breaking Changes**: 100% backwards compatible

## Installation Steps

### Step 1: Extract the Package

```bash
tar -xzf memory_system_package.tar.gz
cd memory_system
```

### Step 2: Copy Files to Your Project

If your project structure is:
```
your_project/
├── src/
├── config/
├── docs/
└── scripts/
```

Then copy files:

```bash
# Copy memory module to src/
cp -r src/memory /path/to/your_project/src/

# Copy configuration
cp config/memory.yaml /path/to/your_project/config/

# Copy documentation
cp docs/MEMORY_SYSTEM_GUIDE.md /path/to/your_project/docs/

# Copy demo script
cp scripts/demo_memory_system.py /path/to/your_project/scripts/

# Copy reference docs (optional)
cp MEMORY_SYSTEM_DELIVERY.md /path/to/your_project/
cp MEMORY_QUICK_REFERENCE.md /path/to/your_project/
```

### Step 3: Install Dependencies

```bash
pip install chromadb>=0.4.0
pip install sentence-transformers>=2.2.0
```

Or update your requirements.txt with the provided one:

```bash
# Merge with your existing requirements.txt or use provided one
cat requirements.txt >> /path/to/your_project/requirements.txt
pip install -r /path/to/your_project/requirements.txt
```

### Step 4: Verify Installation

```bash
cd /path/to/your_project
python -c "from src.memory import MemoryManager; print('✓ Memory system installed successfully!')"
```

### Step 5: Run Demo (Optional but Recommended)

```bash
python scripts/demo_memory_system.py
```

This will:
- Initialize the memory system
- Create sample memories
- Demonstrate all capabilities
- Verify everything works

## Quick Start Integration

### Option 1: Basic Setup (5 minutes)

```python
# In your main application initialization:
from src.memory import MemoryManager
import yaml

# Load configuration
with open('config/memory.yaml') as f:
    config = yaml.safe_load(f)

# Initialize memory manager (create once, use everywhere)
memory_manager = MemoryManager(config['memory'])
```

### Option 2: Add to Existing Agent (10 minutes)

```python
from src.memory import MemoryMixin
from src.agents.base_agent import BaseParameterAgent

class CountryStabilityAgent(BaseParameterAgent, MemoryMixin):
    def __init__(self, mode, config, memory_manager):
        # Initialize base agent as before
        BaseParameterAgent.__init__(self, "Country Stability", mode, config)
        
        # Add memory capabilities (1 line!)
        MemoryMixin.init_memory(self, memory_manager)
    
    def analyze(self, country, period, data=None):
        # Your existing analysis code works unchanged
        result = self._perform_analysis(country, period, data)
        
        # Optionally record in memory (if auto_record is False)
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

### Option 3: Use Memory Features (15 minutes)

```python
# After adding MemoryMixin to your agent:

# 1. Find similar past analyses
similar_cases = agent.get_similar_cases(
    country="Germany",
    top_k=5
)

# 2. Get memory-based context
context = agent.get_memory_context(
    country="Germany",
    max_memories=5
)

# 3. Get score suggestion from memory
suggestion = agent.suggest_score_from_memory(
    country="Germany",
    current_score=7.5
)

# 4. Record expert feedback
agent.record_expert_feedback(
    analysis_id="abc123",
    expert_id="analyst_01",
    feedback_type=FeedbackType.SCORE_ADJUSTMENT,
    original_value=7.5,
    corrected_value=8.2,
    reasoning="Underestimated recent improvements"
)
```

## Configuration

Edit `config/memory.yaml` to customize:

```yaml
memory:
  # Enable/disable globally
  enabled: true
  
  # Storage location
  store_config:
    persist_directory: ./data/memory/chroma_db
  
  # Learning parameters
  learning_config:
    learning_rate: 0.1
    min_feedback_count: 3
  
  # Agent integration
  agent_integration:
    auto_record: true                  # Automatically record all analyses
    use_memory_suggestions: true       # Enable suggestions
    enhance_with_context: true         # Enhance justifications
```

## Verification Checklist

- [ ] Files copied to correct locations
- [ ] Dependencies installed (`chromadb`, `sentence-transformers`)
- [ ] Can import: `from src.memory import MemoryManager`
- [ ] Demo script runs successfully
- [ ] Configuration file reviewed and customized
- [ ] Documentation accessible

## Integration Approaches

### Approach 1: Minimal (Start Here)
- Memory manager available globally
- Agents use memory explicitly when needed
- No changes to existing agent code
- **Time**: 5 minutes

### Approach 2: Mixin (Recommended)
- Add `MemoryMixin` to agent classes
- Memory methods available on agents
- Automatic recording (optional)
- **Time**: 10 minutes per agent

### Approach 3: Full Integration
- Use `MemoryAwareAnalysisMixin`
- Memory drives entire analysis workflow
- Maximum learning capability
- **Time**: 15 minutes per agent

## Project Structure After Installation

```
your_project/
├── src/
│   ├── agents/
│   │   ├── base_agent.py
│   │   └── ... (your existing agents)
│   ├── memory/                        ← NEW
│   │   ├── base/
│   │   ├── stores/
│   │   ├── learning/
│   │   └── integration/
│   └── ... (your other modules)
├── config/
│   ├── parameters.yaml
│   ├── memory.yaml                    ← NEW
│   └── ... (your other configs)
├── docs/
│   ├── MEMORY_SYSTEM_GUIDE.md        ← NEW
│   └── ... (your other docs)
├── scripts/
│   ├── demo_memory_system.py         ← NEW
│   └── ... (your other scripts)
├── data/
│   └── memory/                        ← NEW (created automatically)
│       └── chroma_db/
├── MEMORY_SYSTEM_DELIVERY.md         ← NEW (optional)
├── MEMORY_QUICK_REFERENCE.md         ← NEW (optional)
└── requirements.txt                   ← UPDATED
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src.memory'`

**Solution**: 
```bash
# Ensure src/ is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/your_project"
# Or add to your_project/__init__.py or run scripts from project root
```

### ChromaDB Errors

**Problem**: `ModuleNotFoundError: No module named 'chromadb'`

**Solution**:
```bash
pip install chromadb>=0.4.0 sentence-transformers>=2.2.0
```

### Configuration Errors

**Problem**: `FileNotFoundError: config/memory.yaml`

**Solution**: Ensure memory.yaml is in config/ directory or update path in code:
```python
config_path = 'your/path/to/memory.yaml'
```

### Permission Errors

**Problem**: Cannot create `data/memory/chroma_db/` directory

**Solution**: 
```bash
mkdir -p data/memory/chroma_db
chmod 755 data/memory/chroma_db
```

Or change persist_directory in config/memory.yaml to a writable location.

## Testing Your Installation

### Test 1: Basic Import
```bash
python -c "from src.memory import MemoryManager; print('✓ Import successful')"
```

### Test 2: Initialize Memory
```python
from src.memory import MemoryManager

config = {
    'enabled': True,
    'store_type': 'chromadb',
    'store_config': {
        'persist_directory': './test_memory',
        'embedding_model': 'all-MiniLM-L6-v2'
    }
}

memory = MemoryManager(config)
print(f"✓ Memory enabled: {memory.is_enabled()}")
```

### Test 3: Run Full Demo
```bash
python scripts/demo_memory_system.py
```

If all three tests pass, your installation is complete! ✅

## Next Steps

1. **Read Documentation**: Review `docs/MEMORY_SYSTEM_GUIDE.md`
2. **Pilot Integration**: Add memory to 1-2 agents
3. **Configure**: Customize `config/memory.yaml` for your needs
4. **Collect Data**: Let system record analyses for 1-2 weeks
5. **Enable Learning**: Start collecting expert feedback
6. **Monitor**: Track patterns and suggestions
7. **Scale**: Roll out to all agents

## Getting Help

- **Quick Reference**: See `MEMORY_QUICK_REFERENCE.md`
- **Full Guide**: See `docs/MEMORY_SYSTEM_GUIDE.md`
- **Technical Details**: See `MEMORY_SYSTEM_DELIVERY.md`
- **Demo Script**: Run `scripts/demo_memory_system.py`

## Key Features Summary

✅ **Four Memory Types**: Episodic, Semantic, Procedural, Feedback
✅ **Learning Capabilities**: Pattern recognition, feedback processing
✅ **Multiple Retrieval Strategies**: Similarity, temporal, frequency, hybrid
✅ **Agent Integration**: Three approaches (minimal, mixin, full)
✅ **Production Ready**: Comprehensive error handling, logging
✅ **Fully Configurable**: Everything controlled via YAML
✅ **Zero Breaking Changes**: Works alongside existing code
✅ **Well Documented**: 1,800+ lines of documentation

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review documentation files
3. Examine demo script for examples
4. Check configuration in `config/memory.yaml`

## License

Same as your main project.

---

**Installation complete! You now have a production-ready Memory & Learning system that transforms your rankings platform into an intelligent system that learns from expert experience.** 🎉
