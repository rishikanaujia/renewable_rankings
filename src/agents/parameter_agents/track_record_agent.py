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
- MOCK: Uses hardcoded IRENA 2023 data (for testing)
- RULE_BASED: Estimates capacity from World Bank renewable indicators (production)
"""
from typing import Dict, Any, List, Optional
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
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze track record for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Track Record for {country} ({period}) in {self.mode.value} mode")
            
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
            # Rule-based data has moderate confidence (estimation-based)
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.75  # Moderate-high confidence for estimated data
            else:
                data_quality = "high"
                confidence = 0.85  # High confidence for IRENA mock data

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
                f"Track Record analysis complete for {country}: "
                f"Score={score:.1f}, Capacity={data.get('capacity_mw', 0):.0f}MW, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Track Record analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Track Record analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch track record data.
        
        In MOCK mode: Returns mock IRENA capacity data
        In RULE_BASED mode: Estimates capacity from World Bank renewable indicators
        In AI_POWERED mode: Would use LLM to extract from IRENA reports (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with installed capacity data
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
            
            logger.debug(f"Fetched mock data for {country}: {data.get('capacity_mw')}MW")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate capacity from World Bank renewable energy data
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch renewable consumption percentage
                renewable_consumption_pct = self.data_service.get_value(
                    country=country,
                    indicator='renewable_consumption',
                    default=None
                )
                
                # Fetch electricity production
                electricity_production_kwh = self.data_service.get_value(
                    country=country,
                    indicator='electricity_production',
                    default=None
                )
                
                # Fetch GDP and population for context
                gdp = self.data_service.get_value(
                    country=country,
                    indicator='gdp',
                    default=None
                )
                
                population = self.data_service.get_value(
                    country=country,
                    indicator='population',
                    default=None
                )
                
                if renewable_consumption_pct is None or electricity_production_kwh is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate installed capacity from renewable generation
                capacity_mw = self._estimate_installed_capacity(
                    country,
                    renewable_consumption_pct,
                    electricity_production_kwh,
                    gdp,
                    population
                )
                
                # Estimate technology breakdown (simplified)
                solar_mw, wind_mw = self._estimate_technology_split(
                    country,
                    capacity_mw,
                    gdp,
                    population
                )
                
                # Estimate recent deployment
                recent_deployment_gw = capacity_mw / 1000 * 0.15  # Rough estimate: 15% added in recent year
                
                # Determine status
                status = self._determine_track_record_status(capacity_mw)
                
                data = {
                    'capacity_mw': capacity_mw,
                    'solar_mw': solar_mw,
                    'onshore_wind_mw': wind_mw,
                    'offshore_wind_mw': 0,  # Can't estimate easily
                    'recent_deployment_gw_per_year': recent_deployment_gw,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'estimation_method': 'Renewable generation + capacity factor based'
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: {capacity_mw:.0f} MW capacity "
                    f"(renewable consumption={renewable_consumption_pct:.1f}%)"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating track record for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # Extract track record using AI extraction system
            try:
                from ai_extraction_system import AIExtractionAdapter

                adapter = AIExtractionAdapter(
                    llm_config=self.config.get('llm_config') if self.config else None,
                    cache_config=self.config.get('cache_config') if self.config else None
                )

                extraction_result = adapter.extract_parameter(
                    parameter_name='track_record',
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
                        'total_capacity_gw': metadata.get('capacity_gw', 0),
                        'deployment_history': 'Extracted from AI',
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
            "capacity_mw": 800,
            "solar_mw": 400,
            "onshore_wind_mw": 400,
            "offshore_wind_mw": 0,
            "recent_deployment_gw_per_year": 0.1,
            "status": "Limited track record"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_installed_capacity(
        self,
        country: str,
        renewable_consumption_pct: float,
        electricity_production_kwh: float,
        gdp: Optional[float],
        population: Optional[float]
    ) -> float:
        """Estimate installed renewable capacity from generation data.
        
        This uses capacity factors to back-calculate installed capacity from
        renewable generation. Typical capacity factors:
        - Solar PV: 15-25% (varies by location)
        - Onshore wind: 25-35%
        - Offshore wind: 35-45%
        - Hydro: 40-50%
        - Average renewable mix: ~30%
        
        Args:
            country: Country name
            renewable_consumption_pct: % of energy from renewables
            electricity_production_kwh: Total electricity production in kWh
            gdp: GDP in current USD
            population: Total population
            
        Returns:
            Estimated installed capacity in MW
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Convert electricity production to TWh
        electricity_production_twh = electricity_production_kwh / 1_000_000_000
        
        # Estimate renewable generation (TWh)
        renewable_generation_twh = electricity_production_twh * (renewable_consumption_pct / 100)
        
        # Estimate capacity factor based on country characteristics
        # Countries with high hydro: higher capacity factor (~40%)
        # Countries with solar/wind focus: lower capacity factor (~25%)
        if renewable_consumption_pct > 50:
            # Likely hydro-dominated (Brazil, Norway, etc.)
            capacity_factor = 0.40
        elif renewable_consumption_pct > 30:
            # Mixed renewable (Germany, Spain, etc.)
            capacity_factor = 0.30
        else:
            # Early-stage, likely solar/wind (USA, China, etc.)
            capacity_factor = 0.25
        
        # Calculate installed capacity
        # Capacity (MW) = Generation (TWh) / (Capacity Factor * 8760 hours) * 1,000,000
        hours_per_year = 8760
        capacity_mw = (renewable_generation_twh / (capacity_factor * hours_per_year)) * 1_000_000
        
        # Calibrate with mock data if available
        if base_data:
            base_capacity = base_data.get('capacity_mw', capacity_mw)
            # Adjust estimate to be within reasonable range of known data
            capacity_mw = (capacity_mw + base_capacity) / 2
        
        # Cap at reasonable bounds
        capacity_mw = max(50, min(capacity_mw, 1_000_000))  # 50 MW to 1,000 GW
        
        logger.debug(
            f"Capacity estimation for {country}: "
            f"renewable_gen={renewable_generation_twh:.1f}TWh, "
            f"capacity_factor={capacity_factor:.2f}, "
            f"estimated_capacity={capacity_mw:.0f}MW"
        )
        
        return capacity_mw
    
    def _estimate_technology_split(
        self,
        country: str,
        total_capacity_mw: float,
        gdp: Optional[float],
        population: Optional[float]
    ) -> tuple:
        """Estimate solar vs wind capacity split.
        
        This is a simplified heuristic. In production, use actual technology data.
        
        Args:
            country: Country name
            total_capacity_mw: Total estimated capacity
            gdp: GDP in current USD
            population: Total population
            
        Returns:
            Tuple of (solar_mw, wind_mw)
        """
        # Check if we have mock data for calibration
        base_data = self.MOCK_DATA.get(country)
        if base_data:
            # Use actual split from mock data
            solar_mw = base_data.get('solar_mw', total_capacity_mw * 0.5)
            wind_mw = base_data.get('onshore_wind_mw', total_capacity_mw * 0.5)
            # Scale to match estimated total
            scale = total_capacity_mw / (solar_mw + wind_mw) if (solar_mw + wind_mw) > 0 else 1
            return solar_mw * scale, wind_mw * scale
        
        # Default heuristic split
        # High GDP per capita countries tend toward more solar (rooftop)
        # Large land area countries tend toward more wind
        # Default: 50/50 split
        solar_mw = total_capacity_mw * 0.5
        wind_mw = total_capacity_mw * 0.5
        
        return solar_mw, wind_mw
    
    def _determine_track_record_status(self, capacity_mw: float) -> str:
        """Determine track record status from capacity.
        
        Args:
            capacity_mw: Installed capacity in MW
            
        Returns:
            Status description string
        """
        if capacity_mw < 100:
            return "Minimal track record (nascent market)"
        elif capacity_mw < 500:
            return "Very limited track record"
        elif capacity_mw < 1000:
            return "Limited track record (early stage)"
        elif capacity_mw < 2500:
            return "Below moderate track record"
        elif capacity_mw < 5000:
            return "Moderate track record (emerging market)"
        elif capacity_mw < 10000:
            return "Above moderate track record"
        elif capacity_mw < 25000:
            return "Good track record (established market)"
        elif capacity_mw < 50000:
            return "Very good track record"
        elif capacity_mw < 100000:
            return "Excellent track record (major market)"
        else:
            return "Outstanding track record (world leader)"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate track record score based on installed capacity.

        DIRECT: Higher capacity = better track record = higher score

        Args:
            data: Track record data with capacity_mw
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
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the track record score.

        Args:
            data: Track record data
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
            return f"AI-extracted track record score of {score:.1f}/10 for {country} based on deployment history and installed capacity analysis."

        capacity_mw = data.get("capacity_mw", 0)
        capacity_gw = capacity_mw / 1000.0
        solar_gw = data.get("solar_mw", 0) / 1000.0
        wind_gw = data.get("onshore_wind_mw", 0) / 1000.0
        offshore_gw = data.get("offshore_wind_mw", 0) / 1000.0
        recent_deployment = data.get("recent_deployment_gw_per_year", 0)
        status = data.get("status", "moderate track record")

        # Find description from rubric
        description = "moderate track record"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break

        # Build justification based on source
        if source == 'rule_based':
            method = data.get('estimation_method', 'renewable generation data')
            justification = (
                f"Based on {method}: Estimated cumulative installed capacity of {capacity_gw:.1f} GW "
                f"indicates {description}. Recent deployment estimated at {recent_deployment:.1f} GW/year. "
                f"{status.capitalize()}. This track record "
                f"{'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
                f"demonstrates proven execution capability and reduces regulatory risk."
            )
        else:
            # Mock data - use detailed breakdown
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
            sources.append("AI-Powered Document Extraction (Track Record)")
            sources.append("IRENA Reports and Policy Documents")
        elif data and data.get('source') == 'rule_based':
            sources.append("World Bank Renewable Energy Indicators - Rule-Based Estimation")
            sources.append("IRENA Renewable Energy Statistics 2023 (Reference)")
        else:
            sources.append("IRENA Renewable Energy Statistics 2023 - Mock Data")

        sources.append("IEA Renewables Market Report")
        sources.append(f"{country} National renewable energy agency")

        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Track Record parameter.
        
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
            "IRENA Renewable Energy Statistics",
            "IEA Renewables Market Report",
            "National renewable energy agencies",
            "Industry databases (BNEF, Wood Mackenzie)",
            "Project databases and registries"
        ]


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
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = TrackRecordAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
