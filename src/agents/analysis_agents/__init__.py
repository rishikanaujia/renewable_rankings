"""Analysis agents for country-level synthesis and rankings.

These agents sit above the parameter agents and synthesize their
results into higher-level analyses:

Phase 1 (Synthesis Layer):
- CountryAnalysisAgent - Complete country investment profile

Phase 2 (Comparative Layer):
- ComparativeAnalysisAgent - Multi-country comparison

Phase 3 (Global Layer):
- GlobalRankingsAgent - Global investment rankings with tier assignments

The analysis agents use the parameter agents (via agent_service) to build
comprehensive investment assessments.
"""
from .country_analysis_agent import CountryAnalysisAgent, analyze_country
from .comparative_analysis_agent import ComparativeAnalysisAgent, compare_countries
from .global_rankings_agent import GlobalRankingsAgent

__all__ = [
    "CountryAnalysisAgent",
    "analyze_country",
    "ComparativeAnalysisAgent",
    "compare_countries",
    "GlobalRankingsAgent",
]

# Agent registry for analysis agents
ANALYSIS_AGENT_REGISTRY = {
    "country_analysis": CountryAnalysisAgent,
    "comparative_analysis": ComparativeAnalysisAgent,
    "global_rankings": GlobalRankingsAgent,
}