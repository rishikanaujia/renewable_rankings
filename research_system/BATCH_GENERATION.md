# Batch Research Generation Guide

## Overview

This guide explains how to generate research documents for all parameters across multiple countries, creating a comprehensive research library for the ranking system.

## What Gets Generated

- **18 Parameters** across 6 subcategories:
  - **Regulation** (5): Ambition, Country Stability, Track Record, Support Scheme, Contract Terms
  - **Profitability** (4): Expected Return, Revenue Stream Stability, Offtaker Status, Long Term Interest Rates
  - **Market Size & Fundamentals** (4): Power Market Size, Resource Availability, Energy Dependence, Renewables Penetration
  - **Accommodation** (2): Status of Grid, Ownership Hurdles
  - **Competition & Ease** (2): Ownership Consolidation, Competitive Landscape
  - **System Modifiers** (1): System Modifiers

- **10 Countries**: Brazil, Germany, USA, China, India, UK, Spain, Australia, Chile, Vietnam

- **Total**: 180 research documents (18 parameters × 10 countries)

## Cost & Time Estimates

### Full Batch (180 documents)
- **Cost**: ~$7.20 ($0.04 per document average)
- **Time**: ~2.25 hours (45 seconds per document)
- **API Tokens**: ~900,000 tokens (5,000 per document average)

### Test Batch (6 documents)
- **Cost**: ~$0.24
- **Time**: ~4.5 minutes
- **API Tokens**: ~30,000 tokens

## Prerequisites

1. **OpenAI API Key**: Set in `.env` file
   ```bash
   OPENAI_API_KEY=sk-...
   ```

2. **Python Environment**: Activate virtual environment
   ```bash
   source .venv/bin/activate  # or activate.bat on Windows
   ```

3. **Dependencies**: All installed via `pip install -r requirements.txt`

## Step-by-Step Process

### Step 1: Test with Small Batch First

Before generating all 180 documents, test with a small subset:

```bash
python research_system/test_batch_generation.py
```

This generates research for:
- 3 parameters (Ambition, Country Stability, Expected Return)
- 2 countries (Brazil, India)
- 6 total documents (~$0.24, ~4.5 minutes)

**What to check:**
- ✅ Research generation completes successfully
- ✅ Quality grades are reasonable (C-F is normal for first version)
- ✅ Metrics are being extracted correctly
- ✅ Costs align with estimates (~$0.04 per document)
- ✅ No API errors or rate limiting

### Step 2: Review Test Results

After test batch completes, check:

1. **Console Output**: Review quality grades, costs, timing
2. **Research Files**: Located in `research_system/data/research_documents/`
3. **Summary Report**: Check `research_system/data/batch_generation_summary.txt`

Example structure:
```
research_system/data/research_documents/
├── ambition/
│   ├── brazil/
│   │   └── 1.0.0/
│   │       ├── research.json
│   │       └── metadata.json
│   └── india/
│       └── 1.0.0/
│           ├── research.json
│           └── metadata.json
├── country_stability/
│   └── ...
└── expected_return/
    └── ...
```

### Step 3: Generate Full Batch

Once test batch looks good, generate all 180 documents:

```bash
python research_system/generate_all_research.py
```

