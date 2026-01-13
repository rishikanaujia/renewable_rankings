"""Parsers for Competition & Ease subcategory parameters.

Competition parameters:
1. Ownership Consolidation - Market concentration
2. Competitive Landscape - Number of competitors and barriers
"""
from typing import Dict, Any
from .base_parser import BaseParser
import logging

logger = logging.getLogger(__name__)


class OwnershipConsolidationParser(BaseParser):
    """Parser for Ownership Consolidation - extracts market concentration metrics."""

    def __init__(self):
        super().__init__(parameter_name="Ownership Consolidation")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract market concentration and consolidation metrics.

        Returns:
            {
                'hhi_index': float,  # Herfindahl-Hirschman Index
                'top_3_market_share_percent': float,
                'number_of_players': int,
                'market_concentration': str,  # Low, Medium, High
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for HHI index
        hhi_keywords = ['hhi', 'herfindahl', 'concentration index']
        hhi_metric = self._find_metric(metrics, hhi_keywords)
        hhi_index = self._extract_numeric_value(hhi_metric, 1500.0) if hhi_metric else 1500.0

        # Look for top 3 market share
        share_keywords = ['top 3', 'market share', 'concentration ratio']
        share_metric = self._find_metric(metrics, share_keywords)
        top3_share = self._extract_numeric_value(share_metric, 50.0) if share_metric else 50.0

        # Look for number of players
        players_keywords = ['number of', 'players', 'competitors', 'participants']
        players_metric = self._find_metric(metrics, players_keywords)
        num_players = int(self._extract_numeric_value(players_metric, 10)) if players_metric else 10

        # Determine market concentration based on HHI
        if hhi_index < 1000:
            concentration = "Low"  # Competitive market
        elif hhi_index < 1800:
            concentration = "Medium"  # Moderate concentration
        else:
            concentration = "High"  # Highly concentrated

        return self._create_base_response(
            research_doc,
            additional_data={
                'hhi_index': hhi_index,
                'top_3_market_share_percent': top3_share,
                'number_of_players': num_players,
                'market_concentration': concentration
            }
        )


class CompetitiveLandscapeParser(BaseParser):
    """Parser for Competitive Landscape - extracts competition metrics."""

    def __init__(self):
        super().__init__(parameter_name="Competitive Landscape")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract competitive landscape and barriers to entry.

        Returns:
            {
                'competition_intensity_score': float,  # 0-10 (higher = more competitive)
                'barriers_to_entry_score': float,  # 0-10 (higher = more barriers)
                'number_of_competitors': int,
                'market_maturity': str,  # Emerging, Growing, Mature
                'ease_of_entry': str,  # Easy, Moderate, Difficult
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for competition intensity
        intensity_keywords = ['competition', 'competitive intensity', 'rivalry']
        intensity_metric = self._find_metric(metrics, intensity_keywords)
        competition_intensity = self._extract_numeric_value(intensity_metric, 6.0) if intensity_metric else 6.0

        # Look for barriers
        barrier_keywords = ['barriers', 'entry barriers', 'barriers to entry']
        barrier_metric = self._find_metric(metrics, barrier_keywords)
        barriers_score = self._extract_numeric_value(barrier_metric, 5.0) if barrier_metric else 5.0

        # Look for number of competitors
        competitors_keywords = ['competitors', 'number of competitors', 'market players']
        competitors_metric = self._find_metric(metrics, competitors_keywords)
        num_competitors = int(self._extract_numeric_value(competitors_metric, 15)) if competitors_metric else 15

        # Infer market maturity from overview
        overview = self._get_overview(research_doc).lower()
        if 'emerging' in overview or 'nascent' in overview:
            maturity = "Emerging"
        elif 'growing' in overview or 'developing' in overview:
            maturity = "Growing"
        elif 'mature' in overview or 'established' in overview:
            maturity = "Mature"
        else:
            maturity = "Growing"  # Default

        # Determine ease of entry based on barriers
        if barriers_score < 4.0:
            ease_of_entry = "Easy"
        elif barriers_score < 7.0:
            ease_of_entry = "Moderate"
        else:
            ease_of_entry = "Difficult"

        return self._create_base_response(
            research_doc,
            additional_data={
                'competition_intensity_score': competition_intensity,
                'barriers_to_entry_score': barriers_score,
                'number_of_competitors': num_competitors,
                'market_maturity': maturity,
                'ease_of_entry': ease_of_entry
            }
        )
