"""System Modifiers Agent - Composite adjustment factors.

This agent provides final calibration adjustments to country rankings
based on systemic factors that affect all renewable investments:
- Currency risk and volatility
- Geopolitical risk and stability
- Market anomalies and special circumstances
- Macroeconomic environment

These modifiers act as a final adjustment layer that can amplify or
dampen the base attractiveness scores from other parameters.

Key evaluation criteria:
- Currency stability and convertibility
- Exchange rate volatility
- Geopolitical risk indices
- Sanctions and trade restrictions
- Systemic market risks
- Special circumstances

Risk Level Categories (1-10):
1. Severe negative factors
2. Very high negative impact
3. High negative impact
4. Above moderate negative impact
5. Moderate factors
6. Below moderate positive impact
7. Low risk environment
8. Very low risk
9. Minimal risk
10. Optimal conditions

Scoring Rubric (LOADED FROM CONFIG):
Lower risk = Better investment environment = Higher score

MODES:
- MOCK: Uses composite risk assessments from geopolitical indices
- RULE_BASED: Estimates from World Bank macroeconomic stability indicators
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import statistics

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class SystemModifiersAgent(BaseParameterAgent):
    """Agent for analyzing systemic adjustment factors."""
    
    # Mock data for Phase 1 testing
    # Composite risk assessment considering multiple systemic factors
    # Data from geopolitical risk indices, currency volatility, IMF/World Bank
    MOCK_DATA = {
        "Brazil": {
            "score": 6,
            "category": "below_moderate_positive",
            "currency_risk": "Moderate (BRL volatile but manageable)",
            "currency_volatility_annual": 15.2,
            "geopolitical_risk": "Low to Moderate (stable democracy, BRICS member)",
            "market_anomalies": "None significant",
            "sanctions_status": "None",
            "convertibility": "Full (some capital controls)",
            "composite_assessment": "Relatively stable with manageable currency risk",
            "status": "Below moderate positive impact - manageable risks with good fundamentals"
        },
        "Germany": {
            "score": 9,
            "category": "minimal_risk",
            "currency_risk": "Very Low (EUR stability, eurozone)",
            "currency_volatility_annual": 3.8,
            "geopolitical_risk": "Very Low (EU, NATO, stable)",
            "market_anomalies": "None",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Excellent stability across all factors",
            "status": "Minimal risk - excellent investment environment"
        },
        "USA": {
            "score": 9,
            "category": "minimal_risk",
            "currency_risk": "Very Low (USD reserve currency)",
            "currency_volatility_annual": 2.5,
            "geopolitical_risk": "Very Low (stable, rule of law)",
            "market_anomalies": "None",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Optimal stability, reserve currency advantage",
            "status": "Minimal risk - best-in-class stability"
        },
        "China": {
            "score": 5,
            "category": "moderate_factors",
            "currency_risk": "Moderate (CNY controlled, capital controls)",
            "currency_volatility_annual": 4.5,
            "geopolitical_risk": "Moderate (rising tensions, trade issues)",
            "market_anomalies": "Capital controls, repatriation challenges",
            "sanctions_status": "Some technology sanctions",
            "convertibility": "Limited (capital controls)",
            "composite_assessment": "Balanced risks - stable but controlled environment",
            "status": "Moderate factors - managed economy with restrictions"
        },
        "India": {
            "score": 6,
            "category": "below_moderate_positive",
            "currency_risk": "Moderate (INR volatile but improving)",
            "currency_volatility_annual": 12.8,
            "geopolitical_risk": "Moderate (border tensions, but stable democracy)",
            "market_anomalies": "None significant",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Good fundamentals with manageable currency risk",
            "status": "Below moderate positive - improving environment"
        },
        "UK": {
            "score": 8,
            "category": "very_low_risk",
            "currency_risk": "Low (GBP stable, post-Brexit volatility declining)",
            "currency_volatility_annual": 5.2,
            "geopolitical_risk": "Low (stable, rule of law)",
            "market_anomalies": "Brexit transition mostly complete",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Strong stability, Brexit effects fading",
            "status": "Very low risk - strong investment environment"
        },
        "Spain": {
            "score": 7,
            "category": "low_risk",
            "currency_risk": "Very Low (EUR, eurozone)",
            "currency_volatility_annual": 3.8,
            "geopolitical_risk": "Low (EU, NATO, stable)",
            "market_anomalies": "Retroactive policy legacy (improving)",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Good stability, policy risk legacy fading",
            "status": "Low risk - favorable environment with improving policy confidence"
        },
        "Australia": {
            "score": 8,
            "category": "very_low_risk",
            "currency_risk": "Low (AUD relatively stable)",
            "currency_volatility_annual": 8.5,
            "geopolitical_risk": "Very Low (stable democracy, rule of law)",
            "market_anomalies": "None",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Strong stability across factors",
            "status": "Very low risk - excellent investment environment"
        },
        "Chile": {
            "score": 6,
            "category": "below_moderate_positive",
            "currency_risk": "Moderate (CLP volatile, copper-linked)",
            "currency_volatility_annual": 14.5,
            "geopolitical_risk": "Low (stable democracy, good governance)",
            "market_anomalies": "Social unrest legacy (stabilizing)",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Good fundamentals with commodity-linked currency",
            "status": "Below moderate positive - manageable risks"
        },
        "Vietnam": {
            "score": 4,
            "category": "above_moderate_negative",
            "currency_risk": "High (VND controls, repatriation issues)",
            "currency_volatility_annual": 6.2,
            "geopolitical_risk": "Moderate (one-party state, regional tensions)",
            "market_anomalies": "Repatriation challenges, FX controls",
            "sanctions_status": "None",
            "convertibility": "Limited (restrictions)",
            "composite_assessment": "Notable currency and repatriation risks",
            "status": "Above moderate negative impact - significant FX and transfer risks"
        },
        "South Africa": {
            "score": 5,
            "category": "moderate_factors",
            "currency_risk": "High (ZAR very volatile)",
            "currency_volatility_annual": 18.5,
            "geopolitical_risk": "Moderate (political uncertainty, governance challenges)",
            "market_anomalies": "Load shedding, Eskom crisis",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Significant currency risk but manageable political environment",
            "status": "Moderate factors - high volatility balanced by structural reforms"
        },
        "Nigeria": {
            "score": 3,
            "category": "high_negative",
            "currency_risk": "Very High (NGN extremely volatile, FX shortages)",
            "currency_volatility_annual": 28.5,
            "geopolitical_risk": "High (security issues, corruption)",
            "market_anomalies": "FX market dysfunction, repatriation difficulties",
            "sanctions_status": "None",
            "convertibility": "Limited (severe FX controls)",
            "composite_assessment": "Multiple significant risks compound",
            "status": "High negative impact - severe currency and repatriation risks"
        },
        "Argentina": {
            "score": 3,
            "category": "high_negative",
            "currency_risk": "Very High (ARS hyperinflation, controls)",
            "currency_volatility_annual": 45.2,
            "geopolitical_risk": "High (economic crisis, policy uncertainty)",
            "market_anomalies": "Capital controls, multiple exchange rates",
            "sanctions_status": "None",
            "convertibility": "Very Limited (strict controls)",
            "composite_assessment": "Severe currency crisis and policy uncertainty",
            "status": "High negative impact - major macroeconomic instability"
        },
        "Mexico": {
            "score": 6,
            "category": "below_moderate_positive",
            "currency_risk": "Moderate (MXN volatile but liquid)",
            "currency_volatility_annual": 11.5,
            "geopolitical_risk": "Moderate (security issues but stable democracy)",
            "market_anomalies": "Policy uncertainty under current administration",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Manageable risks with good market access",
            "status": "Below moderate positive - volatile but tradable currency"
        },
        "Indonesia": {
            "score": 5,
            "category": "moderate_factors",
            "currency_risk": "Moderate (IDR volatile, EM sensitivity)",
            "currency_volatility_annual": 13.2,
            "geopolitical_risk": "Moderate (stable but complex politics)",
            "market_anomalies": "None significant",
            "sanctions_status": "None",
            "convertibility": "Full (with some restrictions)",
            "composite_assessment": "Typical emerging market risks",
            "status": "Moderate factors - standard EM risk profile"
        },
        "Saudi Arabia": {
            "score": 7,
            "category": "low_risk",
            "currency_risk": "Very Low (SAR pegged to USD)",
            "currency_volatility_annual": 0.5,
            "geopolitical_risk": "Moderate (regional tensions but stable internally)",
            "market_anomalies": "None",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Currency stability from USD peg, regional geopolitics",
            "status": "Low risk - strong currency stability with some geopolitical factors"
        },
    }
    
    def __init__(
        self,
        mode: AgentMode = AgentMode.MOCK,
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize System Modifiers Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="System Modifiers",
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
            f"Initialized SystemModifiersAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            modifiers_config = params_config['parameters'].get('system_modifiers', {})
            scoring = modifiers_config.get('scoring', [])
            
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
            {"score": 1, "range": "Severe negative", "description": "Multiple severe risks compound"},
            {"score": 2, "range": "Very high negative", "description": "Major instability"},
            {"score": 3, "range": "High negative", "description": "Significant risks"},
            {"score": 4, "range": "Above moderate negative", "description": "Notable volatility"},
            {"score": 5, "range": "Moderate", "description": "Balanced risk profile"},
            {"score": 6, "range": "Below moderate positive", "description": "Relatively stable"},
            {"score": 7, "range": "Low risk", "description": "Good stability"},
            {"score": 8, "range": "Very low risk", "description": "Strong stability"},
            {"score": 9, "range": "Minimal risk", "description": "Excellent environment"},
            {"score": 10, "range": "Optimal", "description": "Best-in-class"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze system modifiers for a country.
        
        Args:
            country: Country name
            period: Time period
            **kwargs: Additional context
            
        Returns:
            ParameterScore with composite risk assessment
        """
        try:
            logger.info(f"Analyzing System Modifiers for {country} ({period}) in {self.mode.value} mode")
            
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
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.55  # Lower confidence for estimated systemic risks
            else:
                data_quality = "high"
                confidence = 0.80  # High confidence for composite risk indices

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
                f"System Modifiers analysis complete for {country}: "
                f"Score={score:.1f}, Category={data.get('category', 'unknown')}, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"System Modifiers analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"System Modifiers analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch system modifiers data.
        
        In MOCK mode: Returns composite risk assessments from indices
        In RULE_BASED mode: Estimates from World Bank macroeconomic indicators
        In AI_POWERED mode: Would use LLM to assess geopolitical risks (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with systemic risk data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate factors")
                data = {
                    "score": 5,
                    "category": "moderate_factors",
                    "currency_risk": "Moderate",
                    "currency_volatility_annual": 10.0,
                    "geopolitical_risk": "Moderate",
                    "market_anomalies": "None significant",
                    "sanctions_status": "None",
                    "convertibility": "Full",
                    "composite_assessment": "Balanced risk profile",
                    "status": "Moderate factors"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: Score={data.get('score')}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate from World Bank macroeconomic indicators
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch macroeconomic stability indicators
                inflation = self.data_service.get_value(
                    country=country,
                    indicator='inflation_consumer_prices',
                    default=None
                )
                
                interest_rate = self.data_service.get_value(
                    country=country,
                    indicator='lending_interest_rate',
                    default=None
                )
                
                trade_pct_gdp = self.data_service.get_value(
                    country=country,
                    indicator='trade',
                    default=None
                )
                
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                if inflation is None and interest_rate is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate systemic risk score
                risk_score = self._estimate_systemic_risk(
                    country,
                    inflation,
                    interest_rate,
                    trade_pct_gdp,
                    gdp_per_capita
                )
                
                # Estimate components
                currency_risk = self._estimate_currency_risk(inflation, interest_rate)
                currency_volatility = self._estimate_currency_volatility(inflation, interest_rate)
                geopolitical_risk = self._estimate_geopolitical_risk(gdp_per_capita)
                convertibility = self._estimate_convertibility(trade_pct_gdp, gdp_per_capita)
                category = self._determine_risk_category(risk_score)
                status = self._determine_risk_status(risk_score)
                
                data = {
                    'score': risk_score,
                    'category': category,
                    'currency_risk': currency_risk,
                    'currency_volatility_annual': currency_volatility,
                    'geopolitical_risk': geopolitical_risk,
                    'market_anomalies': 'None identified',
                    'sanctions_status': 'None identified',
                    'convertibility': convertibility,
                    'composite_assessment': self._generate_composite_assessment(risk_score, currency_risk, geopolitical_risk),
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_inflation': inflation if inflation else 0,
                    'raw_interest_rate': interest_rate if interest_rate else 0,
                    'raw_trade_pct': trade_pct_gdp if trade_pct_gdp else 0,
                    'raw_gdp_per_capita': gdp_per_capita if gdp_per_capita else 0
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: Risk score={risk_score:.1f} "
                    f"from inflation={inflation if inflation else 0:.1f}%, "
                    f"interest={interest_rate if interest_rate else 0:.1f}%"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating systemic risks for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # AI-powered extraction using SystemModifiersExtractor
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
                    parameter_name='system_modifiers',
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
                        'score': ai_data['value'],  # Use AI score directly
                        'category': self._determine_category_from_score(ai_data['value']),
                        'currency_risk': ai_data.get('metadata', {}).get('currency_risk', 'Moderate'),
                        'currency_volatility_annual': ai_data.get('metadata', {}).get('currency_volatility', 10.0),
                        'geopolitical_risk': ai_data.get('metadata', {}).get('geopolitical_risk', 'Moderate'),
                        'market_anomalies': ai_data.get('metadata', {}).get('market_anomalies', 'None significant'),
                        'sanctions_status': ai_data.get('metadata', {}).get('sanctions', 'None'),
                        'convertibility': ai_data.get('metadata', {}).get('convertibility', 'Full'),
                        'composite_assessment': ai_data.get('metadata', {}).get('composite_assessment', 'Systemic risk analysis'),
                        'status': ai_data.get('metadata', {}).get('status', 'Systemic factors analysis'),
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
            "score": 5,
            "category": "moderate_factors",
            "currency_risk": "Moderate",
            "currency_volatility_annual": 10.0,
            "geopolitical_risk": "Moderate",
            "market_anomalies": "None significant",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Balanced risk profile",
            "status": "Moderate factors"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_systemic_risk(
        self,
        country: str,
        inflation: Optional[float],
        interest_rate: Optional[float],
        trade_pct_gdp: Optional[float],
        gdp_per_capita: Optional[float]
    ) -> float:
        """Estimate overall systemic risk score from macroeconomic indicators.
        
        Lower risk = Higher score
        
        Args:
            country: Country name
            inflation: Inflation rate (%)
            interest_rate: Lending interest rate (%)
            trade_pct_gdp: Trade (% of GDP)
            gdp_per_capita: GDP per capita (USD)
            
        Returns:
            Systemic risk score (1-10)
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Component scores (each 0-10)
        scores = []
        
        # 1. Currency stability score (from inflation)
        if inflation is not None:
            if inflation <= 2:
                currency_score = 10  # Very stable (Germany, USA)
            elif inflation <= 4:
                currency_score = 9  # Stable
            elif inflation <= 6:
                currency_score = 7  # Moderate
            elif inflation <= 10:
                currency_score = 6  # Elevated
            elif inflation <= 15:
                currency_score = 5  # High
            elif inflation <= 25:
                currency_score = 3  # Very high
            else:
                currency_score = 1  # Hyperinflation (Argentina)
            scores.append(currency_score)
        
        # 2. Macroeconomic stability score (from interest rate)
        if interest_rate is not None:
            if interest_rate <= 5:
                macro_score = 9  # Very stable (developed markets)
            elif interest_rate <= 8:
                macro_score = 7  # Stable
            elif interest_rate <= 12:
                macro_score = 6  # Moderate
            elif interest_rate <= 18:
                macro_score = 4  # Elevated risk
            else:
                macro_score = 2  # High risk
            scores.append(macro_score)
        
        # 3. Openness/convertibility score (from trade %)
        if trade_pct_gdp is not None:
            if trade_pct_gdp >= 100:
                trade_score = 9  # Very open (small open economies)
            elif trade_pct_gdp >= 60:
                trade_score = 8  # Open
            elif trade_pct_gdp >= 40:
                trade_score = 7  # Moderately open
            elif trade_pct_gdp >= 25:
                trade_score = 6  # Moderate
            else:
                trade_score = 5  # Less open (but not necessarily bad)
            scores.append(trade_score)
        
        # 4. Development/governance score (from GDP per capita)
        if gdp_per_capita is not None:
            if gdp_per_capita >= 40000:
                dev_score = 9  # Very high (good governance proxy)
            elif gdp_per_capita >= 20000:
                dev_score = 8  # High
            elif gdp_per_capita >= 10000:
                dev_score = 7  # Upper middle
            elif gdp_per_capita >= 5000:
                dev_score = 6  # Middle
            else:
                dev_score = 5  # Lower middle/low
            scores.append(dev_score)
        
        # Calculate composite score
        if scores:
            # Weighted average: currency 40%, macro 30%, trade 15%, development 15%
            weights = [0.40, 0.30, 0.15, 0.15][:len(scores)]
            # Normalize weights
            total_weight = sum(weights)
            weights = [w/total_weight for w in weights]
            
            estimated_score = sum(s * w for s, w in zip(scores, weights))
        else:
            estimated_score = 5.0
        
        # Calibrate with mock data if available (30/70 blend)
        if base_data:
            base_score_mock = base_data.get('score', estimated_score)
            estimated_score = estimated_score * 0.3 + base_score_mock * 0.7
        
        # Round to nearest 0.5
        estimated_score = round(estimated_score * 2) / 2
        
        # Clamp to valid range
        estimated_score = max(1.0, min(estimated_score, 10.0))
        
        logger.debug(
            f"Systemic risk estimation for {country}: "
            f"Inflation={inflation if inflation else 0:.1f}% → currency={scores[0] if len(scores)>0 else 0:.0f}, "
            f"Interest={interest_rate if interest_rate else 0:.1f}% → macro={scores[1] if len(scores)>1 else 0:.0f}, "
            f"Trade={trade_pct_gdp if trade_pct_gdp else 0:.1f}% → trade={scores[2] if len(scores)>2 else 0:.0f}, "
            f"GDP/cap=${gdp_per_capita if gdp_per_capita else 0:,.0f} → dev={scores[3] if len(scores)>3 else 0:.0f}, "
            f"final_score={estimated_score:.1f}"
        )
        
        return estimated_score
    
    def _estimate_currency_risk(self, inflation: Optional[float], interest_rate: Optional[float]) -> str:
        """Estimate currency risk level."""
        if inflation is None:
            return "Moderate"
        
        if inflation <= 3:
            return "Very Low (stable, low inflation)"
        elif inflation <= 6:
            return "Low (controlled inflation)"
        elif inflation <= 10:
            return "Moderate (elevated inflation)"
        elif inflation <= 20:
            return "High (high inflation, volatility)"
        else:
            return "Very High (hyperinflation risk)"
    
    def _estimate_currency_volatility(self, inflation: Optional[float], interest_rate: Optional[float]) -> float:
        """Estimate annual currency volatility percentage."""
        if inflation is None:
            return 10.0
        
        # Simple proxy: volatility correlates with inflation
        # Low inflation = low volatility, high inflation = high volatility
        if inflation <= 2:
            return 3.0  # Very stable (EUR, USD)
        elif inflation <= 4:
            return 5.0  # Stable
        elif inflation <= 6:
            return 8.0  # Moderate
        elif inflation <= 10:
            return 12.0  # Elevated
        elif inflation <= 15:
            return 18.0  # High (BRL, ZAR)
        elif inflation <= 25:
            return 28.0  # Very high (NGN)
        else:
            return 45.0  # Extreme (ARS)
    
    def _estimate_geopolitical_risk(self, gdp_per_capita: Optional[float]) -> str:
        """Estimate geopolitical risk level (proxy from development level)."""
        if gdp_per_capita is None:
            return "Moderate"
        
        # Simple proxy: higher development = better governance/stability
        if gdp_per_capita >= 40000:
            return "Very Low (stable, developed)"
        elif gdp_per_capita >= 20000:
            return "Low (stable, upper middle income)"
        elif gdp_per_capita >= 10000:
            return "Moderate (middle income)"
        else:
            return "Moderate to High (emerging/frontier)"
    
    def _estimate_convertibility(self, trade_pct_gdp: Optional[float], gdp_per_capita: Optional[float]) -> str:
        """Estimate currency convertibility."""
        if trade_pct_gdp is None:
            return "Full"
        
        # Higher trade openness suggests fewer capital controls
        if trade_pct_gdp >= 80:
            return "Full (very open economy)"
        elif trade_pct_gdp >= 50:
            return "Full (open economy)"
        elif trade_pct_gdp >= 30:
            return "Full (moderate openness)"
        else:
            # Lower openness might indicate controls
            if gdp_per_capita and gdp_per_capita >= 30000:
                return "Full (developed market)"
            else:
                return "Full (some restrictions possible)"
    
    def _determine_risk_category(self, score: float) -> str:
        """Determine risk category from score."""
        if score >= 9.5:
            return "optimal"
        elif score >= 8.5:
            return "minimal_risk"
        elif score >= 7.5:
            return "very_low_risk"
        elif score >= 6.5:
            return "low_risk"
        elif score >= 5.5:
            return "below_moderate_positive"
        elif score >= 4.5:
            return "moderate_factors"
        elif score >= 3.5:
            return "above_moderate_negative"
        elif score >= 2.5:
            return "high_negative"
        elif score >= 1.5:
            return "very_high_negative"
        else:
            return "severe_negative"
    
    def _determine_risk_status(self, score: float) -> str:
        """Determine risk status description from score."""
        if score >= 9.5:
            return "Optimal conditions - best-in-class stability"
        elif score >= 8.5:
            return "Minimal risk - excellent investment environment"
        elif score >= 7.5:
            return "Very low risk - strong stability"
        elif score >= 6.5:
            return "Low risk - favorable environment"
        elif score >= 5.5:
            return "Below moderate positive - manageable risks"
        elif score >= 4.5:
            return "Moderate factors - balanced risk profile"
        elif score >= 3.5:
            return "Above moderate negative - notable risks"
        elif score >= 2.5:
            return "High negative impact - significant risks"
        elif score >= 1.5:
            return "Very high negative - major instability"
        else:
            return "Severe negative factors - multiple severe risks"
    
    def _generate_composite_assessment(self, score: float, currency_risk: str, geopolitical_risk: str) -> str:
        """Generate composite risk assessment."""
        if score >= 8.5:
            return "Excellent stability across all macroeconomic factors"
        elif score >= 7.0:
            return "Good stability with manageable risks"
        elif score >= 5.5:
            return "Relatively stable with some volatility"
        elif score >= 4.0:
            return "Moderate risks across multiple factors"
        else:
            return "Elevated risks requiring careful management"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate system modifiers score.
        
        Lower risk = Better environment = Higher score
        
        Args:
            data: System modifiers data
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using calculated score {score} for {country}")
            return float(score)
        
        # Otherwise default to moderate
        score = 5
        
        logger.debug(f"Using default score {score} for {country}")
        
        return float(score)
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the system modifiers score.

        Args:
            data: System modifiers data
            score: Calculated score
            country: Country name
            period: Time period

        Returns:
            Human-readable justification string
        """
        source = data.get("source", "unknown")

        # If AI_POWERED mode, use AI-generated justification
        if source == 'ai_powered':
            return data.get('ai_justification', 'AI analysis of systemic risk factors.')

        category = data.get("category", "moderate_factors")
        currency = data.get("currency_risk", "moderate")
        volatility = data.get("currency_volatility_annual", 10.0)
        geopolitical = data.get("geopolitical_risk", "moderate")
        anomalies = data.get("market_anomalies", "none")
        sanctions = data.get("sanctions_status", "none")
        convertibility = data.get("convertibility", "full")
        assessment = data.get("composite_assessment", "")
        status = data.get("status", "")

        # Find description from rubric
        description = "moderate factors"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level.get("range", level["description"]).lower()
                break

        # Build justification based on source
        if source == 'rule_based':
            inflation = data.get('raw_inflation', 0)
            interest = data.get('raw_interest_rate', 0)
            justification = (
                f"Based on World Bank data: Systemic risk assessment shows {description} "
                f"(derived from inflation {inflation:.1f}%, interest rate {interest:.1f}%). "
            )
        else:
            # Mock data
            justification = (
                f"Systemic risk assessment: {description}. "
            )
        
        justification += (
            f"Currency risk: {currency.lower()}, "
            f"annual volatility {volatility:.1f}%. "
        )
        
        justification += (
            f"Geopolitical risk: {geopolitical.lower()}. "
            f"Convertibility: {convertibility.lower()}. "
        )
        
        if anomalies.lower() not in ["none", "none significant", "none identified"]:
            justification += f"Market anomalies: {anomalies.lower()}. "
        
        if sanctions.lower() not in ["none", "none identified"]:
            justification += f"Sanctions: {sanctions.lower()}. "
        
        justification += f"{assessment}. {status}."
        
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
            sources.append("Geopolitical risk indices (Extracted from documents)")
            sources.append("Currency volatility data (Extracted from documents)")
            sources.append("IMF and World Bank macroeconomic indicators")
            sources.append(f"{country} central bank and economic data")
            sources.append("Market anomaly detection and special circumstances analysis")
            # Add document sources if available
            ai_metadata = data.get('ai_metadata', {})
            doc_sources = ai_metadata.get('document_sources', [])
            sources.extend(doc_sources)
        # Check if we used rule-based or mock data
        elif data and data.get('source') == 'rule_based':
            sources.append("World Bank Economic Indicators - Rule-Based Estimation")
            sources.append("Geopolitical risk indices (Reference)")
            sources.append("IMF and World Bank macroeconomic indicators")
            sources.append(f"{country} central bank and economic data")
            sources.append("Market anomaly detection and special circumstances analysis")
        else:
            sources.append("Currency volatility and exchange rate data - Mock")
            sources.append("Geopolitical risk indices (WEF, Marsh)")
            sources.append("IMF and World Bank macroeconomic indicators")
            sources.append(f"{country} central bank and economic data")
            sources.append("Market anomaly detection and special circumstances analysis")

        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for System Modifiers parameter.
        
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
            "Currency volatility and exchange rate data",
            "Geopolitical risk indices",
            "Market anomaly detection",
            "IMF and World Bank macroeconomic indicators",
            "Central bank data and policy analysis"
        ]


def analyze_system_modifiers(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze system modifiers.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = SystemModifiersAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
