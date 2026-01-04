# 🤖 Phase 2: Parameter Agents - Getting Started

## ✅ What Was Just Built

You now have a **complete, working parameter agent system**!

### Files Created

```
src/agents/
├── base_agent.py                    # ✅ Abstract base class
├── parameter_agents/
│   ├── __init__.py                 # ✅ Agent registry
│   └── ambition_agent.py           # ✅ First complete agent
└── agent_service.py                 # ✅ Service layer

scripts/
└── demo_ambition_agent.py           # ✅ Interactive demo

docs/
└── AGENT_SYSTEM_GUIDE.md           # ✅ Complete documentation
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Run the Demo

```bash
# From project root
python scripts/demo_ambition_agent.py
```

**You'll see:**
- ✅ Direct agent usage examples
- ✅ Convenience function usage
- ✅ Service layer integration
- ✅ Scoring rubric visualization
- ✅ All mock countries comparison

### 2. Test in Python REPL

```python
from src.agents.parameter_agents import AmbitionAgent

# Create agent
agent = AmbitionAgent()

# Analyze a country
result = agent.analyze("Brazil", "Q3 2024")

# View results
print(f"Score: {result.score}/10")
print(f"Justification: {result.justification}")
print(f"Confidence: {result.confidence}")
```

### 3. Test via Service Layer

```python
from src.agents.agent_service import agent_service

# Analyze single parameter
result = agent_service.analyze_parameter("ambition", "Germany")

# Analyze subcategory (currently only has ambition)
subcat = agent_service.analyze_subcategory("regulation", "USA")

# Full country analysis (when more agents are implemented)
# ranking = agent_service.analyze_country("Brazil")
```

---

## 📊 What the Ambition Agent Does

### Purpose
Analyzes government renewable energy ambition based on targeted installed capacity (solar PV + onshore wind + offshore wind) by 2030.

### Input
```python
country = "Brazil"
period = "Q3 2024"
```

### Output
```python
ParameterScore(
    parameter_name="Ambition",
    score=7.0,  # 1-10 scale
    justification="26.8 GW of renewable capacity targeted by 2030 "
                  "(solar PV: 15.0 GW, onshore wind: 10.8 GW, "
                  "offshore wind: 1.0 GW). High targets.",
    data_sources=["Brazil NDC 2024", "IRENA Statistics", ...],
    confidence=0.8  # 0-1 scale
)
```

### Scoring Rubric

| Score | GW Range | Example Countries |
|-------|----------|-------------------|
| 1-3 | < 10 GW | Small nations |
| 4-6 | 10-25 GW | Medium economies |
| 7-8 | 25-35 GW | Brazil, Vietnam |
| 9-10 | > 35 GW | USA, China, Germany |

---

## 🏗️ Architecture Deep Dive

### Class Hierarchy

```
BaseParameterAgent (Abstract)
    ↓
AmbitionAgent (Concrete)
    ├─ SCORING_RUBRIC (10 levels)
    ├─ MOCK_DATA (10 countries)
    ├─ analyze() - Main entry point
    ├─ _fetch_data() - Data collection
    ├─ _calculate_score() - Apply rubric
    └─ _generate_justification() - Create explanation
```

### Execution Flow

```
User: agent.analyze("Brazil", "Q3 2024")
    ↓
1. _fetch_data()
    → Returns: {"total_gw": 26.8, "solar": 15.0, ...}
    ↓
2. _calculate_score()
    → Applies rubric: 26.8 GW → Score 7
    ↓
3. _validate_score()
    → Ensures 1-10 range
    ↓
4. _generate_justification()
    → Creates: "26.8 GW of renewable capacity..."
    ↓
5. _estimate_confidence()
    → Calculates: 0.8 (80% confident)
    ↓
