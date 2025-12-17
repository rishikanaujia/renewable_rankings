"""Parameter agents package.

This package contains all 21 parameter analyst agents.
Each agent is responsible for analyzing one specific parameter.

Phase 1 Agents (Implemented):
- AmbitionAgent - Government renewable energy targets

Phase 2 Agents (Coming Soon):
- SupportSchemeAgent
- TrackRecordAgent
- ContractTermsAgent
- CountryStabilityAgent
- RevenueStreamStabilityAgent
- OfftakerStatusAgent
- ExpectedReturnAgent
- LongTermInterestRatesAgent
- StatusOfGridAgent
- OwnershipHurdlesAgent
- PowerMarketSizeAgent
- ResourceAvailabilityAgent
- EnergyDependenceAgent
- RenewablesPenetrationAgent
- OwnershipConsolidationAgent
- CompetitiveLandscapeAgent
- SystemModifiersAgent
"""

from .ambition_agent import AmbitionAgent, analyze_ambition

__all__ = [
    "AmbitionAgent",
    "analyze_ambition",
]

# Agent registry for dynamic loading
AGENT_REGISTRY = {
    "ambition": AmbitionAgent,
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
