"""Analysis agents for country-level synthesis and rankings.

These agents sit above the parameter agents and synthesize their
results into higher-level analyses:

Phase 1 (Synthesis Layer):
- CountryAnalysisAgent - Complete country investment profile

Phase 2 (Comparative Layer):
- ComparativeAnalysisAgent - Multi-country comparison (Coming soon)
- GlobalRankingsAgent - Global investment rankings (Coming soon)

The analysis agents use the parameter agents (via agent_service) to build
comprehensive investment assessments.
"""
from .country_analysis_agent import CountryAnalysisAgent, analyze_country

__all__ = [
    "CountryAnalysisAgent",
    "analyze_country",
]

# Agent registry for analysis agents
ANALYSIS_AGENT_REGISTRY = {
    "country_analysis": CountryAnalysisAgent,
    # "comparative_analysis": ComparativeAnalysisAgent,  # Coming in Agent #20
    # "global_rankings": GlobalRankingsAgent,  # Coming in Agent #21
}
