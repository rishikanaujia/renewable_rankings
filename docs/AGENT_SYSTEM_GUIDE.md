# 🤖 Parameter Agent System - Complete Guide

## 📚 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [The Ambition Agent (Example)](#ambition-agent)
4. [How Agents Work](#how-agents-work)
5. [Creating New Agents](#creating-new-agents)
6. [Integration with UI](#integration-with-ui)
7. [Testing](#testing)
8. [Best Practices](#best-practices)

---

## Overview

The Parameter Agent System is the heart of the renewable energy rankings platform. Each of the 21 parameters has a dedicated agent that:

1. **Fetches Data** - From various sources (APIs, databases, documents)
2. **Calculates Score** - Using predefined rubrics (1-10 scale)
3. **Generates Justification** - Explains the score with data points
4. **Estimates Confidence** - How confident is the agent in its score

---

## Architecture

```
User Request
    ↓
Agent Service (agent_service.py)
    ↓
Base Agent (base_agent.py) ← All agents inherit from this
    ↓
Parameter Agent (e.g., ambition_agent.py)
    ↓
    ├─→ Fetch Data
    ├─→ Calculate Score  
    ├─→ Generate Justification
    └─→ Return ParameterScore
```

### Key Components

**1. BaseParameterAgent** (`base_agent.py`)
- Abstract base class
- Defines interface all agents must implement
- Provides common utilities (validation, confidence estimation)

**2. Parameter Agents** (`parameter_agents/`)
- Concrete implementations for each parameter
- Currently: AmbitionAgent
- Coming: 20 more agents

**3. Agent Service** (`agent_service.py`)
- Coordinates agent execution
- Aggregates results into subcategories
- Calculates overall country score

**4. Agent Modes**
```python
AgentMode.MOCK         # Phase 1: Use mock data
AgentMode.RULE_BASED   # Phase 2: Use database + rules
AgentMode.AI_POWERED   # Phase 3: Use LLM for analysis
```

---

## Ambition Agent (Example)

The **Ambition Agent** analyzes government renewable energy targets.

### What It Measures

Total installed capacity targets (solar PV + onshore wind + offshore wind) by 2030 in GW.

### Scoring Rubric

| Score | GW Range | Description |
|-------|----------|-------------|
| 1 | < 3 | Minimal targets |
| 2 | 3-5 | Very low targets |
| 3 | 5-10 | Low targets |
| 4 | 10-15 | Below moderate |
| 5 | 15-20 | Moderate targets |
| 6 | 20-25 | Above moderate |
| 7 | 25-30 | High targets |
| 8 | 30-35 | Very high targets |
| 9 | 35-40 | Extremely high |
| 10 | ≥ 40 | World-class |

### Example Output

```python
from agents.parameter_agents import analyze_ambition

result = analyze_ambition("Brazil", "Q3 2024")

# Result:
# ParameterScore(
#     parameter_name="Ambition",
#     score=7.0,
#     justification="26.8 GW of renewable capacity targeted by 2030 
#                    (solar PV: 15.0 GW, onshore wind: 10.8 GW, 
#                    offshore wind: 1.0 GW). High targets.",
#     data_sources=["Brazil NDC 2024", "IRENA Statistics", ...],
#     confidence=0.8
# )
```

---

## How Agents Work

### Step-by-Step Execution

```python
# 1. Initialize Agent
agent = AmbitionAgent(mode=AgentMode.MOCK)

# 2. Call analyze()
result = agent.analyze(country="Brazil", period="Q3 2024")

# Internal Flow:
# ├─→ _fetch_data()           # Get target data
# ├─→ _calculate_score()      # Apply rubric
# ├─→ _validate_score()       # Ensure 1-10 range
# ├─→ _generate_justification()  # Create explanation
# ├─→ _estimate_confidence()  # Calculate confidence
# └─→ Return ParameterScore
```

### 1. Data Fetching (`_fetch_data`)

```python
def _fetch_data(self, country: str, period: str) -> Dict[str, Any]:
    """Fetch renewable energy targets."""
    if self.mode == AgentMode.MOCK:
        # Return mock data
        return self.MOCK_DATA.get(country, default_data)
    
    elif self.mode == AgentMode.RULE_BASED:
        # Query database
        return self._query_database(country, period)
    
    elif self.mode == AgentMode.AI_POWERED:
        # Use LLM to extract from documents
        return self._llm_extract(country, period)
```

**Phase 1 (Now):** Returns mock data from `MOCK_DATA` dictionary

**Phase 2 (Future):** Queries PostgreSQL database with real data

**Phase 3 (Future):** Uses LLM to extract from unstructured documents

### 2. Score Calculation (`_calculate_score`)

```python
def _calculate_score(self, data: Dict[str, Any], ...) -> float:
    """Calculate score using rubric."""
    total_gw = data.get("total_gw", 0)
    
    # Find matching rubric level
    for level in self.SCORING_RUBRIC:
        if level["min_gw"] <= total_gw < level["max_gw"]:
            return float(level["score"])
    
    return 1.0  # Fallback
```

**Key Points:**
- Pure deterministic logic (no randomness)
- Based on predefined rubric
- Always returns 1-10

### 3. Justification Generation (`_generate_justification`)

```python
def _generate_justification(self, data, score, country, period) -> str:
    """Create human-readable explanation."""
    total = data.get("total_gw", 0)
    solar = data.get("solar", 0)
    onshore = data.get("onshore_wind", 0)
    offshore = data.get("offshore_wind", 0)
    
    # Get description from rubric
    description = self._get_rubric_description(score)
    
    # Build justification
    return (
        f"{total} GW targeted by 2030 "
        f"(solar: {solar} GW, onshore wind: {onshore} GW, "
        f"offshore wind: {offshore} GW). {description}."
    )
```

**Key Points:**
- Includes specific data points
- References the score level
- Professional, concise language

### 4. Confidence Estimation (`_estimate_confidence`)

```python
def _estimate_confidence(self, data, data_quality="medium") -> float:
    """Estimate confidence in the score."""
    confidence_map = {
        "low": 0.6,      # Incomplete/uncertain data
        "medium": 0.8,   # Good quality data
        "high": 0.95     # Official, verified data
    }
    
    return confidence_map.get(data_quality, 0.8)
```

**Confidence Factors:**
- Data source quality (official vs unofficial)
- Data completeness
- Data recency
- Consistency across sources

---

## Creating New Agents

Follow these steps to create a new parameter agent:

### Step 1: Define the Parameter

**Example: Support Scheme Agent**

```yaml
# What it measures
Parameter: Support Scheme
Description: "Evaluation of support mechanisms for renewables"

# Scoring criteria
Scoring Rubric:
  1: No Support
  2: Emerging but Ineffective
  3: Forces Into Disadvantage
  ...
  10: Highly Mature

# Data sources
Data Sources:
  - Auction calendars
  - FiT schedules  
  - Policy documents
```

### Step 2: Create Agent File

**File:** `src/agents/parameter_agents/support_scheme_agent.py`

```python
"""Support Scheme Agent - Analyzes renewable energy support mechanisms."""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class SupportSchemeAgent(BaseParameterAgent):
    """Agent for analyzing support mechanisms."""
    
    # Define scoring rubric
    SCORING_RUBRIC = [
        {"score": 1, "level": "no_support", "description": "No Support"},
        {"score": 2, "level": "emerging", "description": "Emerging but Ineffective"},
        # ... add all 10 levels
    ]
    
    # Mock data for testing
    MOCK_DATA = {
        "Brazil": {"scheme_type": "auction", "maturity": "mature"},
        "Germany": {"scheme_type": "fit_auction", "maturity": "highly_mature"},
        # ... add more countries
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config=None):
        """Initialize Support Scheme Agent."""
        super().__init__(
            parameter_name="Support Scheme",
            mode=mode,
            config=config
        )
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze support scheme for a country."""
        try:
            logger.info(f"Analyzing Support Scheme for {country}")
            
            # 1. Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # 2. Calculate score
            score = self._calculate_score(data, country, period)
            score = self._validate_score(score)
            
            # 3. Generate justification
            justification = self._generate_justification(
                data, score, country, period
            )
            
            # 4. Estimate confidence
            confidence = self._estimate_confidence(data, "medium")
            
            # 5. Get data sources
            data_sources = self._get_data_sources(country)
            
            # Create result
            return ParameterScore(
                parameter_name=self.parameter_name,
                score=score,
                justification=justification,
                data_sources=data_sources,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            raise AgentError(f"Support Scheme analysis failed: {e}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch support scheme data."""
        if self.mode == AgentMode.MOCK:
            data = self.MOCK_DATA.get(country, {})
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        # TODO Phase 2: Implement database query
        raise NotImplementedError("RULE_BASED mode not yet implemented")
    
    def _calculate_score(self, data: Dict[str, Any], country: str, period: str) -> float:
        """Calculate score based on support mechanism."""
        scheme_type = data.get("scheme_type", "none")
        maturity = data.get("maturity", "emerging")
        
        # Implement your scoring logic here
        # This is simplified - real logic would be more complex
        
        if maturity == "highly_mature":
            return 10.0
        elif maturity == "mature":
            return 8.0
        elif maturity == "developing":
            return 5.0
        else:
            return 2.0
    
    def _generate_justification(
        self, data: Dict[str, Any], score: float, country: str, period: str
    ) -> str:
        """Generate justification."""
        scheme = data.get("scheme_type", "unknown")
        maturity = data.get("maturity", "unknown")
        
        # Customize based on your parameter
        return (
            f"{country} has a {maturity} {scheme} support mechanism. "
            f"Score reflects policy stability and effectiveness."
        )
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources."""
        return [
            f"{country} Renewable Energy Policy Database",
            "IRENA Policy Portal",
            "IEA Policies and Measures Database"
        ]
```

### Step 3: Register Agent

**File:** `src/agents/parameter_agents/__init__.py`

```python
from .ambition_agent import AmbitionAgent, analyze_ambition
from .support_scheme_agent import SupportSchemeAgent, analyze_support_scheme  # NEW

__all__ = [
    "AmbitionAgent",
    "analyze_ambition",
    "SupportSchemeAgent",      # NEW
    "analyze_support_scheme",  # NEW
]

AGENT_REGISTRY = {
    "ambition": AmbitionAgent,
    "support_scheme": SupportSchemeAgent,  # NEW
    # ... add more
}
```

### Step 4: Add Mock Data

Update `MOCK_DATA` dictionary with data for all test countries.

### Step 5: Test

```python
# Test directly
from agents.parameter_agents import SupportSchemeAgent

agent = SupportSchemeAgent()
result = agent.analyze("Brazil", "Q3 2024")
print(f"Score: {result.score}, Justification: {result.justification}")

# Test via service
from agents.agent_service import agent_service

result = agent_service.analyze_parameter("support_scheme", "Brazil")
print(f"Score: {result.score}")
```

---

## Integration with UI

The agent system integrates seamlessly with the existing UI through the **service layer**.

### Current Integration Point

**File:** `src/services/mock_service.py`

Currently uses hardcoded mock data. Replace with:

```python
from ..agents.agent_service import agent_service
from ..agents.base_agent import AgentMode

class RankingService:
    """Rankings service using real agents."""
    
    def __init__(self, use_agents: bool = False):
        self.use_agents = use_agents
        if use_agents:
            self.agent_service = agent_service
    
    def get_country_ranking(self, country: str, period: str):
        """Get country ranking."""
        if self.use_agents:
            # Use real agents!
            return self.agent_service.analyze_country(country, period)
        else:
            # Use mock data
            return self._get_mock_ranking(country, period)
```

### Gradual Migration Strategy

**Phase 1 (Current):** UI uses mock_service → Mock data

**Phase 1.5 (Next):** UI uses mock_service → Agents in MOCK mode

**Phase 2:** UI uses ranking_service → Agents in RULE_BASED mode

**Phase 3:** UI uses ranking_service → Agents in AI_POWERED mode

### Enable Agents in UI

**File:** `config/app_config.yaml`

```yaml
system:
  mock_mode: false  # Set to false to use agents
  agent_mode: "mock"  # Options: mock, rule, ai
```

---

## Testing

### Unit Tests

**File:** `tests/test_agents/test_ambition_agent.py`

```python
import pytest
from src.agents.parameter_agents import AmbitionAgent
from src.agents.base_agent import AgentMode

def test_ambition_agent_brazil():
    """Test Ambition agent for Brazil."""
    agent = AmbitionAgent(mode=AgentMode.MOCK)
    result = agent.analyze("Brazil", "Q3 2024")
    
    assert result.score == 7.0
    assert result.parameter_name == "Ambition"
    assert "26.8 GW" in result.justification
    assert result.confidence > 0

def test_ambition_agent_scoring_rubric():
    """Test scoring rubric logic."""
    agent = AmbitionAgent()
    
    # Test boundary cases
    data_low = {"total_gw": 2.5}
    assert agent._calculate_score(data_low, "Test", "Q3 2024") == 1.0
    
    data_high = {"total_gw": 45.0}
    assert agent._calculate_score(data_high, "Test", "Q3 2024") == 10.0
    
    data_mid = {"total_gw": 27.0}
    assert agent._calculate_score(data_mid, "Test", "Q3 2024") == 7.0
```

### Integration Tests

```python
def test_agent_service_integration():
    """Test agent service integration."""
    from src.agents.agent_service import agent_service
    
    result = agent_service.analyze_parameter("ambition", "Germany")
    assert result.score > 0
    assert result.score <= 10
```

### Run Tests

```bash
# Run all tests
pytest tests/test_agents/

# Run specific test
pytest tests/test_agents/test_ambition_agent.py::test_ambition_agent_brazil

# Run with coverage
pytest --cov=src/agents tests/test_agents/
```

---

## Best Practices

### 1. **Always Inherit from BaseParameterAgent**

```python
class MyAgent(BaseParameterAgent):  # ✅ Good
    pass

class MyAgent:  # ❌ Bad - doesn't inherit
    pass
```

### 2. **Define Scoring Rubric as Class Constant**

```python
class MyAgent(BaseParameterAgent):
    SCORING_RUBRIC = [...]  # ✅ Easy to review and modify
    
    def _calculate_score(self, data, country, period):
        # Use self.SCORING_RUBRIC
        pass
```

### 3. **Use Type Hints**

```python
def analyze(
    self,
    country: str,  # ✅ Clear types
    period: str
) -> ParameterScore:
    pass
```

### 4. **Log Everything**

```python
logger.info("Starting analysis...")
logger.debug(f"Fetched data: {data}")
logger.warning("Data quality low")
logger.error("Analysis failed", exc_info=True)
```

### 5. **Handle Errors Gracefully**

```python
try:
    result = self.analyze(country, period)
except Exception as e:
    logger.error(f"Analysis failed: {e}", exc_info=True)
    # Return placeholder or raise AgentError
    raise AgentError(f"Failed: {e}")
```

### 6. **Make Mock Data Realistic**

```python
MOCK_DATA = {
    "Brazil": {
        "total_gw": 26.8,  # Realistic
        "solar": 15.0,      # Sums to total
        "onshore_wind": 10.8,
        "offshore_wind": 1.0
    }
}
```

### 7. **Keep Agents Focused**

- One parameter per agent
- Single responsibility
- No cross-parameter dependencies

### 8. **Document Everything**

```python
"""Support Scheme Agent.

This agent analyzes renewable energy support mechanisms including:
- Feed-in Tariffs (FiT)
- Auctions
- Tax credits
- Subsidies

Scoring Rubric:
1: No support
...
10: Highly mature support
"""
```

---

## Summary

✅ **You Now Have:**
- Complete BaseParameterAgent class
- Working AmbitionAgent implementation
- Agent Service for coordination
- Demo script showing usage
- Clear pattern for creating 20 more agents

✅ **Next Steps:**
1. Run the demo script
2. Review the agent code
3. Create your second agent (Support Scheme)
4. Gradually replace mock_service with agents

✅ **The Pattern Works:**
- **Scalable** - 21 agents following same pattern
- **Maintainable** - Clear structure, well-documented
- **Testable** - Unit tests for each agent
- **Flexible** - 3 modes (mock/rule/ai)

**Ready to build the next 20 agents! 🚀**
