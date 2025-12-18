# 📋 AGENT #21 QUICK REFERENCE

## **BASIC USAGE**

```python
import yaml
from src.agents.analysis_agents.global_rankings_agent import GlobalRankingsAgent
from src.agents.base_agent import AgentMode

# Load config
with open('config/parameters.yaml') as f:
    config = yaml.safe_load(f)

# Initialize
agent = GlobalRankingsAgent(mode=AgentMode.MOCK, config=config['analysis'])

# Generate rankings
rankings = agent.generate_rankings(
    countries=["Germany", "USA", "China", "India", "Brazil"],
    period="Q3 2024"
)

# Print summary
print(rankings.summary)
```

---

## **KEY METHODS**

| Method | Purpose | Returns |
|--------|---------|---------|
| `generate_rankings()` | Main entry point | `GlobalRankings` |
| `get_top_n(n)` | Get top N countries | `List[CountryRanking]` |
| `get_tier_rankings(tier)` | Get all countries in tier | `List[CountryRanking]` |
| `get_country_rank(country)` | Get specific country rank | `int` |

---

## **TIER SYSTEM**

| Tier | Score Range | Description |
|------|-------------|-------------|
| **A** | ≥ 8.0 | Excellent investment climate |
| **B** | 6.5-7.99 | Strong investment climate |
| **C** | 5.0-6.49 | Moderate investment climate |
| **D** | < 5.0 | Challenging investment climate |

*Thresholds configurable in `config/parameters.yaml`*

---

## **CONFIGURATION**

```yaml
# Location: config/parameters.yaml → analysis: → global_rankings:
global_rankings:
  min_countries_for_ranking: 5
  tier_thresholds:
    tier_a_min: 8.0
    tier_b_min: 6.5
    tier_c_min: 5.0
  ranking_display:
    countries_per_tier: 10
    show_tier_statistics: true
  summary:
    highlight_top_performers: 5
    highlight_bottom_performers: 3
```

---

## **OUTPUT STRUCTURE**

```python
GlobalRankings {
    rankings: List[CountryRanking]  # All countries, sorted
    tier_statistics: Dict[Tier, TierStatistics]  # Stats per tier
    tier_transitions: List[TierTransition]  # Tier changes
    summary: str  # Executive summary
    period: str
    total_countries: int
    metadata: Dict[str, Any]
}

CountryRanking {
    rank: int
    country: str
    overall_score: float
    tier: Tier  # A/B/C/D
    subcategory_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
}

TierStatistics {
    tier: Tier
    count: int
    countries: List[str]
    avg_score: float
    min_score: float
    max_score: float
    score_range: float
}

TierTransition {
    country: str
    from_tier: Tier
    to_tier: Tier
    from_score: float
    to_score: float
    score_change: float
    direction: str  # 'upgrade', 'downgrade', 'stable', 'new'
}
```

---

## **COMMON PATTERNS**

### **Get Top Performers**
```python
top_10 = rankings.get_top_n(10)
for r in top_10:
    print(f"#{r.rank}: {r.country} ({r.overall_score:.2f})")
```

### **Analyze Tier Distribution**
```python
for tier, stats in rankings.tier_statistics.items():
    pct = stats.count / rankings.total_countries * 100
    print(f"{tier.value}-Tier: {stats.count} ({pct:.1f}%)")
```

### **Track Transitions**
```python
for trans in rankings.tier_transitions:
    icon = "⬆️" if trans.direction == "upgrade" else "⬇️"
    print(f"{icon} {trans.country}: {trans.from_tier.value} → {trans.to_tier.value}")
```

### **Find Specific Country**
```python
rank = rankings.get_country_rank("Germany")
country_data = rankings.rankings[rank - 1]  # ranks are 1-indexed
print(f"Germany: #{rank}, Score={country_data.overall_score:.2f}")
```

### **Export to JSON**
```python
data = rankings.to_dict()
import json
with open('rankings.json', 'w') as f:
    json.dump(data, f, indent=2)
```

---

## **ERROR HANDLING**

```python
try:
    rankings = agent.generate_rankings(countries=["USA"])
except AgentError as e:
    print(f"Error: {e}")
    # "Global rankings require at least 5 countries, got 1"
```

**Common Errors**:
- Too few countries (< min_countries_for_ranking)
- Empty country list
- Invalid period format
- Country analysis failures

---

## **TESTING**

```bash
# Run demo
python scripts/demo_global_rankings_agent.py

# Run tests
python scripts/test_global_rankings.py

# Quick verification
python -c "from src.agents.analysis_agents.global_rankings_agent import GlobalRankingsAgent; print('✅ Agent loads successfully')"
```

