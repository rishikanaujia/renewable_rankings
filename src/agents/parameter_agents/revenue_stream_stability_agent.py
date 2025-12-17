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
"""
from typing import Dict, Any, List
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
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Revenue Stream Stability Agent."""
        super().__init__(
            parameter_name="Revenue Stream Stability",
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
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze revenue stream stability for a country."""
        try:
            logger.info(f"Analyzing Revenue Stream Stability for {country} ({period})")
            
            data = self._fetch_data(country, period, **kwargs)
            score = self._calculate_score(data, country, period)
            score = self._validate_score(score)
            justification = self._generate_justification(data, score, country, period)
            
            data_quality = "medium" if data else "low"
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
                f"Revenue Stream Stability analysis complete for {country}: "
                f"Score={score}, Term={data.get('ppa_term_years', 0)}y, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Revenue Stream Stability analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Revenue Stream Stability analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch revenue stream stability data."""
        if self.mode == AgentMode.MOCK:
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
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(self, data: Dict[str, Any], country: str, period: str) -> float:
        """Calculate revenue stream stability score based on PPA term.
        
        DIRECT: Longer PPA term = better stability = higher score
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
        
        logger.warning(f"No rubric match for {ppa_term}y, defaulting to score 5")
        return 5.0
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the revenue stream stability score."""
        ppa_term = data.get("ppa_term_years", 0)
        price_structure = data.get("price_structure", "fixed")
        offtaker_type = data.get("offtaker_type", "utility")
        merchant_exposure = data.get("merchant_exposure_pct", 0)
        status = data.get("status", "moderate stability")
        
        description = "moderate stability"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        justification = (
            f"PPA term of {ppa_term} years indicates {description}. "
            f"Contract structure with {price_structure.lower()} prices backed by {offtaker_type.lower()} "
            f"provides {'strong' if score >= 8 else 'adequate' if score >= 6 else 'limited'} revenue certainty. "
        )
        
        if merchant_exposure > 0:
            justification += f"{merchant_exposure}% merchant exposure introduces price risk. "
        
        justification += (
            f"{status.capitalize()} {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports project bankability and financing."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "PPA databases and registries",
            "Project finance documentation",
            f"{country} Market PPA term benchmarks",
            "Offtaker contract databases"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Revenue Stream Stability parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
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
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze revenue stream stability."""
    agent = RevenueStreamStabilityAgent(mode=mode)
    return agent.analyze(country, period)