**⚠️ Important:**
- This will take ~2.25 hours
- Cost will be ~$7.20 (charged to OpenAI API)
- Script shows progress for each document
- Can interrupt with Ctrl+C (progress is saved)
- Existing documents are skipped (won't regenerate)

### Step 4: Monitor Progress

The script shows real-time progress:

```
════════════════════════════════════════════════════════════════════════════════
 📌 PARAMETER: Ambition (regulation)
════════════════════════════════════════════════════════════════════════════════

[1/180] Brazil               ✅ SUCCESS (v1.0.0, Grade: C, 42.3s, $0.0389)
[2/180] Germany              ⏭️  SKIPPED (exists)
[3/180] United States        ✅ SUCCESS (v1.0.0, Grade: B, 45.1s, $0.0421)
[4/180] China                ✅ SUCCESS (v1.0.0, Grade: C, 38.7s, $0.0356)
...
```

**Status Indicators:**
- ✅ **SUCCESS**: Document generated successfully
- ⏭️ **SKIPPED**: Valid cached version exists
- ❌ **FAILED**: Error occurred (script continues with next)

### Step 5: Review Final Results

After completion, review:

1. **Console Summary**:
   - Success/failure counts
   - Total cost and token usage
   - Quality grade distribution
   - Average generation time

2. **Detailed Report**: `research_system/data/batch_generation_summary.txt`
   - Complete list of all documents
   - Per-document costs and grades
   - Failed documents with error messages

3. **Research Documents**: Browse `research_system/data/research_documents/`

## Using Generated Research

Once generation is complete, the research is automatically available to all agents:

### 1. Individual Agent Use

```python
from src.agents.parameter_agents.ambition_agent import AmbitionAgent

agent = AmbitionAgent(mode=AgentMode.RULE_BASED)
result = agent.analyze("Brazil", "Q4 2024")

# Result will use research data automatically
# Check data_sources to confirm: ["research", ...]
```

### 2. Full Country Analysis

```bash
# Using agent service
from src.agents.agent_service import agent_service

ranking = agent_service.analyze_country("Brazil", "Q4 2024")
# All 18 parameters will use research where available
```

### 3. UI Integration

```bash
# Set environment variable to use real agents
export USE_REAL_AGENTS=true
python src/ui/app.py

# All analyses will now use research-backed data
```

## Cost Optimization Tips

### 1. Skip Existing Documents

The script automatically skips documents with valid cache (7-day TTL):

```python
# Default behavior - skips existing
python research_system/generate_all_research.py

# To force regenerate all (costs full $7.20)
# Edit script: skip_existing=False
```

### 2. Generate Priority Parameters First

Edit `generate_all_research.py` to only include high-priority parameters:

```python
# Only regulation parameters (5 params × 10 countries = 50 docs, ~$2.00)
priority_params = ['Ambition', 'Country Stability', 'Track Record',
                   'Support Scheme', 'Contract Terms']
```

### 3. Prioritize Key Countries

Generate research for top markets first:

```python
# Only top 5 countries (18 params × 5 countries = 90 docs, ~$3.60)
priority_countries = ['China', 'United States', 'India', 'Germany', 'Brazil']
```

### 4. Use Cached Results

Research has 7-day TTL. Re-running analysis within 7 days is free.

## Troubleshooting

### Error: OpenAI API Key Not Found

```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Set if missing
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Error: Rate Limit Exceeded

The script includes 0.5s delays between requests. If you still hit limits:

```python
# Edit generate_all_research.py, increase delay:
time.sleep(1.0)  # Increase from 0.5 to 1.0
```

### Error: Timeout on Long Documents

Some parameters generate longer research. If timeouts occur:

```yaml
# Edit research_system/config/research_config.yaml
llm:
  timeout: 120  # Increase from 60 to 120 seconds
```

### Partial Generation Failure

If script is interrupted or fails partway:

1. Re-run the script - it will skip completed documents
2. Check `batch_generation_summary.txt` for failed items
3. Manually retry failed parameter-country combinations:

```bash
python research_system/test_single_research.py
# Edit to specify parameter and country
```

## Quality Grades Explained

Research documents receive automatic quality grades:

- **A**: Excellent (>90% complete, high-quality sources)
- **B**: Good (80-90% complete, good sources)
- **C**: Satisfactory (70-80% complete, adequate sources)
- **D**: Below Average (60-70% complete, limited sources)
- **F**: Poor (<60% complete, minimal data)

**Normal distribution**: Most documents get C-D grades on first generation. This is expected - the research system does its best with available public data.

**To improve grades**: After initial generation, you can:
1. Manually curate better sources
2. Re-generate with updated prompts
3. Add domain-specific context to prompts

## Advanced: Parallel Generation

For faster generation, you can run multiple instances in parallel:

```bash
# Terminal 1: Regulation parameters
python generate_all_research.py --subcategory regulation

# Terminal 2: Profitability parameters
python generate_all_research.py --subcategory profitability

# etc.
```

**Note**: This feature requires editing the script to add CLI arguments.

## Maintenance

### Re-generating Stale Research

Research cache expires after 7 days. To refresh:

```bash
# Force re-generation (ignores cache)
# Edit script: use_cache=False, skip_existing=False
python research_system/generate_all_research.py
```

### Updating Individual Parameters

To update just one parameter across all countries:

```python
# Edit test_batch_generation.py
TEST_PARAMETERS = [
    {'name': 'Ambition', 'key': 'ambition', 'subcategory': 'regulation'}
]
TEST_COUNTRIES = ["Brazil", "Germany", "United States", ...]  # All 10

python research_system/test_batch_generation.py
```

### Cleaning Old Versions

Research uses semantic versioning (1.0.0, 1.1.0, etc.). Old versions are kept for 5 versions:

```bash
# Manually clean old versions
find research_system/data/research_documents -name "*.json" | grep -v "1.0.0"
```

## Next Steps

After generating research:

1. **Extend to other agents**: Add `ResearchIntegrationMixin` to remaining 16 parameter agents
2. **Test end-to-end**: Run full country analysis with `USE_REAL_AGENTS=true`
3. **Monitor quality**: Review research quality grades and improve prompts
4. **Scale up**: Add more countries or parameters as needed

## Support

For issues:
1. Check logs in `logs/` directory
2. Review `research_system/data/batch_generation_summary.txt`
3. Test individual parameters with `test_single_research.py`
4. Check OpenAI API dashboard for usage and errors