6. Return ParameterScore
```

### Agent Modes

**Currently Implemented:**
```python
AgentMode.MOCK  # Uses MOCK_DATA dictionary
```

**Coming in Phase 2:**
```python
AgentMode.RULE_BASED   # Queries PostgreSQL database
AgentMode.AI_POWERED   # Uses LLM for extraction
```

---

## 🎯 Your Next Tasks

### Task 1: Understand the Code (30 minutes)

**Read these files in order:**
1. `src/agents/base_agent.py` - Base class (15 min)
2. `src/agents/parameter_agents/ambition_agent.py` - Implementation (10 min)
3. `src/agents/agent_service.py` - Integration (5 min)

**Key concepts to understand:**
- Abstract methods (`@abstractmethod`)
- Inheritance (`super().__init__()`)
- Type hints (`Dict[str, Any]`)
- Pydantic models (`ParameterScore`)
- Logging (`logger.info()`)

### Task 2: Modify Mock Data (15 minutes)

**Exercise:**
1. Open `src/agents/parameter_agents/ambition_agent.py`
2. Find the `MOCK_DATA` dictionary
3. Add a new country:

```python
MOCK_DATA = {
    # ... existing countries ...
    "France": {
        "total_gw": 73.0,
        "solar": 35.0,
        "onshore_wind": 33.0,
        "offshore_wind": 5.0
    }
}
```

4. Test it:
```python
from src.agents.parameter_agents import analyze_ambition

result = analyze_ambition("France")
print(f"France: {result.score}/10")  # Should be 8/10
```

### Task 3: Create Your Second Agent (2-3 hours)

**Choose one:**
- **Support Scheme** (Medium difficulty)
- **Track Record** (Medium difficulty)
- **Country Stability** (Easy - just uses ECR rating)

**Steps:**
1. Copy `ambition_agent.py` → `your_agent.py`
2. Update class name
3. Define scoring rubric
4. Add mock data
5. Implement `_calculate_score()`
6. Implement `_generate_justification()`
7. Register in `__init__.py`
8. Test!

**See** `docs/AGENT_SYSTEM_GUIDE.md` for detailed instructions.

---

## 🧪 Testing Your Agents

### Manual Testing

```python
# Test directly
from src.agents.parameter_agents import AmbitionAgent

agent = AmbitionAgent()

# Test scoring logic
data = {"total_gw": 27.0, "solar": 15, "onshore_wind": 11, "offshore_wind": 1}
score = agent._calculate_score(data, "Test Country", "Q3 2024")
assert score == 7.0

# Test justification
justification = agent._generate_justification(data, score, "Test", "Q3 2024")
assert "27.0 GW" in justification
```

### Unit Tests (Coming)

```bash
# Create tests/test_agents/test_ambition_agent.py
pytest tests/test_agents/
```

---

## 🔗 Integration with UI

### Current State

**UI → mock_service → Hardcoded Mock Data**

### Phase 2 Target

**UI → ranking_service → agent_service → Agents**

### How to Enable Agents

**Option 1: Direct Replacement**

Edit `src/services/mock_service.py`:

```python
from ..agents.agent_service import agent_service

class MockRankingService:
    def get_country_ranking(self, country, period):
        # OLD: Return hardcoded mock data
        # NEW: Use agents!
        return agent_service.analyze_country(country, period)
```

**Option 2: Configuration Toggle**

Edit `config/app_config.yaml`:

```yaml
system:
  mock_mode: false  # Enable agents
  agent_mode: "mock"
```

Then in service:
```python
if config['system']['mock_mode']:
    return mock_data
else:
    return agent_service.analyze_country(country)
