"""Contract Terms Agent - Analyzes PPA and contract quality.

This agent evaluates the bankability and robustness of renewable energy
contracts, including:
- Power Purchase Agreement (PPA) standardization
- Risk allocation between parties
- Contract enforceability
- Termination protections
- Currency and political risk provisions

Key evaluation criteria:
- Standardization and best practices
- Bankability for project finance
- Legal framework strength
- International competitiveness
- Track record of enforcement

Contract Quality Categories (1-10):
1. Non-bankable
2. Very poor
3. Poor
4. Below adequate
5. Adequate
6. Above adequate
7. Good
8. Very good
9. Excellent
10. Best-in-class

Scoring Rubric (LOADED FROM CONFIG):
Better contract terms = Higher score (CATEGORICAL/QUALITATIVE)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class ContractTermsAgent(BaseParameterAgent):
    """Agent for analyzing renewable energy contract terms."""
    
    # Mock data for Phase 1 testing
    # Contract quality assessment based on PPA frameworks
    # Data from IFC, legal assessments, project finance transactions
    MOCK_DATA = {
        "Brazil": {
            "score": 8,
            "category": "very_good",
            "ppa_framework": "CCEAR (regulated) and bilateral (merchant)",
            "standardization": "High (standardized auction PPAs)",
            "risk_allocation": "Balanced (shared risks, tested framework)",
            "enforceability": "Strong (mature legal system, arbitration available)",
            "currency_risk": "Moderate (BRL volatility, hedging available)",
            "termination_protections": "Strong",
            "bankability": "Very High (extensive project finance track record)",
            "status": "Well-developed contract framework with strong standardization and proven bankability"
        },
        "Germany": {
            "score": 10,
            "category": "best_in_class",
            "ppa_framework": "EEG (Feed-in/auction) and corporate PPAs",
            "standardization": "Very High (EEG standard contracts)",
            "risk_allocation": "Optimal (government-backed, minimal project risk)",
            "enforceability": "Excellent (German legal system, EU framework)",
            "currency_risk": "Minimal (EUR stability, eurozone)",
            "termination_protections": "Excellent",
            "bankability": "Exceptional (world-class track record)",
            "status": "Gold standard contract framework with decades of proven track record"
        },
        "USA": {
            "score": 9,
            "category": "excellent",
            "ppa_framework": "Utility PPAs and corporate PPAs (state/federal)",
            "standardization": "High (FERC oversight, standard forms)",
            "risk_allocation": "Strong (well-developed legal precedents)",
            "enforceability": "Excellent (US legal system, arbitration)",
            "currency_risk": "Minimal (USD, reserve currency)",
            "termination_protections": "Strong to Excellent",
            "bankability": "Very High (deep project finance market)",
            "status": "Highly developed framework with extensive precedent and strong enforceability"
        },
        "China": {
            "score": 7,
            "category": "good",
            "ppa_framework": "Grid company PPAs (state-guaranteed)",
            "standardization": "High (standardized government PPAs)",
            "risk_allocation": "Government-favorable (but improving)",
            "enforceability": "Moderate to Strong (state enforcement reliable but limited recourse)",
            "currency_risk": "Moderate (CNY controls, conversion issues)",
            "termination_protections": "Moderate",
            "bankability": "Good (improving, but legal system concerns)",
            "status": "Strong standardization but contract enforceability concerns for international investors"
        },
        "India": {
            "score": 6,
            "category": "above_adequate",
            "ppa_framework": "SECI/State DISCOMs PPAs",
            "standardization": "Moderate to High (improving)",
            "risk_allocation": "Variable (DISCOM credit risk significant)",
            "enforceability": "Moderate (legal system slow, disputes common)",
            "currency_risk": "High (INR volatility)",
            "termination_protections": "Moderate",
            "bankability": "Moderate (offtaker credit issues)",
            "status": "Improving framework but persistent offtaker credit and enforcement challenges"
        },
        "UK": {
            "score": 10,
            "category": "best_in_class",
            "ppa_framework": "CfD (government-backed) and corporate PPAs",
            "standardization": "Very High (CfD standard contracts)",
            "risk_allocation": "Optimal (government-backed CfDs)",
            "enforceability": "Excellent (UK legal system, English law gold standard)",
            "currency_risk": "Low (GBP, stable)",
            "termination_protections": "Excellent",
            "bankability": "Exceptional (English law preferred globally)",
            "status": "World-leading contract framework, English law gold standard for global project finance"
        },
        "Spain": {
            "score": 5,
            "category": "adequate",
            "ppa_framework": "REER auctions and bilateral PPAs",
            "standardization": "Moderate (post-reform uncertainty)",
            "risk_allocation": "Uncertain (retroactive reform legacy)",
            "enforceability": "Moderate (retroactive changes undermined confidence)",
            "currency_risk": "Low (EUR)",
            "termination_protections": "Weak to Moderate (reform history)",
            "bankability": "Moderate (rebuilding after retroactive changes)",
            "status": "Framework recovering from retroactive policy changes that damaged investor confidence"
        },
        "Australia": {
            "score": 8,
            "category": "very_good",
            "ppa_framework": "State-level contracts and corporate PPAs",
            "standardization": "High (Commonwealth law)",
            "risk_allocation": "Strong (well-developed commercial framework)",
            "enforceability": "Excellent (Australian legal system)",
            "currency_risk": "Low to Moderate (AUD volatility)",
            "termination_protections": "Strong",
            "bankability": "Very High (sophisticated market)",
            "status": "Strong commercial framework with excellent legal protections"
        },
        "Chile": {
            "score": 8,
            "category": "very_good",
            "ppa_framework": "Auction and bilateral PPAs",
            "standardization": "High (auction standard terms)",
            "risk_allocation": "Balanced (market-tested framework)",
            "enforceability": "Strong (stable legal system)",
            "currency_risk": "Moderate (CLP, dollar-indexed available)",
            "termination_protections": "Strong",
            "bankability": "Very High (strong track record)",
            "status": "Highly developed framework with strong investor protections"
        },
        "Vietnam": {
            "score": 4,
            "category": "below_adequate",
            "ppa_framework": "EVN PPAs (state monopoly)",
            "standardization": "Moderate (standard FiT template)",
            "risk_allocation": "Unfavorable (limited recourse, EVN monopoly)",
            "enforceability": "Weak (legal system limitations)",
            "currency_risk": "High (VND controls, repatriation issues)",
            "termination_protections": "Weak",
            "bankability": "Low to Moderate (financing challenges)",
            "status": "Weak legal framework with significant enforceability and currency concerns"
        },
        "South Africa": {
            "score": 7,
            "category": "good",
            "ppa_framework": "REIPPP standardized PPAs (Eskom offtake)",
            "standardization": "Very High (REIPPP standard contracts)",
            "risk_allocation": "Balanced (well-structured, but Eskom credit risk)",
            "enforceability": "Strong (South African law well-developed)",
            "currency_risk": "High (ZAR volatility)",
            "termination_protections": "Strong",
            "bankability": "Good (well-structured but offtaker concerns)",
            "status": "Excellent contract standardization but Eskom credit concerns impact bankability"
        },
        "Nigeria": {
            "score": 2,
            "category": "very_poor",
            "ppa_framework": "NBET PPAs (limited track record)",
            "standardization": "Low (limited standardization)",
            "risk_allocation": "Unfavorable (significant investor risk)",
            "enforceability": "Weak (legal system challenges)",
            "currency_risk": "Very High (NGN volatility, FX scarcity)",
            "termination_protections": "Weak",
            "bankability": "Very Low (significant financing challenges)",
            "status": "Weak contract framework with major enforceability and currency concerns"
        },
        "Argentina": {
            "score": 4,
            "category": "below_adequate",
            "ppa_framework": "RenovAr PPAs (CAMMESA)",
            "standardization": "Moderate (RenovAr framework)",
            "risk_allocation": "Uncertain (sovereign risk, currency controls)",
            "enforceability": "Weak to Moderate (legal uncertainty)",
            "currency_risk": "Very High (ARS instability)",
            "termination_protections": "Weak",
            "bankability": "Low (significant financing challenges)",
            "status": "Persistent sovereign and currency risk undermines otherwise reasonable contract framework"
        },
        "Mexico": {
            "score": 3,
            "category": "poor",
            "ppa_framework": "Legacy auction PPAs (no new auctions)",
            "standardization": "Was High (auction framework now suspended)",
            "risk_allocation": "Deteriorating (policy reversal)",
            "enforceability": "Weak (government intervention risk)",
            "currency_risk": "Moderate (MXN)",
            "termination_protections": "Weak (policy uncertainty)",
            "bankability": "Low (policy reversal damaged confidence)",
            "status": "Once-strong framework severely damaged by policy reversals"
        },
        "Indonesia": {
            "score": 5,
            "category": "adequate",
            "ppa_framework": "PLN PPAs (state monopoly)",
            "standardization": "Moderate (standard PLN template)",
            "risk_allocation": "Unfavorable (limited recourse)",
            "enforceability": "Moderate (improving but challenges remain)",
            "currency_risk": "High (IDR volatility)",
            "termination_protections": "Moderate",
            "bankability": "Moderate (financing possible but challenging)",
            "status": "Basic framework with material weaknesses in risk allocation and enforceability"
        },
        "Saudi Arabia": {
            "score": 9,
            "category": "excellent",
            "ppa_framework": "NREP auction PPAs (ACWA Power, SEC, others)",
            "standardization": "Very High (NREP standard contracts)",
            "risk_allocation": "Strong (government-backed, favorable terms)",
            "enforceability": "Strong (well-developed legal framework)",
            "currency_risk": "Minimal (SAR pegged to USD)",
            "termination_protections": "Strong",
            "bankability": "Very High (sovereign backing, attractive terms)",
            "status": "High-quality contract framework with strong government backing and attractive terms"
        },
    }
    
    # Category to score mapping
    CATEGORY_SCORES = {
        "non_bankable": 1,
        "very_poor": 2,
        "poor": 3,
        "below_adequate": 4,
        "adequate": 5,
        "above_adequate": 6,
        "good": 7,
        "very_good": 8,
        "excellent": 9,
        "best_in_class": 10
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Contract Terms Agent."""
        super().__init__(
            parameter_name="Contract Terms",
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
            
            contract_config = params_config['parameters'].get('contract_terms', {})
            scoring = contract_config.get('scoring', [])
            
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
            {"score": 1, "range": "Non-bankable", "description": "Highly unfavorable terms"},
            {"score": 2, "range": "Very poor", "description": "Major risk allocation issues"},
            {"score": 3, "range": "Poor", "description": "Significant enforceability concerns"},
            {"score": 4, "range": "Below adequate", "description": "Below-market terms"},
            {"score": 5, "range": "Adequate", "description": "Basic framework exists"},
            {"score": 6, "range": "Above adequate", "description": "Reasonable terms"},
            {"score": 7, "range": "Good", "description": "Solid framework"},
            {"score": 8, "range": "Very good", "description": "Strong standardization, highly bankable"},
            {"score": 9, "range": "Excellent", "description": "Internationally-competitive"},
            {"score": 10, "range": "Best-in-class", "description": "World-class framework"}
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze contract terms for a country."""
        try:
            logger.info(f"Analyzing Contract Terms for {country} ({period})")
            
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
                f"Contract Terms analysis complete for {country}: "
                f"Score={score}, Category={data.get('category', 'unknown')}, "
                f"Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Contract Terms analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Contract Terms analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch contract terms data."""
        if self.mode == AgentMode.MOCK:
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default adequate framework")
                data = {
                    "score": 6,
                    "category": "above_adequate",
                    "ppa_framework": "Standard PPAs",
                    "standardization": "Moderate",
                    "risk_allocation": "Balanced",
                    "enforceability": "Moderate",
                    "currency_risk": "Moderate",
                    "termination_protections": "Moderate",
                    "bankability": "Moderate",
                    "status": "Reasonable contract framework with room for improvement"
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
        """Calculate contract terms score.
        
        CATEGORICAL: Category determines score
        Better terms = higher score
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using pre-calculated score {score} for {country}")
            return float(score)
        
        # Otherwise map from category
        category = data.get("category", "above_adequate")
        score = self.CATEGORY_SCORES.get(category, 6)
        
        logger.debug(f"Score {score} assigned for category {category}")
        
        return float(score)
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the contract terms score."""
        category = data.get("category", "above_adequate")
        ppa_framework = data.get("ppa_framework", "standard PPAs")
        standardization = data.get("standardization", "moderate")
        risk_allocation = data.get("risk_allocation", "balanced")
        enforceability = data.get("enforceability", "moderate")
        currency = data.get("currency_risk", "moderate")
        termination = data.get("termination_protections", "moderate")
        bankability = data.get("bankability", "moderate")
        status = data.get("status", "reasonable framework")
        
        description = "above adequate"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level.get("range", level["description"]).lower()
                break
        
        justification = (
            f"Contract framework quality: {description}. "
            f"PPA framework: {ppa_framework}. "
        )
        
        justification += (
            f"Standardization: {standardization.lower()}, "
            f"risk allocation: {risk_allocation.lower()}, "
            f"enforceability: {enforceability.lower()}. "
        )
        
        justification += (
            f"Currency risk: {currency.lower()}, "
            f"termination protections: {termination.lower()}, "
            f"bankability: {bankability.lower()}. "
        )
        
        justification += f"{status}."
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "Sample PPAs and contract templates",
            "Legal framework assessments",
            "IFC and development bank due diligence",
            f"{country} legal and regulatory analysis",
            "Project finance transaction databases"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Contract Terms parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
        return [
            "Sample PPAs and contracts",
            "Legal framework assessments",
            "International lender due diligence",
            "Project finance transaction data",
            "IFC and development bank reports"
        ]


def analyze_contract_terms(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze contract terms."""
    agent = ContractTermsAgent(mode=mode)
    return agent.analyze(country, period)
