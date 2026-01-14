"""Research Integration Parsers - Parameter-specific metric extractors.

This package contains parsers for all 18 parameters that extract relevant
metrics from research documents.
"""

# Base parser
from .base_parser import BaseParser

# Regulation parsers (5)
from .regulation_parsers import (
    AmbitionParser,
    CountryStabilityParser,
    TrackRecordParser,
    SupportSchemeParser,
    ContractTermsParser
)

# Profitability parsers (4)
from .profitability_parsers import (
    ExpectedReturnParser,
    RevenueStreamStabilityParser,
    OfftakerStatusParser,
    LongTermInterestRatesParser
)

# Market parsers (4)
from .market_parsers import (
    PowerMarketSizeParser,
    ResourceAvailabilityParser,
    EnergyDependenceParser,
    RenewablesPenetrationParser
)

# Accommodation parsers (2)
from .accommodation_parsers import (
    StatusOfGridParser,
    OwnershipHurdlesParser
)

# Competition parsers (2)
from .competition_parsers import (
    OwnershipConsolidationParser,
    CompetitiveLandscapeParser
)

# System Modifiers parser (1)
from .system_modifiers_parser import SystemModifiersParser


# Parser registry - maps parameter names to parser classes
PARSER_REGISTRY = {
    # Regulation
    'Ambition': AmbitionParser,
    'Country Stability': CountryStabilityParser,
    'Track Record': TrackRecordParser,
    'Support Scheme': SupportSchemeParser,
    'Contract Terms': ContractTermsParser,

    # Profitability
    'Expected Return': ExpectedReturnParser,
    'Revenue Stream Stability': RevenueStreamStabilityParser,
    'Offtaker Status': OfftakerStatusParser,
    'Long Term Interest Rates': LongTermInterestRatesParser,

    # Market Size & Fundamentals
    'Power Market Size': PowerMarketSizeParser,
    'Resource Availability': ResourceAvailabilityParser,
    'Energy Dependence': EnergyDependenceParser,
    'Renewables Penetration': RenewablesPenetrationParser,

    # Accommodation
    'Status of Grid': StatusOfGridParser,
    'Ownership Hurdles': OwnershipHurdlesParser,

    # Competition & Ease
    'Ownership Consolidation': OwnershipConsolidationParser,
    'Competitive Landscape': CompetitiveLandscapeParser,

    # System Modifiers
    'System Modifiers': SystemModifiersParser
}


def get_parser(parameter_name: str) -> BaseParser:
    """Get parser instance for a parameter.

    Args:
        parameter_name: Name of the parameter

    Returns:
        Parser instance

    Raises:
        KeyError: If parameter not found in registry
    """
    parser_class = PARSER_REGISTRY.get(parameter_name)
    if not parser_class:
        raise KeyError(f"No parser found for parameter: {parameter_name}")

    return parser_class()


__all__ = [
    # Base
    'BaseParser',
    'get_parser',
    'PARSER_REGISTRY',

    # Regulation
    'AmbitionParser',
    'CountryStabilityParser',
    'TrackRecordParser',
    'SupportSchemeParser',
    'ContractTermsParser',

    # Profitability
    'ExpectedReturnParser',
    'RevenueStreamStabilityParser',
    'OfftakerStatusParser',
    'LongTermInterestRatesParser',

    # Market
    'PowerMarketSizeParser',
    'ResourceAvailabilityParser',
    'EnergyDependenceParser',
    'RenewablesPenetrationParser',

    # Accommodation
    'StatusOfGridParser',
    'OwnershipHurdlesParser',

    # Competition
    'OwnershipConsolidationParser',
    'CompetitiveLandscapeParser',

    # System Modifiers
    'SystemModifiersParser',
]
