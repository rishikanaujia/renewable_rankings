"""Resource Availability Agent - Analyzes solar and wind renewable energy resources.

This agent evaluates the natural endowment of renewable energy resources by combining
solar irradiation potential and wind speed characteristics. Higher quality resources
enable more cost-effective renewable energy deployment.

Resource Metrics:
- Solar Irradiation: kWh/m²/day (global horizontal irradiation - GHI)
- Wind Speed: m/s (at 100m hub height)

Scoring combines both metrics with equal weighting:
- Combined Score = (Solar_normalized * 0.5) + (Wind_normalized * 0.5)
- Solar normalized: (solar_kwh_per_m2_day / 6.5) * 10
- Wind normalized: (wind_m_per_s / 9.0) * 10

Resource Quality Scale:
- < 2.0: Very poor (both weak)
- 2-3: Poor
- 3-4: Below average
- 4-5: Moderate
- 5-6: Average
- 6-7: Good
- 7-8: Very good
- 8-9: Excellent
- 9-10: Outstanding
- ≥ 10: World-class

Scoring Rubric (LOADED FROM CONFIG):
Higher combined resource score = better renewable potential = higher score
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class ResourceAvailabilityAgent(BaseParameterAgent):
    """Agent for analyzing solar and wind renewable energy resource availability."""
    
    # Mock data for Phase 1 testing
    # Solar: Global Horizontal Irradiation (kWh/m²/day) from Global Solar Atlas
    # Wind: Average wind speed at 100m (m/s) from Global Wind Atlas
    MOCK_DATA = {
        "Brazil": {
            "solar_kwh_m2_day": 5.2,  # Good solar in Northeast
            "wind_m_s": 7.5,          # Excellent coastal wind
            "solar_quality": "Good",
            "wind_quality": "Excellent"
        },
        "Germany": {
            "solar_kwh_m2_day": 3.0,  # Moderate solar
            "wind_m_s": 6.0,          # Good wind (North Sea)
            "solar_quality": "Moderate",
            "wind_quality": "Good"
        },
        "USA": {
            "solar_kwh_m2_day": 5.5,  # Excellent solar (Southwest)
            "wind_m_s": 7.0,          # Excellent wind (Great Plains)
            "solar_quality": "Excellent",
            "wind_quality": "Excellent"
        },
        "China": {
            "solar_kwh_m2_day": 4.5,  # Good solar (West/North)
            "wind_m_s": 6.5,          # Good wind (Inner Mongolia)
            "solar_quality": "Good",
            "wind_quality": "Good"
        },
        "India": {
            "solar_kwh_m2_day": 5.8,  # Outstanding solar (Rajasthan)
            "wind_m_s": 6.0,          # Good wind (Tamil Nadu, Gujarat)
            "solar_quality": "Outstanding",
            "wind_quality": "Good"
        },
        "UK": {
            "solar_kwh_m2_day": 2.5,  # Low solar
            "wind_m_s": 8.0,          # Excellent offshore wind
            "solar_quality": "Low",
            "wind_quality": "Excellent"
        },
        "Spain": {
            "solar_kwh_m2_day": 5.0,  # Good solar
            "wind_m_s": 6.5,          # Good wind
            "solar_quality": "Good",
            "wind_quality": "Good"
        },
        "Australia": {
            "solar_kwh_m2_day": 6.0,  # Outstanding solar (highest in world)
            "wind_m_s": 7.0,          # Very good wind (South Australia)
            "solar_quality": "Outstanding",
            "wind_quality": "Very Good"
        },
        "Chile": {
            "solar_kwh_m2_day": 6.5,  # World-class solar (Atacama Desert)
            "wind_m_s": 8.5,          # Excellent wind (Patagonia)
            "solar_quality": "World-class",
            "wind_quality": "Excellent"
        },
        "Vietnam": {
            "solar_kwh_m2_day": 4.8,  # Good solar
            "wind_m_s": 7.0,          # Very good coastal wind
            "solar_quality": "Good",
            "wind_quality": "Very Good"
        },
        "South Africa": {
            "solar_kwh_m2_day": 5.5,  # Excellent solar (Northern Cape)
            "wind_m_s": 6.0,          # Good wind (Western Cape)
            "solar_quality": "Excellent",
            "wind_quality": "Good"
        },
        "Nigeria": {
            "solar_kwh_m2_day": 5.0,  # Good solar
            "wind_m_s": 4.5,          # Moderate wind
            "solar_quality": "Good",
            "wind_quality": "Moderate"
        },
        "Argentina": {
            "solar_kwh_m2_day": 5.5,  # Excellent solar (Puna region)
            "wind_m_s": 9.0,          # Outstanding wind (Patagonia)
            "solar_quality": "Excellent",
            "wind_quality": "Outstanding"
        },
        "Morocco": {
            "solar_kwh_m2_day": 5.8,  # Outstanding solar
            "wind_m_s": 7.5,          # Excellent wind
            "solar_quality": "Outstanding",
            "wind_quality": "Excellent"
        },
        "Mexico": {
            "solar_kwh_m2_day": 5.5,  # Excellent solar
            "wind_m_s": 7.0,          # Very good wind (Oaxaca)
            "solar_quality": "Excellent",
            "wind_quality": "Very Good"
        },
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Resource Availability Agent."""
        super().__init__(
            parameter_name="Resource Availability",
            mode=mode,
            config=config
        )
        
        # Load scoring rubric and calculation params from config (NO HARDCODING!)
        self.scoring_rubric = self._load_scoring_rubric()
        self.calculation_params = self._load_calculation_params()
        
        logger.debug(f"Loaded scoring rubric with {len(self.scoring_rubric)} levels")
        logger.debug(f"Calculation params: {self.calculation_params}")
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.
        
        Returns:
            List of scoring levels with combined score thresholds
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            # Get rubric for resource_availability parameter
            resource_config = params_config['parameters'].get('resource_availability', {})
            scoring = resource_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_combined": item.get('min_combined', 0.0),
                        "max_combined": item.get('max_combined', 100.0),
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
    
    def _load_calculation_params(self) -> Dict[str, float]:
        """Load calculation parameters from configuration.
        
        Returns:
            Dictionary with normalization and weighting parameters
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            resource_config = params_config['parameters'].get('resource_availability', {})
            calc_config = resource_config.get('calculation', {})
            
            if calc_config:
                logger.info("Loaded calculation parameters from config")
                return {
                    "solar_weight": calc_config.get('solar_weight', 0.5),
                    "wind_weight": calc_config.get('wind_weight', 0.5),
                    "solar_normalization": calc_config.get('solar_normalization', 2.5),
                    "wind_normalization": calc_config.get('wind_normalization', 1.0)
                }
            else:
                logger.warning("No calculation params in config, using defaults")
                return self._get_default_calculation_params()
                
        except Exception as e:
            logger.warning(f"Could not load calculation params: {e}. Using defaults.")
            return self._get_default_calculation_params()
    
    def _get_default_calculation_params(self) -> Dict[str, float]:
        """Get default calculation parameters.
        
        Returns:
            Default normalization and weighting parameters
        """
        return {
            "solar_weight": 0.5,
            "wind_weight": 0.5,
            "solar_normalization": 6.5,
            "wind_normalization": 9.0
        }
    
    def _get_fallback_rubric(self) -> List[Dict[str, Any]]:
        """Fallback scoring rubric if config is not available.
        
        This ensures agent works even without full config.
        
        Returns:
            Default scoring rubric
        """
        return [
            {"score": 1, "min_combined": 0.0, "max_combined": 2.0, "range": "< 2.0", "description": "Very poor resources (both solar and wind weak)"},
            {"score": 2, "min_combined": 2.0, "max_combined": 3.0, "range": "2.0-3.0", "description": "Poor resources"},
            {"score": 3, "min_combined": 3.0, "max_combined": 4.0, "range": "3.0-4.0", "description": "Below average resources"},
            {"score": 4, "min_combined": 4.0, "max_combined": 5.0, "range": "4.0-5.0", "description": "Moderate resources"},
            {"score": 5, "min_combined": 5.0, "max_combined": 6.0, "range": "5.0-6.0", "description": "Average resources"},
            {"score": 6, "min_combined": 6.0, "max_combined": 7.0, "range": "6.0-7.0", "description": "Good resources"},
            {"score": 7, "min_combined": 7.0, "max_combined": 8.0, "range": "7.0-8.0", "description": "Very good resources"},
            {"score": 8, "min_combined": 8.0, "max_combined": 9.0, "range": "8.0-9.0", "description": "Excellent resources"},
            {"score": 9, "min_combined": 9.0, "max_combined": 10.0, "range": "9.0-10.0", "description": "Outstanding resources"},
            {"score": 10, "min_combined": 10.0, "max_combined": 100.0, "range": "≥ 10.0", "description": "World-class resources (exceptional solar and wind)"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze resource availability for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Resource Availability for {country} ({period})")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate combined resource score
            combined_score = self._calculate_combined_resource_score(data, country)
            
            # Step 3: Map to 1-10 score
            score = self._calculate_score(combined_score, country, period)
            
            # Step 4: Validate score
            score = self._validate_score(score)
            
            # Step 5: Generate justification
            justification = self._generate_justification(data, combined_score, score, country, period)
            
            # Step 6: Estimate confidence
            # Solar and wind atlas data is high quality
            data_quality = "high" if data else "low"
            confidence = self._estimate_confidence(data, data_quality)
            
            # Step 7: Identify data sources
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
                f"Resource Availability analysis complete for {country}: "
                f"Score={score}, Combined={combined_score:.1f}, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Resource Availability analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Resource Availability analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch renewable resource data.
        
        In MOCK mode: Returns mock solar and wind data
        In RULE mode: Would query GIS database
        In AI mode: Would use LLM to extract from atlas documents
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with solar and wind resource data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate resources")
                data = {
                    "solar_kwh_m2_day": 4.0,
                    "wind_m_s": 5.0,
                    "solar_quality": "Moderate",
                    "wind_quality": "Moderate"
                }
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # TODO Phase 2: Query from GIS database
            # return self._query_resource_database(country, period)
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from atlas documents
            # return self._llm_extract_resources(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_combined_resource_score(
        self,
        data: Dict[str, Any],
        country: str
    ) -> float:
        """Calculate combined resource score from solar and wind data.
        
        Normalizes solar and wind to 0-10 scale, then calculates weighted average.
        
        Args:
            data: Resource data with solar and wind metrics
            country: Country name
            
        Returns:
            Combined resource score (0-10+ scale)
        """
        solar_kwh = data.get("solar_kwh_m2_day", 0)
        wind_ms = data.get("wind_m_s", 0)
        
        # Get calculation parameters
        solar_norm = self.calculation_params["solar_normalization"]
        wind_norm = self.calculation_params["wind_normalization"]
        solar_weight = self.calculation_params["solar_weight"]
        wind_weight = self.calculation_params["wind_weight"]
        
        # Normalize to 0-10 scale
        solar_normalized = (solar_kwh / solar_norm) * 10
        wind_normalized = (wind_ms / wind_norm) * 10
        
        # Calculate weighted average
        combined = (solar_normalized * solar_weight) + (wind_normalized * wind_weight)
        
        logger.debug(
            f"Combined score for {country}: "
            f"Solar {solar_kwh} kWh/m²/day ({solar_normalized:.1f}/10) × {solar_weight} + "
            f"Wind {wind_ms} m/s ({wind_normalized:.1f}/10) × {wind_weight} = "
            f"{combined:.1f}"
        )
        
        return combined
    
    def _calculate_score(
        self,
        combined_score: float,
        country: str,
        period: str
    ) -> float:
        """Map combined resource score to 1-10 rating.
        
        Args:
            combined_score: Combined resource score
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        logger.debug(f"Calculating rating for {country}: combined score {combined_score:.1f}")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_combined = level.get("min_combined", 0.0)
            max_combined = level.get("max_combined", 100.0)
            
            if min_combined <= combined_score < max_combined:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"Combined {combined_score:.1f} falls in range {min_combined}-{max_combined}"
                )
                return float(score)
        
        # Fallback (shouldn't reach here with proper rubric)
        logger.warning(f"No rubric match for combined score {combined_score:.1f}, defaulting to 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        combined_score: float,
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the resource availability score.
        
        Args:
            data: Resource data
            combined_score: Combined resource score
            score: Final 1-10 score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        solar_kwh = data.get("solar_kwh_m2_day", 0)
        wind_ms = data.get("wind_m_s", 0)
        solar_quality = data.get("solar_quality", "moderate")
        wind_quality = data.get("wind_quality", "moderate")
        
        # Find description from rubric
        description = "average renewable energy resources"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification
        justification = (
            f"Solar irradiation of {solar_kwh:.1f} kWh/m²/day ({solar_quality.lower()}) "
            f"and wind speeds of {wind_ms:.1f} m/s ({wind_quality.lower()}) "
            f"indicate {description}. "
            f"Combined resource score of {combined_score:.1f} enables cost-effective "
            f"renewable energy deployment."
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
            "Global Solar Atlas (World Bank) 2024",
            "Global Wind Atlas (DTU) 2024",
            f"{country} Renewable Energy Resource Assessment"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Resource Availability parameter.
        
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
            "Global Solar Atlas (World Bank)",
            "Global Wind Atlas (DTU Wind Energy)",
            "NREL Renewable Energy Data",
            "NASA POWER Data Access Viewer",
            "National renewable energy resource assessments"
        ]


# Convenience function for direct usage
def analyze_resource_availability(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze resource availability.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode
        
    Returns:
        ParameterScore
    """
    agent = ResourceAvailabilityAgent(mode=mode)
    return agent.analyze(country, period)
