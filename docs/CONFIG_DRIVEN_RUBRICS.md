# ✅ Config-Driven Scoring Rubrics

## 🎯 Architecture Principle

**Design Philosophy:** All scoring rubrics are defined in configuration files, not hardcoded in agent source code.

**Current Implementation:** All 18 parameter agents load their scoring rubrics from `config/parameters.yaml` at initialization.

**Why This Matters:**
- ✅ Honors DRY (Don't Repeat Yourself) principle
- ✅ Single source of truth for all scoring logic
- ✅ Changes require editing only one file
- ✅ Domain experts can review/modify rubrics without reading Python code
- ✅ Configuration-driven architecture throughout the system

**Implementation Status:** Fully implemented across all 18 parameter agents as of v11 branch.

---

## ✅ The Solution

**Design:** All 18 parameter agents load scoring rubrics from `config/parameters.yaml` at initialization using a standardized `_load_scoring_rubric()` method.

### How It Works (Current Implementation)

**All parameter agents follow this pattern:**

```python
class AmbitionAgent(BaseParameterAgent):
    """Agent for analyzing government renewable energy ambition."""

    def __init__(
        self,
        mode: AgentMode = AgentMode.MOCK,
        config: Dict[str, Any] = None,
        data_service = None
    ):
        super().__init__(
            parameter_name="Ambition",
            mode=mode,
            config=config
        )

        # Store data service for RULE_BASED mode
        self.data_service = data_service

        # Load scoring rubric from config (NO HARDCODING!)
        self.scoring_rubric = self._load_scoring_rubric()

        logger.debug(
            f"Initialized AmbitionAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )

    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.

        Returns:
            List of scoring levels
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()

            # Get rubric for ambition parameter
            ambition_config = params_config['parameters'].get('ambition', {})
            scoring = ambition_config.get('scoring', [])

            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_gw": item.get('min_gw', 0),
                        "max_gw": item.get('max_gw', 10000),
                        "range": item['range'],
                        "description": item['description']
                    })

                logger.debug(f"Converted {len(rubric)} rubric levels from config")
                return rubric
            else:
                logger.warning("No scoring rubric in config, using fallback")
                return self._get_fallback_rubric()

        except Exception as e:
            logger.warning(f"Could not load rubric from config: {e}. Using fallback.")
            return self._get_fallback_rubric()
```

**File Location:** `src/agents/parameter_agents/ambition_agent.py:88-138`

---

## 📊 Configuration Format

### config/parameters.yaml

The configuration file defines all 21 parameters (18 active parameter agents) with complete scoring rubrics.

**Example 1: Ambition Agent (GW-based thresholds)**

```yaml
parameters:
  ambition:
    name: "Ambition"
    subcategory: "regulation"
    level: 1
    description: "Government renewable energy targets for solar PV + onshore wind + offshore wind in GW by 2030"
    scoring:
      - value: 1
        min_gw: 0
        max_gw: 3
        range: "< 3 GW"
        description: "Minimal renewable targets"
      - value: 2
        min_gw: 3
        max_gw: 5
        range: "3 – 4.99 GW"
        description: "Very low targets"
      # ... levels 3-9 ...
      - value: 10
        min_gw: 40
        max_gw: 10000
        range: "> 40 GW"
        description: "World-class targets"
    data_sources:
      - "Government NDCs"
      - "Ministry of Energy publications"
      - "IRENA country profiles"
```

**Example 2: Country Stability Agent (ECR-based rating)**

```yaml
  country_stability:
    name: "Country Stability"
    subcategory: "regulation"
    level: 1
    description: "Political and economic risk assessment based on Euromoney Country Risk (ECR) rating"
    scoring:
      - value: 10
        min_ecr: 0.0
        max_ecr: 1.0
        range: "< 1.0"
        description: "Extremely stable (minimal risk)"
      - value: 9
        min_ecr: 1.0
        max_ecr: 2.0
        range: "1.0 – 1.99"
        description: "Very stable (very low risk)"
      # ... levels 8-2 ...
      - value: 1
        min_ecr: 9.0
        max_ecr: 100.0
        range: "≥ 9.0"
        description: "Failed/fragile state (extreme risk)"
    data_sources:
      - "Euromoney Country Risk (ECR)"
```

**Key Fields:**
- `name`: Parameter display name
- `subcategory`: Parent category (regulation, profitability, accommodation, market, competition, modifiers)
- `level`: Hierarchy level (1 for parameter agents)
- `description`: What the parameter measures
- `scoring`: Array of 10 scoring levels (1-10 scale)
  - `value`: Score value (1-10)
  - Threshold fields: `min_gw`/`max_gw`, `min_ecr`/`max_ecr`, etc. (parameter-specific)
  - `range`: Human-readable range
  - `description`: Score interpretation
- `data_sources`: List of data source names

---

## 🎁 Benefits of Config-Driven Approach

### 1. **Single Source of Truth**
```
✅ Change rubric in ONE place → config/parameters.yaml
❌ OLD: Change in config AND agent code
```

### 2. **No Code Changes Needed**
```yaml
# Want to adjust thresholds? Just edit YAML:
- value: 7
  min_gw: 25    # Changed from 25
  max_gw: 32    # Changed from 30
```

### 3. **Domain Experts Can Modify**
```
Non-programmers can:
✅ Review rubrics in YAML
✅ Suggest changes to YAML
✅ Test different thresholds
❌ OLD: Had to read Python code
```

### 4. **Version Control**
```bash
git diff config/parameters.yaml

# Shows exactly what changed:
- min_gw: 25
+ min_gw: 22
```

### 5. **Environment-Specific Configs**
```bash
config/
├── parameters.yaml           # Default
├── parameters.dev.yaml       # Relaxed thresholds for testing
├── parameters.prod.yaml      # Strict production thresholds
```

### 6. **Consistency Across All 18 Agents**

**Every parameter agent implements the exact same pattern:**

```python
# Pattern implemented in ALL 18 parameter agents:
# 1. Ambition Agent
# 2. Country Stability Agent
# 3. Power Market Size Agent
# 4. Resource Availability Agent
# 5. Energy Dependence Agent
# 6. Renewables Penetration Agent
# 7. Expected Return Agent
# 8. Revenue Stream Stability Agent
# 9. Offtaker Status Agent
# 10. Long Term Interest Rates Agent
# 11. Track Record Agent
# 12. Status of Grid Agent
# 13. Ownership Hurdles Agent
# 14. Support Scheme Agent
# 15. Contract Terms Agent
# 16. Ownership Consolidation Agent
# 17. Competitive Landscape Agent
# 18. System Modifiers Agent

class AnyParameterAgent(BaseParameterAgent):
    def __init__(self, mode: AgentMode = AgentMode.MOCK, ...):
        super().__init__(...)
        # Consistent across all 18 agents
        self.scoring_rubric = self._load_scoring_rubric()

    def _load_scoring_rubric(self):
        # Same method signature and structure
        # Only difference: parameter name in config lookup
        pass
```

**Verified Implementation:**
All 18 agents have `_load_scoring_rubric()` method (verified via `grep -r "_load_scoring_rubric" src/agents/parameter_agents/`)

---

## 🛡️ Robustness: Fallback Mechanism

**All agents include a fallback rubric** to ensure they work even if the config file is unavailable or malformed.

**Implementation Pattern (from actual codebase):**

```python
def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
    """Load scoring rubric from configuration."""
    try:
        from ...core.config_loader import config_loader
        params_config = config_loader.get_parameters()

        # Get rubric for this parameter
        param_config = params_config['parameters'].get('parameter_name', {})
        scoring = param_config.get('scoring', [])

        if scoring:
            logger.info("Loaded scoring rubric from config/parameters.yaml")
            # Convert config format to internal format
            return self._convert_rubric(scoring)
        else:
            logger.warning("No scoring rubric in config, using fallback")
            return self._get_fallback_rubric()

    except Exception as e:
        logger.warning(f"Could not load rubric from config: {e}. Using fallback.")
        return self._get_fallback_rubric()


def _get_fallback_rubric(self) -> List[Dict[str, Any]]:
    """Fallback scoring rubric if config is not available.

    This ensures agent works even without full config.

    Returns:
        Default scoring rubric
    """
    return [
        {"score": 1, "min_gw": 0, "max_gw": 3, "range": "< 3 GW", "description": "Minimal"},
        # ... all 10 levels ...
        {"score": 10, "min_gw": 40, "max_gw": 10000, "range": "≥ 40 GW", "description": "World-class"}
    ]
```

**File Reference:** `src/agents/parameter_agents/ambition_agent.py:125-144`

**Why This Matters:**
- ✅ Agent works during development even without config
- ✅ Agent works in unit tests (no config dependency)
- ✅ Agent works if config has syntax errors
- ✅ Fails gracefully with warning (logged via Loguru)
- ✅ Enables iterative development without breaking existing code

**Logging Example:**
```
WARNING | Could not load rubric from config: FileNotFoundError. Using fallback.
INFO    | AmbitionAgent initialized with 10 scoring levels (fallback mode)
```

---

## 🔄 Implementation Guide for New Parameter Agents

**Status:** All 18 existing parameter agents already implement this pattern. Use this guide when adding new parameter agents.

### Step 1: Define Scoring Rubric in config/parameters.yaml

Add complete 10-level rubric for your new parameter:

```yaml
parameters:
  your_new_parameter:
    name: "Your New Parameter"
    subcategory: "regulation"  # or profitability, accommodation, market, competition, modifiers
    level: 1
    description: "What this parameter measures and how"
    scoring:
      - value: 1
        min_threshold: 0        # Use parameter-appropriate field names
        max_threshold: 10
        range: "< 10"
        description: "Low performance"
      - value: 2
        min_threshold: 10
        max_threshold: 20
        range: "10-20"
        description: "Below moderate"
      # ... add all 10 levels (scores 1-10) ...
      - value: 10
        min_threshold: 90
        max_threshold: 100
        range: ">= 90"
        description: "Excellent performance"
    data_sources:
      - "Primary data source"
      - "Secondary data source"
```

**Important:** Threshold field names should be parameter-specific (e.g., `min_gw`/`max_gw`, `min_ecr`/`max_ecr`, `min_percent`/`max_percent`).

### Step 2: Create Agent Class Following Standard Pattern

```python
from typing import Dict, Any, List, Optional
from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class YourNewParameterAgent(BaseParameterAgent):
    """Agent for analyzing [parameter description]."""

    # Mock data for testing
    MOCK_DATA = {
        "Germany": {"your_metric": 85.0},
        "USA": {"your_metric": 72.0},
        # ... more countries
    }

    def __init__(
        self,
        mode: AgentMode = AgentMode.MOCK,
        config: Dict[str, Any] = None,
        data_service = None
    ):
        """Initialize Your New Parameter Agent."""
        super().__init__(
            parameter_name="Your New Parameter",
            mode=mode,
            config=config
        )

        self.data_service = data_service

        # CRITICAL: Load scoring rubric from config
        self.scoring_rubric = self._load_scoring_rubric()

        logger.debug(
            f"Initialized YourNewParameterAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
```

### Step 3: Implement _load_scoring_rubric() Method

```python
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.

        Returns:
            List of scoring levels
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()

            # Get rubric for your parameter (use config key)
            param_config = params_config['parameters'].get('your_new_parameter', {})
            scoring = param_config.get('scoring', [])

            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_threshold": item.get('min_threshold', 0),
                        "max_threshold": item.get('max_threshold', 100),
                        "range": item['range'],
                        "description": item['description']
                    })

                logger.debug(f"Converted {len(rubric)} rubric levels from config")
                return rubric
            else:
                logger.warning("No scoring rubric in config, using fallback")
                return self._get_fallback_rubric()

        except Exception as e:
            logger.warning(f"Could not load rubric from config: {e}. Using fallback.")
            return self._get_fallback_rubric()
```

### Step 4: Implement Fallback Rubric

```python
    def _get_fallback_rubric(self) -> List[Dict[str, Any]]:
        """Fallback scoring rubric if config is not available.

        Returns:
            Default scoring rubric
        """
        return [
            {"score": 1, "min_threshold": 0, "max_threshold": 10, "range": "< 10", "description": "Low"},
            {"score": 2, "min_threshold": 10, "max_threshold": 20, "range": "10-20", "description": "Below moderate"},
            # ... all 10 levels ...
            {"score": 10, "min_threshold": 90, "max_threshold": 100, "range": ">= 90", "description": "Excellent"}
        ]
```

### Step 5: Use self.scoring_rubric in Scoring Logic

```python
    def _calculate_score(self, data: Dict[str, Any], country: str, period: str) -> float:
        """Calculate score using loaded rubric."""
        metric_value = data.get('your_metric', 0)

        # Iterate through loaded rubric to find matching range
        for level in self.scoring_rubric:
            if level['min_threshold'] <= metric_value < level['max_threshold']:
                logger.info(
                    f"{country}: {metric_value} falls in range {level['range']} "
                    f"→ Score {level['score']}"
                )
                return float(level['score'])

        # Default to lowest score if no match
        logger.warning(f"{country}: {metric_value} outside all ranges, defaulting to score 1")
        return 1.0
```

### Step 6: Register Agent

Add to `src/agents/parameter_agents/__init__.py`:

```python
from .your_new_parameter_agent import YourNewParameterAgent

AGENT_REGISTRY = {
    # ... existing agents ...
    "your_new_parameter": YourNewParameterAgent,
}
```

---

## 🧪 Testing

### Test Config Loading

```python
def test_rubric_loaded_from_config():
    agent = AmbitionAgent()
    
    # Should load 10 levels
    assert len(agent.scoring_rubric) == 10
    
    # Check first level
    assert agent.scoring_rubric[0]['score'] == 1
    assert agent.scoring_rubric[0]['min_gw'] == 0
    assert agent.scoring_rubric[0]['max_gw'] == 3
```

### Test Fallback Mechanism

```python
def test_rubric_fallback_on_config_error():
    # Simulate config error
    with patch('config_loader.get_parameters', side_effect=Exception("Config error")):
        agent = AmbitionAgent()
        
        # Should still have rubric (fallback)
        assert len(agent.scoring_rubric) > 0
```

### Test Scoring Still Works

```python
def test_scoring_with_loaded_rubric():
    agent = AmbitionAgent()
    
    data = {"total_gw": 27.0}
    score = agent._calculate_score(data, "Test", "Q3 2024")
    
    # 27 GW should score 7 (25-30 range)
    assert score == 7.0
```

---

## 📈 Impact Summary

### Without Config-Driven Approach (Hypothetical)
```
To change a scoring rubric:
1. Edit config/parameters.yaml
2. Edit parameter_agent.py (SCORING_RUBRIC constant)
3. Ensure both definitions match exactly
4. Test agent with both config and hardcoded rubric
5. Risk of inconsistency between two sources

Risk: High (two sources of truth) ⚠️
Effort: High (multiple files to update) 😓
Maintenance: Difficult (domain experts need to read Python)
```

### With Config-Driven Approach (Current Implementation)
```
To change a scoring rubric:
1. Edit config/parameters.yaml
2. Test (rubric loads automatically)

Risk: None (single source of truth) ✅
Effort: Minimal (one file edit) 😊
Maintenance: Easy (domain experts can review YAML) 🎯
```

**Real-World Example:**

To adjust Country Stability scoring thresholds from ECR 4.0-5.0 (score 6) to ECR 4.0-4.5:

```yaml
# config/parameters.yaml - ONLY file to edit
  - value: 6
    min_ecr: 4.0
    max_ecr: 4.5  # Changed from 5.0
    range: "4.0 – 4.49"  # Updated range
    description: "Fair stability (elevated risk)"
```

**No Python code changes needed!** The agent automatically uses the new thresholds on next initialization.

---

## 🎯 Best Practice Established

**All 18 parameter agents consistently implement:**

✅ **Load rubrics from config** - `self.scoring_rubric = self._load_scoring_rubric()` in `__init__`
✅ **Have fallback mechanism** - `_get_fallback_rubric()` ensures robustness
✅ **Never hardcode scoring logic** - All scoring data lives in `config/parameters.yaml`
✅ **Follow this pattern identically** - Same method signatures across all agents

**Verified Agents (18/18):**
1. ✅ Ambition Agent
2. ✅ Country Stability Agent
3. ✅ Power Market Size Agent
4. ✅ Resource Availability Agent
5. ✅ Energy Dependence Agent
6. ✅ Renewables Penetration Agent
7. ✅ Expected Return Agent
8. ✅ Revenue Stream Stability Agent
9. ✅ Offtaker Status Agent
10. ✅ Long Term Interest Rates Agent
11. ✅ Track Record Agent
12. ✅ Status of Grid Agent
13. ✅ Ownership Hurdles Agent
14. ✅ Support Scheme Agent
15. ✅ Contract Terms Agent
16. ✅ Ownership Consolidation Agent
17. ✅ Competitive Landscape Agent
18. ✅ System Modifiers Agent

**This creates:**
- ✨ Easier maintenance (edit one file, not 18+ agents)
- 🤝 Better collaboration (domain experts can review/modify YAML)
- 🧹 Cleaner code (agents focus on logic, not rubric data)
- 📍 Single source of truth (config is canonical)
- 📜 Version-controlled rubrics (git tracks all changes)
- 🔧 Environment-specific configs (dev/staging/prod rubrics)

---

## ✨ Conclusion

**Current Architecture:** Config-Driven Scoring System

All 18 parameter agents load their 10-level scoring rubrics from `config/parameters.yaml` at initialization. This architecture ensures:

**Single Source of Truth:**
```yaml
# config/parameters.yaml - ONLY place rubrics are defined
parameters:
  ambition:
    scoring:
      - value: 7
        min_gw: 25
        max_gw: 30
        range: "25 – 29.99 GW"
        description: "High targets"
```

**No Hardcoded Rubrics:**
```python
# src/agents/parameter_agents/ambition_agent.py
# ❌ No SCORING_RUBRIC constant
# ✅ Loaded dynamically from config
self.scoring_rubric = self._load_scoring_rubric()
```

**Benefits Realized:**
- 🎯 Maintainable: Update rubrics without touching Python code
- 🔍 Transparent: All scoring logic visible in configuration
- 🏗️ Professional: Industry-standard configuration-driven design
- 🚀 Scalable: Easy to add new parameters or adjust thresholds
- 📊 Auditable: Git history shows all rubric changes

---

## 📁 Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `config/parameters.yaml` | All 21 parameter definitions with scoring rubrics | 2000+ |
| `src/core/config_loader.py` | YAML configuration loading service | ~150 |
| `src/agents/parameter_agents/*.py` | 18 agents implementing `_load_scoring_rubric()` | ~600-1000 each |
| `src/agents/base_agent.py` | Base class defining agent interface | ~214 |

---

**This design pattern is now the established standard for all parameter agents in the renewable_rankings project.** 🎉

---

## 🔍 Parameter-Specific Threshold Examples

Different parameters use different threshold field names to match their domain:

| Parameter | Threshold Fields | Example Range | Score |
|-----------|-----------------|---------------|-------|
| Ambition | `min_gw`, `max_gw` | 25-30 GW | 7 |
| Country Stability | `min_ecr`, `max_ecr` | 2.0-3.0 ECR | 8 |
| Power Market Size | `min_twh`, `max_twh` | 300-500 TWh | 6 |
| Resource Availability | `min_quality`, `max_quality` | 7.0-8.0 (quality index) | 7 |
| Energy Dependence | `min_percent`, `max_percent` | 30-40% imports | 5 |
| Renewables Penetration | `min_share`, `max_share` | 20-30% renewables | 6 |
| Expected Return | `min_irr`, `max_irr` | 8-10% IRR | 7 |
| Long-Term Interest Rates | `min_rate`, `max_rate` | 3-4% yield | 6 |

**Key Insight:** The config-driven approach supports any threshold type by using parameter-specific field names in the YAML configuration.

---

## 📋 Quick Reference for Developers

### To Update a Scoring Rubric

1. Open `config/parameters.yaml`
2. Find your parameter section
3. Modify the `scoring` array
4. Save (no code changes needed)
5. Restart application (rubric loads automatically)

### To Add a New Parameter Agent

1. Add parameter definition to `config/parameters.yaml` with 10-level `scoring` array
2. Create agent class inheriting from `BaseParameterAgent`
3. Implement `_load_scoring_rubric()` method (copy from existing agent)
4. Implement `_get_fallback_rubric()` method
5. Register in `src/agents/parameter_agents/__init__.py`

### To Verify Rubric Loading

Check logs during agent initialization:
```
INFO | Loaded scoring rubric from config/parameters.yaml
DEBUG | Converted 10 rubric levels from config
DEBUG | Initialized AmbitionAgent in mock mode with 10 scoring levels
```

### To Debug Configuration Issues

If rubric fails to load:
```
WARNING | Could not load rubric from config: [error details]. Using fallback.
```

Check:
1. `config/parameters.yaml` exists and is valid YAML
2. Parameter key matches config lookup (e.g., `'ambition'`)
3. All required fields present (`value`, threshold fields, `range`, `description`)

---

## 📚 Related Documentation

- **Project Overview:** `docs/PROJECT_SUMMARY.md`
- **Agent System Guide:** `docs/PHASE2_README.md`
- **Parameter Agents Documentation:** `docs/parameters_agent_doc/`
- **Configuration Files:** `config/parameters.yaml`, `config/weights.yaml`
- **Base Agent Implementation:** `src/agents/base_agent.py`

---

**Last Updated:** v11 branch (2025)
**Implementation Status:** ✅ Complete (18/18 parameter agents)
