"""Renewables Penetration Agent - Analyzes renewable energy share in electricity generation.

This agent evaluates the current penetration of renewable energy sources (solar, wind,
hydro, biomass, geothermal) in a country's electricity generation mix. Higher penetration
indicates market maturity, proven integration capabilities, and favorable conditions for
further renewable development.

Renewables Share Scale:
- < 5%: Minimal renewables (fossil fuel dominated)
- 5-10%: Very low penetration
- 10-15%: Low penetration
- 15-20%: Below moderate
- 20-30%: Moderate penetration
- 30-40%: Above moderate
- 40-50%: High penetration
- 50-60%: Very high penetration
- 60-75%: Outstanding penetration
- ≥ 75%: World-leading (renewable-dominated grid)

Scoring Rubric (LOADED FROM CONFIG):
Higher renewables share = Better market maturity = Higher score (DIRECT relationship)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class RenewablesPenetrationAgent(BaseParameterAgent):
    """Agent for analyzing renewable energy penetration in electricity generation."""
    
    # Mock data for Phase 1 testing
    # Renewables % = (Renewable generation / Total generation) × 100
    # Includes: solar, wind, hydro, biomass, geothermal
    # Data sourced from Ember Climate Global Electricity Review 2023 / IEA
    MOCK_DATA = {
        "Brazil": {
            "renewables_pct": 83.2,  # Hydro-dominated (64%) + wind (12%) + solar + biomass
            "total_generation_twh": 631,
            "renewable_generation_twh": 525,
            "dominant_source": "Hydro",
            "status": "World-leading (hydro + wind + biomass)"
        },
        "Germany": {
            "renewables_pct": 46.2,  # Wind (27%) + solar (11%) + biomass (7%) + hydro (3%)
            "total_generation_twh": 509,
            "renewable_generation_twh": 235,
            "dominant_source": "Wind",
            "status": "High penetration (wind + solar leader)"
        },
        "USA": {
            "renewables_pct": 21.4,  # Wind (10%) + hydro (6%) + solar (4%) + biomass (1%)
            "total_generation_twh": 4050,
            "renewable_generation_twh": 867,
            "dominant_source": "Wind",
            "status": "Moderate penetration (growing rapidly)"
        },
        "China": {
            "renewables_pct": 31.8,  # Hydro (16%) + wind (9%) + solar (5%) + biomass (2%)
            "total_generation_twh": 8540,
            "renewable_generation_twh": 2716,
            "dominant_source": "Hydro",
            "status": "Above moderate (world's largest in absolute terms)"
        },
        "India": {
            "renewables_pct": 22.3,  # Hydro (10%) + wind (7%) + solar (4%) + biomass (1%)
            "total_generation_twh": 1730,
            "renewable_generation_twh": 386,
            "dominant_source": "Hydro",
            "status": "Moderate penetration (solar + wind growing fast)"
        },
        "UK": {
            "renewables_pct": 42.3,  # Wind (29%) + biomass (6%) + solar (5%) + hydro (2%)
            "total_generation_twh": 301,
            "renewable_generation_twh": 127,
            "dominant_source": "Wind",
            "status": "High penetration (offshore wind leader)"
        },
        "Spain": {
            "renewables_pct": 50.6,  # Wind (24%) + hydro (10%) + solar (14%) + biomass (3%)
            "total_generation_twh": 249,
            "renewable_generation_twh": 126,
            "dominant_source": "Wind",
            "status": "Very high penetration"
        },
        "Australia": {
            "renewables_pct": 35.9,  # Solar (14%) + wind (12%) + hydro (8%) + biomass (2%)
            "total_generation_twh": 251,
            "renewable_generation_twh": 90,
            "dominant_source": "Solar",
            "status": "Above moderate (rooftop solar leader)"
        },
        "Chile": {
            "renewables_pct": 56.3,  # Hydro (25%) + solar (18%) + wind (12%) + biomass (1%)
            "total_generation_twh": 82,
            "renewable_generation_twh": 46,
            "dominant_source": "Hydro",
            "status": "Very high penetration (solar boom)"
        },
        "Vietnam": {
            "renewables_pct": 47.8,  # Hydro (36%) + solar (10%) + wind (2%)
            "total_generation_twh": 267,
            "renewable_generation_twh": 128,
            "dominant_source": "Hydro",
            "status": "High penetration"
        },
        "South Africa": {
            "renewables_pct": 13.5,  # Solar (5%) + wind (5%) + hydro (3%)
            "total_generation_twh": 215,
            "renewable_generation_twh": 29,
            "dominant_source": "Coal (85%)",
            "status": "Low penetration (coal-dominated)"
        },
        "Nigeria": {
            "renewables_pct": 82.4,  # Hydro (81%) + solar (1%)
            "total_generation_twh": 31,
            "renewable_generation_twh": 26,
            "dominant_source": "Hydro",
            "status": "World-leading (hydro-dominated)"
        },
        "Argentina": {
            "renewables_pct": 37.5,  # Hydro (23%) + wind (11%) + solar (2%) + biomass (2%)
            "total_generation_twh": 141,
            "renewable_generation_twh": 53,
            "dominant_source": "Hydro",
            "status": "Above moderate"
        },
        "Mexico": {
            "renewables_pct": 26.8,  # Hydro (11%) + wind (9%) + solar (5%) + geothermal (2%)
            "total_generation_twh": 324,
            "renewable_generation_twh": 87,
            "dominant_source": "Hydro",
            "status": "Moderate penetration"
        },
        "Indonesia": {
            "renewables_pct": 17.2,  # Hydro (8%) + geothermal (6%) + biomass (2%) + solar (1%)
            "total_generation_twh": 303,
            "renewable_generation_twh": 52,
            "dominant_source": "Coal (60%)",
            "status": "Below moderate (geothermal potential)"
        },
        "Norway": {
            "renewables_pct": 98.5,  # Hydro (93%) + wind (5%)
            "total_generation_twh": 156,
            "renewable_generation_twh": 154,
            "dominant_source": "Hydro",
            "status": "World-leading (nearly 100% renewable)"
        },
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Renewables Penetration Agent."""
        super().__init__(
            parameter_name="Renewables Penetration",
            mode=mode,
            config=config
        )
        
        # Load scoring rubric from config (NO HARDCODING!)
        self.scoring_rubric = self._load_scoring_rubric()
        
        logger.debug(f"Loaded scoring rubric with {len(self.scoring_rubric)} levels")
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.
        
        Returns:
            List of scoring levels with renewables % thresholds
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            # Get rubric for renewables_penetration parameter
            penetration_config = params_config['parameters'].get('renewables_penetration', {})
            scoring = penetration_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_renewables_pct": item.get('min_renewables_pct', 0.0),
                        "max_renewables_pct": item.get('max_renewables_pct', 100.0),
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
            {"score": 1, "min_renewables_pct": 0.0, "max_renewables_pct": 5.0, "range": "< 5%", "description": "Minimal renewables (coal/gas/nuclear dominated)"},
            {"score": 2, "min_renewables_pct": 5.0, "max_renewables_pct": 10.0, "range": "5-10%", "description": "Very low renewables penetration"},
            {"score": 3, "min_renewables_pct": 10.0, "max_renewables_pct": 15.0, "range": "10-15%", "description": "Low renewables penetration"},
            {"score": 4, "min_renewables_pct": 15.0, "max_renewables_pct": 20.0, "range": "15-20%", "description": "Below moderate penetration"},
            {"score": 5, "min_renewables_pct": 20.0, "max_renewables_pct": 30.0, "range": "20-30%", "description": "Moderate renewables penetration"},
            {"score": 6, "min_renewables_pct": 30.0, "max_renewables_pct": 40.0, "range": "30-40%", "description": "Above moderate penetration"},
            {"score": 7, "min_renewables_pct": 40.0, "max_renewables_pct": 50.0, "range": "40-50%", "description": "High renewables penetration"},
            {"score": 8, "min_renewables_pct": 50.0, "max_renewables_pct": 60.0, "range": "50-60%", "description": "Very high renewables penetration"},
            {"score": 9, "min_renewables_pct": 60.0, "max_renewables_pct": 75.0, "range": "60-75%", "description": "Outstanding renewables penetration"},
            {"score": 10, "min_renewables_pct": 75.0, "max_renewables_pct": 100.0, "range": "≥ 75%", "description": "World-leading renewables penetration (renewable-dominated grid)"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze renewables penetration for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Renewables Penetration for {country} ({period})")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # IEA/Ember electricity data is official and reliable
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
                f"Renewables Penetration analysis complete for {country}: "
                f"Score={score}, Renewables%={data.get('renewables_pct', 0):.1f}, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Renewables Penetration analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Renewables Penetration analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch renewables penetration data.
        
        In MOCK mode: Returns mock renewables % data
        In RULE mode: Would query electricity database
        In AI mode: Would use LLM to extract from IEA/Ember reports
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with renewables penetration data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate penetration")
                data = {
                    "renewables_pct": 25.0,
                    "total_generation_twh": 100,
                    "renewable_generation_twh": 25,
                    "dominant_source": "Mixed",
                    "status": "Moderate penetration"
                }
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # TODO Phase 2: Query from electricity database
            # return self._query_electricity_database(country, period)
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from IEA/Ember reports
            # return self._llm_extract_penetration(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate renewables penetration score based on %.
        
        DIRECT: Higher renewables % = better market maturity = higher score
        
        Args:
            data: Renewables penetration data with renewables_pct
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        renewables_pct = data.get("renewables_pct", 0)
        
        logger.debug(f"Calculating score for {country}: {renewables_pct:.1f}% renewables penetration")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_pct = level.get("min_renewables_pct", 0.0)
            max_pct = level.get("max_renewables_pct", 100.0)
            
            if min_pct <= renewables_pct < max_pct:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{renewables_pct:.1f}% falls in range {min_pct:.0f}-{max_pct:.0f}%"
                )
                return float(score)
        
        # Fallback (shouldn't reach here with proper rubric)
        logger.warning(f"No rubric match for {renewables_pct:.1f}%, defaulting to score 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the renewables penetration score.
        
        Args:
            data: Renewables penetration data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        renewables_pct = data.get("renewables_pct", 0)
        total_gen = data.get("total_generation_twh", 0)
        renewable_gen = data.get("renewable_generation_twh", 0)
        dominant_source = data.get("dominant_source", "mixed sources")
        status = data.get("status", "moderate penetration")
        
        # Find description from rubric
        description = "moderate renewables penetration"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification with context
        justification = (
            f"Renewables account for {renewables_pct:.1f}% of electricity generation "
            f"({renewable_gen:.0f} TWh of {total_gen:.0f} TWh total), indicating {description}. "
            f"Generation mix dominated by {dominant_source}. {status.capitalize()} demonstrates "
            f"proven renewable integration capabilities and favorable market conditions for "
            f"additional renewable investment."
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
            "Ember Climate - Global Electricity Review 2023",
            "IEA Electricity Information 2023",
            "IRENA Renewable Energy Statistics 2023",
            f"{country} National Grid Operator Data"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Renewables Penetration parameter.
        
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
            "Ember Climate - Global Electricity Review",
            "IEA Electricity Information",
            "IRENA Renewable Energy Statistics",
            "National grid operators and energy ministries",
            "Energy Information Administration (EIA)"
        ]


# Convenience function for direct usage
def analyze_renewables_penetration(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze renewables penetration.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode
        
    Returns:
        ParameterScore
    """
    agent = RenewablesPenetrationAgent(mode=mode)
    return agent.analyze(country, period)
