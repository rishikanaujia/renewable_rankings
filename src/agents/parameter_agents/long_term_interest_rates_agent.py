"""Long Term Interest Rates Agent - Analyzes financing cost environment.

This agent evaluates the long-term interest rate environment in each country,
typically using 10-year government bond yields as a proxy for the cost of capital.
Lower interest rates reduce debt service costs, improve project economics, and
enhance investment attractiveness.

Interest Rate Scale:
- < 2%: Ultra-low (optimal financing environment)
- 2-3%: Exceptionally low
- 3-4%: Very low (attractive financing)
- 4-5%: Low (favorable financing)
- 5-6%: Below moderate
- 6-8%: Moderate (average costs)
- 8-10%: Above moderate
- 10-12%: Elevated (challenging economics)
- 12-15%: High (expensive financing)
- ≥ 15%: Very high (prohibitive costs)

Scoring Rubric (LOADED FROM CONFIG):
Lower interest rate = Lower financing cost = Higher score (INVERSE relationship)

MODES:
- MOCK: Uses hardcoded bond yield data (for testing)
- RULE_BASED: Uses World Bank lending interest rate as proxy (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class LongTermInterestRatesAgent(BaseParameterAgent):
    """Agent for analyzing long-term interest rates and financing costs."""
    
    # Mock data for Phase 1 testing
    # 10-year government bond yields (%)
    # Data from central banks, Bloomberg, Trading Economics
    MOCK_DATA = {
        "Brazil": {
            "rate_pct": 12.5,
            "bond_type": "10-year government",
            "currency": "BRL",
            "central_bank_rate": 13.75,
            "trend": "Elevated",
            "status": "High rates (tight monetary policy, inflation)"
        },
        "Germany": {
            "rate_pct": 2.4,
            "bond_type": "10-year Bund",
            "currency": "EUR",
            "central_bank_rate": 4.5,
            "trend": "Low",
            "status": "Exceptionally low (ECB policy, safe haven)"
        },
        "USA": {
            "rate_pct": 4.2,
            "bond_type": "10-year Treasury",
            "currency": "USD",
            "central_bank_rate": 5.5,
            "trend": "Moderate",
            "status": "Low rates (Fed policy normalization)"
        },
        "China": {
            "rate_pct": 2.6,
            "bond_type": "10-year government",
            "currency": "CNY",
            "central_bank_rate": 3.45,
            "trend": "Low",
            "status": "Exceptionally low (PBOC accommodative policy)"
        },
        "India": {
            "rate_pct": 7.2,
            "bond_type": "10-year government",
            "currency": "INR",
            "central_bank_rate": 6.5,
            "trend": "Moderate",
            "status": "Moderate rates (RBI managing inflation)"
        },
        "UK": {
            "rate_pct": 4.0,
            "bond_type": "10-year Gilt",
            "currency": "GBP",
            "central_bank_rate": 5.25,
            "trend": "Low",
            "status": "Very low rates (BoE policy)"
        },
        "Spain": {
            "rate_pct": 3.2,
            "bond_type": "10-year government",
            "currency": "EUR",
            "central_bank_rate": 4.5,
            "trend": "Low",
            "status": "Very low rates (Eurozone member)"
        },
        "Australia": {
            "rate_pct": 4.3,
            "bond_type": "10-year government",
            "currency": "AUD",
            "central_bank_rate": 4.35,
            "trend": "Moderate",
            "status": "Low rates (RBA policy)"
        },
        "Chile": {
            "rate_pct": 5.8,
            "bond_type": "10-year government",
            "currency": "CLP",
            "central_bank_rate": 7.5,
            "trend": "Moderate",
            "status": "Below moderate (BCCh managing inflation)"
        },
        "Vietnam": {
            "rate_pct": 3.5,
            "bond_type": "10-year government",
            "currency": "VND",
            "central_bank_rate": 4.5,
            "trend": "Low",
            "status": "Very low rates (SBV accommodative)"
        },
        "South Africa": {
            "rate_pct": 11.2,
            "bond_type": "10-year government",
            "currency": "ZAR",
            "central_bank_rate": 8.25,
            "trend": "Elevated",
            "status": "Elevated rates (SARB inflation targeting)"
        },
        "Nigeria": {
            "rate_pct": 16.5,
            "bond_type": "10-year government",
            "currency": "NGN",
            "central_bank_rate": 18.75,
            "trend": "Very high",
            "status": "Very high rates (CBN tight policy, inflation)"
        },
        "Argentina": {
            "rate_pct": 45.0,
            "bond_type": "10-year government (USD)",
            "currency": "USD",
            "central_bank_rate": 133.0,
            "trend": "Prohibitive",
            "status": "Prohibitive rates (extreme inflation, currency risk)"
        },
        "Mexico": {
            "rate_pct": 9.8,
            "bond_type": "10-year government",
            "currency": "MXN",
            "central_bank_rate": 11.25,
            "trend": "Above moderate",
            "status": "Above moderate (Banxico managing inflation)"
        },
        "Indonesia": {
            "rate_pct": 6.8,
            "bond_type": "10-year government",
            "currency": "IDR",
            "central_bank_rate": 6.0,
            "trend": "Moderate",
            "status": "Moderate rates (BI policy)"
        },
        "Saudi Arabia": {
            "rate_pct": 4.8,
            "bond_type": "10-year government",
            "currency": "SAR",
            "central_bank_rate": 5.5,
            "trend": "Moderate",
            "status": "Low rates (SAMA USD peg)"
        },
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Long Term Interest Rates Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Long Term Interest Rates",
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
            f"Initialized LongTermInterestRatesAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            rates_config = params_config['parameters'].get('long_term_interest_rates', {})
            scoring = rates_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_rate_pct": item.get('min_rate_pct', 0.0),
                        "max_rate_pct": item.get('max_rate_pct', 100.0),
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
            {"score": 1, "min_rate_pct": 15.0, "max_rate_pct": 100.0, "range": "≥15%", "description": "Very high rates (prohibitive financing costs)"},
            {"score": 2, "min_rate_pct": 12.0, "max_rate_pct": 15.0, "range": "12-15%", "description": "High rates (expensive financing)"},
            {"score": 3, "min_rate_pct": 10.0, "max_rate_pct": 12.0, "range": "10-12%", "description": "Elevated rates (challenging economics)"},
            {"score": 4, "min_rate_pct": 8.0, "max_rate_pct": 10.0, "range": "8-10%", "description": "Above moderate rates"},
            {"score": 5, "min_rate_pct": 6.0, "max_rate_pct": 8.0, "range": "6-8%", "description": "Moderate rates (average financing costs)"},
            {"score": 6, "min_rate_pct": 5.0, "max_rate_pct": 6.0, "range": "5-6%", "description": "Below moderate rates"},
            {"score": 7, "min_rate_pct": 4.0, "max_rate_pct": 5.0, "range": "4-5%", "description": "Low rates (favorable financing)"},
            {"score": 8, "min_rate_pct": 3.0, "max_rate_pct": 4.0, "range": "3-4%", "description": "Very low rates (attractive financing)"},
            {"score": 9, "min_rate_pct": 2.0, "max_rate_pct": 3.0, "range": "2-3%", "description": "Exceptionally low rates"},
            {"score": 10, "min_rate_pct": 0.0, "max_rate_pct": 2.0, "range": "<2%", "description": "Ultra-low rates (optimal financing environment)"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze long-term interest rates for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Long Term Interest Rates for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # Rule-based data has high confidence (World Bank official data)
            if self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "high"
                confidence = 0.85  # High confidence for World Bank data
            else:
                data_quality = "high"
                confidence = 0.9  # Very high confidence for bond yield data
            
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
                f"Long Term Interest Rates analysis complete for {country}: "
                f"Score={score:.1f}, Rate={data.get('rate_pct', 0):.1f}%, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Long Term Interest Rates analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Long Term Interest Rates analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch long-term interest rate data.
        
        In MOCK mode: Returns mock bond yield data
        In RULE_BASED mode: Uses World Bank lending interest rate as proxy
        In AI_POWERED mode: Would use LLM to extract from financial reports (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with interest rate data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate rates")
                data = {
                    "rate_pct": 6.5,
                    "bond_type": "10-year government",
                    "currency": "Local",
                    "central_bank_rate": 7.0,
                    "trend": "Moderate",
                    "status": "Moderate rates"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: {data.get('rate_pct')}%")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Use World Bank lending interest rate as proxy
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch lending interest rate (% per annum)
                lending_rate = self.data_service.get_value(
                    country=country,
                    indicator='lending_interest_rate',
                    default=None
                )
                
                # Fetch real interest rate for additional context
                real_rate = self.data_service.get_value(
                    country=country,
                    indicator='real_interest_rate',
                    default=None
                )
                
                # Fetch inflation for context
                inflation = self.data_service.get_value(
                    country=country,
                    indicator='inflation',
                    default=None
                )
                
                if lending_rate is None:
                    logger.warning(
                        f"No lending rate data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Use lending rate as proxy for long-term financing cost
                # Note: Lending rates are typically 2-4% higher than government bond yields
                # We adjust down slightly to approximate 10-year government bond yield
                estimated_bond_yield = lending_rate * 0.75  # Rough approximation
                
                # Calibrate with mock data if available
                base_data = self.MOCK_DATA.get(country)
                if base_data:
                    base_rate = base_data.get('rate_pct', estimated_bond_yield)
                    # Blend: 70% World Bank, 30% mock for calibration
                    rate_pct = estimated_bond_yield * 0.7 + base_rate * 0.3
                else:
                    rate_pct = estimated_bond_yield
                
                # Determine trend and status
                trend = self._determine_rate_trend(rate_pct)
                status = self._determine_rate_status(rate_pct)
                
                data = {
                    'rate_pct': rate_pct,
                    'bond_type': '10-year government (estimated from lending rate)',
                    'currency': 'Local',
                    'central_bank_rate': lending_rate,  # Use lending rate as proxy
                    'trend': trend,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_lending_rate': lending_rate
                }
                
                logger.info(
                    f"Calculated RULE_BASED data for {country}: {rate_pct:.1f}% "
                    f"(from lending rate {lending_rate:.1f}%)"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error fetching interest rate for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from financial reports
            # return self._llm_extract_rates(country, period)
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
            "rate_pct": 6.5,
            "bond_type": "10-year government",
            "currency": "Local",
            "central_bank_rate": 7.0,
            "trend": "Moderate",
            "status": "Moderate rates"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _determine_rate_trend(self, rate_pct: float) -> str:
        """Determine rate trend description from rate level.
        
        Args:
            rate_pct: Interest rate percentage
            
        Returns:
            Trend description string
        """
        if rate_pct < 2:
            return "Ultra-low"
        elif rate_pct < 3:
            return "Exceptionally low"
        elif rate_pct < 4:
            return "Very low"
        elif rate_pct < 5:
            return "Low"
        elif rate_pct < 6:
            return "Below moderate"
        elif rate_pct < 8:
            return "Moderate"
        elif rate_pct < 10:
            return "Above moderate"
        elif rate_pct < 12:
            return "Elevated"
        elif rate_pct < 15:
            return "High"
        else:
            return "Very high"
    
    def _determine_rate_status(self, rate_pct: float) -> str:
        """Determine rate status description from rate level.
        
        Args:
            rate_pct: Interest rate percentage
            
        Returns:
            Status description string
        """
        if rate_pct < 2:
            return "Ultra-low rates (optimal financing environment)"
        elif rate_pct < 3:
            return "Exceptionally low rates"
        elif rate_pct < 4:
            return "Very low rates (attractive financing)"
        elif rate_pct < 5:
            return "Low rates (favorable financing)"
        elif rate_pct < 6:
            return "Below moderate rates"
        elif rate_pct < 8:
            return "Moderate rates (average financing costs)"
        elif rate_pct < 10:
            return "Above moderate rates"
        elif rate_pct < 12:
            return "Elevated rates (challenging economics)"
        elif rate_pct < 15:
            return "High rates (expensive financing)"
        else:
            return "Very high rates (prohibitive financing costs)"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate interest rate score.
        
        INVERSE: Lower interest rate = lower financing cost = higher score
        
        Args:
            data: Interest rate data with rate_pct
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        rate_pct = data.get("rate_pct", 0)
        
        logger.debug(f"Calculating score for {country}: {rate_pct:.1f}% interest rate")
        
        # Find matching rubric level (INVERSE - lower is better)
        for level in self.scoring_rubric:
            min_rate = level.get("min_rate_pct", 0.0)
            max_rate = level.get("max_rate_pct", 100.0)
            
            if min_rate <= rate_pct < max_rate:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{rate_pct:.1f}% falls in range {min_rate:.0f}-{max_rate:.0f}%"
                )
                return float(score)
        
        # Fallback
        logger.warning(f"No rubric match for {rate_pct:.1f}%, defaulting to score 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the interest rate score.
        
        Args:
            data: Interest rate data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        rate_pct = data.get("rate_pct", 0)
        bond_type = data.get("bond_type", "10-year government")
        currency = data.get("currency", "local")
        central_bank_rate = data.get("central_bank_rate", 0)
        trend = data.get("trend", "moderate")
        status = data.get("status", "moderate rates")
        source = data.get("source", "unknown")
        
        # Find description from rubric
        description = "moderate financing costs"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification based on source
        if source == 'rule_based':
            raw_lending = data.get('raw_lending_rate', rate_pct)
            justification = (
                f"Based on World Bank lending rate data: Estimated long-term financing cost of {rate_pct:.1f}% "
                f"(derived from lending rate {raw_lending:.1f}%) indicates {description}. "
                f"{status.capitalize()}. "
            )
        else:
            # Mock data - use detailed bond information
            justification = (
                f"{bond_type} yield of {rate_pct:.1f}% ({currency}) indicates {description}. "
                f"Central bank policy rate at {central_bank_rate:.2f}% sets monetary backdrop. "
                f"{status.capitalize()}. "
            )
        
        justification += (
            f"This interest rate environment {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports renewable energy project financing through {'low' if score >= 7 else 'moderate' if score >= 5 else 'high'} "
            f"debt service costs."
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
            sources.append("World Bank Lending Interest Rate - Rule-Based Data")
            sources.append("10-year government bond markets (Reference)")
        else:
            sources.append(f"{country} Central Bank - Mock Data")
            sources.append("Bloomberg Terminal")
        
        sources.append("Trading Economics")
        sources.append("OECD interest rate statistics")
        
        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Long Term Interest Rates parameter.
        
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
            "Central bank policy rates",
            "Government 10-year bond yields",
            "Bloomberg terminal data",
            "Trading Economics",
            "OECD interest rate statistics",
            "Bond market data"
        ]


def analyze_long_term_interest_rates(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze long-term interest rates.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = LongTermInterestRatesAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
