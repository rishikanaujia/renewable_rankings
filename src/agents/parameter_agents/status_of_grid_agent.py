"""Status of Grid Agent - Analyzes grid infrastructure quality and reliability.

This agent evaluates the electricity grid infrastructure quality by analyzing:
- Grid reliability (SAIDI/SAIFI outage metrics)
- Transmission capacity and congestion
- Infrastructure modernization and smartgrid capabilities

Higher grid quality enables:
- Greater renewable energy integration
- Reduced curtailment risk
- Lower connection costs
- Faster project development

Grid Quality Composite Score (0-10):
- 0-1: Critical deficiencies (frequent outages, severe congestion)
- 1-2: Major challenges (poor reliability, limited capacity)
- 2-3: Significant constraints (regular congestion, aging)
- 3-4: Below adequate (moderate reliability issues)
- 4-5: Adequate (basic functionality, some constraints)
- 5-6: Above adequate (reliable, minor constraints)
- 6-7: Good (strong reliability, manageable constraints)
- 7-8: Very good (high reliability, modern infrastructure)
- 8-9: Excellent (very high reliability, advanced)
- 9-10: Outstanding (world-class, cutting-edge)

Scoring Rubric (LOADED FROM CONFIG):
Higher grid quality = Better infrastructure = Higher score (DIRECT relationship)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class StatusOfGridAgent(BaseParameterAgent):
    """Agent for analyzing grid infrastructure status and quality."""
    
    # Mock data for Phase 1 testing
    # Composite grid quality scores (0-10) based on:
    # - Reliability (SAIDI/SAIFI metrics)
    # - Transmission capacity
    # - Infrastructure quality
    # Data from World Bank, IEA, national grid operators
    MOCK_DATA = {
        "Brazil": {
            "grid_score": 6.5,
            "saidi_minutes": 720,  # System Average Interruption Duration Index
            "saifi_outages": 8.5,  # System Average Interruption Frequency Index
            "transmission_gw": 180,
            "congestion_level": "Moderate",
            "infrastructure_age": "Mixed (aging with new investments)",
            "smartgrid_deployment": "Moderate",
            "status": "Good grid (reliable with manageable constraints)"
        },
        "Germany": {
            "grid_score": 9.2,
            "saidi_minutes": 12,  # Among world's best
            "saifi_outages": 0.3,
            "transmission_gw": 220,
            "congestion_level": "Low",
            "infrastructure_age": "Modern",
            "smartgrid_deployment": "Advanced",
            "status": "Excellent grid (world-class Energiewende infrastructure)"
        },
        "USA": {
            "grid_score": 7.8,
            "saidi_minutes": 240,
            "saifi_outages": 1.3,
            "transmission_gw": 700,
            "congestion_level": "Moderate",
            "infrastructure_age": "Aging but upgrading",
            "smartgrid_deployment": "Moderate to Advanced",
            "status": "Very good grid (large but aging, regional variation)"
        },
        "China": {
            "grid_score": 8.2,
            "saidi_minutes": 180,
            "saifi_outages": 1.8,
            "transmission_gw": 1500,
            "congestion_level": "Low to Moderate",
            "infrastructure_age": "Modern (massive recent investment)",
            "smartgrid_deployment": "Advanced",
            "status": "Very good grid (UHVDC backbone, rapid modernization)"
        },
        "India": {
            "grid_score": 5.8,
            "saidi_minutes": 480,
            "saifi_outages": 6.2,
            "transmission_gw": 450,
            "congestion_level": "Moderate to High",
            "infrastructure_age": "Mixed",
            "smartgrid_deployment": "Emerging",
            "status": "Above adequate (improving but faces congestion)"
        },
        "UK": {
            "grid_score": 8.8,
            "saidi_minutes": 48,
            "saifi_outages": 0.6,
            "transmission_gw": 75,
            "congestion_level": "Low",
            "infrastructure_age": "Modern",
            "smartgrid_deployment": "Advanced",
            "status": "Excellent grid (high reliability, offshore wind ready)"
        },
        "Spain": {
            "grid_score": 7.5,
            "saidi_minutes": 96,
            "saifi_outages": 1.2,
            "transmission_gw": 105,
            "congestion_level": "Low to Moderate",
            "infrastructure_age": "Modern",
            "smartgrid_deployment": "Moderate to Advanced",
            "status": "Very good grid (strong renewables integration)"
        },
        "Australia": {
            "grid_score": 7.2,
            "saidi_minutes": 120,
            "saifi_outages": 1.8,
            "transmission_gw": 50,
            "congestion_level": "Moderate",
            "infrastructure_age": "Aging in parts",
            "smartgrid_deployment": "Moderate",
            "status": "Good grid (long distances, regional challenges)"
        },
        "Chile": {
            "grid_score": 6.8,
            "saidi_minutes": 180,
            "saifi_outages": 2.5,
            "transmission_gw": 25,
            "congestion_level": "Moderate",
            "infrastructure_age": "Mixed",
            "smartgrid_deployment": "Emerging to Moderate",
            "status": "Good grid (improving, Norte-Centro interconnection)"
        },
        "Vietnam": {
            "grid_score": 5.2,
            "saidi_minutes": 540,
            "saifi_outages": 7.8,
            "transmission_gw": 65,
            "congestion_level": "High",
            "infrastructure_age": "Aging with bottlenecks",
            "smartgrid_deployment": "Limited",
            "status": "Adequate grid (rapid demand growth straining system)"
        },
        "South Africa": {
            "grid_score": 4.8,
            "saidi_minutes": 1200,  # Load shedding frequent
            "saifi_outages": 15.0,
            "transmission_gw": 40,
            "congestion_level": "High",
            "infrastructure_age": "Aging",
            "smartgrid_deployment": "Limited",
            "status": "Adequate grid (Eskom challenges, load shedding)"
        },
        "Nigeria": {
            "grid_score": 2.5,
            "saidi_minutes": 4200,  # Very poor reliability
            "saifi_outages": 35.0,
            "transmission_gw": 8,
            "congestion_level": "Severe",
            "infrastructure_age": "Very old, deteriorated",
            "smartgrid_deployment": "Minimal",
            "status": "Significant constraints (frequent outages, severe congestion)"
        },
        "Argentina": {
            "grid_score": 5.5,
            "saidi_minutes": 420,
            "saifi_outages": 6.0,
            "transmission_gw": 45,
            "congestion_level": "Moderate to High",
            "infrastructure_age": "Aging",
            "smartgrid_deployment": "Limited",
            "status": "Adequate grid (investment needed)"
        },
        "Mexico": {
            "grid_score": 6.2,
            "saidi_minutes": 300,
            "saifi_outages": 4.2,
            "transmission_gw": 95,
            "congestion_level": "Moderate",
            "infrastructure_age": "Mixed",
            "smartgrid_deployment": "Moderate",
            "status": "Above adequate (CFE modernization ongoing)"
        },
        "Indonesia": {
            "grid_score": 4.5,
            "saidi_minutes": 720,
            "saifi_outages": 12.0,
            "transmission_gw": 75,
            "congestion_level": "High",
            "infrastructure_age": "Mixed, island challenges",
            "smartgrid_deployment": "Limited",
            "status": "Below adequate (archipelago challenges, reliability issues)"
        },
        "Saudi Arabia": {
            "grid_score": 7.8,
            "saidi_minutes": 60,
            "saifi_outages": 0.8,
            "transmission_gw": 85,
            "congestion_level": "Low",
            "infrastructure_age": "Modern",
            "smartgrid_deployment": "Moderate to Advanced",
            "status": "Very good grid (well-funded, Vision 2030 investment)"
        },
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Status of Grid Agent."""
        super().__init__(
            parameter_name="Status of Grid",
            mode=mode,
            config=config
        )
        
        # Load scoring rubric from config
        self.scoring_rubric = self._load_scoring_rubric()
        
        logger.debug(f"Loaded scoring rubric with {len(self.scoring_rubric)} levels")
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            grid_config = params_config['parameters'].get('status_of_grid', {})
            scoring = grid_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_score": item.get('min_score', 0.0),
                        "max_score": item.get('max_score', 10.1),
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
        """Fallback scoring rubric if config is not available."""
        return [
            {"score": 1, "min_score": 0.0, "max_score": 1.0, "range": "0-1", "description": "Critical grid deficiencies"},
            {"score": 2, "min_score": 1.0, "max_score": 2.0, "range": "1-2", "description": "Major grid challenges"},
            {"score": 3, "min_score": 2.0, "max_score": 3.0, "range": "2-3", "description": "Significant grid constraints"},
            {"score": 4, "min_score": 3.0, "max_score": 4.0, "range": "3-4", "description": "Below adequate grid"},
            {"score": 5, "min_score": 4.0, "max_score": 5.0, "range": "4-5", "description": "Adequate grid"},
            {"score": 6, "min_score": 5.0, "max_score": 6.0, "range": "5-6", "description": "Above adequate grid"},
            {"score": 7, "min_score": 6.0, "max_score": 7.0, "range": "6-7", "description": "Good grid"},
            {"score": 8, "min_score": 7.0, "max_score": 8.0, "range": "7-8", "description": "Very good grid"},
            {"score": 9, "min_score": 8.0, "max_score": 9.0, "range": "8-9", "description": "Excellent grid"},
            {"score": 10, "min_score": 9.0, "max_score": 10.1, "range": "9-10", "description": "Outstanding grid"}
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze grid status for a country."""
        try:
            logger.info(f"Analyzing Status of Grid for {country} ({period})")
            
            data = self._fetch_data(country, period, **kwargs)
            score = self._calculate_score(data, country, period)
            score = self._validate_score(score)
            justification = self._generate_justification(data, score, country, period)
            
            data_quality = "high" if data else "low"
            confidence = self._estimate_confidence(data, data_quality)
            data_sources = self._get_data_sources(country)
            
            result = ParameterScore(
                parameter_name=self.parameter_name,
                score=score,
                justification=justification,
                data_sources=data_sources,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
            logger.info(
                f"Status of Grid analysis complete for {country}: "
                f"Score={score}, GridScore={data.get('grid_score', 0):.1f}, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Status of Grid analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Status of Grid analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch grid status data."""
        if self.mode == AgentMode.MOCK:
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default adequate grid")
                data = {
                    "grid_score": 5.0,
                    "saidi_minutes": 400,
                    "saifi_outages": 5.0,
                    "transmission_gw": 50,
                    "congestion_level": "Moderate",
                    "infrastructure_age": "Mixed",
                    "smartgrid_deployment": "Limited",
                    "status": "Adequate grid"
                }
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(self, data: Dict[str, Any], country: str, period: str) -> float:
        """Calculate grid status score.
        
        DIRECT: Higher grid quality = better infrastructure = higher score
        """
        grid_score = data.get("grid_score", 5.0)
        
        logger.debug(f"Calculating score for {country}: {grid_score:.1f} grid quality score")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_val = level.get("min_score", 0.0)
            max_val = level.get("max_score", 10.1)
            
            if min_val <= grid_score < max_val:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{grid_score:.1f} falls in range {min_val:.1f}-{max_val:.1f}"
                )
                return float(score)
        
        # Fallback
        logger.warning(f"No rubric match for {grid_score:.1f}, defaulting to score 5")
        return 5.0
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the grid status score."""
        grid_score = data.get("grid_score", 5.0)
        saidi = data.get("saidi_minutes", 0)
        saifi = data.get("saifi_outages", 0)
        transmission = data.get("transmission_gw", 0)
        congestion = data.get("congestion_level", "moderate")
        infrastructure = data.get("infrastructure_age", "mixed")
        smartgrid = data.get("smartgrid_deployment", "limited")
        status = data.get("status", "adequate grid")
        
        description = "adequate grid"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        justification = (
            f"Grid quality score of {grid_score:.1f}/10 indicates {description}. "
            f"Reliability metrics show SAIDI of {saidi:.0f} minutes/year and SAIFI of {saifi:.1f} outages/year. "
            f"Transmission capacity of {transmission:.0f} GW with {congestion.lower()} congestion levels. "
        )
        
        justification += (
            f"Infrastructure is {infrastructure.lower()} with {smartgrid.lower()} smartgrid deployment. "
            f"{status.capitalize()}. "
        )
        
        justification += (
            f"This grid infrastructure {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports renewable energy integration and reduces curtailment risk."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "World Bank Enterprise Surveys",
            "IEA Electricity Security reports",
            f"{country} National grid operator",
            "SAIDI/SAIFI reliability metrics",
            "Transmission capacity reports"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Status of Grid parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
        return [
            "World Bank Enterprise Surveys",
            "IEA Electricity Security reports",
            "National grid operator data",
            "SAIDI/SAIFI reliability metrics",
            "Transmission capacity reports",
            "Grid modernization reports"
        ]


def analyze_status_of_grid(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze grid status."""
    agent = StatusOfGridAgent(mode=mode)
    return agent.analyze(country, period)