---

## **FILE LOCATIONS**

```
renewable_rankings_setup/
├── src/agents/analysis_agents/
│   └── global_rankings_agent.py  (main agent)
├── src/models/
│   └── global_rankings.py  (data models)
├── config/
│   └── parameters.yaml  (configuration)
├── scripts/
│   ├── demo_global_rankings_agent.py  (4 demos)
│   └── test_global_rankings.py  (test suite)
└── docs/
    └── AGENT_21_GLOBAL_RANKINGS_COMPLETE.md  (full docs)
```

---

## **DEPENDENCIES**

```
GlobalRankingsAgent
    ↓
CountryAnalysisAgent (#19)
    ↓
AgentService
    ↓
18 Parameter Agents (#1-#18)
```

**Required Config**: `analysis:` section in `config/parameters.yaml`

---

## **CUSTOMIZATION**

### **Change Tier Thresholds**
```yaml
tier_thresholds:
  tier_a_min: 8.5  # Stricter A-tier
  tier_b_min: 7.0  # Higher B-tier
  tier_c_min: 5.5  # Adjusted C-tier
```

### **Adjust Summary Detail**
```yaml
summary:
  highlight_top_performers: 10  # Show top 10
  highlight_bottom_performers: 5  # Show bottom 5
  mention_tier_movers: false  # Hide transitions
```

### **Change Country Limit**
```yaml
min_countries_for_ranking: 10  # Require at least 10
```

---

## **INTEGRATION**

### **With Gradio UI**
```python
def rank_countries(country_list):
    rankings = agent.generate_rankings(
        countries=country_list.split(','),
        period="Q3 2024"
    )
    return rankings.summary
```

### **With REST API**
```python
@app.post("/api/rankings")
def get_rankings(request: RankingRequest):
    rankings = agent.generate_rankings(
        countries=request.countries,
        period=request.period
    )
    return rankings.to_dict()
```

### **With Database**
```python
# Store rankings
for ranking in rankings.rankings:
    db.insert('rankings', ranking.to_dict())

# Store transitions
for trans in rankings.tier_transitions:
    db.insert('transitions', trans.to_dict())
```

---

## **PERFORMANCE**

| Countries | Time | Memory |
|-----------|------|--------|
| 5 | ~1s | <10MB |
| 10 | ~2s | <15MB |
| 30 | ~5s | <30MB |
| 100 | ~15s | <100MB |

*MOCK mode, approximate values*

---

## **MODES**

| Mode | Data Source | Use Case |
|------|-------------|----------|
| **MOCK** | Pre-defined test data | Development, testing |
| **RULE_BASED** | Algorithmic calculations | Production (phase 1) |
| **AI_POWERED** | LLM analysis | Production (phase 2) |

```python
# Change mode
agent = GlobalRankingsAgent(mode=AgentMode.RULE_BASED, config=config)
```

---

## **TROUBLESHOOTING**

| Issue | Solution |
|-------|----------|
| "Too few countries" | Provide at least 5 countries (or adjust `min_countries_for_ranking`) |
| "Import error" | Ensure you're in the project root directory |
| "Config not found" | Check `config/parameters.yaml` exists and has `analysis:` → `global_rankings:` |
| "Attribute error" | Ensure latest code version (fixed in v1.1) |

---

## **BEST PRACTICES**

✅ **DO**:
- Provide meaningful sample size (≥10 countries recommended)
- Use consistent period format
- Handle AgentError exceptions
- Store previous rankings for transition tracking
- Export results for persistence

❌ **DON'T**:
- Assume rankings with <5 countries
- Mix different time periods
- Ignore error handling
- Hard-code tier thresholds
- Skip configuration loading

---

## **QUICK CHECKS**

### **Verify Installation**
```python
from src.agents.analysis_agents.global_rankings_agent import GlobalRankingsAgent
from src.models.global_rankings import Tier
print("✅ Imports successful")
```

### **Test Configuration**
```python
import yaml
config = yaml.safe_load(open('config/parameters.yaml'))
assert 'global_rankings' in config['analysis']
print("✅ Config loaded")
```

### **Run Quick Demo**
```bash
python scripts/demo_global_rankings_agent.py
# Should complete with: "🎉 CONGRATULATIONS! All 21 agents are now complete!"
```

---

**Last Updated**: December 18, 2024  
**Agent**: #21 of 21  
**Status**: ✅ PRODUCTION READY  
**Achievement**: 🎉 ALL AGENTS COMPLETE!
