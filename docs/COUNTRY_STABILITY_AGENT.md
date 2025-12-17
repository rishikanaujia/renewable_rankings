# 🏛️ Country Stability Agent - Complete Documentation

## Overview

The **Country Stability Agent** analyzes political and economic risk for renewable energy investments using **Euromoney Country Risk (ECR)** ratings.

**Key Principle:** Lower ECR rating = Higher stability = Higher score (inverse relationship)

---

## ✅ Best Practices Implemented

### 1. **Config-Driven (No Hardcoding)**

**❌ Bad (Hardcoded):**
```python
class CountryStabilityAgent:
    SCORING_RUBRIC = [  # Hardcoded in code
        {"score": 10, "min_ecr": 0.0, "max_ecr": 1.0, ...},
        # ...
    ]
```

**✅ Good (Config-Driven):**
```python
class CountryStabilityAgent:
    def __init__(self, ...):
        # Load from config/parameters.yaml
        self.scoring_rubric = self._load_scoring_rubric()
```

**Benefits:**
- ✅ Single source of truth
- ✅ No code changes to modify rubric
- ✅ Domain experts can edit YAML
- ✅ Better version control

---

### 2. **Follows Established Pattern**

Same structure as AmbitionAgent:
```python
class CountryStabilityAgent(BaseParameterAgent):
    def __init__(self, ...):
        self.scoring_rubric = self._load_scoring_rubric()
    
    def analyze(self, country, period) -> ParameterScore:
        # 1. Fetch data
        # 2. Calculate score
        # 3. Validate
        # 4. Generate justification
        # 5. Estimate confidence
        # 6. Return ParameterScore
```

**Consistency = Maintainability**

---

### 3. **Robust Fallback Mechanism**

```python
def _load_scoring_rubric(self):
    try:
        # Try to load from config
        return load_from_config()
    except Exception as e:
        logger.warning(f"Config failed: {e}")
        # Fallback to embedded rubric
        return self._get_fallback_rubric()
```

**Agent still works even if config is broken!**

---

### 4. **Comprehensive Logging**

```python
logger.info(f"Analyzing Country Stability for {country}")
logger.debug(f"Fetched mock data: {data}")
logger.debug(f"Score {score} assigned: ECR {ecr}")
logger.warning(f"No rubric match, defaulting to 5")
logger.error(f"Analysis failed: {e}", exc_info=True)
```

**Benefits:**
- Easy debugging
- Audit trail
- Production monitoring

---

### 5. **Type Safety with Type Hints**

```python
def analyze(
    self,
    country: str,           # Clear parameter types
    period: str,
    **kwargs
) -> ParameterScore:       # Clear return type
    pass
```

**Benefits:**
- IDE autocomplete
- Catch errors early
- Self-documenting

---

### 6. **Complete Documentation**

Every method has docstrings:
```python
def _calculate_score(self, data, country, period) -> float:
    """Calculate stability score based on ECR rating.
    
    Lower ECR = higher stability = higher score (inverse relationship)
    
    Args:
        data: Risk data with ecr_rating
        country: Country name
        period: Time period
        
    Returns:
        Score between 1-10
    """
```

---

### 7. **Three-Mode Architecture**

```python
if self.mode == AgentMode.MOCK:
    # Use mock data for testing
    return self.MOCK_DATA.get(country)

elif self.mode == AgentMode.RULE_BASED:
    # Query database (Phase 2)
    return self._query_database(country)

elif self.mode == AgentMode.AI_POWERED:
    # Use LLM (Phase 3)
    return self._llm_extract(country)
```

**Future-proof architecture!**

---

## 📊 Scoring Rubric (From Config)

| ECR Rating | Score | Risk Level | Description |
|------------|-------|------------|-------------|
| 0.0 - 1.0 | 10 | Extremely Low | Minimal risk |
| 1.0 - 2.0 | 9 | Very Low | Very stable |
| 2.0 - 3.0 | 8 | Low | Stable |
| 3.0 - 4.0 | 7 | Moderate | Moderately stable |
| 4.0 - 5.0 | 6 | Elevated | Fair stability |
| 5.0 - 6.0 | 5 | Significant | Moderate instability |
| 6.0 - 7.0 | 4 | High | Unstable |
| 7.0 - 8.0 | 3 | Very High | Very unstable |
| 8.0 - 9.0 | 2 | Severe | Extremely unstable |
| ≥ 9.0 | 1 | Extreme | Failed/fragile state |

