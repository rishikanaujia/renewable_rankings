## Integration Example: Country Stability Agent

This example shows how to integrate the `research_integration` package with the `CountryStabilityAgent`.

### Step 1: Import the Mixin and Parser

```python
# In src/agents/parameter_agents/country_stability_agent.py

from research_integration.mixins import ResearchIntegrationMixin
from research_integration.parsers import CountryStabilityParser
```

### Step 2: Add Mixin to Agent Class

```python
class CountryStabilityAgent(BaseParameterAgent, MemoryMixin, ResearchIntegrationMixin):
    """Agent for analyzing country stability based on political/economic risk.

    Now includes:
    - Memory system integration for learning from past analyses
    - Research system integration for using generated research documents
    """
```

### Step 3: Configure Parser in __init__

```python
def __init__(
    self,
    mode: AgentMode = AgentMode.MOCK,
    config: Dict[str, Any] = None,
    data_service = None
):
    super().__init__(
        parameter_name="Country Stability",
        mode=mode,
        config=config
    )

    self.data_service = data_service
    self.scoring_rubric = self._load_scoring_rubric()

    # Initialize memory system
    if MEMORY_AVAILABLE:
        self.init_memory()

    # Configure research parser
    self.research_parser = CountryStabilityParser()  # <-- ADD THIS

    logger.debug(f"Initialized CountryStabilityAgent with research integration")
```

### Step 4: Add Research Fallback in _fetch_data

```python
def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
    """Fetch country risk data.

    Data source hierarchy:
    1. DataService (real ECR data)
    2. Research System (research documents)
    3. MOCK data (fallback)
    """
    if self.mode == AgentMode.MOCK:
        return self._fetch_data_mock(country)

    elif self.mode == AgentMode.RULE_BASED:
        # Try data service first
        if self.data_service:
            try:
                ecr_rating = self.data_service.get_value(
                    country=country,
                    indicator='ecr',
                    default=None
                )

                if ecr_rating is not None:
                    risk_category = self._determine_risk_category(ecr_rating)
                    return {
                        'ecr_rating': float(ecr_rating),
                        'risk_category': risk_category,
                        'source': 'rule_based',
                        'period': period
                    }
            except Exception as e:
                logger.error(f"Error fetching from data service: {e}")

        # Fallback to research system
        research_data = self._fetch_data_from_research(country, period)  # <-- ADD THIS
        if research_data:
            return research_data

        # Final fallback to MOCK
        logger.warning(f"No data available for {country}, falling back to MOCK")
        return self._fetch_data_mock_fallback(country)

    # ... other modes ...
```

### Complete Example

Here's the complete modified `_fetch_data` method:

```python
def _fetch_data(
    self,
    country: str,
    period: str,
    **kwargs
) -> Dict[str, Any]:
    """Fetch country risk data with research integration.

    Data source hierarchy:
    1. MOCK: Mock data for testing
    2. RULE_BASED:
       a. DataService (real ECR data)
       b. Research System (LLM-generated research)
       c. MOCK fallback
    """
    if self.mode == AgentMode.MOCK:
        # Return mock data
        data = self.MOCK_DATA.get(country, None)
        if not data:
            logger.warning(f"No mock data for {country}, using default")
            data = {"ecr_rating": 5.0, "risk_category": "Moderate Instability"}

        data['source'] = 'mock'
        logger.debug(f"Fetched mock data for {country}: ECR={data.get('ecr_rating')}")
        return data

    elif self.mode == AgentMode.RULE_BASED:
        # Try data service first (highest priority)
        if self.data_service is None:
            logger.warning("No data_service available, trying research system")
        else:
            try:
                ecr_rating = self.data_service.get_value(
                    country=country,
                    indicator='ecr',
                    default=None
                )

                if ecr_rating is not None:
                    risk_category = self._determine_risk_category(ecr_rating)

                    data = {
                        'ecr_rating': float(ecr_rating),
                        'risk_category': risk_category,
                        'source': 'rule_based',
                        'period': period
                    }

                    logger.info(
                        f"Fetched REAL data for {country}: ECR={ecr_rating:.1f}, "
                        f"Category={risk_category}"
                    )

                    return data
            except Exception as e:
                logger.error(f"Error fetching from data service: {e}")

        # Try research system (second priority)
        research_data = self._fetch_data_from_research(country, period)
        if research_data:
            logger.info(f"Using research data for {country}")
            return research_data

        # Final fallback to MOCK (lowest priority)
        logger.warning(f"No real data or research available for {country}, falling back to MOCK")
        return self._fetch_data_mock_fallback(country)

    # ... other modes ...

def _fetch_data_mock_fallback(self, country: str) -> Dict[str, Any]:
    """Fallback to mock data when other sources fail."""
    data = self.MOCK_DATA.get(country, {
        "ecr_rating": 5.0,
        "risk_category": "Moderate Instability"
    })
    data['source'] = 'mock_fallback'
    logger.debug(f"Using mock fallback data for {country}")
    return data
```

### Step 5: Test the Integration

```python
#!/usr/bin/env python3
"""Test Country Stability Agent with Research Integration"""

from src.agents.parameter_agents.country_stability_agent import CountryStabilityAgent
from src.agents.base_agent import AgentMode

# Create agent
agent = CountryStabilityAgent(mode=AgentMode.RULE_BASED)

# Test with a country that has research
result = agent.analyze("China", "Q4 2024")

print(f"Score: {result.score}/10")
print(f"Justification: {result.justification}")
print(f"Data Sources: {result.data_sources}")
print(f"Confidence: {result.confidence}")

# Check research status
status = agent.get_research_status()
print(f"\nResearch Integration Status:")
print(f"  Enabled: {status['enabled']}")
print(f"  Orchestrator Available: {status['orchestrator_available']}")
print(f"  Parser Configured: {status['parser_configured']}")
print(f"  Parser Class: {status['parser_class']}")
```

Expected output:
```
Score: 8.0/10
Justification: Based on comprehensive research analysis (Ministry of Commerce):
ECR rating of 2.8 indicates Stable country (low risk). This places China in the
top tier for political and economic stability...

Data Sources: ['research', 'Ministry of Commerce', 'World Bank']
Confidence: 0.75

Research Integration Status:
  Enabled: True
  Orchestrator Available: True
  Parser Configured: True
  Parser Class: CountryStabilityParser
```

### What Changed?

1. **Added imports**: `ResearchIntegrationMixin` and `CountryStabilityParser`
2. **Updated class inheritance**: Added `ResearchIntegrationMixin`
3. **Configured parser**: Set `self.research_parser = CountryStabilityParser()` in `__init__`
4. **Added fallback**: Call `self._fetch_data_from_research()` in `_fetch_data` method

### Benefits

✅ **Clean separation**: Parser logic separate from agent logic
✅ **Reusable**: Same mixin works for all 18 agents
✅ **Type-safe**: Each parser returns parameter-specific data structure
✅ **Testable**: Can test parsers independently from agents
✅ **Maintainable**: Easy to update parser logic without touching agents
✅ **Backward compatible**: Doesn't break existing code, just adds fallback

### Next Steps

Repeat this process for the remaining 16 agents:
1. Import mixin and appropriate parser
2. Add mixin to class inheritance
3. Configure parser in `__init__`
4. Add research fallback in `_fetch_data`

Each agent takes ~5 minutes to integrate!
