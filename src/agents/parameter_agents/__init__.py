"""Parameter agents package.

This package contains all 21 parameter analyst agents.
Each agent is responsible for analyzing one specific parameter.

Phase 1 Agents (Implemented):
- AmbitionAgent - Government renewable energy targets
- CountryStabilityAgent - Political and economic risk assessment
- PowerMarketSizeAgent - Total electricity market size (TWh consumption)
- ResourceAvailabilityAgent - Solar and wind renewable energy resources
- EnergyDependenceAgent - Energy import dependency and security
- RenewablesPenetrationAgent - Current renewables share in electricity generation
- ExpectedReturnAgent - Projected IRR for renewable energy projects
- RevenueStreamStabilityAgent - PPA contract term and revenue security
- OfftakerStatusAgent - PPA offtaker creditworthiness
- LongTermInterestRatesAgent - Long-term interest rates and financing costs
- TrackRecordAgent - Historical renewable energy deployment track record
- SupportSchemeAgent - Government support mechanisms (FiT, auctions, tax credits)
- ContractTermsAgent - PPA bankability and risk allocation
- OwnershipConsolidationAgent - Market concentration and competition
- CompetitiveLandscapeAgent - Market entry ease and competitive dynamics
- StatusOfGridAgent - Grid infrastructure quality and reliability
- OwnershipHurdlesAgent - Foreign ownership restrictions and market access

Phase 2 Agents (Coming Soon):
- SupportSchemeAgent
- ContractTermsAgent
- OwnershipHurdlesAgent
- OwnershipConsolidationAgent
- CompetitiveLandscapeAgent
- SystemModifiersAgent
"""

from .ambition_agent import AmbitionAgent, analyze_ambition
from .country_stability_agent import CountryStabilityAgent, analyze_country_stability
from .power_market_size_agent import PowerMarketSizeAgent, analyze_power_market_size
from .resource_availability_agent import ResourceAvailabilityAgent, analyze_resource_availability
from .energy_dependence_agent import EnergyDependenceAgent, analyze_energy_dependence
from .renewables_penetration_agent import RenewablesPenetrationAgent, analyze_renewables_penetration
from .expected_return_agent import ExpectedReturnAgent, analyze_expected_return
from .revenue_stream_stability_agent import RevenueStreamStabilityAgent, analyze_revenue_stream_stability
from .offtaker_status_agent import OfftakerStatusAgent, analyze_offtaker_status
from .long_term_interest_rates_agent import LongTermInterestRatesAgent, analyze_long_term_interest_rates
from .track_record_agent import TrackRecordAgent, analyze_track_record
from .status_of_grid_agent import StatusOfGridAgent, analyze_status_of_grid
from .ownership_hurdles_agent import OwnershipHurdlesAgent, analyze_ownership_hurdles
from .support_scheme_agent import SupportSchemeAgent, analyze_support_scheme
from .contract_terms_agent import ContractTermsAgent, analyze_contract_terms
from .ownership_consolidation_agent import OwnershipConsolidationAgent, analyze_ownership_consolidation
from .competitive_landscape_agent import CompetitiveLandscapeAgent, analyze_competitive_landscape

__all__ = [
    "AmbitionAgent",
    "analyze_ambition",
    "CountryStabilityAgent",
    "analyze_country_stability",
    "PowerMarketSizeAgent",
    "analyze_power_market_size",
    "ResourceAvailabilityAgent",
    "analyze_resource_availability",
    "EnergyDependenceAgent",
    "analyze_energy_dependence",
    "RenewablesPenetrationAgent",
    "analyze_renewables_penetration",
    "ExpectedReturnAgent",
    "analyze_expected_return",
    "RevenueStreamStabilityAgent",
    "analyze_revenue_stream_stability",
    "OfftakerStatusAgent",
    "analyze_offtaker_status",
    "LongTermInterestRatesAgent",
    "analyze_long_term_interest_rates",
    "TrackRecordAgent",
    "analyze_track_record",
    "StatusOfGridAgent",
    "analyze_status_of_grid",
    "OwnershipHurdlesAgent",
    "analyze_ownership_hurdles",
    "SupportSchemeAgent",
    "analyze_support_scheme",
    "ContractTermsAgent",
    "analyze_contract_terms",
    "OwnershipConsolidationAgent",
    "analyze_ownership_consolidation",
    "CompetitiveLandscapeAgent",
    "analyze_competitive_landscape",
]

# Agent registry for dynamic loading
AGENT_REGISTRY = {
    "ambition": AmbitionAgent,
    "country_stability": CountryStabilityAgent,
    "power_market_size": PowerMarketSizeAgent,
    "resource_availability": ResourceAvailabilityAgent,
    "energy_dependence": EnergyDependenceAgent,
    "renewables_penetration": RenewablesPenetrationAgent,
    "expected_return": ExpectedReturnAgent,
    "revenue_stream_stability": RevenueStreamStabilityAgent,
    "offtaker_status": OfftakerStatusAgent,
    "long_term_interest_rates": LongTermInterestRatesAgent,
    "track_record": TrackRecordAgent,
    "support_scheme": SupportSchemeAgent,
    "contract_terms": ContractTermsAgent,
    "ownership_consolidation": OwnershipConsolidationAgent,
    "competitive_landscape": CompetitiveLandscapeAgent,
    "status_of_grid": StatusOfGridAgent,
    "ownership_hurdles": OwnershipHurdlesAgent,
    # Add more agents as they're implemented
    # ...
}


def get_agent(parameter_name: str):
    """Get agent class for a parameter.
    
    Args:
        parameter_name: Parameter name (lowercase, underscored)
        
    Returns:
        Agent class
        
    Raises:
        KeyError: If agent not found
    """
    parameter_key = parameter_name.lower().replace(" ", "_")
    
    if parameter_key not in AGENT_REGISTRY:
        raise KeyError(
            f"Agent for parameter '{parameter_name}' not implemented yet. "
            f"Available: {list(AGENT_REGISTRY.keys())}"
        )
    
    return AGENT_REGISTRY[parameter_key]


def list_available_agents():
    """List all available parameter agents.
    
    Returns:
        List of parameter names
    """
    return list(AGENT_REGISTRY.keys())
