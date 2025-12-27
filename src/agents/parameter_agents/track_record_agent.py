"""Track Record Agent - Analyzes historical renewable energy deployment.

This agent evaluates the cumulative installed renewable energy capacity (solar PV +
onshore wind + offshore wind) in each country. Higher installed capacity demonstrates:
- Proven market execution capability
- Established supply chains and expertise
- Reduced regulatory and execution risk
- Track record of successful project development

Installed Capacity Scale:
- < 100 MW: Minimal (nascent market)
- 100-500 MW: Very limited
- 500-1000 MW: Limited (early stage)
- 1-2.5 GW: Below moderate
- 2.5-5 GW: Moderate (emerging)
- 5-10 GW: Above moderate
- 10-25 GW: Good (established)
- 25-50 GW: Very good
- 50-100 GW: Excellent (major market)
- ≥ 100 GW: Outstanding (world leader)

Scoring Rubric (LOADED FROM CONFIG):
Higher installed capacity = Better track record = Higher score (DIRECT relationship)

MODES:
- MOCK: Uses hardcoded test data (for testing)
- RULE_BASED: Fetches from World Bank renewable capacity data or estimates from generation data (production)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class TrackRecordAgent(BaseParameterAgent):
    """Agent for analyzing renewable energy deployment track record."""
    
    # Mock data for Phase 1 testing
    # Cumulative installed capacity (MW) for solar PV + onshore wind + offshore wind
    # Data from IRENA Renewable Capacity Statistics 2023
    MOCK_DATA = {
        "Brazil": {
            "capacity_mw": 38500,
            "solar_mw": 24000,
            "onshore_wind_mw": 14200,
            "offshore_wind_mw": 300,
            "recent_deployment_gw_per_year": 6.5,
            "status": "Very good track record (major Latin America market)"
        },
        "Germany": {
            "capacity_mw": 134000,
            "solar_mw": 67000,
            "onshore_wind_mw": 58000,
            "offshore_wind_mw": 9000,
            "recent_deployment_gw_per_year": 8.2,
            "status": "Outstanding track record (world leader, Energiewende)"
        },
        "USA": {
            "capacity_mw": 257000,
            "solar_mw": 115000,
            "onshore_wind_mw": 137000,
            "offshore_wind_mw": 5000,
            "recent_deployment_gw_per_year": 32.5,
            "status": "Outstanding track record (world's largest market)"
        },
        "China": {
            "capacity_mw": 758000,
            "solar_mw": 414000,
            "onshore_wind_mw": 336000,
            "offshore_wind_mw": 8000,
            "recent_deployment_gw_per_year": 125.0,
            "status": "Outstanding track record (absolute world leader)"
        },
        "India": {
            "capacity_mw": 175000,
            "solar_mw": 66000,
            "onshore_wind_mw": 109000,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 18.5,
            "status": "Outstanding track record (third largest market)"
        },
        "UK": {
            "capacity_mw": 49000,
            "solar_mw": 14500,
            "onshore_wind_mw": 14500,
            "offshore_wind_mw": 20000,
            "recent_deployment_gw_per_year": 4.2,
            "status": "Very good track record (offshore wind leader)"
        },
        "Spain": {
            "capacity_mw": 53000,
            "solar_mw": 20000,
            "onshore_wind_mw": 33000,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 7.8,
            "status": "Excellent track record (early wind pioneer)"
        },
        "Australia": {
            "capacity_mw": 28000,
            "solar_mw": 21000,
            "onshore_wind_mw": 7000,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 3.5,
            "status": "Very good track record (rooftop solar leader)"
        },
        "Chile": {
            "capacity_mw": 11500,
            "solar_mw": 6500,
            "onshore_wind_mw": 5000,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 1.8,
            "status": "Good track record (Atacama solar boom)"
        },
        "Vietnam": {
            "capacity_mw": 19500,
            "solar_mw": 16500,
            "onshore_wind_mw": 3000,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 5.2,
            "status": "Good track record (FiT-driven rapid growth)"
        },
        "South Africa": {
            "capacity_mw": 7200,
            "solar_mw": 3800,
            "onshore_wind_mw": 3400,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 0.8,
            "status": "Above moderate (REIPPP success, but slow)"
        },
        "Nigeria": {
            "capacity_mw": 180,
            "solar_mw": 150,
            "onshore_wind_mw": 30,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 0.05,
            "status": "Minimal track record (nascent market)"
        },
        "Argentina": {
            "capacity_mw": 6500,
            "solar_mw": 1500,
            "onshore_wind_mw": 5000,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 1.2,
            "status": "Above moderate (RenovAr driving growth)"
        },
        "Mexico": {
            "capacity_mw": 15800,
            "solar_mw": 8500,
            "onshore_wind_mw": 7300,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 2.1,
            "status": "Good track record (auction success)"
        },
        "Indonesia": {
            "capacity_mw": 950,
            "solar_mw": 450,
            "onshore_wind_mw": 500,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 0.15,
            "status": "Limited track record (early stage)"
        },
        "Saudi Arabia": {
            "capacity_mw": 1800,
            "solar_mw": 1700,
            "onshore_wind_mw": 100,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 0.6,
            "status": "Below moderate (Vision 2030 starting)"
        },
    }
    
    def __init__(
        self,
        mode: AgentMode = AgentMode.MOCK,
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Track Record Agent.

        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Track Record",
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

        # Load scoring rubric from config
        self.scoring_rubric = self._load_scoring_rubric()

        logger.debug(
            f"Initialized TrackRecordAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            track_config = params_config['parameters'].get('track_record', {})
            scoring = track_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_capacity_mw": item.get('min_capacity_mw', 0),
                        "max_capacity_mw": item.get('max_capacity_mw', 10000000),
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
            {"score": 1, "min_capacity_mw": 0, "max_capacity_mw": 100, "range": "<100MW", "description": "Minimal track record (nascent market)"},
            {"score": 2, "min_capacity_mw": 100, "max_capacity_mw": 500, "range": "100-500MW", "description": "Very limited track record"},
            {"score": 3, "min_capacity_mw": 500, "max_capacity_mw": 1000, "range": "500MW-1GW", "description": "Limited track record (early stage)"},
            {"score": 4, "min_capacity_mw": 1000, "max_capacity_mw": 2500, "range": "1-2.5GW", "description": "Below moderate track record"},
            {"score": 5, "min_capacity_mw": 2500, "max_capacity_mw": 5000, "range": "2.5-5GW", "description": "Moderate track record (emerging market)"},
            {"score": 6, "min_capacity_mw": 5000, "max_capacity_mw": 10000, "range": "5-10GW", "description": "Above moderate track record"},
            {"score": 7, "min_capacity_mw": 10000, "max_capacity_mw": 25000, "range": "10-25GW", "description": "Good track record (established market)"},
            {"score": 8, "min_capacity_mw": 25000, "max_capacity_mw": 50000, "range": "25-50GW", "description": "Very good track record"},
            {"score": 9, "min_capacity_mw": 50000, "max_capacity_mw": 100000, "range": "50-100GW", "description": "Excellent track record (major market)"},
            {"score": 10, "min_capacity_mw": 100000, "max_capacity_mw": 10000000, "range": "≥100GW", "description": "Outstanding track record (world leader)"}
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze track record for a country."""
        try:
            logger.info(f"Analyzing Track Record for {country} ({period})")
            
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
                f"Track Record analysis complete for {country}: "
                f"Score={score}, Capacity={data.get('capacity_mw', 0):.0f}MW, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Track Record analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Track Record analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch track record data.

        In MOCK mode: Returns mock installed capacity data
        In RULE_BASED mode: Fetches from World Bank renewable capacity data
        In AI_POWERED mode: Would use LLM to extract from IRENA/IEA reports (not yet implemented)

        Args:
            country: Country name
            period: Time period

        Returns:
            Dictionary with track record data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default limited track record")
                data = {
                    "capacity_mw": 800,
                    "solar_mw": 400,
                    "onshore_wind_mw": 400,
                    "offshore_wind_mw": 0,
                    "recent_deployment_gw_per_year": 0.1,
                    "status": "Limited track record"
                }

            # Add source indicator
            data['source'] = 'mock'

            logger.debug(f"Fetched mock data for {country}: {data.get('capacity_mw', 0):.0f} MW")
            return data

        elif self.mode == AgentMode.RULE_BASED:
            # Fetch from World Bank renewable capacity data
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)

            try:
                # Fetch renewable capacity from World Bank
                # World Bank indicator: EG.ELC.RNWX.KH (Renewable electricity output, kWh)
                # or renewable_capacity if available
                renewable_capacity_gw = self.data_service.get_value(
                    country=country,
                    indicator='renewable_capacity',
                    default=None
                )

                # Also try to get electricity production for context
                electricity_production_kwh = self.data_service.get_value(
                    country=country,
                    indicator='electricity_production',
                    default=None
                )

                # Get renewable consumption % for additional context
                renewable_consumption_pct = self.data_service.get_value(
                    country=country,
                    indicator='renewable_consumption',
                    default=None
                )

                if renewable_capacity_gw is None:
                    # Try to estimate from electricity production and renewable percentage
                    if electricity_production_kwh and renewable_consumption_pct:
                        # Very rough estimation: assume capacity factor of ~25% (typical for solar/wind)
                        # electricity_production_kwh is total annual electricity production in kWh
                        renewable_generation_kwh = electricity_production_kwh * (renewable_consumption_pct / 100)
                        hours_per_year = 8760
                        capacity_factor = 0.25
                        # Capacity (kW) = Annual generation (kWh) / (hours/year * capacity_factor)
                        estimated_capacity_kw = renewable_generation_kwh / (hours_per_year * capacity_factor)
                        # Convert kW to GW
                        renewable_capacity_gw = estimated_capacity_kw / 1_000_000

                        logger.info(
                            f"Estimated renewable capacity for {country}: {renewable_capacity_gw:.2f} GW "
                            f"(from {renewable_generation_kwh:.0f} kWh annual generation, "
                            f"{renewable_consumption_pct:.1f}% renewable share)"
                        )
                    else:
                        logger.warning(
                            f"No renewable capacity data for {country}, falling back to MOCK data"
                        )
                        return self._fetch_data_mock_fallback(country)

                # Convert GW to MW
                capacity_mw = renewable_capacity_gw * 1000

                # Estimate breakdown (we don't have detailed breakdown from World Bank)
                # Use typical global ratios as proxy: ~40% solar, ~55% wind, ~5% offshore
                solar_mw = capacity_mw * 0.40
                onshore_wind_mw = capacity_mw * 0.50
                offshore_wind_mw = capacity_mw * 0.05

                # Estimate recent deployment (assume ~15% annual growth rate as global average)
                recent_deployment_gw_per_year = renewable_capacity_gw * 0.15

                # Determine status based on capacity
                status = self._determine_deployment_status(capacity_mw)

                data = {
                    'capacity_mw': capacity_mw,
                    'solar_mw': solar_mw,
                    'onshore_wind_mw': onshore_wind_mw,
                    'offshore_wind_mw': offshore_wind_mw,
                    'recent_deployment_gw_per_year': recent_deployment_gw_per_year,
                    'status': status,
                    'source': 'rule_based',
                    'period': period
                }

                logger.info(
                    f"Calculated RULE_BASED data for {country}: {capacity_mw:.0f} MW capacity "
                    f"({renewable_capacity_gw:.2f} GW total)"
                )

                return data

            except Exception as e:
                logger.error(
                    f"Error fetching track record for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)

        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from IRENA/IEA reports
            # return self._llm_extract_track_record(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")

        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(self, data: Dict[str, Any], country: str, period: str) -> float:
        """Calculate track record score based on installed capacity.
        
        DIRECT: Higher capacity = better track record = higher score
        """
        capacity_mw = data.get("capacity_mw", 0)
        
        logger.debug(f"Calculating score for {country}: {capacity_mw:.0f} MW installed")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_cap = level.get("min_capacity_mw", 0)
            max_cap = level.get("max_capacity_mw", 10000000)
            
            if min_cap <= capacity_mw < max_cap:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{capacity_mw:.0f}MW falls in range {min_cap:.0f}-{max_cap:.0f}MW"
                )
                return float(score)
        
        # Fallback
        logger.warning(f"No rubric match for {capacity_mw:.0f}MW, defaulting to score 5")
        return 5.0
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the track record score."""
        capacity_mw = data.get("capacity_mw", 0)
        capacity_gw = capacity_mw / 1000.0
        solar_gw = data.get("solar_mw", 0) / 1000.0
        wind_gw = data.get("onshore_wind_mw", 0) / 1000.0
        offshore_gw = data.get("offshore_wind_mw", 0) / 1000.0
        recent_deployment = data.get("recent_deployment_gw_per_year", 0)
        status = data.get("status", "moderate track record")
        
        description = "moderate track record"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        justification = (
            f"Cumulative installed capacity of {capacity_gw:.1f} GW "
            f"(solar: {solar_gw:.1f} GW, wind: {wind_gw:.1f} GW"
        )
        
        if offshore_gw > 0:
            justification += f", offshore: {offshore_gw:.1f} GW"
        
        justification += f") indicates {description}. "
        justification += f"Recent deployment of {recent_deployment:.1f} GW/year shows market momentum. "
        justification += (
            f"{status.capitalize()}. "
            f"This track record {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"demonstrates proven execution capability and reduces regulatory risk."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "IRENA Renewable Energy Statistics",
            "IEA Renewables Market Report",
            f"{country} National renewable energy agency",
            "Bloomberg New Energy Finance (BNEF)",
            "Wood Mackenzie Power & Renewables"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Track Record parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
        return [
            "IRENA Renewable Energy Statistics",
            "IEA Renewables Market Report",
            "National renewable energy agencies",
            "Industry databases (BNEF, Wood Mackenzie)",
            "Project databases and registries"
        ]

    def _fetch_data_mock_fallback(self, country: str) -> Dict[str, Any]:
        """Fallback to mock data when rule-based data is unavailable.

        Args:
            country: Country name

        Returns:
            Mock data with source indicator
        """
        data = self.MOCK_DATA.get(country, None)
        if not data:
            logger.warning(f"No mock fallback data for {country}, using default")
            data = {
                "capacity_mw": 800,
                "solar_mw": 400,
                "onshore_wind_mw": 400,
                "offshore_wind_mw": 0,
                "recent_deployment_gw_per_year": 0.1,
                "status": "Limited track record (estimated)"
            }

        # Add source indicator
        data['source'] = 'mock_fallback'

        logger.debug(f"Using mock fallback data for {country}")
        return data

    def _determine_deployment_status(self, capacity_mw: float) -> str:
        """Determine deployment status description based on capacity.

        Args:
            capacity_mw: Installed renewable capacity in MW

        Returns:
            Status description string
        """
        if capacity_mw >= 100000:
            return "Outstanding track record (world leader)"
        elif capacity_mw >= 50000:
            return "Excellent track record (major market)"
        elif capacity_mw >= 25000:
            return "Very good track record"
        elif capacity_mw >= 10000:
            return "Good track record (established market)"
        elif capacity_mw >= 5000:
            return "Above moderate track record"
        elif capacity_mw >= 2500:
            return "Moderate track record (emerging market)"
        elif capacity_mw >= 1000:
            return "Below moderate track record"
        elif capacity_mw >= 500:
            return "Limited track record (early stage)"
        elif capacity_mw >= 100:
            return "Very limited track record"
        else:
            return "Minimal track record (nascent market)"


def analyze_track_record(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze track record.

    Args:
        country: Country name
        period: Time period
        mode: Agent operation mode
        data_service: DataService instance (required for RULE_BASED mode)

    Returns:
        ParameterScore with track record analysis
    """
    agent = TrackRecordAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
