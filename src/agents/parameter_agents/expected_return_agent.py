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
"""
from typing import Dict, Any, List
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
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Expected Return Agent."""
        super().__init__(
            parameter_name="Expected Return",
            mode=mode,
            config=config
        )
        
        # Load scoring rubric from config (NO HARDCODING!)
        self.scoring_rubric = self._load_scoring_rubric()
        
        logger.debug(f"Loaded scoring rubric with {len(self.scoring_rubric)} levels")
    
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
        """Fallback scoring rubric if config is not available.
        
        This ensures agent works even without full config.
        
        Returns:
            Default scoring rubric
        """
        return [
            {"score": 1, "min_irr_pct": 0.0, "max_irr_pct": 2.0, "range": "< 2%", "description": "Very poor returns (below risk-free rate)"},
            {"score": 2, "min_irr_pct": 2.0, "max_irr_pct": 4.0, "range": "2-4%", "description": "Poor returns (marginal profitability)"},
            {"score": 3, "min_irr_pct": 4.0, "max_irr_pct": 6.0, "range": "4-6%", "description": "Below acceptable returns"},
            {"score": 4, "min_irr_pct": 6.0, "max_irr_pct": 8.0, "range": "6-8%", "description": "Minimally acceptable returns"},
            {"score": 5, "min_irr_pct": 8.0, "max_irr_pct": 10.0, "range": "8-10%", "description": "Moderate returns (acceptable for low-risk)"},
            {"score": 6, "min_irr_pct": 10.0, "max_irr_pct": 12.0, "range": "10-12%", "description": "Good returns (above hurdle rate)"},
            {"score": 7, "min_irr_pct": 12.0, "max_irr_pct": 14.0, "range": "12-14%", "description": "Very good returns"},
            {"score": 8, "min_irr_pct": 14.0, "max_irr_pct": 16.0, "range": "14-16%", "description": "Excellent returns"},
            {"score": 9, "min_irr_pct": 16.0, "max_irr_pct": 20.0, "range": "16-20%", "description": "Outstanding returns"},
            {"score": 10, "min_irr_pct": 20.0, "max_irr_pct": 100.0, "range": "≥ 20%", "description": "Exceptional returns (highly attractive)"}
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
            logger.info(f"Analyzing Expected Return for {country} ({period})")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # Project IRR models are reasonably reliable but subject to assumptions
            data_quality = "medium" if data else "low"
            confidence = self._estimate_confidence(data, data_quality)
            
            # Step 6: Identify data sources
            data_sources = self._get_data_sources(country)
            
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
                f"Score={score}, IRR={data.get('irr_pct', 0):.1f}%, Confidence={confidence}"
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
        
        In MOCK mode: Returns mock IRR data
        In RULE mode: Would query project financial models
        In AI mode: Would use LLM to extract from IRENA/BNEF reports
        
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
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # TODO Phase 2: Query from project financial models
            # return self._query_project_models(country, period)
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from IRENA/BNEF reports
            # return self._llm_extract_returns(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate expected return score based on IRR %.
        
        DIRECT: Higher IRR = better profitability = higher score
        
        Args:
            data: Expected return data with irr_pct
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
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
        
        # Find description from rubric
        description = "moderate returns"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification with economic context
        justification = (
            f"Expected IRR of {irr_pct:.1f}% for {project_type} projects indicates {description}. "
            f"Economics driven by LCOE of ${lcoe:.0f}/MWh, PPA prices of ${ppa_price:.0f}/MWh, "
            f"and WACC of {wacc:.1f}%. {status.capitalize()} makes this market "
            f"{'highly attractive' if score >= 8 else 'moderately attractive' if score >= 6 else 'viable but tight'} "
            f"for renewable energy investment."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis.
        
        Args:
            country: Country name
            
        Returns:
            List of data source identifiers
        """
        # In production, these would be actual URLs/documents
        return [
            "IRENA Renewable Power Generation Costs 2023",
            "Bloomberg New Energy Finance (BNEF) Market Outlook",
            "Lazard Levelized Cost of Energy Analysis v16.0",
            f"{country} Project Financial Models",
            "Developer IRR Benchmarks"
        ]
    
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
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze expected return.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode
        
    Returns:
        ParameterScore
    """
    agent = ExpectedReturnAgent(mode=mode)
    return agent.analyze(country, period)
