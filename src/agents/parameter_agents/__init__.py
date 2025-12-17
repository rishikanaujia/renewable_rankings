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

Phase 2 Agents (Coming Soon):
- SupportSchemeAgent
- TrackRecordAgent
- ContractTermsAgent
- LongTermInterestRatesAgent
- StatusOfGridAgent
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
    # Add more agents as they're implemented
    # "support_scheme": SupportSchemeAgent,
    # "track_record": TrackRecordAgent,
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
