# Quick Start: Batch Research Generation

## TL;DR

Generate research documents for all 18 parameters × 10 countries = 180 documents.

**Cost**: ~$7.20 | **Time**: ~2.25 hours

## Step 1: Test First (Recommended)

Generate 6 test documents to verify everything works:

```bash
python research_system/test_batch_generation.py
```

**Cost**: $0.24 | **Time**: 4.5 minutes

This tests:
- ✅ Ambition (Brazil, India)
- ✅ Country Stability (Brazil, India)
- ✅ Expected Return (Brazil, India)

## Step 2: Generate All Research

Once test looks good:

```bash
python research_system/generate_all_research.py
```

**What happens:**
- Generates research for all 18 parameters × 10 countries
- Shows real-time progress
- Skips existing documents (won't regenerate)
- Can interrupt with Ctrl+C (progress is saved)

## Step 3: Use Research

Research is automatically available to agents:

```python
# Example: Analyze Brazil with research
from src.agents.parameter_agents.ambition_agent import AmbitionAgent
from src.agents.base_agent import AgentMode

agent = AmbitionAgent(mode=AgentMode.RULE_BASED)
result = agent.analyze("Brazil", "Q4 2024")

# result now uses research data automatically
print(result.data_sources)  # Should include "research"
```

## Configuration

All 18 parameters across 6 subcategories:

### Regulation (5)
- Ambition ✅ (already integrated with research)
- Country Stability
- Track Record
- Support Scheme
- Contract Terms

### Profitability (4)
- Expected Return
- Revenue Stream Stability
- Offtaker Status
- Long Term Interest Rates

### Market Size & Fundamentals (4)
- Power Market Size
- Resource Availability
- Energy Dependence
- Renewables Penetration

### Accommodation (2)
- Status of Grid
- Ownership Hurdles

### Competition & Ease (2)
- Ownership Consolidation
- Competitive Landscape

### System Modifiers (1)
- System Modifiers

### Countries (10)
Brazil, Germany, United States, China, India, United Kingdom, Spain, Australia, Chile, Vietnam

## Cost Breakdown

- **Test batch**: 6 docs × $0.04 = **$0.24**
- **Full batch**: 180 docs × $0.04 = **$7.20**
- **Regulation only**: 50 docs × $0.04 = **$2.00**
- **Top 5 countries**: 90 docs × $0.04 = **$3.60**

## Output

Research is stored in:
```
research_system/data/research_documents/
├── ambition/
│   ├── brazil/1.0.0/research.json
│   ├── india/1.0.0/research.json
│   └── ...
├── country_stability/
│   └── ...
└── ...
```

Summary report: `research_system/data/batch_generation_summary.txt`

## Next Steps After Generation

1. **Extend research to other agents**:
   ```python
   # Add to each *_agent.py file:
   from .ambition_agent_research_integration import ResearchIntegrationMixin

   class YourAgent(BaseParameterAgent, MemoryMixin, ResearchIntegrationMixin):
       pass
   ```

2. **Test full country analysis**:
   ```python
   from src.agents.agent_service import agent_service
   ranking = agent_service.analyze_country("Brazil", "Q4 2024")
   ```

3. **Enable in UI**:
   ```bash
   USE_REAL_AGENTS=true python src/ui/app.py
   ```

## Troubleshooting

### API Key Error
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY
```

### Rate Limit
Script includes 0.5s delays. If you hit limits, edit script to increase delay.

### Partial Failure
Re-run script - it automatically skips completed documents.

## Full Documentation

See `BATCH_GENERATION.md` for detailed documentation.
