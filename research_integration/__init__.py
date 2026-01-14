"""Research Integration Package - Bridge between Research System and Agents.

This package provides a clean, modular interface for integrating research system
data with parameter agents.

Architecture:
- parsers/: Parameter-specific metric extractors (18 parsers, one per parameter)
- mixins/: ResearchIntegrationMixin for agent integration
- tests/: Unit tests for parsers and integration

Usage Example:
    from research_integration.mixins import ResearchIntegrationMixin
    from research_integration.parsers import CountryStabilityParser

    class CountryStabilityAgent(BaseParameterAgent, ResearchIntegrationMixin):
        def __init__(self, mode, config=None, data_service=None):
            super().__init__(parameter_name="Country Stability", mode=mode, config=config)

            # Configure research parser
            self.research_parser = CountryStabilityParser()

        def _fetch_data(self, country, period):
            # Try research as fallback
            research_data = self._fetch_data_from_research(country, period)
            if research_data:
                return research_data
            # ... other fallbacks ...
"""

__version__ = '1.0.0'

# Export main components
from .mixins import ResearchIntegrationMixin
from .parsers import (
    BaseParser,
    get_parser,
    PARSER_REGISTRY,

    # All specific parsers
    AmbitionParser,
    CountryStabilityParser,
    TrackRecordParser,
    SupportSchemeParser,
    ContractTermsParser,
    ExpectedReturnParser,
    RevenueStreamStabilityParser,
    OfftakerStatusParser,
    LongTermInterestRatesParser,
    PowerMarketSizeParser,
    ResourceAvailabilityParser,
    EnergyDependenceParser,
    RenewablesPenetrationParser,
    StatusOfGridParser,
    OwnershipHurdlesParser,
    OwnershipConsolidationParser,
    CompetitiveLandscapeParser,
    SystemModifiersParser
)

__all__ = [
    'ResearchIntegrationMixin',
    'BaseParser',
    'get_parser',
    'PARSER_REGISTRY',

    # All parsers
    'AmbitionParser',
    'CountryStabilityParser',
    'TrackRecordParser',
    'SupportSchemeParser',
    'ContractTermsParser',
    'ExpectedReturnParser',
    'RevenueStreamStabilityParser',
    'OfftakerStatusParser',
    'LongTermInterestRatesParser',
    'PowerMarketSizeParser',
    'ResourceAvailabilityParser',
    'EnergyDependenceParser',
    'RenewablesPenetrationParser',
    'StatusOfGridParser',
    'OwnershipHurdlesParser',
    'OwnershipConsolidationParser',
    'CompetitiveLandscapeParser',
    'SystemModifiersParser',
]
