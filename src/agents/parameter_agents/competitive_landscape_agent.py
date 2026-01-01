"""Competitive Landscape Agent - Analyzes market entry ease and competition.

This agent evaluates the competitive dynamics and ease of market entry
in renewable energy markets by assessing:
- Regulatory barriers to entry
- Licensing and permitting complexity
- Market openness to new players
- Competitive intensity
- Exit and entry patterns

Key evaluation criteria:
- Licensing requirements and timelines
- Capital requirements and access
- Grid connection processes
- Land acquisition complexity
- Environmental permitting
- Local content requirements

Market Openness Categories (1-10):
1. Extreme barriers (market closed)
2. Very high barriers
3. High barriers
4. Above moderate barriers
5. Moderate barriers
6. Below moderate barriers
7. Low barriers
8. Very low barriers
9. Minimal barriers
10. No barriers (fully open)

Scoring Rubric (LOADED FROM CONFIG):
Lower barriers = More competitive = Higher score

MODES:
- MOCK: Uses hardcoded market entry assessments (for testing)
- RULE_BASED: Estimates from World Bank business ease + FDI indicators (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class CompetitiveLandscapeAgent(BaseParameterAgent):
    """Agent for analyzing competitive landscape and market entry ease."""
    
    # Mock data for Phase 1 testing
    # Market entry ease assessment based on regulatory frameworks
    # Data from World Bank Doing Business, IEA, regulatory analysis
    MOCK_DATA = {
        "Brazil": {
            "score": 7,
            "category": "low_barriers",
            "licensing_complexity": "Moderate (auction-based, clear rules)",
            "permitting_timeline_months": 12,
            "grid_connection_ease": "Moderate (improving infrastructure)",
            "market_openness": "High (open to international and domestic players)",
            "competitive_intensity": "High (active auctions, many participants)",
            "entry_examples": "Strong IPP participation, international developers active",
            "status": "Open market with low barriers, active competition through auction system"
        },
        "Germany": {
            "score": 9,
            "category": "minimal_barriers",
            "licensing_complexity": "Low (streamlined EEG process)",
            "permitting_timeline_months": 6,
            "grid_connection_ease": "High (mature grid, clear rules)",
            "market_openness": "Very High (fully open market)",
            "competitive_intensity": "Very High (diverse players, cooperatives)",
            "entry_examples": "Thousands of small players, community projects",
            "status": "Highly competitive open market with minimal barriers and strong participation"
        },
        "USA": {
            "score": 8,
            "category": "very_low_barriers",
            "licensing_complexity": "Low to Moderate (state-dependent)",
            "permitting_timeline_months": 9,
            "grid_connection_ease": "Moderate to High (varies by region)",
            "market_openness": "Very High (competitive markets)",
            "competitive_intensity": "Very High (utilities, IPPs, yieldcos)",
            "entry_examples": "Robust IPP market, strong competition",
            "status": "Very competitive market with low barriers, though varies by state"
        },
        "China": {
            "score": 5,
            "category": "moderate_barriers",
            "licensing_complexity": "Moderate to High (government approvals)",
            "permitting_timeline_months": 18,
            "grid_connection_ease": "Moderate (state grid control)",
            "market_openness": "Moderate (preference for SOEs, JV requirements)",
            "competitive_intensity": "Moderate (large SOEs dominate)",
            "entry_examples": "Primarily state-owned enterprises, some private players",
            "status": "Moderate barriers with preference for state-owned enterprises"
        },
        "India": {
            "score": 7,
            "category": "low_barriers",
            "licensing_complexity": "Moderate (auction-based, improving)",
            "permitting_timeline_months": 15,
            "grid_connection_ease": "Moderate (grid constraints)",
            "market_openness": "High (open to domestic and international)",
            "competitive_intensity": "High (active IPP participation)",
            "entry_examples": "Strong IPP growth, international developers",
            "status": "Increasingly open market with improving ease of entry"
        },
        "UK": {
            "score": 8,
            "category": "very_low_barriers",
            "licensing_complexity": "Low (CfD auctions, clear process)",
            "permitting_timeline_months": 8,
            "grid_connection_ease": "High (mature system)",
            "market_openness": "Very High (competitive market)",
            "competitive_intensity": "Very High (especially offshore wind)",
            "entry_examples": "International developers, strong IPP market",
            "status": "Highly competitive market with low barriers and strong international participation"
        },
        "Spain": {
            "score": 6,
            "category": "below_moderate_barriers",
            "licensing_complexity": "Moderate (recovering from reforms)",
            "permitting_timeline_months": 14,
            "grid_connection_ease": "Moderate (grid queue issues)",
            "market_openness": "High (reopening to competition)",
            "competitive_intensity": "Moderate to High (recovering)",
            "entry_examples": "Renewed activity post-reform",
            "status": "Market reopening with improving entry conditions after past policy issues"
        },
        "Australia": {
            "score": 8,
            "category": "very_low_barriers",
            "licensing_complexity": "Low (state-level, generally streamlined)",
            "permitting_timeline_months": 7,
            "grid_connection_ease": "Moderate to High (NEM system)",
            "market_openness": "Very High (competitive market)",
            "competitive_intensity": "Very High (active IPP market)",
            "entry_examples": "Strong independent developer activity",
            "status": "Highly competitive market with low barriers and active entry"
        },
        "Chile": {
            "score": 7,
            "category": "low_barriers",
            "licensing_complexity": "Low to Moderate (auction system)",
            "permitting_timeline_months": 10,
            "grid_connection_ease": "Moderate (transmission challenges)",
            "market_openness": "High (open to competition)",
            "competitive_intensity": "High (competitive auctions)",
            "entry_examples": "Active international and domestic participation",
            "status": "Open competitive market with relatively low entry barriers"
        },
        "Vietnam": {
            "score": 4,
            "category": "above_moderate_barriers",
            "licensing_complexity": "High (complex approvals, EVN control)",
            "permitting_timeline_months": 24,
            "grid_connection_ease": "Low (EVN monopoly, curtailment)",
            "market_openness": "Moderate (opening but controlled)",
            "competitive_intensity": "Low to Moderate (limited by EVN)",
            "entry_examples": "Some IPP entry but significant challenges",
            "status": "Significant barriers with EVN control limiting competition"
        },
        "South Africa": {
            "score": 6,
            "category": "below_moderate_barriers",
            "licensing_complexity": "Moderate (REIPPP process established)",
            "permitting_timeline_months": 16,
            "grid_connection_ease": "Moderate (Eskom constraints)",
            "market_openness": "High (competitive bidding)",
            "competitive_intensity": "Moderate to High (REIPPP rounds)",
            "entry_examples": "Diverse IPP participation through REIPPP",
            "status": "Structured competitive market but Eskom challenges create barriers"
        },
        "Nigeria": {
            "score": 2,
            "category": "very_high_barriers",
            "licensing_complexity": "Very High (complex, uncertain)",
            "permitting_timeline_months": 36,
            "grid_connection_ease": "Very Low (grid unreliability)",
            "market_openness": "Low (limited by infrastructure and policy)",
            "competitive_intensity": "Very Low (limited market activity)",
            "entry_examples": "Few successful entries, major barriers",
            "status": "Very high barriers with infrastructure and regulatory challenges"
        },
        "Argentina": {
            "score": 5,
            "category": "moderate_barriers",
            "licensing_complexity": "Moderate (RenovAr framework)",
            "permitting_timeline_months": 18,
            "grid_connection_ease": "Moderate",
            "market_openness": "Moderate to High (auction-based)",
            "competitive_intensity": "Moderate",
            "entry_examples": "RenovAr program attracted diverse bidders",
            "status": "Moderate barriers with auction framework but economic volatility"
        },
        "Mexico": {
            "score": 4,
            "category": "above_moderate_barriers",
            "licensing_complexity": "High (policy reversal post-2018)",
            "permitting_timeline_months": 24,
            "grid_connection_ease": "Low (CFE control, barriers)",
            "market_openness": "Moderate (deteriorating post-2018)",
            "competitive_intensity": "Low to Moderate (declining)",
            "entry_examples": "Entry declining after policy changes",
            "status": "Above moderate barriers with policy reversal creating challenges"
        },
        "Indonesia": {
            "score": 4,
            "category": "above_moderate_barriers",
            "licensing_complexity": "High (PLN control, complex approvals)",
            "permitting_timeline_months": 24,
            "grid_connection_ease": "Low to Moderate (PLN monopoly)",
            "market_openness": "Moderate (opening slowly)",
            "competitive_intensity": "Low to Moderate",
            "entry_examples": "Limited IPP participation",
            "status": "Above moderate barriers with PLN control and complex processes"
        },
        "Saudi Arabia": {
            "score": 7,
            "category": "low_barriers",
            "licensing_complexity": "Low to Moderate (REPDO auctions)",
            "permitting_timeline_months": 12,
            "grid_connection_ease": "Moderate to High (state support)",
            "market_openness": "High (Vision 2030 opening)",
            "competitive_intensity": "High (competitive auctions)",
            "entry_examples": "Strong international participation in auctions",
            "status": "Low barriers with Vision 2030 driving market opening"
        },
    }
    
    # Category to score mapping
    CATEGORY_SCORES = {
        "extreme_barriers": 1,
        "very_high_barriers": 2,
        "high_barriers": 3,
        "above_moderate_barriers": 4,
        "moderate_barriers": 5,
        "below_moderate_barriers": 6,
        "low_barriers": 7,
        "very_low_barriers": 8,
        "minimal_barriers": 9,
        "no_barriers": 10
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Competitive Landscape Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Competitive Landscape",
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
            f"Initialized CompetitiveLandscapeAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            landscape_config = params_config['parameters'].get('competitive_landscape', {})
            scoring = landscape_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "range": item.get('range', ''),
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
            {"score": 1, "range": "Extreme barriers", "description": "Market effectively closed"},
            {"score": 2, "range": "Very high barriers", "description": "Severe entry restrictions"},
            {"score": 3, "range": "High barriers", "description": "Significant entry barriers"},
            {"score": 4, "range": "Above moderate barriers", "description": "Notable barriers"},
            {"score": 5, "range": "Moderate barriers", "description": "Balanced entry requirements"},
            {"score": 6, "range": "Below moderate barriers", "description": "Relatively open market"},
            {"score": 7, "range": "Low barriers", "description": "Open market, easy entry"},
            {"score": 8, "range": "Very low barriers", "description": "Minimal restrictions"},
            {"score": 9, "range": "Minimal barriers", "description": "Nearly open market"},
            {"score": 10, "range": "No barriers", "description": "Completely open market"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze competitive landscape for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Competitive Landscape for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            if self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.65  # Lower confidence for estimated data
            else:
                data_quality = "high"
                confidence = 0.85  # High confidence for detailed assessments
            
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
                f"Competitive Landscape analysis complete for {country}: "
                f"Score={score:.1f}, Category={data.get('category', 'unknown')}, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Competitive Landscape analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Competitive Landscape analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch competitive landscape data.
        
        In MOCK mode: Returns mock market entry assessments
        In RULE_BASED mode: Estimates from World Bank business ease + FDI indicators
        In AI_POWERED mode: Would use LLM to extract from market reports (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with competitive landscape data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate barriers")
                data = {
                    "score": 5,
                    "category": "moderate_barriers",
                    "licensing_complexity": "Moderate",
                    "permitting_timeline_months": 18,
                    "grid_connection_ease": "Moderate",
                    "market_openness": "Moderate",
                    "competitive_intensity": "Moderate",
                    "entry_examples": "Some entry activity",
                    "status": "Moderate barriers to entry"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: score={data.get('score')}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate from World Bank indicators
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch FDI net inflows (% of GDP) - proxy for market openness
                fdi_inflows_pct = self.data_service.get_value(
                    country=country,
                    indicator='fdi_net_inflows',
                    default=None
                )
                
                # Fetch GDP per capita (development level correlates with market maturity)
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch trade openness (% of GDP)
                trade_pct_gdp = self.data_service.get_value(
                    country=country,
                    indicator='trade',
                    default=None
                )
                
                # Fetch renewable electricity output (market activity indicator)
                renewable_output = self.data_service.get_value(
                    country=country,
                    indicator='renewable_electricity_output',
                    default=None
                )
                
                if fdi_inflows_pct is None or gdp_per_capita is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate competitive landscape score
                score, category = self._estimate_competitive_landscape(
                    country,
                    fdi_inflows_pct,
                    gdp_per_capita,
                    trade_pct_gdp,
                    renewable_output
                )
                
                # Estimate characteristics
                licensing = self._determine_licensing_complexity(category, gdp_per_capita)
                timeline = self._estimate_permitting_timeline(category)
                grid_ease = self._determine_grid_connection_ease(category)
                openness = self._determine_market_openness(category, fdi_inflows_pct)
                intensity = self._determine_competitive_intensity(category)
                status = self._determine_landscape_status(category, score)
                
                data = {
                    'score': score,
                    'category': category,
                    'licensing_complexity': licensing,
                    'permitting_timeline_months': timeline,
                    'grid_connection_ease': grid_ease,
                    'market_openness': openness,
                    'competitive_intensity': intensity,
                    'entry_examples': 'Estimated from market indicators',
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_fdi_inflows_pct': fdi_inflows_pct,
                    'raw_gdp_per_capita': gdp_per_capita
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: score={score:.1f} ({category}) "
                    f"from FDI={fdi_inflows_pct:.1f}%, GDP/capita=${gdp_per_capita:,.0f}"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating competitive landscape for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from market reports
            # return self._llm_extract_competitive_landscape(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
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
            "score": 5,
            "category": "moderate_barriers",
            "licensing_complexity": "Moderate",
            "permitting_timeline_months": 18,
            "grid_connection_ease": "Moderate",
            "market_openness": "Moderate",
            "competitive_intensity": "Moderate",
            "entry_examples": "Some entry activity",
            "status": "Moderate barriers to entry"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_competitive_landscape(
        self,
        country: str,
        fdi_inflows_pct: float,
        gdp_per_capita: float,
        trade_pct_gdp: Optional[float],
        renewable_output: Optional[float]
    ) -> tuple:
        """Estimate competitive landscape from World Bank indicators.
        
        Higher FDI + Higher development = More competitive, open markets
        
        Args:
            country: Country name
            fdi_inflows_pct: FDI net inflows (% of GDP)
            gdp_per_capita: GDP per capita in current USD
            trade_pct_gdp: Trade (% of GDP)
            renewable_output: Renewable electricity output (kWh)
            
        Returns:
            Tuple of (score, category)
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Start with FDI openness score (higher FDI = more open market)
        if fdi_inflows_pct >= 4.0:
            # Very high FDI (Chile, Vietnam pre-policy change)
            fdi_score = 8.0
        elif fdi_inflows_pct >= 3.0:
            # High FDI
            fdi_score = 7.0
        elif fdi_inflows_pct >= 2.0:
            # Moderate-high FDI
            fdi_score = 6.0
        elif fdi_inflows_pct >= 1.0:
            # Moderate FDI
            fdi_score = 5.0
        elif fdi_inflows_pct >= 0.5:
            # Low-moderate FDI
            fdi_score = 4.0
        else:
            # Low FDI (may indicate barriers or low activity)
            fdi_score = 3.0
        
        # Adjust based on development level
        # High-income countries tend to have more mature, competitive markets
        if gdp_per_capita >= 40000:
            # High income (Germany, UK, USA, Australia)
            gdp_adjustment = +2.0
        elif gdp_per_capita >= 15000:
            # Upper middle income (Brazil, China)
            gdp_adjustment = +1.0
        elif gdp_per_capita >= 5000:
            # Lower middle income (India, Vietnam)
            gdp_adjustment = 0.0
        else:
            # Low income (Nigeria)
            gdp_adjustment = -1.5
        
        # Adjust based on trade openness (if available)
        trade_adjustment = 0.0
        if trade_pct_gdp is not None:
            if trade_pct_gdp >= 80:  # Very open (small trading nations)
                trade_adjustment = +0.5
            elif trade_pct_gdp >= 50:  # Open
                trade_adjustment = +0.3
            elif trade_pct_gdp < 30:  # Relatively closed
                trade_adjustment = -0.3
        
        # Calculate estimated score
        score = fdi_score + gdp_adjustment + trade_adjustment
        
        # Calibrate with mock data if available (60/40 blend - less confident)
        if base_data:
            base_score = base_data.get('score', score)
            score = score * 0.6 + base_score * 0.4
        
        # Clamp to valid range
        score = max(1.0, min(score, 10.0))
        
        # Determine category from score
        category = self._determine_category_from_score(score)
        
        logger.debug(
            f"Competitive landscape estimation for {country}: "
            f"FDI={fdi_inflows_pct:.1f}% → fdi_score={fdi_score:.1f}, "
            f"GDP/capita=${gdp_per_capita:,.0f} → adj={gdp_adjustment:+.1f}, "
            f"final_score={score:.1f} ({category})"
        )
        
        return score, category
    
    def _determine_category_from_score(self, score: float) -> str:
        """Determine category from score."""
        if score >= 9.5:
            return "no_barriers"
        elif score >= 8.5:
            return "minimal_barriers"
        elif score >= 7.5:
            return "very_low_barriers"
        elif score >= 6.5:
            return "low_barriers"
        elif score >= 5.5:
            return "below_moderate_barriers"
        elif score >= 4.5:
            return "moderate_barriers"
        elif score >= 3.5:
            return "above_moderate_barriers"
        elif score >= 2.5:
            return "high_barriers"
        elif score >= 1.5:
            return "very_high_barriers"
        else:
            return "extreme_barriers"
    
    def _determine_licensing_complexity(self, category: str, gdp_per_capita: float) -> str:
        """Determine licensing complexity level."""
        if category in ["no_barriers", "minimal_barriers"]:
            return "Low (streamlined process)"
        elif category in ["very_low_barriers", "low_barriers"]:
            return "Low to Moderate"
        elif category in ["below_moderate_barriers", "moderate_barriers"]:
            return "Moderate"
        elif category == "above_moderate_barriers":
            return "Moderate to High"
        else:
            return "High to Very High"
    
    def _estimate_permitting_timeline(self, category: str) -> int:
        """Estimate permitting timeline in months."""
        timeline_map = {
            "no_barriers": 4,
            "minimal_barriers": 6,
            "very_low_barriers": 8,
            "low_barriers": 10,
            "below_moderate_barriers": 14,
            "moderate_barriers": 18,
            "above_moderate_barriers": 24,
            "high_barriers": 30,
            "very_high_barriers": 36,
            "extreme_barriers": 48
        }
        return timeline_map.get(category, 18)
    
    def _determine_grid_connection_ease(self, category: str) -> str:
        """Determine grid connection ease."""
        if category in ["no_barriers", "minimal_barriers"]:
            return "High (mature infrastructure)"
        elif category in ["very_low_barriers", "low_barriers"]:
            return "Moderate to High"
        elif category in ["below_moderate_barriers", "moderate_barriers"]:
            return "Moderate"
        else:
            return "Low (infrastructure challenges)"
    
    def _determine_market_openness(self, category: str, fdi_pct: float) -> str:
        """Determine market openness level."""
        if category in ["no_barriers", "minimal_barriers"]:
            return "Very High (fully open)"
        elif category in ["very_low_barriers", "low_barriers"]:
            return "High (open to competition)"
        elif category in ["below_moderate_barriers", "moderate_barriers"]:
            return "Moderate (some restrictions)"
        else:
            return "Low (significant restrictions)"
    
    def _determine_competitive_intensity(self, category: str) -> str:
        """Determine competitive intensity."""
        if category in ["no_barriers", "minimal_barriers"]:
            return "Very High (active competition)"
        elif category in ["very_low_barriers", "low_barriers"]:
            return "High (competitive market)"
        elif category in ["below_moderate_barriers", "moderate_barriers"]:
            return "Moderate"
        else:
            return "Low (limited competition)"
    
    def _determine_landscape_status(self, category: str, score: float) -> str:
        """Determine landscape status description."""
        if score >= 8:
            return "Highly competitive market with low barriers and strong participation"
        elif score >= 6:
            return "Competitive market with relatively low entry barriers"
        elif score >= 4:
            return "Moderate competition with some entry barriers"
        else:
            return "Significant barriers limiting market competition"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate competitive landscape score.
        
        Lower barriers = More competitive = Higher score
        
        Args:
            data: Competitive landscape data
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using score {score} for {country}")
            return float(score)
        
        # Otherwise use category if available
        category = data.get("category", "moderate_barriers")
        score = self.CATEGORY_SCORES.get(category, 5)
        
        logger.debug(f"Using category {category} → score {score} for {country}")
        
        return float(score)
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the competitive landscape score.
        
        Args:
            data: Competitive landscape data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        category = data.get("category", "moderate_barriers")
        licensing = data.get("licensing_complexity", "moderate")
        timeline = data.get("permitting_timeline_months", 18)
        grid = data.get("grid_connection_ease", "moderate")
        openness = data.get("market_openness", "moderate")
        intensity = data.get("competitive_intensity", "moderate")
        examples = data.get("entry_examples", "some activity")
        status = data.get("status", "")
        source = data.get("source", "unknown")
        
        # Find description from rubric
        description = "moderate barriers"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level.get("range", level["description"]).lower()
                break
        
        # Build justification based on source
        if source == 'rule_based':
            fdi = data.get('raw_fdi_inflows_pct', 0)
            gdp = data.get('raw_gdp_per_capita', 0)
            justification = (
                f"Based on World Bank data: Estimated market shows {description} "
                f"(derived from FDI inflows {fdi:.1f}% of GDP and GDP/capita ${gdp:,.0f}). "
                f"Estimated licensing complexity: {licensing.lower()}, "
                f"permitting timeline ~{timeline} months. {status}. "
            )
        else:
            # Mock data - use detailed assessments
            justification = (
                f"Market shows {description}. "
                f"Licensing complexity: {licensing.lower()}, "
                f"permitting timeline ~{timeline} months, "
                f"grid connection: {grid.lower()}. "
                f"Market openness: {openness.lower()}, "
                f"competitive intensity: {intensity.lower()}. "
                f"{examples}. {status}. "
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
        
        # Check if we used rule-based or mock data
        if data and data.get('source') == 'rule_based':
            sources.append("World Bank FDI & Trade Indicators - Rule-Based Estimation")
            sources.append("Market entry analysis (Reference)")
        else:
            sources.append("Market entry analysis and regulatory frameworks - Mock Data")
            sources.append("World Bank Doing Business indicators")
        
        sources.append("Competitive intensity assessments")
        sources.append(f"{country} licensing and permitting requirements")
        
        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Competitive Landscape parameter.
        
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
            "Market entry analysis and regulatory frameworks",
            "Competitive intensity assessments",
            "Licensing and permitting requirements",
            "Industry entry and exit data",
            "World Bank Doing Business indicators"
        ]


def analyze_competitive_landscape(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze competitive landscape.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = CompetitiveLandscapeAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
