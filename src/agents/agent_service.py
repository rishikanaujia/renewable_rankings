"""Agent service for coordinating parameter analysts.

This service provides the integration layer between the UI and agents.
It handles agent execution, result aggregation, and error recovery.
"""
from typing import Dict, List, Optional
from datetime import datetime

from .base_agent import AgentMode
from .parameter_agents import get_agent, list_available_agents
from ..models.parameter import ParameterScore, SubcategoryScore
from ..models.ranking import CountryRanking
from ..core.config_loader import config_loader
from ..core.logger import get_logger
from ..core.exceptions import AgentError

logger = get_logger(__name__)


class AgentService:
    """Service for coordinating parameter analyst agents."""
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK):
        """Initialize agent service.
        
        Args:
            mode: Operation mode for all agents
        """
        self.mode = mode
        self.weights = config_loader.get_weights()['weights']
        logger.info(f"AgentService initialized in {mode} mode")
    
    def analyze_parameter(
        self,
        parameter_name: str,
        country: str,
        period: str = "Q3 2024"
    ) -> ParameterScore:
        """Analyze a single parameter for a country.
        
        Args:
            parameter_name: Parameter to analyze (e.g., "Ambition")
            country: Country name
            period: Time period
            
        Returns:
            ParameterScore
            
        Raises:
            AgentError: If agent not found or analysis fails
        """
        try:
            logger.info(f"Analyzing {parameter_name} for {country}")
            
            # Get agent class
            agent_class = get_agent(parameter_name.lower())
            
            # Initialize agent
            agent = agent_class(mode=self.mode)
            
            # Run analysis
            result = agent.analyze(country, period)
            
            logger.info(
                f"{parameter_name} analysis complete: "
                f"Score={result.score}, Confidence={result.confidence}"
            )
            
            return result
            
        except KeyError as e:
            logger.warning(f"Agent not implemented for {parameter_name}: {e}")
            # Return placeholder for unimplemented agents
            return self._create_placeholder_score(parameter_name, country)
        
        except Exception as e:
            logger.error(f"Parameter analysis failed: {e}", exc_info=True)
            raise AgentError(f"Failed to analyze {parameter_name}: {str(e)}")
    
    def analyze_subcategory(
        self,
        subcategory_name: str,
        country: str,
        period: str = "Q3 2024",
        parameter_names: Optional[List[str]] = None
    ) -> SubcategoryScore:
        """Analyze all parameters in a subcategory.
        
        Args:
            subcategory_name: Subcategory (e.g., "regulation")
            country: Country name
            period: Time period
            parameter_names: Optional list of parameters to analyze
            
        Returns:
            SubcategoryScore with aggregated results
        """
        logger.info(f"Analyzing subcategory {subcategory_name} for {country}")
        
        # Get parameters for this subcategory
        if not parameter_names:
            parameter_names = self._get_subcategory_parameters(subcategory_name)
        
        # Analyze each parameter
        parameter_scores = []
        for param_name in parameter_names:
            try:
                score = self.analyze_parameter(param_name, country, period)
                parameter_scores.append(score)
            except Exception as e:
                logger.warning(f"Skipping {param_name}: {e}")
                # Add placeholder
                parameter_scores.append(
                    self._create_placeholder_score(param_name, country)
                )
        
        # Calculate subcategory score (average of parameter scores)
        avg_score = sum(s.score for s in parameter_scores) / len(parameter_scores)
        
        result = SubcategoryScore(
            subcategory_name=subcategory_name,
            score=round(avg_score, 2),
            parameter_scores=parameter_scores,
            timestamp=datetime.now()
        )
        
        logger.info(
            f"Subcategory {subcategory_name} analysis complete: "
            f"Score={result.score} (from {len(parameter_scores)} parameters)"
        )
        
        return result
    
    def analyze_country(
        self,
        country: str,
        period: str = "Q3 2024"
    ) -> CountryRanking:
        """Complete analysis for a country (all parameters).
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            CountryRanking with all scores
        """
        logger.info(f"Starting complete analysis for {country}")
        
        # Analyze all subcategories
        subcategories = [
            "regulation",
            "profitability", 
            "accommodation",
            "market_size_fundamentals",
            "competition_ease",
            "system_modifiers"
        ]
        
        subcategory_scores = []
        for subcat in subcategories:
            try:
                score = self.analyze_subcategory(subcat, country, period)
                subcategory_scores.append(score)
            except Exception as e:
                logger.error(f"Subcategory {subcat} analysis failed: {e}")
        
        # Calculate overall weighted score
        overall_score = self._calculate_overall_score(subcategory_scores)
        
        # Create ranking
        ranking = CountryRanking(
            country_name=country,
            country_code=self._get_country_code(country),
            period=period,
            overall_score=overall_score,
            subcategory_scores=subcategory_scores,
            timestamp=datetime.now()
        )
        
        logger.info(
            f"Complete analysis for {country} finished: "
            f"Overall Score={overall_score}"
        )
        
        return ranking
    
    def _calculate_overall_score(
        self,
        subcategory_scores: List[SubcategoryScore]
    ) -> float:
        """Calculate weighted overall score.
        
        Args:
            subcategory_scores: List of subcategory scores
            
        Returns:
            Weighted overall score (0-10)
        """
        total_score = 0.0
        
        for sc_score in subcategory_scores:
            # Get weight for this subcategory
            weight = self.weights.get(sc_score.subcategory_name, {}).get('weight', 0)
            
            # Add weighted contribution
            total_score += sc_score.score * weight
            
            logger.debug(
                f"  {sc_score.subcategory_name}: "
                f"{sc_score.score} × {weight} = {sc_score.score * weight}"
            )
        
        return round(total_score, 2)
    
    def _get_subcategory_parameters(self, subcategory_name: str) -> List[str]:
        """Get parameter names for a subcategory.
        
        Args:
            subcategory_name: Subcategory name
            
        Returns:
            List of parameter names
        """
        # Mapping of subcategories to parameters
        subcategory_params = {
            "regulation": [
                "ambition",
                "country_stability",
                "track_record",  # Regulation now 3/5 = 60%!
                # "support_scheme",
                # "contract_terms",
            ],
            "profitability": [
                "expected_return",
                "revenue_stream_stability",
                "offtaker_status",
                "long_term_interest_rates"  # Profitability 4/4 = 100% COMPLETE! 🏆
            ],
            "accommodation": [
                "status_of_grid",  # Accommodation now 1/2 = 50%! NEW SUBCATEGORY!
                # "ownership_hurdles"
            ],
            "market_size_fundamentals": [
                "power_market_size",
                "resource_availability",
                "energy_dependence",
                "renewables_penetration"  # COMPLETE! 4/4 = 100%
            ],
            "competition_ease": [
                # "ownership_consolidation",
                # "competitive_landscape"
            ],
            "system_modifiers": [
                # "system_modifiers"  # Combined parameter
            ]
        }
        
        params = subcategory_params.get(subcategory_name, [])
        
        if not params:
            logger.warning(
                f"No parameters implemented yet for {subcategory_name}. "
                f"Returning empty list."
            )
        
        return params
    
    def _create_placeholder_score(
        self,
        parameter_name: str,
        country: str
    ) -> ParameterScore:
        """Create placeholder score for unimplemented parameters.
        
        Args:
            parameter_name: Parameter name
            country: Country name
            
        Returns:
            Placeholder ParameterScore
        """
        return ParameterScore(
            parameter_name=parameter_name,
            score=5.0,  # Neutral score
            justification=f"{parameter_name} analysis not yet implemented (placeholder score)",
            data_sources=["Placeholder"],
            confidence=0.0,  # Zero confidence for placeholders
            timestamp=datetime.now()
        )
    
    def _get_country_code(self, country_name: str) -> str:
        """Get ISO 3-letter country code.
        
        Args:
            country_name: Country name
            
        Returns:
            ISO 3-letter code
        """
        # Simple mapping - in production, use a proper library
        code_map = {
            "Brazil": "BRA",
            "Germany": "DEU",
            "United States": "USA",
            "USA": "USA",
            "China": "CHN",
            "India": "IND",
            "United Kingdom": "GBR",
            "Spain": "ESP",
            "Australia": "AUS",
            "Chile": "CHL",
            "Vietnam": "VNM",
        }
        return code_map.get(country_name, "XXX")
    
    def get_available_parameters(self) -> List[str]:
        """Get list of implemented parameters.
        
        Returns:
            List of parameter names
        """
        return list_available_agents()


# Global agent service instance
agent_service = AgentService(mode=AgentMode.MOCK)