```

---

## 📈 Roadmap: All 21 Agents

### Level I: Critical (11 agents)

**Regulation (5 agents):**
- ✅ Ambition (DONE)
- 🔄 Support Scheme
- 🔄 Track Record
- 🔄 Contract Terms
- 🔄 Country Stability

**Profitability (4 agents):**
- 🔄 Revenue Stream Stability
- 🔄 Offtaker Status
- 🔄 Expected Return
- 🔄 Long-Term Interest Rates

**Accommodation (2 agents):**
- 🔄 Status of Grid
- 🔄 Ownership Hurdles

### Level II: Important (6 agents)

**Market Size & Fundamentals (4 agents):**
- 🔄 Power Market Size
- 🔄 Resource Availability
- 🔄 Energy Dependence
- 🔄 Renewables Penetration

**Competition & Ease (2 agents):**
- 🔄 Ownership Consolidation
- 🔄 Competitive Landscape

### Level III: Modifiers (1 agents)

**System/External (1 agents, could be combined):**
- 🔄 Cannibalization
- 🔄 Curtailment
- 🔄 Queue Dynamics
- 🔄 Supply Chain

**Estimated Effort:**
- Simple agents (e.g., Country Stability): 1-2 hours
- Medium agents (e.g., Support Scheme): 2-4 hours
- Complex agents (e.g., Track Record): 4-6 hours

**Total:** ~60-80 hours for all 21 agents

---

## 💡 Tips & Best Practices

### 1. Start Simple
Build the simplest agents first (Country Stability, Power Market Size) to get comfortable with the pattern.

### 2. One Agent at a Time
Don't try to build multiple agents simultaneously. Complete one, test it, then move to the next.

### 3. Copy-Paste is OK
The agents are intentionally similar. Copy `ambition_agent.py` as your template.

### 4. Focus on Rubric
The hardest part is defining the scoring rubric. Get this right first.

### 5. Mock Data is Temporary
Don't spend too much time perfecting mock data. It's just for testing.

### 6. Test Incrementally
Test each method (`_fetch_data`, `_calculate_score`, etc.) individually.

### 7. Use Logging
Add `logger.debug()` statements to understand what's happening.

### 8. Read the Guide
`docs/AGENT_SYSTEM_GUIDE.md` has complete step-by-step instructions.

---

## 🎓 Learning Resources

### Key Concepts

**1. Abstract Base Classes**
```python
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def analyze(self):
        pass  # Must be implemented by subclasses
```

**2. Type Hints**
```python
def analyze(self, country: str) -> ParameterScore:
    # Returns ParameterScore object
    pass
```

**3. Pydantic Models**
```python
from pydantic import BaseModel

class ParameterScore(BaseModel):
    score: float  # Auto-validated
    justification: str
```

**4. Logging**
```python
from core.logger import get_logger

logger = get_logger(__name__)
logger.info("Analysis starting...")
```

### External Resources

- **Python Abstract Classes:** https://docs.python.org/3/library/abc.html
- **Type Hints:** https://docs.python.org/3/library/typing.html
- **Pydantic:** https://docs.pydantic.dev/
- **Loguru:** https://github.com/Delgan/loguru

---

## ❓ FAQ

**Q: Do I need LangChain for Phase 2?**  
A: No! Agents currently use simple Python logic. LangChain comes in Phase 3 for AI_POWERED mode.

**Q: Can I test agents without the UI?**  
A: Yes! Use the demo script or Python REPL.

**Q: What if I want to change the scoring rubric?**  
A: Just edit the `SCORING_RUBRIC` constant in the agent class.

**Q: How do I add more countries to mock data?**  
A: Add entries to the `MOCK_DATA` dictionary.

**Q: When should I switch from MOCK to RULE_BASED mode?**  
A: After implementing the database and data pipeline (Phase 2.2).

**Q: Can agents call other agents?**  
A: Yes, but avoid it. Keep agents independent. Use the service layer for orchestration.

**Q: How do I handle missing data?**  
A: Return default/conservative values and reduce confidence score.

---

## ✅ Success Checklist

After completing this phase, you should be able to:

- [ ] Run `python scripts/demo_ambition_agent.py` successfully
- [ ] Create a new parameter agent from scratch
- [ ] Explain how the BaseParameterAgent class works
- [ ] Modify scoring rubrics
- [ ] Add/modify mock data
- [ ] Test agents via Python REPL
- [ ] Understand the service layer integration
- [ ] Know the difference between agent modes

---

## 🚀 Ready to Build!

**You have everything you need:**
- ✅ Working example (AmbitionAgent)
- ✅ Base class to inherit from
- ✅ Service layer for integration
- ✅ Demo script to learn from
- ✅ Complete documentation

**Next steps:**
1. Run the demo script
2. Read the agent code
3. Create your second agent
4. Repeat 20 more times! 😄

**Questions?** Check `docs/AGENT_SYSTEM_GUIDE.md`

**Happy coding! 🎯**