---

## 🧪 Testing

### Quick Test
```bash
python -c "from src.agents.parameter_agents import analyze_country_stability; print(analyze_country_stability('Brazil').score)"
# Expected: 8.0
```

### Full Demo
```bash
python scripts/demo_country_stability_agent.py
```

### Python REPL
```python
from src.agents.parameter_agents import CountryStabilityAgent

agent = CountryStabilityAgent()

# Test different countries
for country in ["Germany", "Brazil", "India", "Nigeria"]:
    result = agent.analyze(country, "Q3 2024")
    print(f"{country}: {result.score}/10")
```

---

## 📈 Mock Data Included

```python
MOCK_DATA = {
    "Germany": {"ecr_rating": 0.8, "risk_category": "Extremely Stable"},
    "USA": {"ecr_rating": 1.2, "risk_category": "Very Stable"},
    "Brazil": {"ecr_rating": 2.3, "risk_category": "Stable"},
    "India": {"ecr_rating": 3.2, "risk_category": "Moderately Stable"},
    "Argentina": {"ecr_rating": 5.8, "risk_category": "Moderate Instability"},
    "Nigeria": {"ecr_rating": 6.2, "risk_category": "Unstable"},
    # ... 13 countries total
}
```

**Covers full range of risk levels!**

---

## 🔗 Integration with System

### Service Layer
```python
from src.agents.agent_service import agent_service

# Analyze single parameter
result = agent_service.analyze_parameter("country_stability", "Germany")

# Analyze subcategory (now includes ambition + country_stability)
result = agent_service.analyze_subcategory("regulation", "Brazil")
# Returns average of: Ambition (7.0) + Country Stability (8.0) = 7.5
```

### Registered in Agent Registry
```python
AGENT_REGISTRY = {
    "ambition": AmbitionAgent,
    "country_stability": CountryStabilityAgent,  # ✅ Registered
}
```

### Configuration File
```yaml
# config/parameters.yaml
parameters:
  country_stability:
    name: "Country Stability"
    subcategory: "regulation"
    scoring: [...]  # Complete rubric
```

---

## 🎯 Key Differences from Ambition Agent

### 1. **Inverse Relationship**

**Ambition:** Higher GW = Higher Score (direct)
```python
26.8 GW → Score 7
115 GW → Score 10
```

**Country Stability:** Lower ECR = Higher Score (inverse)
```python
ECR 2.3 → Score 8 (low risk = good)
ECR 6.2 → Score 4 (high risk = bad)
```

### 2. **Simpler Calculation**

**Ambition:** Requires summing multiple energy types
```python
total_gw = solar + onshore_wind + offshore_wind
```

**Country Stability:** Direct lookup
```python
ecr_rating = data.get("ecr_rating")
# Match to rubric
```

### 3. **Different Data Sources**

**Ambition:**
- Government NDCs
- Ministry publications
- IRENA statistics

**Country Stability:**
- Euromoney Country Risk (ECR)
- World Bank indicators
- Political Risk Services

---

## 🚀 Impact on Subcategories

### Before (Only Ambition)
```
Regulation Score = Ambition Score
USA: 10.0/10
```

### After (Ambition + Country Stability)
```
Regulation Score = (Ambition + Country Stability) / 2
USA: (10.0 + 9.0) / 2 = 9.5/10
```

**More nuanced scoring!**

---

## 💡 Usage Examples

### Example 1: Direct Usage
```python
from src.agents.parameter_agents import CountryStabilityAgent

agent = CountryStabilityAgent()
result = agent.analyze("Brazil", "Q3 2024")

print(f"Score: {result.score}/10")
print(f"Justification: {result.justification}")
# Output:
# Score: 8.0/10
# Justification: ECR rating of 2.3 indicates stable. Stable (low risk). 
# Political and economic environment supports renewable energy investments.
```

