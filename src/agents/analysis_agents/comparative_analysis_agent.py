"""Comparative Analysis Agent - Compares multiple countries side-by-side.

This agent uses the Country Analysis Agent to analyze multiple countries
and then compares them across all dimensions to identify:
- Relative rankings
- Best/worst performers by subcategory
- Comparative strengths and weaknesses
- Investment opportunity gaps

This is the second synthesis agent in the analysis layer.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from .country_analysis_agent import CountryAnalysisAgent
from ..base_agent import AgentMode
from ...models.comparative_analysis import (
    ComparativeAnalysis,
    CountryComparison,
    SubcategoryComparison
)
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class ComparativeAnalysisAgent:
    """Agent for comparative analysis across multiple countries."""
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Comparative Analysis Agent.
        
        Args:
            mode: Agent operation mode (MOCK, RULE_BASED, AI_POWERED)
            config: Optional configuration dictionary
        """
        self.mode = mode
        self.config = config or {}
        self.country_agent = CountryAnalysisAgent(mode=mode, config=config)
        
        logger.info(f"Initialized ComparativeAnalysisAgent in {mode} mode")
    
    def compare(
        self,
        countries: List[str],
        period: str = "Q3 2024",
        **kwargs
    ) -> ComparativeAnalysis:
        """Perform comparative analysis across multiple countries.
        
        Args:
            countries: List of country names to compare
            period: Analysis period
            **kwargs: Additional parameters
            
        Returns:
            ComparativeAnalysis with complete comparison
        """
        try:
            # Get config values with defaults
            comp_config = self.config.get('comparative_analysis', {})
            min_countries = comp_config.get('min_countries', 2)
            max_countries = comp_config.get('max_countries', 100)
            
            # Validate country count
            if len(countries) < min_countries:
                raise AgentError(
                    f"Comparative analysis requires at least {min_countries} countries"
                )
            if len(countries) > max_countries:
                raise AgentError(
                    f"Comparative analysis limited to {max_countries} countries"
                )
            
            logger.info(f"Comparing {len(countries)} countries: {', '.join(countries)}")
            
            # Analyze each country
            country_results = {}
            for country in countries:
                logger.info(f"Analyzing {country}...")
                result = self.country_agent.analyze(country, period)
                country_results[country] = result
            
            # Build comparisons
            country_comparisons = self._build_country_comparisons(country_results)
            subcategory_comparisons = self._build_subcategory_comparisons(country_results)
            
            # Generate summary
            summary = self._generate_summary(
                countries, country_comparisons, subcategory_comparisons
            )
            
            result = ComparativeAnalysis(
                countries=countries,
                period=period,
                country_comparisons=country_comparisons,
                subcategory_comparisons=subcategory_comparisons,
                summary=summary,
                timestamp=datetime.now(),
                metadata={
                    "mode": str(self.mode),
                    "country_count": len(countries)
                }
            )
            
            logger.info(
                f"Comparative analysis complete: {len(countries)} countries, "
                f"{len(subcategory_comparisons)} subcategories"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Comparative analysis failed: {str(e)}", exc_info=True)
            raise AgentError(f"Comparative analysis failed: {str(e)}")
    
    def _build_country_comparisons(
        self,
        country_results: Dict[str, Any]
    ) -> List[CountryComparison]:
        """Build country comparison data with rankings."""
        # Sort by overall score
        sorted_countries = sorted(
            country_results.items(),
            key=lambda x: x[1].overall_score,
            reverse=True
        )
        
        comparisons = []
        for rank, (country, result) in enumerate(sorted_countries, 1):
            # Extract subcategory scores
            subcategory_scores = {
                subcat.name: subcat.score
                for subcat in result.subcategory_scores
            }
            
            comparison = CountryComparison(
                country=country,
                overall_score=result.overall_score,
                rank=rank,
                subcategory_scores=subcategory_scores,
                strengths_count=len(result.strengths),
                weaknesses_count=len(result.weaknesses)
            )
            comparisons.append(comparison)
        
        return comparisons
    
    def _build_subcategory_comparisons(
        self,
        country_results: Dict[str, Any]
    ) -> List[SubcategoryComparison]:
        """Build subcategory comparison data."""
        # Get all subcategories from first country
        first_result = next(iter(country_results.values()))
        subcategories = first_result.subcategory_scores
        
        comparisons = []
        for subcat in subcategories:
            # Collect scores for this subcategory across all countries
            country_scores = {}
            for country, result in country_results.items():
                for sc in result.subcategory_scores:
                    if sc.name == subcat.name:
                        country_scores[country] = sc.score
                        break
            
            # Find best and worst
            best_country = max(country_scores.items(), key=lambda x: x[1])
            worst_country = min(country_scores.items(), key=lambda x: x[1])
            
            # Calculate average
            average_score = sum(country_scores.values()) / len(country_scores)
            
            comparison = SubcategoryComparison(
                name=subcat.name,
                weight=subcat.weight,
                country_scores=country_scores,
                best_country=best_country[0],
                best_score=best_country[1],
                worst_country=worst_country[0],
                worst_score=worst_country[1],
                average_score=round(average_score, 2)
            )
            comparisons.append(comparison)
        
        return comparisons
    
    def _generate_summary(
        self,
        countries: List[str],
        country_comparisons: List[CountryComparison],
        subcategory_comparisons: List[SubcategoryComparison]
    ) -> str:
        """Generate comparative analysis summary."""
        # Get config values
        comp_config = self.config.get('comparative_analysis', {})
        gap_thresholds = comp_config.get('gap_thresholds', {})
        highly_competitive = gap_thresholds.get('highly_competitive', 1.0)
        moderately_competitive = gap_thresholds.get('moderately_competitive', 2.0)
        
        # Top performer
        top_country = country_comparisons[0]
        
        # Score range
        scores = [c.overall_score for c in country_comparisons]
        score_range = max(scores) - min(scores)
        
        # Determine variation level using config thresholds
        if score_range <= highly_competitive:
            variation_level = "minimal"
        elif score_range <= moderately_competitive:
            variation_level = "moderate"
        else:
            variation_level = "substantial"
        
        # Most competitive subcategory (smallest range)
        most_competitive = min(
            subcategory_comparisons,
            key=lambda s: max(s.country_scores.values()) - min(s.country_scores.values())
        )
        
        # Least competitive subcategory (largest range)
        least_competitive = max(
            subcategory_comparisons,
            key=lambda s: max(s.country_scores.values()) - min(s.country_scores.values())
        )
        
        summary = (
            f"Comparative analysis of {len(countries)} countries reveals "
            f"{top_country.country} as the top performer ({top_country.overall_score:.1f}/10). "
            f"Overall scores span {score_range:.1f} points, indicating "
            f"{variation_level} variation. "
            f"{most_competitive.name.lower()} shows the most competitive landscape "
            f"(average {most_competitive.average_score:.1f}), while "
            f"{least_competitive.name.lower()} exhibits the widest performance gap."
        )
        
        return summary


def compare_countries(
    countries: List[str],
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ComparativeAnalysis:
    """Convenience function to compare countries."""
    agent = ComparativeAnalysisAgent(mode=mode)
    return agent.compare(countries, period)
