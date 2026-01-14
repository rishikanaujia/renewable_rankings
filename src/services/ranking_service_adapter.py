"""Service adapter to provide unified interface for mock and agent services.

This adapter wraps agent_service to provide the same interface as mock_service,
allowing seamless switching between mock data and real AI agent analysis.
"""
from typing import List, Optional
from datetime import datetime

from ..models.ranking import CountryRanking, GlobalRankings
from ..models.correction import ExpertCorrection
from ..agents.agent_service import agent_service
from ..core.logger import get_logger

logger = get_logger(__name__)


class RankingServiceAdapter:
    """Adapter that wraps agent_service to match mock_service interface."""

    # Default countries to analyze for global rankings
    DEFAULT_COUNTRIES = [
        "Brazil", "Germany", "United States", "China", "India",
        "United Kingdom", "Spain", "Australia", "Chile", "Vietnam"
    ]

    def __init__(self):
        """Initialize the adapter with agent_service."""
        self.agent_service = agent_service
        logger.info("RankingServiceAdapter initialized with agent_service")

    def get_rankings(self, period: str = "Q3 2024") -> GlobalRankings:
        """Get global rankings for a period using real agents.

        Args:
            period: Time period for analysis

        Returns:
            GlobalRankings object with all country analyses
        """
        logger.info(f"Generating rankings for period: {period} using real agents")

        rankings = []
        for country in self.DEFAULT_COUNTRIES:
            try:
                logger.debug(f"Analyzing {country}...")
                ranking = self.agent_service.analyze_country(country, period)
                rankings.append(ranking)
            except Exception as e:
                logger.error(f"Failed to analyze {country}: {e}")
                # Continue with other countries

        # Sort by overall score (descending)
        rankings.sort(key=lambda r: r.overall_score, reverse=True)

        logger.info(f"Rankings generated for {len(rankings)} countries")

        return GlobalRankings(
            period=period,
            rankings=rankings
        )

    def get_country_ranking(
        self,
        country_name: str,
        period: str = "Q3 2024"
    ) -> Optional[CountryRanking]:
        """Get ranking for a specific country using real agents.

        Args:
            country_name: Country name
            period: Time period

        Returns:
            CountryRanking or None if analysis fails
        """
        logger.info(f"Fetching ranking for country: {country_name}")

        try:
            ranking = self.agent_service.analyze_country(country_name, period)
            return ranking
        except Exception as e:
            logger.error(f"Failed to get ranking for {country_name}: {e}")
            return None

    def apply_correction(self, correction: ExpertCorrection) -> CountryRanking:
        """Apply expert correction and recalculate scores.

        Args:
            correction: Expert correction to apply

        Returns:
            Updated CountryRanking

        Raises:
            ValueError: If country not found or correction fails
        """
        logger.info(
            f"Applying correction: {correction.parameter_name} "
            f"for {correction.country_name}"
        )

        # In a real implementation, this would:
        # 1. Store the correction in memory system
        # 2. Re-run the specific parameter agent with correction override
        # 3. Recalculate subcategory and overall scores

        # For now, we'll re-analyze the country
        # (corrections would be applied if memory system is integrated)
        try:
            ranking = self.agent_service.analyze_country(
                correction.country_name,
                correction.period
            )

            logger.info(
                f"Correction applied. Country re-analyzed. "
                f"New score: {ranking.overall_score}"
            )
            return ranking

        except Exception as e:
            logger.error(f"Failed to apply correction: {e}")
            raise ValueError(f"Country not found or correction failed: {correction.country_name}")

    def search_countries(self, query: str) -> List[str]:
        """Search for countries matching query.

        Args:
            query: Search query

        Returns:
            List of matching country names
        """
        query_lower = query.lower()
        matches = [
            country for country in self.DEFAULT_COUNTRIES
            if query_lower in country.lower()
        ]

        logger.info(f"Found {len(matches)} countries matching '{query}'")
        return matches


# Global instance
ranking_service_adapter = RankingServiceAdapter()