### Example 2: Convenience Function
```python
from src.agents.parameter_agents import analyze_country_stability

result = analyze_country_stability("Germany")
print(f"{result.parameter_name}: {result.score}/10")
# Output: Country Stability: 10.0/10
```

### Example 3: Batch Analysis
```python
countries = ["Germany", "Brazil", "India", "Nigeria"]
agent = CountryStabilityAgent()

for country in countries:
    result = agent.analyze(country, "Q3 2024")
    ecr = agent.MOCK_DATA[country]["ecr_rating"]
    print(f"{country}: ECR {ecr:.1f} → Score {result.score}/10")

# Output:
# Germany: ECR 0.8 → Score 10.0/10
# Brazil: ECR 2.3 → Score 8.0/10
# India: ECR 3.2 → Score 7.0/10
# Nigeria: ECR 6.2 → Score 4.0/10
```

### Example 4: Compare with Ambition
```python
from src.agents.parameter_agents import AmbitionAgent, CountryStabilityAgent

ambition = AmbitionAgent()
stability = CountryStabilityAgent()

country = "Brazil"
amb_result = ambition.analyze(country, "Q3 2024")
stab_result = stability.analyze(country, "Q3 2024")

print(f"{country}:")
print(f"  Ambition: {amb_result.score}/10 (26.8 GW target)")
print(f"  Stability: {stab_result.score}/10 (ECR 2.3)")
print(f"  Average: {(amb_result.score + stab_result.score) / 2:.1f}/10")

# Output:
# Brazil:
#   Ambition: 7.0/10 (26.8 GW target)
#   Stability: 8.0/10 (ECR 2.3)
#   Average: 7.5/10
```

---

## 🎓 What You Learned

By building this agent, you now understand:

✅ **Config-driven architecture** - No hardcoding  
✅ **Pattern replication** - Copy and adapt  
✅ **Inverse relationships** - Lower = Better scoring  
✅ **Multi-parameter subcategories** - Aggregation  
✅ **Fallback mechanisms** - Robustness  
✅ **Professional logging** - Production-ready  
✅ **Type safety** - Python best practices  
✅ **Comprehensive testing** - Demo scripts  

---

## 📋 Checklist for Next Agent

When building your third agent, follow this checklist:

- [ ] Add parameter to `config/parameters.yaml` with complete rubric
- [ ] Create agent file: `src/agents/parameter_agents/your_agent.py`
- [ ] Inherit from `BaseParameterAgent`
- [ ] Implement `_load_scoring_rubric()` method
- [ ] Implement `_get_fallback_rubric()` method
- [ ] Implement `analyze()` method
- [ ] Implement `_fetch_data()` method (MOCK mode)
- [ ] Implement `_calculate_score()` method (use rubric)
- [ ] Implement `_generate_justification()` method
- [ ] Add mock data for 10+ countries
- [ ] Register in `__init__.py`
- [ ] Update `agent_service.py` subcategory mapping
- [ ] Create demo script
- [ ] Test with quick command
- [ ] Run full demo
- [ ] Document in README

**Follow this checklist and building agents becomes mechanical!** ⚙️

---

## 🎊 Congratulations!

You've successfully built your **second parameter agent** following all best practices:

- ✅ Config-driven (no hardcoding)
- ✅ Follows established pattern
- ✅ Robust with fallbacks
- ✅ Comprehensive logging
- ✅ Type-safe
- ✅ Well-documented
- ✅ Fully tested

**19 more to go!** 🚀

---

## 🤔 Next Agent Suggestions

**Easy (2-3 hours):**
- Power Market Size - TWh consumption mapping
- Resource Availability - Solar irradiation + wind speed

**Medium (3-4 hours):**
- Support Scheme - Categorical analysis (FiT, auction, etc.)
- Track Record - Historical deployment analysis

**See `docs/AGENT_SYSTEM_GUIDE.md` for templates!**
