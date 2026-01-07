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

MODES:
- MOCK: Uses hardcoded composite grid quality scores (for testing)
- RULE_BASED: Estimates from World Bank power transmission losses + GDP (production)
"""
from typing import Dict, Any, List, Optional
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
            "saidi_minutes": 900,
            "saifi_outages": 12.0,
            "transmission_gw": 60,
            "congestion_level": "High",
            "infrastructure_age": "Mixed to Aging",
            "smartgrid_deployment": "Limited",
            "status": "Adequate grid (island geography challenges)"
        },
        "Saudi Arabia": {
            "grid_score": 7.0,
            "saidi_minutes": 150,
            "saifi_outages": 1.5,
            "transmission_gw": 85,
            "congestion_level": "Low to Moderate",
            "infrastructure_age": "Modern (oil wealth investment)",
            "smartgrid_deployment": "Moderate",
            "status": "Good grid (Vision 2030 upgrades)"
        },
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Status of Grid Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Status of Grid",
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
            f"Initialized StatusOfGridAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
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
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze grid status for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Status of Grid for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)

            # Step 5: Estimate confidence
            if data.get('source') == 'ai_powered':
                # Use AI-provided confidence
                confidence = data.get('ai_confidence', 0.75)
                data_quality = "high"
                logger.debug(f"Using AI-provided confidence: {confidence:.2f}")
            # Rule-based data has moderate confidence (estimation-based)
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.70  # Moderate confidence for estimated data
            else:
                data_quality = "high"
                confidence = 0.85  # High confidence for composite mock data

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
                f"Status of Grid analysis complete for {country}: "
                f"Score={score:.1f}, GridScore={data.get('grid_score', 0):.1f}, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Status of Grid analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Status of Grid analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch grid status data.
        
        In MOCK mode: Returns mock composite grid quality scores
        In RULE_BASED mode: Estimates from World Bank transmission losses + GDP
        In AI_POWERED mode: Would use LLM to extract from grid reports (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with grid quality data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
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
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: grid_score={data.get('grid_score')}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate grid quality from World Bank data
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch electric power transmission and distribution losses (% of output)
                transmission_losses = self.data_service.get_value(
                    country=country,
                    indicator='electric_power_transmission_losses',
                    default=None
                )
                
                # Fetch GDP per capita for development level
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch electricity access for additional context
                electricity_access = self.data_service.get_value(
                    country=country,
                    indicator='electricity_access',
                    default=None
                )
                
                if transmission_losses is None or gdp_per_capita is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate grid quality from transmission losses + GDP
                grid_score = self._estimate_grid_quality(
                    country,
                    transmission_losses,
                    gdp_per_capita,
                    electricity_access
                )
                
                # Estimate reliability metrics based on grid score
                saidi, saifi = self._estimate_reliability_metrics(grid_score)
                
                # Estimate other characteristics
                congestion = self._determine_congestion_level(grid_score)
                infrastructure = self._determine_infrastructure_age(grid_score, gdp_per_capita)
                smartgrid = self._determine_smartgrid_deployment(grid_score, gdp_per_capita)
                status = self._determine_grid_status(grid_score)
                
                data = {
                    'grid_score': grid_score,
                    'saidi_minutes': saidi,
                    'saifi_outages': saifi,
                    'transmission_gw': 50,  # Can't estimate without specific data
                    'congestion_level': congestion,
                    'infrastructure_age': infrastructure,
                    'smartgrid_deployment': smartgrid,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_transmission_losses': transmission_losses,
                    'raw_gdp_per_capita': gdp_per_capita
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: grid_score={grid_score:.1f} "
                    f"(losses={transmission_losses:.1f}%, GDP/capita=${gdp_per_capita:,.0f})"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating grid quality for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # AI-powered extraction using StatusOfGridExtractor
            try:
                from ai_extraction_system import AIExtractionAdapter

                # Get documents from kwargs
                documents = kwargs.get('documents', [])
                if not documents:
                    logger.warning(f"No documents provided for AI extraction, falling back to MOCK mode")
                    return self._fetch_data_mock_fallback(country)

                # Use AI extraction adapter
                adapter = AIExtractionAdapter()
                result = adapter.extract_parameter(
                    parameter_name='status_of_grid',
                    country=country,
                    period=period,
                    documents=documents
                )

                if result['success']:
                    # Extract AI data
                    ai_data = result['data']

                    # Return in expected format
                    return {
                        'ai_score': ai_data['value'],
                        'ai_confidence': ai_data['confidence'],
                        'ai_justification': ai_data['justification'],
                        'ai_metadata': ai_data.get('metadata', {}),
                        'ai_quotes': ai_data.get('quotes', []),
                        'source': 'ai_powered',
                        'period': period,
                        'grid_score': ai_data['value'],  # AI score IS the grid score
                        'saidi_minutes': ai_data.get('metadata', {}).get('saidi_minutes', 0),
                        'saifi_outages': ai_data.get('metadata', {}).get('saifi_outages', 0),
                        'transmission_gw': ai_data.get('metadata', {}).get('transmission_gw', 50),
                        'congestion_level': ai_data.get('metadata', {}).get('congestion_level', 'Moderate'),
                        'infrastructure_age': ai_data.get('metadata', {}).get('infrastructure_age', 'Mixed'),
                        'smartgrid_deployment': ai_data.get('metadata', {}).get('smartgrid_deployment', 'Limited'),
                        'status': ai_data.get('metadata', {}).get('status', 'Adequate grid'),
                    }
                else:
                    logger.error(f"AI extraction failed: {result['error']}, falling back to MOCK")
                    return self._fetch_data_mock_fallback(country)

            except Exception as e:
                logger.error(f"AI_POWERED mode error: {e}, falling back to MOCK mode")
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
            "grid_score": 5.0,
            "saidi_minutes": 400,
            "saifi_outages": 5.0,
            "transmission_gw": 50,
            "congestion_level": "Moderate",
            "infrastructure_age": "Mixed",
            "smartgrid_deployment": "Limited",
            "status": "Adequate grid"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_grid_quality(
        self,
        country: str,
        transmission_losses: float,
        gdp_per_capita: float,
        electricity_access: Optional[float]
    ) -> float:
        """Estimate grid quality score from World Bank indicators.
        
        Grid quality estimation model:
        - Lower transmission losses = Better grid
        - Higher GDP per capita = Better infrastructure investment
        - Higher electricity access = More developed grid
        
        Typical transmission losses:
        - Excellent grids: 3-6% (Germany, UK, Japan)
        - Good grids: 6-10% (USA, Spain, Brazil)
        - Adequate grids: 10-15% (India, Mexico)
        - Poor grids: 15-25% (Nigeria, many developing)
        - Very poor grids: > 25%
        
        Args:
            country: Country name
            transmission_losses: % of electricity lost in transmission/distribution
            gdp_per_capita: GDP per capita in current USD
            electricity_access: % of population with electricity access
            
        Returns:
            Estimated grid quality score (0-10)
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Start with base score from transmission losses (INVERSE relationship)
        # Lower losses = Higher quality
        if transmission_losses <= 5:
            # Excellent (Germany 3.9%, UK 7.8%)
            loss_score = 9.5
        elif transmission_losses <= 8:
            # Very good (USA 6.1%, Spain 9.3%)
            loss_score = 8.0
        elif transmission_losses <= 12:
            # Good (Brazil 14.5%, Chile 6.9%)
            loss_score = 6.5
        elif transmission_losses <= 16:
            # Adequate (India 21%, Mexico 14%)
            loss_score = 5.0
        elif transmission_losses <= 25:
            # Below adequate
            loss_score = 3.5
        else:
            # Poor (Nigeria 45%)
            loss_score = 2.0
        
        # Adjust based on GDP per capita (development level)
        if gdp_per_capita >= 40000:
            # High income (Germany $48k, USA $70k)
            gdp_adjustment = +1.0
        elif gdp_per_capita >= 15000:
            # Upper middle income (Brazil $9k, China $13k)
            gdp_adjustment = +0.5
        elif gdp_per_capita >= 5000:
            # Lower middle income (India $2k)
            gdp_adjustment = 0.0
        else:
            # Low income (Nigeria $2k)
            gdp_adjustment = -0.5
        
        # Adjust based on electricity access (if available)
        access_adjustment = 0.0
        if electricity_access is not None:
            if electricity_access >= 99:
                access_adjustment = +0.3
            elif electricity_access < 90:
                access_adjustment = -0.5
        
        # Calculate estimated score
        grid_score = loss_score + gdp_adjustment + access_adjustment
        
        # Calibrate with mock data if available (70/30 blend)
        if base_data:
            base_score = base_data.get('grid_score', grid_score)
            grid_score = grid_score * 0.7 + base_score * 0.3
        
        # Clamp to valid range
        grid_score = max(0.5, min(grid_score, 10.0))
        
        logger.debug(
            f"Grid quality estimation for {country}: "
            f"losses={transmission_losses:.1f}% → loss_score={loss_score:.1f}, "
            f"GDP/capita=${gdp_per_capita:,.0f} → adj={gdp_adjustment:+.1f}, "
            f"final_score={grid_score:.1f}"
        )
        
        return grid_score
    
    def _estimate_reliability_metrics(self, grid_score: float) -> tuple:
        """Estimate SAIDI and SAIFI from grid quality score.
        
        Args:
            grid_score: Grid quality score (0-10)
            
        Returns:
            Tuple of (SAIDI minutes, SAIFI outages)
        """
        # Rough correlation between grid score and reliability
        if grid_score >= 9:
            saidi = 20  # Excellent: 10-50 minutes/year
            saifi = 0.5
        elif grid_score >= 8:
            saidi = 100  # Very good: 50-150 minutes/year
            saifi = 1.0
        elif grid_score >= 7:
            saidi = 200  # Good: 150-300 minutes/year
            saifi = 2.0
        elif grid_score >= 6:
            saidi = 400  # Above adequate: 300-600 minutes/year
            saifi = 4.0
        elif grid_score >= 5:
            saidi = 700  # Adequate: 600-1000 minutes/year
            saifi = 7.0
        elif grid_score >= 4:
            saidi = 1500  # Below adequate: 1000-2000 minutes/year
            saifi = 12.0
        else:
            saidi = 3000  # Poor: > 2000 minutes/year
            saifi = 25.0
        
        return saidi, saifi
    
    def _determine_congestion_level(self, grid_score: float) -> str:
        """Determine congestion level from grid quality score."""
        if grid_score >= 8:
            return "Low"
        elif grid_score >= 6:
            return "Low to Moderate"
        elif grid_score >= 4:
            return "Moderate"
        elif grid_score >= 3:
            return "Moderate to High"
        else:
            return "High to Severe"
    
    def _determine_infrastructure_age(self, grid_score: float, gdp_per_capita: float) -> str:
        """Determine infrastructure age description."""
        if grid_score >= 8 and gdp_per_capita >= 40000:
            return "Modern"
        elif grid_score >= 7:
            return "Modern with some aging components"
        elif grid_score >= 5:
            return "Mixed (aging with selective upgrades)"
        else:
            return "Aging to deteriorated"
    
    def _determine_smartgrid_deployment(self, grid_score: float, gdp_per_capita: float) -> str:
        """Determine smartgrid deployment level."""
        if grid_score >= 8.5 and gdp_per_capita >= 40000:
            return "Advanced"
        elif grid_score >= 7:
            return "Moderate to Advanced"
        elif grid_score >= 5:
            return "Emerging to Moderate"
        else:
            return "Limited to Minimal"
    
    def _determine_grid_status(self, grid_score: float) -> str:
        """Determine grid status description from score."""
        if grid_score >= 9:
            return "Outstanding grid (world-class reliability and capability)"
        elif grid_score >= 8:
            return "Excellent grid (very high reliability, advanced infrastructure)"
        elif grid_score >= 7:
            return "Very good grid (high reliability, modern infrastructure)"
        elif grid_score >= 6:
            return "Good grid (strong reliability, manageable constraints)"
        elif grid_score >= 5:
            return "Above adequate grid (reliable, minor constraints)"
        elif grid_score >= 4:
            return "Adequate grid (basic functionality, some constraints)"
        elif grid_score >= 3:
            return "Below adequate grid (moderate reliability issues)"
        else:
            return "Significant constraints (poor reliability, severe congestion)"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate grid status score.

        DIRECT: Higher grid quality = better infrastructure = higher score

        Args:
            data: Grid status data with grid_score
            country: Country name
            period: Time period

        Returns:
            Score between 1-10
        """
        # If AI_POWERED mode, use AI-provided score directly
        if data.get('source') == 'ai_powered':
            score = data.get('ai_score', 5.0)
            logger.debug(f"Using AI-provided score for {country}: {score:.1f}")
            return float(score)

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
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the grid status score.

        Args:
            data: Grid status data
            score: Calculated score
            country: Country name
            period: Time period

        Returns:
            Human-readable justification string
        """
        source = data.get("source", "unknown")

        # If AI_POWERED mode, use AI-generated justification
        if source == 'ai_powered':
            return data.get('ai_justification', 'AI analysis of grid infrastructure quality.')

        grid_score = data.get("grid_score", 5.0)
        saidi = data.get("saidi_minutes", 0)
        saifi = data.get("saifi_outages", 0)
        transmission = data.get("transmission_gw", 0)
        congestion = data.get("congestion_level", "moderate")
        infrastructure = data.get("infrastructure_age", "mixed")
        smartgrid = data.get("smartgrid_deployment", "limited")
        status = data.get("status", "adequate grid")

        # Find description from rubric
        description = "adequate grid"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break

        # Build justification based on source
        if source == 'rule_based':
            losses = data.get('raw_transmission_losses', 0)
            gdp = data.get('raw_gdp_per_capita', 0)
            justification = (
                f"Based on World Bank data: Estimated grid quality score of {grid_score:.1f}/10 "
                f"(from transmission losses {losses:.1f}% and GDP/capita ${gdp:,.0f}) "
                f"indicates {description}. Estimated reliability: SAIDI {saidi:.0f} min/year, "
                f"SAIFI {saifi:.1f} outages/year. {status.capitalize()}. "
            )
        else:
            # Mock data - use detailed metrics
            justification = (
                f"Grid quality score of {grid_score:.1f}/10 indicates {description}. "
                f"Reliability metrics show SAIDI of {saidi:.0f} minutes/year and SAIFI of {saifi:.1f} outages/year. "
                f"Transmission capacity of {transmission:.0f} GW with {congestion.lower()} congestion levels. "
                f"Infrastructure is {infrastructure.lower()} with {smartgrid.lower()} smartgrid deployment. "
                f"{status.capitalize()}. "
            )

        justification += (
            f"This grid infrastructure {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports renewable energy integration and reduces curtailment risk."
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

        # Check if we used AI extraction
        if data and data.get('source') == 'ai_powered':
            sources.append("AI-Powered Document Extraction")
            sources.append("IEA Electricity Security reports (Extracted from documents)")
            sources.append(f"{country} National grid operator (Extracted from documents)")
            sources.append("SAIDI/SAIFI reliability metrics (Extracted from documents)")
            # Add document sources if available
            ai_metadata = data.get('ai_metadata', {})
            doc_sources = ai_metadata.get('document_sources', [])
            sources.extend(doc_sources)
        # Check if we used rule-based or mock data
        elif data and data.get('source') == 'rule_based':
            sources.append("World Bank Electric Power Transmission Losses - Rule-Based Estimation")
            sources.append("IEA Electricity Security reports (Reference)")
            sources.append(f"{country} National grid operator")
            sources.append("SAIDI/SAIFI reliability metrics")
        else:
            sources.append("World Bank Enterprise Surveys - Mock Data")
            sources.append("IEA Electricity Security reports")
            sources.append(f"{country} National grid operator")
            sources.append("SAIDI/SAIFI reliability metrics")

        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Status of Grid parameter.
        
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
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze grid status.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = StatusOfGridAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
