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

MODES:
- MOCK: Uses hardcoded test data (for testing)
- RULE_BASED: Fetches real electricity data from data service (production)
"""
from typing import Dict, Any, List, Optional
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
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Power Market Size Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Power Market Size",
            mode=mode,
            config=config
        )
        
        # Store data service for RULE_BASED mode
        self.data_service = data_service
        
        # Validate data service if in RULE_BASED mode
        if self.mode == AgentMode.RULE_BASED and self.data_service is None:
            logger.warning(
                "RULE_BASED mode enabled but no data_service provided. "
                "Agent will fall back to MOCK data."
            )
        
        # Load scoring rubric from config (NO HARDCODING!)
        self.scoring_rubric = self._load_scoring_rubric()
        
        logger.debug(
            f"Initialized PowerMarketSizeAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
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
            logger.info(f"Analyzing Power Market Size for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # For AI-powered mode, use AI confidence directly
            if data.get('source') == 'ai_powered':
                data_quality = "high"
                ai_confidence = data.get('ai_confidence', 0.8)
                confidence = ai_confidence  # Use AI's confidence directly
            # Rule-based data has higher confidence than mock data
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "high"
                confidence = 0.9  # High confidence for rule-based data
            else:
                data_quality = "medium"
                confidence = 0.7  # Lower confidence for mock data

            confidence = self._estimate_confidence(data, data_quality)
            
            # Step 6: Identify data sources
            data_sources = self._get_data_sources(country, data)
            
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
                f"Score={score:.1f}, Confidence={confidence:.2f}, Mode={self.mode.value}"
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
        In RULE_BASED mode: Fetches real electricity data from data service
        In AI_POWERED mode: Would use LLM to extract from documents (not yet implemented)
        
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
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: {data.get('twh_consumption')} TWh")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Fetch rule-based data from data service
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch electricity production from World Bank
                # World Bank indicator: EG.ELC.PROD.KH (Electricity production, kWh)
                electricity_kwh = self.data_service.get_value(
                    country=country,
                    indicator='electricity_production',
                    default=None
                )
                
                # Fetch population for per capita calculation
                population = self.data_service.get_value(
                    country=country,
                    indicator='population',
                    default=None
                )
                
                # Fetch GDP as additional context
                gdp = self.data_service.get_value(
                    country=country,
                    indicator='gdp',
                    default=None
                )
                
                if electricity_kwh is None and gdp is None:
                    logger.warning(
                        f"No rule-based data found for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Calculate TWh consumption
                if electricity_kwh is not None:
                    # Convert from kWh to TWh (divide by 1 billion)
                    twh_consumption = electricity_kwh / 1_000_000_000
                elif gdp is not None:
                    # Estimate from GDP if electricity data not available
                    # Rule of thumb: ~0.2 TWh per billion USD GDP (rough approximation)
                    twh_consumption = (gdp / 1_000_000_000) * 0.2
                else:
                    return self._fetch_data_mock_fallback(country)
                
                # Calculate per capita
                if population is not None:
                    # Population is in absolute numbers, convert to millions
                    population_millions = population / 1_000_000
                    # Calculate per capita kWh
                    per_capita_kwh = (twh_consumption * 1_000_000_000) / population
                else:
                    population_millions = 50.0  # Default
                    per_capita_kwh = 3000  # Default
                
                data = {
                    'twh_consumption': twh_consumption,
                    'population_millions': population_millions,
                    'per_capita_kwh': per_capita_kwh,
                    'source': 'rule_based',
                    'period': period,
                    'data_source': 'World Bank' if electricity_kwh else 'GDP estimate'
                }
                
                logger.info(
                    f"Fetched RULE_BASED data for {country}: {twh_consumption:.1f} TWh "
                    f"({per_capita_kwh:.0f} kWh per capita)"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error fetching rule-based data for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # Extract power market size using AI extraction system
            try:
                from ai_extraction_system import AIExtractionAdapter

                adapter = AIExtractionAdapter(
                    llm_config=self.config.get('llm_config') if self.config else None,
                    cache_config=self.config.get('cache_config') if self.config else None
                )

                extraction_result = adapter.extract_parameter(
                    parameter_name='power_market_size',
                    country=country,
                    period=period,
                    documents=kwargs.get('documents'),
                    document_urls=kwargs.get('document_urls')
                )

                logger.info(f"Using AI_POWERED mode for {country}")

                if extraction_result and extraction_result.get('value') is not None:
                    score = float(extraction_result['value'])
                    metadata = extraction_result.get('metadata', {})

                    data = {
                        'source': 'ai_powered',
                        'ai_confidence': extraction_result.get('confidence', 0.8),
                        'ai_justification': extraction_result.get('justification', ''),
                        'ai_score': score,
                        'consumption_twh': metadata.get('consumption_twh', 0),
                        'market_size': metadata.get('market_size', 'Unknown'),
                        'period': period
                    }

                    logger.info(f"AI extraction successful for {country}: score={score}/10, confidence={data['ai_confidence']:.2f}")
                    return data
                else:
                    logger.warning(f"AI extraction returned no value for {country}, falling back to MOCK")
                    return self._fetch_data_mock_fallback(country)

            except Exception as e:
                logger.error(f"Error using AI extraction for {country}: {e}. Falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _fetch_data_mock_fallback(self, country: str) -> Dict[str, Any]:
        """Fallback to mock data when rule-based data is unavailable.
        
        Args:
            country: Country name
            
        Returns:
            Mock data dictionary
        """
        data = self.MOCK_DATA.get(country, {
            "twh_consumption": 150.0,
            "population_millions": 50,
            "per_capita_kwh": 3000
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
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
        # For AI-powered mode, use the score directly
        if data.get('source') == 'ai_powered' and 'ai_score' in data:
            score = float(data['ai_score'])
            logger.debug(f"Using AI-provided score for {country}: {score}/10")
            return score

        twh_consumption = data.get("twh_consumption", 0)

        logger.debug(f"Calculating score for {country}: {twh_consumption:.1f} TWh/year")

        # Find matching rubric level
        for level in self.scoring_rubric:
            min_twh = level.get("min_twh", 0)
            max_twh = level.get("max_twh", 100000)

            if min_twh <= twh_consumption < max_twh:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{twh_consumption:.1f} TWh falls in range {min_twh}-{max_twh} TWh"
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
        source = data.get("source", "unknown")

        # For AI-powered mode, use AI justification directly
        if source == 'ai_powered':
            ai_justification = data.get('ai_justification', '')
            if ai_justification:
                return ai_justification
            # Fallback if no AI justification provided
            return f"AI-extracted power market size score of {score:.1f}/10 for {country} based on electricity consumption and market analysis."

        twh_consumption = data.get("twh_consumption", 0)
        population = data.get("population_millions", 0)
        per_capita = data.get("per_capita_kwh", 0)

        # Find description from rubric
        description = "moderate-sized electricity market"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break

        # Build justification based on source
        if source == 'rule_based':
            data_source = data.get('data_source', 'World Bank')
            justification = (
                f"Based on {data_source} data: Annual electricity consumption of {twh_consumption:,.1f} TWh "
                f"({per_capita:,.0f} kWh per capita across {population:.1f}M people) indicates "
                f"{description}. "
                f"Large absolute market size provides substantial opportunity for renewable energy deployment."
            )
        else:
            justification = (
                f"Annual electricity consumption of {twh_consumption:,.0f} TWh "
                f"({per_capita:,.0f} kWh per capita across {population:.0f}M people) indicates "
                f"{description}. "
                f"Large absolute market size provides substantial opportunity for renewable energy deployment."
            )

        return justification
    
    def _get_data_sources(self, country: str, data: Dict[str, Any] = None) -> List[str]:
        """Get data sources used for this analysis.

        Args:
            country: Country name
            data: Data dictionary with source info

        Returns:
            List of data source identifiers
        """
        sources = []

        # Check data source type
        if data and data.get('source') == 'ai_powered':
            sources.append("AI-Powered Document Extraction (Power Market Size)")
            sources.append("IEA and National Energy Statistics")
        elif data and data.get('source') == 'rule_based':
            sources.append("World Bank Energy Indicators - Rule-Based Data")
            sources.append("IEA World Energy Statistics 2023")
        else:
            sources.append("IEA World Energy Statistics 2023 - Mock Data")
        
        sources.append(f"{country} National Energy Balance")
        sources.append("BP Statistical Review of World Energy 2023")
        
        return sources
    
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
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze power market size.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = PowerMarketSizeAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
