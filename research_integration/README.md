# Research Integration Package

A modular, extensible package for integrating research system data with parameter agents.

## Architecture

```
research_integration/
├── base.py                      # Base research integration class
├── parsers/                     # Parameter-specific metric parsers
│   ├── base_parser.py          # Abstract parser base class
│   ├── regulation_parsers.py   # Regulation parameters (5)
│   ├── profitability_parsers.py# Profitability parameters (4)
│   ├── market_parsers.py       # Market fundamentals (4)
│   ├── accommodation_parsers.py# Accommodation parameters (2)
│   ├── competition_parsers.py  # Competition parameters (2)
│   └── system_modifiers_parser.py # System modifiers (1)
├── mixins/                      # Mixin for agent integration
│   └── research_mixin.py       # ResearchIntegrationMixin
└── tests/                       # Unit tests
```

## Design Principles

### 1. Separation of Concerns
- **Base class**: Handles research fetching, caching, error handling
- **Parsers**: Extract parameter-specific metrics from research
- **Mixin**: Provides integration interface for agents

### 2. Extensibility
- Adding new parameter = create new parser class
- All parsers inherit from `BaseParser`
- Consistent interface across all parameters

### 3. Type Safety
- Each parser returns typed data dictionary
- Clear contracts between research system and agents

## Usage

### For Agent Developers

```python
from research_integration.mixins import ResearchIntegrationMixin
from research_integration.parsers.regulation_parsers import CountryStabilityParser

class CountryStabilityAgent(BaseParameterAgent, ResearchIntegrationMixin):
    def __init__(self, mode, config=None, data_service=None):
        super().__init__(parameter_name="Country Stability", mode=mode, config=config)

        # Set the parser for this agent
        self.research_parser = CountryStabilityParser()

    def _fetch_data(self, country, period):
        if self.mode == AgentMode.RULE_BASED:
            # Try data service first
            if self.data_service:
                data = self._try_data_service(country)
                if data:
                    return data

            # Fallback to research
            research_data = self._fetch_data_from_research(country, period)
            if research_data:
                return research_data

            # Final fallback to MOCK
            return self._fetch_data_mock_fallback(country)
```

### For Parser Developers

```python
from research_integration.parsers.base_parser import BaseParser

class MyParameterParser(BaseParser):
    """Parser for MyParameter research documents."""

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract MyParameter-specific metrics from research.

        Returns:
            Dict with parameter-specific data structure
        """
        metrics = research_doc.content.get('key_metrics', [])

        # Extract relevant metrics
        my_value = self._extract_my_metric(metrics)

        return {
            'my_metric': my_value,
            'source': 'research',
            'confidence': research_doc.content.get('confidence', 0.0),
            'version': research_doc.version
        }

    def _extract_my_metric(self, metrics):
        # Parameter-specific logic
        pass
```

## Parameter Parsers

### Regulation (5 parameters)
- **AmbitionParser**: Extracts GW capacity targets (solar, wind, total)
- **CountryStabilityParser**: Extracts ECR ratings and risk indicators
- **TrackRecordParser**: Extracts project completion rates, historical performance
- **SupportSchemeParser**: Extracts policy incentives, subsidies, feed-in tariffs
- **ContractTermsParser**: Extracts PPA terms, contract durations, pricing structures

### Profitability (4 parameters)
- **ExpectedReturnParser**: Extracts IRR, ROE, return metrics
- **RevenueStreamStabilityParser**: Extracts revenue volatility, contract coverage
- **OfftakerStatusParser**: Extracts offtaker creditworthiness, payment history
- **LongTermInterestRatesParser**: Extracts benchmark rates, cost of capital

### Market Size & Fundamentals (4 parameters)
- **PowerMarketSizeParser**: Extracts electricity demand (TWh), growth rates
- **ResourceAvailabilityParser**: Extracts solar irradiation, wind speeds, capacity factors
- **EnergyDependenceParser**: Extracts import dependency ratios, energy security metrics
- **RenewablesPenetrationParser**: Extracts renewable share, growth trends

### Accommodation (2 parameters)
- **StatusOfGridParser**: Extracts grid capacity, interconnection costs, reliability
- **OwnershipHurdlesParser**: Extracts land ownership complexity, permitting timelines

### Competition & Ease (2 parameters)
- **OwnershipConsolidationParser**: Extracts market concentration, HHI index
- **CompetitiveLandscapeParser**: Extracts number of competitors, barriers to entry

### System Modifiers (1 parameter)
- **SystemModifiersParser**: Extracts composite modifiers and adjustment factors

## Benefits

### For Agents
✅ Simple integration via mixin
✅ Automatic fallback hierarchy (DataService → Research → MOCK)
✅ No need to understand research system internals
✅ Type-safe data contracts

### For Research System
✅ Decoupled from agent implementation
✅ Single responsibility: generate research
✅ Easy to test and improve

### For Maintainability
✅ Parameter-specific logic isolated in parsers
✅ Easy to add new parameters
✅ Clear testing boundaries
✅ Reusable across different agent implementations

## Testing

```bash
# Test all parsers
pytest research_integration/tests/test_parsers.py

# Test specific parser
pytest research_integration/tests/test_parsers.py::TestAmbitionParser

# Test integration
pytest research_integration/tests/test_integration.py
```

## Development Workflow

1. **Research Generated**: Use `research_system/generate_all_research.py`
2. **Parser Development**: Create parser in appropriate file
3. **Parser Testing**: Write unit tests for parser
4. **Agent Integration**: Add mixin to agent, set parser
5. **End-to-End Testing**: Test full agent analysis with research

## Version History

- v1.0.0: Initial package with all 18 parameter parsers
