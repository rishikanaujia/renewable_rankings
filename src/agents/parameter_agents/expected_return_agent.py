"""Expected Return Agent - Analyzes projected IRR for renewable energy projects.

This agent evaluates the expected Internal Rate of Return (IRR) for typical renewable
energy projects in each country. IRR represents the discount rate that makes the net
present value of all cash flows equal to zero, and is a key metric for investment
decision-making.

IRR Scale:
- < 2%: Very poor returns (below risk-free rate)
- 2-4%: Poor returns (marginal profitability)
- 4-6%: Below acceptable returns
- 6-8%: Minimally acceptable returns
- 8-10%: Moderate returns (acceptable for low-risk)
- 10-12%: Good returns (above hurdle rate)
- 12-14%: Very good returns
- 14-16%: Excellent returns
- 16-20%: Outstanding returns
- ≥ 20%: Exceptional returns (highly attractive)

Scoring Rubric (LOADED FROM CONFIG):
Higher IRR = Better profitability = Higher score (DIRECT relationship)

MODES:
- MOCK: Uses hardcoded IRR assessments from project benchmarks (for testing)
- RULE_BASED: Estimates from World Bank economic indicators (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class ExpectedReturnAgent(BaseParameterAgent):
    """Agent for analyzing expected returns (IRR) for renewable energy projects."""
    
    # Mock data for Phase 1 testing
    # IRR % based on typical solar/wind project economics
    # Factors: LCOE, PPA prices, capacity factors, WACC, policy support
    # Data sourced from IRENA, BNEF, Lazard LCOE reports, project benchmarks
    MOCK_DATA = {
        "Brazil": {
            "irr_pct": 12.5,  # Good PPA prices, strong resources, moderate risk
            "project_type": "Solar + Wind",
            "lcoe_usd_mwh": 35,
            "ppa_price_usd_mwh": 50,
            "wacc_pct": 7.5,
            "status": "Very good returns (good PPA prices + resources)"
        },
        "Germany": {
            "irr_pct": 6.8,  # Low LCOE but also low PPA prices, stable market
            "project_type": "Solar + Wind",
            "lcoe_usd_mwh": 40,
            "ppa_price_usd_mwh": 55,
            "wacc_pct": 3.5,
            "status": "Minimally acceptable (low risk compensates)"
        },
        "USA": {
            "irr_pct": 11.2,  # Strong tax incentives (ITC/PTC), good resources
            "project_type": "Solar + Wind",
            "lcoe_usd_mwh": 33,
            "ppa_price_usd_mwh": 45,
            "wacc_pct": 5.8,
            "status": "Good returns (ITC/PTC boost economics)"
        },
        "China": {
            "irr_pct": 8.5,  # Low LCOE, moderate prices, efficient execution
            "project_type": "Solar + Wind",
            "lcoe_usd_mwh": 28,
            "ppa_price_usd_mwh": 40,
            "wacc_pct": 6.2,
            "status": "Moderate returns (scale + efficiency)"
        },
        "India": {
            "irr_pct": 13.8,  # Very low LCOE, good solar resource, auction prices
            "project_type": "Solar",
            "lcoe_usd_mwh": 26,
            "ppa_price_usd_mwh": 42,
            "wacc_pct": 9.5,
            "status": "Very good returns (low LCOE + scale)"
        },
        "UK": {
            "irr_pct": 7.2,  # Mature market, CFD prices, offshore wind
            "project_type": "Offshore Wind",
            "lcoe_usd_mwh": 55,
            "ppa_price_usd_mwh": 70,
            "wacc_pct": 4.2,
            "status": "Minimally acceptable (stable but tight)"
        },
        "Spain": {
            "irr_pct": 10.5,  # Excellent solar resource, competitive auctions
            "project_type": "Solar",
            "lcoe_usd_mwh": 32,
            "ppa_price_usd_mwh": 45,
            "wacc_pct": 5.0,
            "status": "Good returns (resource quality + low WACC)"
        },
        "Australia": {
            "irr_pct": 14.2,  # Excellent resources, high electricity prices
            "project_type": "Solar + Wind",
            "lcoe_usd_mwh": 35,
            "ppa_price_usd_mwh": 60,
            "wacc_pct": 6.8,
            "status": "Excellent returns (premium prices)"
        },
        "Chile": {
            "irr_pct": 15.8,  # World-class resources, competitive market
            "project_type": "Solar",
            "lcoe_usd_mwh": 25,
            "ppa_price_usd_mwh": 48,
            "wacc_pct": 8.5,
            "status": "Excellent returns (Atacama solar)"
        },
        "Vietnam": {
            "irr_pct": 16.5,  # High FiT initially, good resources, growth market
            "project_type": "Solar",
            "lcoe_usd_mwh": 38,
            "ppa_price_usd_mwh": 70,
            "wacc_pct": 10.0,
            "status": "Outstanding returns (attractive FiT)"
        },
        "South Africa": {
            "irr_pct": 11.8,  # REIPPP auctions, good resources, currency risk
            "project_type": "Solar + Wind",
            "lcoe_usd_mwh": 40,
            "ppa_price_usd_mwh": 60,
            "wacc_pct": 9.2,
            "status": "Good returns (REIPPP program)"
        },
        "Nigeria": {
            "irr_pct": 18.5,  # High electricity prices, off-grid premium
            "project_type": "Solar",
            "lcoe_usd_mwh": 45,
            "ppa_price_usd_mwh": 90,
            "wacc_pct": 15.0,
            "status": "Outstanding returns (high prices offset risk)"
        },
        "Argentina": {
            "irr_pct": 9.2,  # RenovAr auctions, excellent wind, macro risk
            "project_type": "Wind",
            "lcoe_usd_mwh": 42,
            "ppa_price_usd_mwh": 60,
            "wacc_pct": 11.0,
            "status": "Moderate returns (macro risk premium)"
        },
        "Mexico": {
            "irr_pct": 10.8,  # Competitive auctions, good resources
            "project_type": "Solar + Wind",
            "lcoe_usd_mwh": 35,
            "ppa_price_usd_mwh": 48,
            "wacc_pct": 7.8,
            "status": "Good returns (auction framework)"
        },
        "Indonesia": {
            "irr_pct": 12.2,  # Growing market, reasonable FiT, execution risk
            "project_type": "Solar + Geothermal",
            "lcoe_usd_mwh": 48,
            "ppa_price_usd_mwh": 70,
            "wacc_pct": 10.5,
            "status": "Very good returns (growth potential)"
        },
        "Saudi Arabia": {
            "irr_pct": 13.5,  # Excellent solar, low LCOE, stable offtake
            "project_type": "Solar",
            "lcoe_usd_mwh": 18,
            "ppa_price_usd_mwh": 30,
            "wacc_pct": 4.5,
            "status": "Very good returns (world's lowest LCOE)"
        },
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Expected Return Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Expected Return",
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
            f"Initialized ExpectedReturnAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.
        
        Returns:
            List of scoring levels with IRR % thresholds
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            # Get rubric for expected_return parameter
            return_config = params_config['parameters'].get('expected_return', {})
            scoring = return_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_irr_pct": item.get('min_irr_pct', 0.0),
                        "max_irr_pct": item.get('max_irr_pct', 100.0),
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
            {"score": 1, "min_irr_pct": 0.0, "max_irr_pct": 2.0, "range": "< 2%", "description": "Very poor returns"},
            {"score": 2, "min_irr_pct": 2.0, "max_irr_pct": 4.0, "range": "2-4%", "description": "Poor returns"},
            {"score": 3, "min_irr_pct": 4.0, "max_irr_pct": 6.0, "range": "4-6%", "description": "Below acceptable"},
            {"score": 4, "min_irr_pct": 6.0, "max_irr_pct": 8.0, "range": "6-8%", "description": "Minimally acceptable"},
            {"score": 5, "min_irr_pct": 8.0, "max_irr_pct": 10.0, "range": "8-10%", "description": "Moderate returns"},
            {"score": 6, "min_irr_pct": 10.0, "max_irr_pct": 12.0, "range": "10-12%", "description": "Good returns"},
            {"score": 7, "min_irr_pct": 12.0, "max_irr_pct": 14.0, "range": "12-14%", "description": "Very good returns"},
            {"score": 8, "min_irr_pct": 14.0, "max_irr_pct": 16.0, "range": "14-16%", "description": "Excellent returns"},
            {"score": 9, "min_irr_pct": 16.0, "max_irr_pct": 20.0, "range": "16-20%", "description": "Outstanding returns"},
            {"score": 10, "min_irr_pct": 20.0, "max_irr_pct": 100.0, "range": "≥ 20%", "description": "Exceptional returns"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze expected return for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Expected Return for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # AI-powered data uses AI's own confidence assessment
            if data.get('source') == 'ai_powered':
                data_quality = "high"
                ai_confidence = data.get('ai_confidence', 0.8)
                confidence = ai_confidence  # Use AI's confidence directly
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.55  # Lower confidence for estimated IRR
            else:
                data_quality = "high"
                confidence = 0.85  # High confidence for project benchmarks

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
                f"Expected Return analysis complete for {country}: "
                f"Score={score:.1f}, IRR={data.get('irr_pct', 0):.1f}%, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Expected Return analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Expected Return analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch expected return data.
        
        In MOCK mode: Returns mock IRR data from project benchmarks
        In RULE_BASED mode: Estimates from World Bank economic indicators
        In AI_POWERED mode: Would use LLM to extract from IRENA/BNEF reports (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with expected return data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate returns")
                data = {
                    "irr_pct": 9.0,
                    "project_type": "Solar",
                    "lcoe_usd_mwh": 40,
                    "ppa_price_usd_mwh": 52,
                    "wacc_pct": 8.0,
                    "status": "Moderate returns"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: IRR={data.get('irr_pct')}%")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate from World Bank economic indicators
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch GDP per capita (proxy for electricity prices and WACC)
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch lending interest rate (proxy for WACC)
                lending_rate = self.data_service.get_value(
                    country=country,
                    indicator='lending_interest_rate',
                    default=None
                )
                
                # Fetch renewable consumption % (proxy for market maturity/LCOE)
                renewable_pct = self.data_service.get_value(
                    country=country,
                    indicator='renewable_consumption',
                    default=None
                )
                
                # Fetch energy use per capita (proxy for electricity demand/prices)
                energy_use = self.data_service.get_value(
                    country=country,
                    indicator='energy_use',
                    default=None
                )
                
                if gdp_per_capita is None or lending_rate is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate project IRR
                irr_pct = self._estimate_project_irr(
                    country,
                    gdp_per_capita,
                    lending_rate,
                    renewable_pct,
                    energy_use
                )
                
                # Estimate project economics
                lcoe = self._estimate_lcoe(renewable_pct, gdp_per_capita)
                ppa_price = self._estimate_ppa_price(gdp_per_capita, energy_use)
                wacc = self._estimate_wacc(lending_rate, gdp_per_capita)
                status = self._determine_return_status(irr_pct)
                
                data = {
                    'irr_pct': irr_pct,
                    'project_type': 'Solar + Wind',
                    'lcoe_usd_mwh': lcoe,
                    'ppa_price_usd_mwh': ppa_price,
                    'wacc_pct': wacc,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_gdp_per_capita': gdp_per_capita,
                    'raw_lending_rate': lending_rate,
                    'raw_renewable_pct': renewable_pct if renewable_pct else 0
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: IRR={irr_pct:.1f}% "
                    f"from GDP/capita=${gdp_per_capita:,.0f}, lending={lending_rate:.1f}%"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating IRR for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # Extract expected returns using AI extraction system
            try:
                from ai_extraction_system import AIExtractionAdapter

                # Initialize AI extraction adapter
                adapter = AIExtractionAdapter(
                    llm_config=self.config.get('llm_config') if self.config else None,
                    cache_config=self.config.get('cache_config') if self.config else None
                )

                # Extract expected returns using AI
                extraction_result = adapter.extract_parameter(
                    parameter_name='expected_return',
                    country=country,
                    period=period,
                    documents=kwargs.get('documents'),
                    document_urls=kwargs.get('document_urls')
                )

                logger.info(f"Using AI_POWERED mode for {country}")

                if extraction_result and extraction_result.get('value') is not None:
                    # AI returns score (1-10)
                    score = float(extraction_result['value'])

                    # Get metadata from extraction
                    metadata = extraction_result.get('metadata', {})

                    # Determine status from score
                    status = self._score_to_status(score)

                    # Build data dictionary
                    data = {
                        'irr_pct': metadata.get('typical_irr', score * 1.5),  # Approximate IRR from score
                        'project_type': metadata.get('technology', 'Mixed'),
                        'status': status,
                        'source': 'ai_powered',
                        'ai_confidence': extraction_result.get('confidence', 0.8),
                        'ai_justification': extraction_result.get('justification', ''),
                        'ai_score': score,
                        'irr_range_min': metadata.get('irr_range_min'),
                        'irr_range_max': metadata.get('irr_range_max'),
                        'equity_return': metadata.get('equity_return'),
                        'debt_cost': metadata.get('debt_cost'),
                        'ppa_price': metadata.get('ppa_price_solar') or metadata.get('ppa_price_wind'),
                        'period': period
                    }

                    logger.info(
                        f"AI extraction successful for {country}: "
                        f"score={score}/10, "
                        f"confidence={data['ai_confidence']:.2f}"
                    )

                    return data
                else:
                    logger.warning(f"AI extraction returned no value for {country}, falling back to MOCK")
                    return self._fetch_data_mock_fallback(country)

            except Exception as e:
                logger.error(
                    f"Error using AI extraction for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
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
            "irr_pct": 9.0,
            "project_type": "Solar",
            "lcoe_usd_mwh": 40,
            "ppa_price_usd_mwh": 52,
            "wacc_pct": 8.0,
            "status": "Moderate returns"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_project_irr(
        self,
        country: str,
        gdp_per_capita: float,
        lending_rate: float,
        renewable_pct: Optional[float],
        energy_use: Optional[float]
    ) -> float:
        """Estimate project IRR from economic indicators.
        
        Simplified IRR estimation:
        IRR ≈ WACC + Risk Premium + Margin from (PPA Price - LCOE) spread
        
        Args:
            country: Country name
            gdp_per_capita: GDP per capita (USD)
            lending_rate: Lending interest rate (%)
            renewable_pct: Renewable consumption (%)
            energy_use: Energy use per capita
            
        Returns:
            Estimated IRR in %
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Estimate WACC (lending rate * 0.75 is typical project finance adjustment)
        wacc = lending_rate * 0.75
        
        # Estimate risk premium based on GDP per capita
        if gdp_per_capita >= 40000:
            # High income - low risk premium
            risk_premium = 2.0
        elif gdp_per_capita >= 15000:
            # Upper middle income
            risk_premium = 4.0
        elif gdp_per_capita >= 5000:
            # Lower middle income
            risk_premium = 6.0
        else:
            # Low income - high risk premium
            risk_premium = 8.0
        
        # Estimate project economics margin
        # Higher renewable % = lower LCOE but also lower PPA prices (competition)
        # Lower renewable % = higher LCOE but potentially higher PPA prices (scarcity)
        if renewable_pct is not None and renewable_pct > 0:
            if renewable_pct >= 40:
                # Very mature market - tight margins
                economics_margin = 2.0
            elif renewable_pct >= 20:
                # Mature market - moderate margins
                economics_margin = 3.5
            elif renewable_pct >= 10:
                # Growing market - good margins
                economics_margin = 5.0
            else:
                # Early market - high margins but execution risk
                economics_margin = 6.0
        else:
            # No data - use GDP as proxy
            if gdp_per_capita >= 30000:
                economics_margin = 2.5  # Mature, competitive
            elif gdp_per_capita >= 10000:
                economics_margin = 4.0  # Developing
            else:
                economics_margin = 5.5  # Emerging
        
        # Calculate estimated IRR
        irr = wacc + risk_premium + economics_margin
        
        # Calibrate with mock data if available (40/60 blend - less confident)
        if base_data:
            base_irr = base_data.get('irr_pct', irr)
            irr = irr * 0.4 + base_irr * 0.6
        
        # Clamp to reasonable range
        irr = max(2.0, min(irr, 25.0))
        
        logger.debug(
            f"IRR estimation for {country}: "
            f"WACC={wacc:.1f}% + risk_premium={risk_premium:.1f}% + "
            f"margin={economics_margin:.1f}% = {irr:.1f}%"
        )
        
        return irr
    
    def _estimate_lcoe(self, renewable_pct: Optional[float], gdp_per_capita: float) -> float:
        """Estimate LCOE based on market maturity."""
        # Higher renewable % = more mature = lower LCOE
        if renewable_pct is not None and renewable_pct > 0:
            if renewable_pct >= 40:
                base_lcoe = 30
            elif renewable_pct >= 20:
                base_lcoe = 35
            elif renewable_pct >= 10:
                base_lcoe = 40
            else:
                base_lcoe = 45
        else:
            # Use GDP as proxy
            if gdp_per_capita >= 30000:
                base_lcoe = 35
            elif gdp_per_capita >= 10000:
                base_lcoe = 40
            else:
                base_lcoe = 45
        
        return base_lcoe
    
    def _estimate_ppa_price(self, gdp_per_capita: float, energy_use: Optional[float]) -> float:
        """Estimate PPA price based on economic development."""
        # Higher GDP = higher electricity prices generally
        if gdp_per_capita >= 40000:
            base_price = 60
        elif gdp_per_capita >= 20000:
            base_price = 50
        elif gdp_per_capita >= 10000:
            base_price = 45
        elif gdp_per_capita >= 5000:
            base_price = 40
        else:
            base_price = 50  # Low GDP but potentially higher prices due to scarcity
        
        return base_price
    
    def _estimate_wacc(self, lending_rate: float, gdp_per_capita: float) -> float:
        """Estimate WACC from lending rate."""
        # Project finance WACC typically ~75% of lending rate
        base_wacc = lending_rate * 0.75
        
        # Adjust for country risk
        if gdp_per_capita >= 40000:
            adjustment = -1.0  # Developed markets
        elif gdp_per_capita >= 15000:
            adjustment = 0.0
        else:
            adjustment = +1.0  # Higher risk
        
        wacc = base_wacc + adjustment
        return max(3.0, min(wacc, 18.0))
    
    def _determine_return_status(self, irr_pct: float) -> str:
        """Determine return status description."""
        if irr_pct >= 20:
            return "Exceptional returns (highly attractive)"
        elif irr_pct >= 16:
            return "Outstanding returns"
        elif irr_pct >= 14:
            return "Excellent returns"
        elif irr_pct >= 12:
            return "Very good returns"
        elif irr_pct >= 10:
            return "Good returns (above hurdle rate)"
        elif irr_pct >= 8:
            return "Moderate returns (acceptable)"
        elif irr_pct >= 6:
            return "Minimally acceptable returns"
        else:
            return "Below acceptable returns"

    def _score_to_status(self, score: float) -> str:
        """Convert numeric score (1-10) to status string.

        This is the inverse of _calculate_score() - used when AI provides score directly.

        Args:
            score: Score value 1-10

        Returns:
            Status description string
        """
        score = round(score)
        if score >= 10:
            return "Exceptional returns (highly attractive)"
        elif score >= 9:
            return "Outstanding returns"
        elif score >= 8:
            return "Excellent returns"
        elif score >= 7:
            return "Very good returns"
        elif score >= 6:
            return "Good returns (above hurdle rate)"
        elif score >= 5:
            return "Moderate returns (acceptable)"
        elif score >= 4:
            return "Minimally acceptable returns"
        else:
            return "Below acceptable returns"

    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate expected return score based on IRR %.

        DIRECT: Higher IRR = better profitability = higher score

        Args:
            data: Expected return data with irr_pct (or ai_score for AI mode)
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

        irr_pct = data.get("irr_pct", 0)

        logger.debug(f"Calculating score for {country}: {irr_pct:.1f}% IRR")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_pct = level.get("min_irr_pct", 0.0)
            max_pct = level.get("max_irr_pct", 100.0)
            
            if min_pct <= irr_pct < max_pct:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{irr_pct:.1f}% falls in range {min_pct:.0f}-{max_pct:.0f}%"
                )
                return float(score)
        
        # Handle IRR >= 20% (score 10)
        if irr_pct >= 20.0:
            logger.debug(f"Score 10 assigned: {irr_pct:.1f}% >= 20%")
            return 10.0
        
        # Fallback (shouldn't reach here with proper rubric)
        logger.warning(f"No rubric match for {irr_pct:.1f}%, defaulting to score 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the expected return score.
        
        Args:
            data: Expected return data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        irr_pct = data.get("irr_pct", 0)
        project_type = data.get("project_type", "renewable energy")
        lcoe = data.get("lcoe_usd_mwh", 0)
        ppa_price = data.get("ppa_price_usd_mwh", 0)
        wacc = data.get("wacc_pct", 0)
        status = data.get("status", "moderate returns")
        source = data.get("source", "unknown")
        
        # Find description from rubric
        description = "moderate returns"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification based on source
        if source == 'ai_powered':
            # Use AI-generated justification directly
            ai_justification = data.get('ai_justification', '')
            if ai_justification:
                return ai_justification
            # Fallback if AI didn't provide justification
            else:
                return (
                    f"AI-extracted expected return score of {score}/10 indicates {description}. "
                    f"Renewable energy projects show {'highly attractive' if score >= 8 else 'good' if score >= 6 else 'moderate'} "
                    f"profitability in this market."
                )
        elif source == 'rule_based':
            gdp = data.get('raw_gdp_per_capita', 0)
            lending = data.get('raw_lending_rate', 0)
            justification = (
                f"Based on World Bank data: Estimated IRR of {irr_pct:.1f}% for {project_type} projects "
                f"indicates {description} (derived from GDP/capita ${gdp:,.0f} and lending rate {lending:.1f}%). "
                f"Estimated economics: LCOE ${lcoe:.0f}/MWh, PPA price ${ppa_price:.0f}/MWh, "
                f"WACC {wacc:.1f}%. {status.capitalize()} makes this market "
                f"{'highly attractive' if score >= 8 else 'moderately attractive' if score >= 6 else 'viable but tight'} "
                f"for renewable energy investment. "
            )
        else:
            # Mock data - use detailed project economics
            justification = (
                f"Expected IRR of {irr_pct:.1f}% for {project_type} projects indicates {description}. "
                f"Economics driven by LCOE of ${lcoe:.0f}/MWh, PPA prices of ${ppa_price:.0f}/MWh, "
                f"and WACC of {wacc:.1f}%. {status.capitalize()} makes this market "
                f"{'highly attractive' if score >= 8 else 'moderately attractive' if score >= 6 else 'viable but tight'} "
                f"for renewable energy investment. "
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

        # Check source type
        if data and data.get('source') == 'ai_powered':
            sources.append("AI-Powered Extraction from Investment Reports")
            sources.append("IRENA Renewable Power Generation Costs")
            sources.append("BloombergNEF Market Analysis")
            sources.append(f"{country} Project Financial Models")
        elif data and data.get('source') == 'rule_based':
            sources.append("World Bank Economic Indicators - Rule-Based Estimation")
            sources.append("Project financial models (Reference)")
            sources.append(f"{country} Project Financial Models")
            sources.append("Developer IRR Benchmarks")
        else:
            sources.append("IRENA Renewable Power Generation Costs 2023 - Mock Data")
            sources.append("Bloomberg New Energy Finance (BNEF) Market Outlook")
            sources.append("Lazard Levelized Cost of Energy Analysis v16.0")
            sources.append(f"{country} Project Financial Models")
            sources.append("Developer IRR Benchmarks")
        
        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Expected Return parameter.
        
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
            "IRENA Renewable Power Generation Costs",
            "Bloomberg New Energy Finance (BNEF)",
            "Lazard Levelized Cost of Energy (LCOE)",
            "Project financial models and pro formas",
            "Developer and investor IRR benchmarks",
            "Auction results and PPA databases"
        ]


# Convenience function for direct usage
def analyze_expected_return(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze expected return.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = ExpectedReturnAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
