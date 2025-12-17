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
"""
from typing import Dict, Any, List
from datetime import datetime

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
            "composite_assessment": "High currency volatility offset by legal framework",
            "status": "Moderate factors - significant currency risk but manageable"
        },
        "Nigeria": {
            "score": 2,
            "category": "very_high_negative",
            "currency_risk": "Very High (NGN volatility, FX scarcity)",
            "currency_volatility_annual": 28.5,
            "geopolitical_risk": "High (security challenges, corruption)",
            "market_anomalies": "FX scarcity, multiple exchange rates",
            "sanctions_status": "None",
            "convertibility": "Very Limited (FX scarcity)",
            "composite_assessment": "Severe currency and repatriation challenges",
            "status": "Very high negative impact - major FX and operational risks"
        },
        "Argentina": {
            "score": 2,
            "category": "very_high_negative",
            "currency_risk": "Very High (ARS instability, controls)",
            "currency_volatility_annual": 45.8,
            "geopolitical_risk": "High (default history, policy unpredictability)",
            "market_anomalies": "Multiple FX rates, capital controls",
            "sanctions_status": "None",
            "convertibility": "Severely Limited (capital controls)",
            "composite_assessment": "Severe currency instability and capital control risks",
            "status": "Very high negative impact - major currency and sovereign risk"
        },
        "Mexico": {
            "score": 5,
            "category": "moderate_factors",
            "currency_risk": "Moderate (MXN volatile but tradeable)",
            "currency_volatility_annual": 11.2,
            "geopolitical_risk": "Moderate (policy uncertainty, USMCA tensions)",
            "market_anomalies": "Energy policy reversal",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Moderate risks from policy uncertainty",
            "status": "Moderate factors - policy risk primary concern"
        },
        "Indonesia": {
            "score": 5,
            "category": "moderate_factors",
            "currency_risk": "Moderate (IDR volatile)",
            "currency_volatility_annual": 10.5,
            "geopolitical_risk": "Low to Moderate (stable democracy, some governance issues)",
            "market_anomalies": "None significant",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Balanced risk profile",
            "status": "Moderate factors - manageable emerging market risks"
        },
        "Saudi Arabia": {
            "score": 7,
            "category": "low_risk",
            "currency_risk": "Very Low (SAR pegged to USD)",
            "currency_volatility_annual": 0.1,
            "geopolitical_risk": "Moderate (regional tensions, but stable domestically)",
            "market_anomalies": "None",
            "sanctions_status": "None",
            "convertibility": "Full",
            "composite_assessment": "Excellent currency stability, regional geopolitical context",
            "status": "Low risk - strong currency stability with moderate geopolitical considerations"
        },
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize System Modifiers Agent."""
        super().__init__(
            parameter_name="System Modifiers",
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
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze system modifiers for a country."""
        try:
            logger.info(f"Analyzing System Modifiers for {country} ({period})")
            
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
                f"System Modifiers analysis complete for {country}: "
                f"Score={score}, Category={data.get('category', 'unknown')}, "
                f"Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"System Modifiers analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"System Modifiers analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch system modifiers data."""
        if self.mode == AgentMode.MOCK:
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
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(self, data: Dict[str, Any], country: str, period: str) -> float:
        """Calculate system modifiers score.
        
        Lower risk = Better environment = Higher score
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using pre-calculated score {score} for {country}")
            return float(score)
        
        # Otherwise could calculate from components
        # (This would require complex weighting of currency, geopolitical, etc.)
        # For now, default to moderate
        score = 5
        
        logger.debug(f"Using default score {score} for {country}")
        
        return float(score)
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the system modifiers score."""
        category = data.get("category", "moderate_factors")
        currency = data.get("currency_risk", "moderate")
        volatility = data.get("currency_volatility_annual", 10.0)
        geopolitical = data.get("geopolitical_risk", "moderate")
        anomalies = data.get("market_anomalies", "none")
        sanctions = data.get("sanctions_status", "none")
        convertibility = data.get("convertibility", "full")
        assessment = data.get("composite_assessment", "")
        status = data.get("status", "")
        
        description = "moderate factors"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level.get("range", level["description"]).lower()
                break
        
        justification = (
            f"Systemic risk assessment: {description}. "
            f"Currency risk: {currency.lower()}, "
            f"annual volatility {volatility:.1f}%. "
        )
        
        justification += (
            f"Geopolitical risk: {geopolitical.lower()}. "
            f"Convertibility: {convertibility.lower()}. "
        )
        
        if anomalies.lower() != "none" and anomalies.lower() != "none significant":
            justification += f"Market anomalies: {anomalies.lower()}. "
        
        if sanctions.lower() != "none":
            justification += f"Sanctions: {sanctions.lower()}. "
        
        justification += f"{assessment}. {status}."
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "Currency volatility and exchange rate data",
            "Geopolitical risk indices (WEF, Marsh)",
            "IMF and World Bank macroeconomic indicators",
            f"{country} central bank and economic data",
            "Market anomaly detection and special circumstances analysis"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for System Modifiers parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
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
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze system modifiers."""
    agent = SystemModifiersAgent(mode=mode)
    return agent.analyze(country, period)
