"""Revenue Stream Stability Agent - Analyzes PPA contract term and revenue security.

This agent evaluates the predictability and security of project revenues through
Power Purchase Agreement (PPA) contracts. Longer contract terms with fixed prices
provide greater revenue certainty, reduce merchant exposure risk, and improve
project bankability.

PPA Term Scale:
- < 3 years: Minimal security (merchant or very short-term)
- 3-5 years: Very low stability
- 5-7 years: Low stability (below typical debt tenor)
- 7-10 years: Below moderate stability
- 10-12 years: Moderate stability (covers partial debt)
- 12-15 years: Above moderate stability
- 15-18 years: Good stability (covers typical debt tenor)
- 18-20 years: Very good stability
- 20-25 years: Outstanding stability (full project life)
- ≥ 25 years: Exceptional stability (ultra-long term)

Scoring Rubric (LOADED FROM CONFIG):
Longer PPA term = Better revenue stability = Higher score (DIRECT relationship)

MODES:
- MOCK: Uses typical PPA terms from market benchmarks (for testing)
- RULE_BASED: Estimates from World Bank economic indicators (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class RevenueStreamStabilityAgent(BaseParameterAgent):
    """Agent for analyzing revenue stream stability through PPA contracts."""
    
    # Mock data for Phase 1 testing
    # PPA term in years - typical contracts in different markets
    # Data from project finance databases, market benchmarks
    MOCK_DATA = {
        "Brazil": {
            "ppa_term_years": 20,
            "price_structure": "Fixed with inflation indexation",
            "offtaker_type": "Utility (state-owned)",
            "merchant_exposure_pct": 0,
            "status": "Outstanding stability (20-year utility PPAs)"
        },
        "Germany": {
            "ppa_term_years": 20,
            "price_structure": "Fixed FiT",
            "offtaker_type": "Government (FiT)",
            "merchant_exposure_pct": 0,
            "status": "Outstanding stability (20-year FiT)"
        },
        "USA": {
            "ppa_term_years": 25,
            "price_structure": "Fixed",
            "offtaker_type": "Utility (investment grade)",
            "merchant_exposure_pct": 0,
            "status": "Exceptional stability (25-year PPAs common)"
        },
        "China": {
            "ppa_term_years": 20,
            "price_structure": "Fixed FiT",
            "offtaker_type": "State Grid",
            "merchant_exposure_pct": 0,
            "status": "Outstanding stability (20-year state backing)"
        },
        "India": {
            "ppa_term_years": 25,
            "price_structure": "Fixed",
            "offtaker_type": "Government-backed (SECI/NTPC)",
            "merchant_exposure_pct": 0,
            "status": "Exceptional stability (25-year government PPAs)"
        },
        "UK": {
            "ppa_term_years": 15,
            "price_structure": "CFD (Contract for Difference)",
            "offtaker_type": "Government (CFD)",
            "merchant_exposure_pct": 0,
            "status": "Good stability (15-year CFD)"
        },
        "Spain": {
            "ppa_term_years": 12,
            "price_structure": "Fixed",
            "offtaker_type": "Corporate PPA",
            "merchant_exposure_pct": 0,
            "status": "Above moderate (12-year corporate)"
        },
        "Australia": {
            "ppa_term_years": 10,
            "price_structure": "Fixed + merchant tail",
            "offtaker_type": "Corporate PPA",
            "merchant_exposure_pct": 50,
            "status": "Moderate (10-year + merchant exposure)"
        },
        "Chile": {
            "ppa_term_years": 20,
            "price_structure": "Fixed",
            "offtaker_type": "Mining companies",
            "merchant_exposure_pct": 0,
            "status": "Outstanding (20-year mining PPAs)"
        },
        "Vietnam": {
            "ppa_term_years": 20,
            "price_structure": "Fixed FiT",
            "offtaker_type": "EVN (state utility)",
            "merchant_exposure_pct": 0,
            "status": "Outstanding (20-year state utility)"
        },
        "South Africa": {
            "ppa_term_years": 20,
            "price_structure": "Fixed",
            "offtaker_type": "Eskom (REIPPP)",
            "merchant_exposure_pct": 0,
            "status": "Outstanding (20-year REIPPP)"
        },
        "Nigeria": {
            "ppa_term_years": 5,
            "price_structure": "Partial fixed + merchant",
            "offtaker_type": "Local distribution companies",
            "merchant_exposure_pct": 40,
            "status": "Low stability (short term + offtaker risk)"
        },
        "Argentina": {
            "ppa_term_years": 20,
            "price_structure": "USD-denominated fixed",
            "offtaker_type": "CAMMESA (RenovAr)",
            "merchant_exposure_pct": 0,
            "status": "Outstanding (20-year RenovAr PPAs)"
        },
        "Mexico": {
            "ppa_term_years": 15,
            "price_structure": "Fixed",
            "offtaker_type": "CFE + private",
            "merchant_exposure_pct": 0,
            "status": "Good (15-year PPAs)"
        },
        "Indonesia": {
            "ppa_term_years": 25,
            "price_structure": "Fixed FiT",
            "offtaker_type": "PLN (state utility)",
            "merchant_exposure_pct": 0,
            "status": "Exceptional (25-year PLN PPAs)"
        },
        "Saudi Arabia": {
            "ppa_term_years": 25,
            "price_structure": "Fixed",
            "offtaker_type": "ACWA/SEC (sovereign)",
            "merchant_exposure_pct": 0,
            "status": "Exceptional (25-year sovereign backing)"
        },
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Revenue Stream Stability Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Revenue Stream Stability",
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
            f"Initialized RevenueStreamStabilityAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            stability_config = params_config['parameters'].get('revenue_stream_stability', {})
            scoring = stability_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_term_years": item.get('min_term_years', 0),
                        "max_term_years": item.get('max_term_years', 100),
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
            {"score": 1, "min_term_years": 0, "max_term_years": 3, "range": "< 3y", "description": "Minimal revenue security (merchant or very short-term)"},
            {"score": 2, "min_term_years": 3, "max_term_years": 5, "range": "3-5y", "description": "Very low stability (short-term contracts)"},
            {"score": 3, "min_term_years": 5, "max_term_years": 7, "range": "5-7y", "description": "Low stability (below typical debt tenor)"},
            {"score": 4, "min_term_years": 7, "max_term_years": 10, "range": "7-10y", "description": "Below moderate stability"},
            {"score": 5, "min_term_years": 10, "max_term_years": 12, "range": "10-12y", "description": "Moderate stability (covers partial debt)"},
            {"score": 6, "min_term_years": 12, "max_term_years": 15, "range": "12-15y", "description": "Above moderate stability"},
            {"score": 7, "min_term_years": 15, "max_term_years": 18, "range": "15-18y", "description": "Good stability (covers typical debt tenor)"},
            {"score": 8, "min_term_years": 18, "max_term_years": 20, "range": "18-20y", "description": "Very good stability"},
            {"score": 9, "min_term_years": 20, "max_term_years": 25, "range": "20-25y", "description": "Outstanding stability (full project life)"},
            {"score": 10, "min_term_years": 25, "max_term_years": 100, "range": "≥ 25y", "description": "Exceptional stability (ultra-long term contracts)"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze revenue stream stability for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Revenue Stream Stability for {country} ({period}) in {self.mode.value} mode")
            
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
                confidence = 0.60  # Lower confidence for estimated PPA terms
            else:
                data_quality = "medium"
                confidence = 0.75  # Medium-high confidence for market benchmarks
            
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
                f"Revenue Stream Stability analysis complete for {country}: "
                f"Score={score:.1f}, Term={data.get('ppa_term_years', 0):.0f}y, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Revenue Stream Stability analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Revenue Stream Stability analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch revenue stream stability data.
        
        In MOCK mode: Returns typical PPA terms from market benchmarks
        In RULE_BASED mode: Estimates from World Bank economic indicators
        In AI_POWERED mode: Would use LLM to extract from PPA databases (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with revenue stream stability data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate stability")
                data = {
                    "ppa_term_years": 12,
                    "price_structure": "Fixed",
                    "offtaker_type": "Utility",
                    "merchant_exposure_pct": 0,
                    "status": "Above moderate stability"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: PPA term={data.get('ppa_term_years')}y")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate from World Bank economic indicators
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch GDP per capita (developed markets = longer PPAs)
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch renewable consumption % (mature markets = established frameworks)
                renewable_pct = self.data_service.get_value(
                    country=country,
                    indicator='renewable_consumption',
                    default=None
                )
                
                # Fetch FDI net inflows (investor confidence in legal framework)
                fdi_inflows_pct = self.data_service.get_value(
                    country=country,
                    indicator='fdi_net_inflows',
                    default=None
                )
                
                if gdp_per_capita is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate PPA term
                ppa_term_years = self._estimate_ppa_term(
                    country,
                    gdp_per_capita,
                    renewable_pct,
                    fdi_inflows_pct
                )
                
                # Estimate contract characteristics
                price_structure = self._determine_price_structure(gdp_per_capita, renewable_pct)
                offtaker_type = self._determine_offtaker_type(gdp_per_capita)
                merchant_exposure = self._estimate_merchant_exposure(ppa_term_years, gdp_per_capita)
                status = self._determine_stability_status(ppa_term_years)
                
                data = {
                    'ppa_term_years': ppa_term_years,
                    'price_structure': price_structure,
                    'offtaker_type': offtaker_type,
                    'merchant_exposure_pct': merchant_exposure,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_gdp_per_capita': gdp_per_capita,
                    'raw_renewable_pct': renewable_pct if renewable_pct else 0,
                    'raw_fdi_inflows_pct': fdi_inflows_pct if fdi_inflows_pct else 0
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: PPA term={ppa_term_years:.0f}y "
                    f"from GDP/capita=${gdp_per_capita:,.0f}, RE={renewable_pct if renewable_pct else 0:.1f}%"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating PPA terms for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from PPA databases
            # return self._llm_extract_ppa_terms(country, period)
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
            "ppa_term_years": 12,
            "price_structure": "Fixed",
            "offtaker_type": "Utility",
            "merchant_exposure_pct": 0,
            "status": "Above moderate stability"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_ppa_term(
        self,
        country: str,
        gdp_per_capita: float,
        renewable_pct: Optional[float],
        fdi_inflows_pct: Optional[float]
    ) -> float:
        """Estimate typical PPA term from economic indicators.
        
        Higher GDP + Mature renewable market + Good FDI = Longer PPAs
        
        Args:
            country: Country name
            gdp_per_capita: GDP per capita (USD)
            renewable_pct: Renewable consumption (%)
            fdi_inflows_pct: FDI net inflows (% of GDP)
            
        Returns:
            Estimated PPA term in years
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Start with GDP-based term (developed markets = longer PPAs)
        if gdp_per_capita >= 40000:
            # Very high income (Germany, USA, UK, Australia)
            base_term = 22  # 20-25 years typical
        elif gdp_per_capita >= 20000:
            # Upper-middle income (Chile)
            base_term = 18  # 15-20 years
        elif gdp_per_capita >= 10000:
            # Middle income (Brazil, China, Mexico)
            base_term = 18  # 15-20 years
        elif gdp_per_capita >= 5000:
            # Lower-middle income (India, Indonesia, Vietnam)
            base_term = 22  # Often longer for security (20-25)
        else:
            # Low income (Nigeria)
            base_term = 8  # Shorter, less established
        
        # Adjust based on renewable market maturity
        maturity_adjustment = 0
        if renewable_pct is not None:
            if renewable_pct >= 40:
                # Very mature market (established PPA frameworks)
                maturity_adjustment = +3
            elif renewable_pct >= 20:
                # Mature market
                maturity_adjustment = +2
            elif renewable_pct >= 10:
                # Growing market
                maturity_adjustment = +1
            else:
                # Early market (less established)
                maturity_adjustment = -2
        
        # Adjust based on FDI (investor confidence in legal framework)
        fdi_adjustment = 0
        if fdi_inflows_pct is not None:
            if fdi_inflows_pct >= 4.0:
                # Very high FDI (strong confidence)
                fdi_adjustment = +2
            elif fdi_inflows_pct >= 2.0:
                # High FDI
                fdi_adjustment = +1
            elif fdi_inflows_pct < 0.5:
                # Low FDI (weaker confidence)
                fdi_adjustment = -1
        
        # Calculate estimated term
        ppa_term = base_term + maturity_adjustment + fdi_adjustment
        
        # Calibrate with mock data if available (40/60 blend)
        if base_data:
            base_term_mock = base_data.get('ppa_term_years', ppa_term)
            ppa_term = ppa_term * 0.4 + base_term_mock * 0.6
        
        # Clamp to reasonable range
        ppa_term = max(3.0, min(ppa_term, 30.0))
        
        logger.debug(
            f"PPA term estimation for {country}: "
            f"GDP/capita=${gdp_per_capita:,.0f} → base={base_term:.0f}y, "
            f"RE={renewable_pct if renewable_pct else 0:.1f}% → adj={maturity_adjustment:+.0f}y, "
            f"FDI={fdi_inflows_pct if fdi_inflows_pct else 0:.1f}% → adj={fdi_adjustment:+.0f}y, "
            f"final_term={ppa_term:.0f}y"
        )
        
        return round(ppa_term)
    
    def _determine_price_structure(self, gdp_per_capita: float, renewable_pct: Optional[float]) -> str:
        """Determine typical price structure."""
        if gdp_per_capita >= 30000:
            if renewable_pct and renewable_pct >= 30:
                return "Fixed (FiT or CFD)"
            else:
                return "Fixed"
        elif gdp_per_capita >= 10000:
            return "Fixed with inflation indexation"
        else:
            return "Partial fixed + merchant"
    
    def _determine_offtaker_type(self, gdp_per_capita: float) -> str:
        """Determine typical offtaker type."""
        if gdp_per_capita >= 40000:
            return "Utility (investment grade) or Government"
        elif gdp_per_capita >= 15000:
            return "Utility or Corporate PPA"
        else:
            return "State utility (government-backed)"
    
    def _estimate_merchant_exposure(self, ppa_term_years: float, gdp_per_capita: float) -> int:
        """Estimate merchant exposure percentage."""
        # Shorter PPAs in developed markets may have merchant tail
        if ppa_term_years < 12 and gdp_per_capita >= 30000:
            return 30  # Corporate PPAs with merchant tail
        elif ppa_term_years < 8:
            return 20  # Some merchant exposure
        else:
            return 0  # Full PPA coverage
    
    def _determine_stability_status(self, ppa_term_years: float) -> str:
        """Determine stability status description."""
        if ppa_term_years >= 25:
            return "Exceptional stability (ultra-long term contracts)"
        elif ppa_term_years >= 20:
            return "Outstanding stability (full project life coverage)"
        elif ppa_term_years >= 18:
            return "Very good stability (strong revenue certainty)"
        elif ppa_term_years >= 15:
            return "Good stability (covers typical debt tenor)"
        elif ppa_term_years >= 12:
            return "Above moderate stability (reasonable coverage)"
        elif ppa_term_years >= 10:
            return "Moderate stability (covers partial debt)"
        elif ppa_term_years >= 7:
            return "Below moderate stability (limited coverage)"
        else:
            return "Low stability (short-term contracts with risk)"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate revenue stream stability score based on PPA term.
        
        DIRECT: Longer PPA term = better stability = higher score
        
        Args:
            data: Revenue stream stability data
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        ppa_term = data.get("ppa_term_years", 0)
        
        logger.debug(f"Calculating score for {country}: {ppa_term} year PPA term")
        
        for level in self.scoring_rubric:
            min_term = level.get("min_term_years", 0)
            max_term = level.get("max_term_years", 100)
            
            if min_term <= ppa_term < max_term:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{ppa_term}y falls in range {min_term}-{max_term}y"
                )
                return float(score)
        
        # Handle PPA >= 25 years (score 10)
        if ppa_term >= 25:
            logger.debug(f"Score 10 assigned: {ppa_term}y >= 25y")
            return 10.0
        
        logger.warning(f"No rubric match for {ppa_term}y, defaulting to score 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the revenue stream stability score.
        
        Args:
            data: Revenue stream stability data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        ppa_term = data.get("ppa_term_years", 0)
        price_structure = data.get("price_structure", "fixed")
        offtaker_type = data.get("offtaker_type", "utility")
        merchant_exposure = data.get("merchant_exposure_pct", 0)
        status = data.get("status", "moderate stability")
        source = data.get("source", "unknown")
        
        # Find description from rubric
        description = "moderate stability"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification based on source
        if source == 'rule_based':
            gdp = data.get('raw_gdp_per_capita', 0)
            re_pct = data.get('raw_renewable_pct', 0)
            justification = (
                f"Based on World Bank data: Estimated PPA term of {ppa_term:.0f} years indicates {description} "
                f"(derived from GDP/capita ${gdp:,.0f} and renewable maturity {re_pct:.1f}%). "
            )
        else:
            # Mock data
            justification = (
                f"PPA term of {ppa_term:.0f} years indicates {description}. "
            )
        
        justification += (
            f"Contract structure with {price_structure.lower()} prices backed by {offtaker_type.lower()} "
            f"provides {'strong' if score >= 8 else 'adequate' if score >= 6 else 'limited'} revenue certainty. "
        )
        
        if merchant_exposure > 0:
            justification += f"{merchant_exposure}% merchant exposure introduces price risk. "
        
        justification += (
            f"{status.capitalize()} {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports project bankability and financing. "
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
            sources.append("World Bank Economic Indicators - Rule-Based Estimation")
            sources.append("PPA databases and registries (Reference)")
        else:
            sources.append("PPA databases and registries - Mock Data")
            sources.append("Project finance documentation")
        
        sources.append(f"{country} Market PPA term benchmarks")
        sources.append("Offtaker contract databases")
        
        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Revenue Stream Stability parameter.
        
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
            "PPA databases and registries",
            "Project finance documentation",
            "Market PPA term benchmarks",
            "Offtaker contract databases",
            "Developer and investor benchmarks"
        ]


def analyze_revenue_stream_stability(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze revenue stream stability.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = RevenueStreamStabilityAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
