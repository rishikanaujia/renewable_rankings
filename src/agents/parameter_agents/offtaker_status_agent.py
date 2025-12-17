"""Offtaker Status Agent - Analyzes PPA offtaker creditworthiness.

This agent evaluates the credit quality and reliability of Power Purchase Agreement
(PPA) offtakers. Higher creditworthiness reduces payment default risk, improves
project bankability, and lowers financing costs.

Credit Rating Scale:
- AAA/AA+: Superior (sovereign/AAA utilities) - Score 10
- AA/A+: Excellent (very strong capacity) - Score 9
- A/A-: Very good (strong capacity) - Score 8
- BBB+/BBB: Good (solid investment grade) - Score 7
- BBB-: Adequate (lower investment grade) - Score 6
- BB+/BB: Moderate (below investment grade) - Score 5
- BB-: Below moderate (speculative) - Score 4
- B+/B: Weak (significant risk) - Score 3
- B-/CCC+: Very weak (substantial risk) - Score 2
- CCC/D: Distressed (high default risk) - Score 1

Scoring Rubric (LOADED FROM CONFIG):
Higher credit rating = Lower default risk = Higher score (DIRECT relationship)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class OfftakerStatusAgent(BaseParameterAgent):
    """Agent for analyzing offtaker credit status and reliability."""
    
    # Mock data for Phase 1 testing
    # Credit ratings for typical offtakers in each market
    # Data from S&P, Moody's, Fitch, sovereign ratings
    MOCK_DATA = {
        "Brazil": {
            "offtaker": "Eletrobras (state utility)",
            "credit_rating": "BBB",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "BB- (Brazil)",
            "status": "Good credit (solid investment grade utility)"
        },
        "Germany": {
            "offtaker": "German utilities (FiT backed)",
            "credit_rating": "AAA",
            "rating_agency": "S&P",
            "category": "superior",
            "sovereign_rating": "AAA (Germany)",
            "status": "Superior credit (sovereign-backed FiT)"
        },
        "USA": {
            "offtaker": "Investment grade utilities",
            "credit_rating": "A",
            "rating_agency": "S&P",
            "category": "very_good",
            "sovereign_rating": "AA+ (USA)",
            "status": "Very good credit (strong utilities)"
        },
        "China": {
            "offtaker": "State Grid Corporation",
            "credit_rating": "AA-",
            "rating_agency": "S&P",
            "category": "excellent",
            "sovereign_rating": "A+ (China)",
            "status": "Excellent credit (state-owned enterprise)"
        },
        "India": {
            "offtaker": "SECI/NTPC (government-backed)",
            "credit_rating": "BBB-",
            "rating_agency": "S&P",
            "category": "adequate",
            "sovereign_rating": "BBB- (India)",
            "status": "Adequate credit (government backing)"
        },
        "UK": {
            "offtaker": "CFD counterparty (LCCC)",
            "credit_rating": "AA",
            "rating_agency": "S&P",
            "category": "excellent",
            "sovereign_rating": "AA (UK)",
            "status": "Excellent credit (government CFD mechanism)"
        },
        "Spain": {
            "offtaker": "Corporate PPAs",
            "credit_rating": "BBB+",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "A- (Spain)",
            "status": "Good credit (investment grade corporates)"
        },
        "Australia": {
            "offtaker": "Corporate PPAs / retailers",
            "credit_rating": "BBB",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "AAA (Australia)",
            "status": "Good credit (corporate offtakers)"
        },
        "Chile": {
            "offtaker": "Mining companies / utilities",
            "credit_rating": "A-",
            "rating_agency": "S&P",
            "category": "very_good",
            "sovereign_rating": "A+ (Chile)",
            "status": "Very good credit (strong mining companies)"
        },
        "Vietnam": {
            "offtaker": "EVN (state utility)",
            "credit_rating": "BB",
            "rating_agency": "S&P",
            "category": "moderate",
            "sovereign_rating": "BB (Vietnam)",
            "status": "Moderate credit (state utility, below investment grade)"
        },
        "South Africa": {
            "offtaker": "Eskom (REIPPP)",
            "credit_rating": "BB-",
            "rating_agency": "S&P",
            "category": "below_moderate",
            "sovereign_rating": "BB- (South Africa)",
            "status": "Below moderate (Eskom financial challenges)"
        },
        "Nigeria": {
            "offtaker": "Local distribution companies",
            "credit_rating": "B",
            "rating_agency": "S&P",
            "category": "weak",
            "sovereign_rating": "B (Nigeria)",
            "status": "Weak credit (DISCO payment challenges)"
        },
        "Argentina": {
            "offtaker": "CAMMESA (RenovAr)",
            "credit_rating": "BB-",
            "rating_agency": "S&P",
            "category": "below_moderate",
            "sovereign_rating": "CCC+ (Argentina)",
            "status": "Below moderate (macro challenges despite RenovAr)"
        },
        "Mexico": {
            "offtaker": "CFE (state utility)",
            "credit_rating": "BBB",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "BBB (Mexico)",
            "status": "Good credit (CFE investment grade)"
        },
        "Indonesia": {
            "offtaker": "PLN (state utility)",
            "credit_rating": "BBB",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "BBB (Indonesia)",
            "status": "Good credit (state utility, sovereign level)"
        },
        "Saudi Arabia": {
            "offtaker": "ACWA/SEC (sovereign-backed)",
            "credit_rating": "AA",
            "rating_agency": "S&P",
            "category": "excellent",
            "sovereign_rating": "A- (Saudi Arabia)",
            "status": "Excellent credit (sovereign backing)"
        },
    }
    
    # Credit rating category mapping
    CATEGORY_SCORES = {
        "superior": 10,        # AAA/AA+
        "excellent": 9,        # AA/A+
        "very_good": 8,        # A/A-
        "good": 7,             # BBB+/BBB
        "adequate": 6,         # BBB-
        "moderate": 5,         # BB+/BB
        "below_moderate": 4,   # BB-
        "weak": 3,             # B+/B
        "very_weak": 2,        # B-/CCC+
        "distressed": 1        # CCC/D
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Offtaker Status Agent."""
        super().__init__(
            parameter_name="Offtaker Status",
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
            
            offtaker_config = params_config['parameters'].get('offtaker_status', {})
            scoring = offtaker_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "category": item.get('category', ''),
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
            {"score": 1, "category": "distressed", "range": "D/CCC", "description": "Distressed offtaker (high default risk)"},
            {"score": 2, "category": "very_weak", "range": "CCC+/B-", "description": "Very weak credit (substantial credit risk)"},
            {"score": 3, "category": "weak", "range": "B/B+", "description": "Weak credit (significant risk)"},
            {"score": 4, "category": "below_moderate", "range": "BB-", "description": "Below investment grade (speculative)"},
            {"score": 5, "category": "moderate", "range": "BB/BB+", "description": "Moderate credit (below investment grade)"},
            {"score": 6, "category": "adequate", "range": "BBB-", "description": "Adequate credit (lower investment grade)"},
            {"score": 7, "category": "good", "range": "BBB/BBB+", "description": "Good credit (solid investment grade)"},
            {"score": 8, "category": "very_good", "range": "A-/A", "description": "Very good credit (strong capacity)"},
            {"score": 9, "category": "excellent", "range": "A+/AA", "description": "Excellent credit (very strong capacity)"},
            {"score": 10, "category": "superior", "range": "AA+/AAA", "description": "Superior credit (sovereign/AAA utilities)"}
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze offtaker status for a country."""
        try:
            logger.info(f"Analyzing Offtaker Status for {country} ({period})")
            
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
                f"Offtaker Status analysis complete for {country}: "
                f"Score={score}, Rating={data.get('credit_rating', 'N/A')}, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Offtaker Status analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Offtaker Status analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch offtaker status data."""
        if self.mode == AgentMode.MOCK:
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default adequate credit")
                data = {
                    "offtaker": "Utility",
                    "credit_rating": "BBB-",
                    "rating_agency": "S&P",
                    "category": "adequate",
                    "sovereign_rating": "BBB-",
                    "status": "Adequate credit"
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
        """Calculate offtaker status score based on credit category.
        
        DIRECT: Higher credit rating = lower default risk = higher score
        """
        category = data.get("category", "adequate")
        
        # Get score from category mapping
        score = self.CATEGORY_SCORES.get(category, 6)
        
        logger.debug(
            f"Calculating score for {country}: "
            f"Category={category}, Rating={data.get('credit_rating')}, Score={score}"
        )
        
        return float(score)
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the offtaker status score."""
        offtaker = data.get("offtaker", "utility")
        credit_rating = data.get("credit_rating", "N/A")
        rating_agency = data.get("rating_agency", "S&P")
        sovereign_rating = data.get("sovereign_rating", "")
        status = data.get("status", "moderate credit")
        
        description = "moderate credit"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        justification = (
            f"Offtaker {offtaker} carries {rating_agency} credit rating of {credit_rating}, indicating {description}. "
            f"{status.capitalize()}. "
        )
        
        if sovereign_rating:
            justification += f"Sovereign rating of {sovereign_rating} provides context for offtaker creditworthiness. "
        
        justification += (
            f"This credit profile {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports project financing and reduces payment default risk."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "S&P Global Ratings",
            "Moody's Ratings",
            "Fitch Ratings",
            f"{country} Offtaker financial statements",
            "Sovereign credit ratings"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Offtaker Status parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
        return [
            "S&P Global Ratings",
            "Moody's Ratings",
            "Fitch Ratings",
            "Offtaker financial statements",
            "Sovereign credit ratings",
            "Project finance documentation"
        ]


def analyze_offtaker_status(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze offtaker status."""
    agent = OfftakerStatusAgent(mode=mode)
    return agent.analyze(country, period)
