"""Power Market Size Agent - Analyzes total electricity market size.

This agent evaluates market opportunity based on total annual electricity consumption
in terawatt-hours (TWh). Larger markets offer greater absolute opportunity for 
renewable energy deployment and investment.

Market Size Scale (TWh/year):
- < 50 TWh: Very small market (limited opportunity)
- 50-100 TWh: Small market
- 100-200 TWh: Below moderate market
- 200-300 TWh: Moderate market
- 300-500 TWh: Above moderate market
- 500-750 TWh: Large market
- 750-1000 TWh: Very large market
- 1000-2000 TWh: Major market
- 2000-4000 TWh: Huge market
- 4000+ TWh: Massive market (world-leading)

Scoring Rubric (LOADED FROM CONFIG):
Higher consumption = larger market = higher score (direct relationship)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class PowerMarketSizeAgent(BaseParameterAgent):
    """Agent for analyzing electricity market size based on total consumption."""
    
    # Mock data for Phase 1 testing (Annual electricity consumption in TWh)
    # Data sourced from IEA World Energy Statistics 2023
    MOCK_DATA = {
        "Brazil": {"twh_consumption": 631.0, "population_millions": 215, "per_capita_kwh": 2935},
        "Germany": {"twh_consumption": 509.0, "population_millions": 84, "per_capita_kwh": 6060},
        "USA": {"twh_consumption": 4050.0, "population_millions": 332, "per_capita_kwh": 12200},
        "China": {"twh_consumption": 8540.0, "population_millions": 1412, "per_capita_kwh": 6050},
        "India": {"twh_consumption": 1730.0, "population_millions": 1408, "per_capita_kwh": 1229},
        "United Kingdom": {"twh_consumption": 301.0, "population_millions": 68, "per_capita_kwh": 4426},
        "Spain": {"twh_consumption": 249.0, "population_millions": 47, "per_capita_kwh": 5298},
        "Australia": {"twh_consumption": 251.0, "population_millions": 26, "per_capita_kwh": 9654},
        "Chile": {"twh_consumption": 82.0, "population_millions": 19, "per_capita_kwh": 4316},
        "Vietnam": {"twh_consumption": 267.0, "population_millions": 98, "per_capita_kwh": 2724},
        "South Africa": {"twh_consumption": 215.0, "population_millions": 60, "per_capita_kwh": 3583},
        "Nigeria": {"twh_consumption": 31.0, "population_millions": 218, "per_capita_kwh": 142},
        "Argentina": {"twh_consumption": 141.0, "population_millions": 46, "per_capita_kwh": 3065},
        "Mexico": {"twh_consumption": 324.0, "population_millions": 128, "per_capita_kwh": 2531},
        "Indonesia": {"twh_consumption": 303.0, "population_millions": 275, "per_capita_kwh": 1102},
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Power Market Size Agent."""
        super().__init__(
            parameter_name="Power Market Size",
            mode=mode,
            config=config
        )
        
        # Load scoring rubric from config (NO HARDCODING!)
        self.scoring_rubric = self._load_scoring_rubric()
        
        logger.debug(f"Loaded scoring rubric with {len(self.scoring_rubric)} levels")
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.
        
        Returns:
            List of scoring levels with TWh thresholds
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            # Get rubric for power_market_size parameter
            market_config = params_config['parameters'].get('power_market_size', {})
            scoring = market_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_twh": item.get('min_twh', 0),
                        "max_twh": item.get('max_twh', 100000),
                        "range": item['range'],
                        "description": item['description']
                    })
                
                logger.debug(f"Converted {len(rubric)} rubric levels from config")
                return rubric
            else:
                logger.warning("No scoring rubric in config, using fallback")
                return self._get_fallback_rubric()
                
        except Exception as e:
            logger.warning(f"Could not load rubric from config: {e}. Using fallback.")
            return self._get_fallback_rubric()
    
    def _get_fallback_rubric(self) -> List[Dict[str, Any]]:
        """Fallback scoring rubric if config is not available.
        
        This ensures agent works even without full config.
        
        Returns:
            Default scoring rubric
        """
        return [
            {"score": 1, "min_twh": 0, "max_twh": 50, "range": "< 50 TWh", "description": "Very small market (limited opportunity)"},
            {"score": 2, "min_twh": 50, "max_twh": 100, "range": "50-100 TWh", "description": "Small market"},
            {"score": 3, "min_twh": 100, "max_twh": 200, "range": "100-200 TWh", "description": "Below moderate market"},
            {"score": 4, "min_twh": 200, "max_twh": 300, "range": "200-300 TWh", "description": "Moderate market"},
            {"score": 5, "min_twh": 300, "max_twh": 500, "range": "300-500 TWh", "description": "Above moderate market"},
            {"score": 6, "min_twh": 500, "max_twh": 750, "range": "500-750 TWh", "description": "Large market"},
            {"score": 7, "min_twh": 750, "max_twh": 1000, "range": "750-1000 TWh", "description": "Very large market"},
            {"score": 8, "min_twh": 1000, "max_twh": 2000, "range": "1000-2000 TWh", "description": "Major market"},
            {"score": 9, "min_twh": 2000, "max_twh": 4000, "range": "2000-4000 TWh", "description": "Huge market"},
            {"score": 10, "min_twh": 4000, "max_twh": 100000, "range": "≥ 4000 TWh", "description": "Massive market (world-leading)"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze power market size for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Power Market Size for {country} ({period})")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # IEA data is official and regularly updated, so high confidence
            data_quality = "high" if data else "low"
            confidence = self._estimate_confidence(data, data_quality)
            
            # Step 6: Identify data sources
            data_sources = self._get_data_sources(country)
            
            # Create result
            result = ParameterScore(
                parameter_name=self.parameter_name,
                score=score,
                justification=justification,
                data_sources=data_sources,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
            logger.info(
                f"Power Market Size analysis complete for {country}: "
                f"Score={score}, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Power Market Size analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Power Market Size analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch electricity consumption data.
        
        In MOCK mode: Returns mock TWh consumption
        In RULE mode: Would query database
        In AI mode: Would use LLM to extract from documents
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with TWh consumption and per capita data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default small market")
                data = {"twh_consumption": 150.0, "population_millions": 50, "per_capita_kwh": 3000}
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # TODO Phase 2: Query from database
            # return self._query_energy_database(country, period)
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from documents
            # return self._llm_extract_consumption(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate market size score based on TWh consumption.
        
        Higher consumption = larger market = higher score (direct relationship)
        
        Args:
            data: Consumption data with twh_consumption
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        twh_consumption = data.get("twh_consumption", 0)
        
        logger.debug(f"Calculating score for {country}: {twh_consumption} TWh/year")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_twh = level.get("min_twh", 0)
            max_twh = level.get("max_twh", 100000)
            
            if min_twh <= twh_consumption < max_twh:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{twh_consumption} TWh falls in range {min_twh}-{max_twh} TWh"
                )
                return float(score)
        
        # Fallback (shouldn't reach here with proper rubric)
        logger.warning(f"No rubric match for {twh_consumption} TWh, defaulting to score 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the market size score.
        
        Args:
            data: Consumption data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        twh_consumption = data.get("twh_consumption", 0)
        population = data.get("population_millions", 0)
        per_capita = data.get("per_capita_kwh", 0)
        
        # Find description from rubric
        description = "moderate-sized electricity market"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification with context
        justification = (
            f"Annual electricity consumption of {twh_consumption:,.0f} TWh "
            f"({per_capita:,.0f} kWh per capita across {population:.0f}M people) indicates "
            f"{description}. "
            f"Large absolute market size provides substantial opportunity for renewable energy deployment."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis.
        
        Args:
            country: Country name
            
        Returns:
            List of data source identifiers
        """
        # In production, these would be actual URLs/documents
        return [
            "IEA World Energy Statistics 2023",
            f"{country} National Energy Balance",
            "BP Statistical Review of World Energy 2023"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Power Market Size parameter.
        
        Returns:
            Complete scoring rubric
        """
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter.
        
        Returns:
            List of typical data sources
        """
        return [
            "IEA World Energy Statistics",
            "BP Statistical Review of World Energy",
            "National energy statistics agencies",
            "IRENA Renewable Energy Statistics",
            "World Bank Energy Indicators"
        ]


# Convenience function for direct usage
def analyze_power_market_size(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze power market size.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode
        
    Returns:
        ParameterScore
    """
    agent = PowerMarketSizeAgent(mode=mode)
    return agent.analyze(country, period)
