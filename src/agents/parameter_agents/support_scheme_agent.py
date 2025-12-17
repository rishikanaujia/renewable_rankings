"""Support Scheme Agent - Analyzes renewable energy support mechanisms.

This agent evaluates government support schemes and their effectiveness:
- Feed-in Tariffs (FiT)
- Auction/tender systems
- Tax credits and incentives
- Renewable Portfolio Standards (RPS)
- Net metering policies

Key evaluation criteria:
- Stability and predictability
- Scalability
- Effectiveness in driving deployment
- Investment certainty

Support Quality Categories (1-10):
1. No Support
2. Emerging but Ineffective
3. Forces Into Disadvantage
4. Boom-Bust Support
5. Under Threat
6. Federal-State Misalignment
7. Solid but Uncertain
8. Broad but Uneven
9. Strong but Not Scalable
10. Highly Mature

Scoring Rubric (LOADED FROM CONFIG):
Better support mechanisms = Higher score (CATEGORICAL/QUALITATIVE)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class SupportSchemeAgent(BaseParameterAgent):
    """Agent for analyzing renewable energy support schemes."""
    
    # Mock data for Phase 1 testing
    # Support mechanism quality assessment
    # Data from IEA, IRENA, national policy documents
    MOCK_DATA = {
        "Brazil": {
            "category": "broad_but_uneven",
            "score": 8,
            "primary_mechanism": "Auctions (A-3, A-4, A-5, A-6)",
            "secondary_mechanisms": ["Tax incentives (REIDI)", "BNDES financing"],
            "stability": "High",
            "predictability": "Moderate (calendar exists but volumes vary)",
            "scalability": "High",
            "recent_capacity_gw": 6.5,
            "status": "Multiple auction routes with proven track record, but effectiveness varies by technology and region"
        },
        "Germany": {
            "category": "highly_mature",
            "score": 10,
            "primary_mechanism": "Feed-in Tariff transitioning to Auctions",
            "secondary_mechanisms": ["EEG surcharge", "Grid priority access"],
            "stability": "Very High",
            "predictability": "Very High (Energiewende long-term commitment)",
            "scalability": "Very High",
            "recent_capacity_gw": 8.2,
            "status": "World-class support framework with decades of proven success, clear long-term targets"
        },
        "USA": {
            "category": "broad_but_uneven",
            "score": 8,
            "primary_mechanism": "Investment Tax Credit (ITC), Production Tax Credit (PTC)",
            "secondary_mechanisms": ["State RPS", "Net metering", "IRA incentives"],
            "stability": "Moderate (federal extensions, state variation)",
            "predictability": "Moderate (political cycles, IRA provides 10-year certainty)",
            "scalability": "Very High",
            "recent_capacity_gw": 32.5,
            "status": "Multiple effective routes (federal tax credits + state policies), but effectiveness varies significantly by state"
        },
        "China": {
            "category": "highly_mature",
            "score": 10,
            "primary_mechanism": "Feed-in Tariff transitioning to Grid Parity + Auctions",
            "secondary_mechanisms": ["Guaranteed grid access", "Provincial targets"],
            "stability": "Very High",
            "predictability": "Very High (centralized planning)",
            "scalability": "Exceptional",
            "recent_capacity_gw": 125.0,
            "status": "Massive scale deployment driven by top-down planning and comprehensive support"
        },
        "India": {
            "category": "strong_but_not_scalable",
            "score": 9,
            "primary_mechanism": "Auctions (SECI, state DISCOMs)",
            "secondary_mechanisms": ["RPO targets", "Accelerated depreciation"],
            "stability": "High",
            "predictability": "High (regular auction calendar)",
            "scalability": "Moderate (grid constraints, DISCOM finances)",
            "recent_capacity_gw": 18.5,
            "status": "Strong auction program with clear targets, but scale limited by grid and off-taker constraints"
        },
        "UK": {
            "category": "highly_mature",
            "score": 10,
            "primary_mechanism": "Contracts for Difference (CfD)",
            "secondary_mechanisms": ["ROCs (legacy)", "Business rates relief"],
            "stability": "Very High",
            "predictability": "Very High (regular CfD rounds)",
            "scalability": "High (especially offshore wind)",
            "recent_capacity_gw": 4.2,
            "status": "Well-designed CfD mechanism with proven track record, particularly successful for offshore wind"
        },
        "Spain": {
            "category": "solid_but_uncertain",
            "score": 7,
            "primary_mechanism": "Auctions (REER)",
            "secondary_mechanisms": ["Feed-in premiums (legacy)", "Self-consumption incentives"],
            "stability": "Moderate (post-2013 reform uncertainty resolved)",
            "predictability": "Moderate (auction calendar exists)",
            "scalability": "High",
            "recent_capacity_gw": 7.8,
            "status": "Recovering from retroactive policy changes, new auction framework established but investor confidence rebuilding"
        },
        "Australia": {
            "category": "federal_state_misalignment",
            "score": 6,
            "primary_mechanism": "State-level auctions and schemes",
            "secondary_mechanisms": ["Federal RET (closed 2020)", "State feed-in tariffs"],
            "stability": "Low to Moderate (federal-state conflicts)",
            "predictability": "Low (policy uncertainty)",
            "scalability": "Moderate",
            "recent_capacity_gw": 3.5,
            "status": "Federal-state policy misalignment creates uncertainty, reliance on state-level schemes"
        },
        "Chile": {
            "category": "broad_but_uneven",
            "score": 8,
            "primary_mechanism": "Auctions + Merchant market",
            "secondary_mechanisms": ["Net billing", "Tax stability agreements"],
            "stability": "High",
            "predictability": "High (regular auctions)",
            "scalability": "High",
            "recent_capacity_gw": 1.8,
            "status": "Effective auction program plus strong merchant market for renewables"
        },
        "Vietnam": {
            "category": "boom_bust",
            "score": 4,
            "primary_mechanism": "Feed-in Tariff (expired 2021)",
            "secondary_mechanisms": ["Direct PPAs", "Pilot auctions"],
            "stability": "Low (FiT boom ended abruptly)",
            "predictability": "Low (policy transition unclear)",
            "scalability": "Moderate",
            "recent_capacity_gw": 5.2,
            "status": "FiT drove massive boom (2019-2020) then expired without clear successor, creating boom-bust cycle"
        },
        "South Africa": {
            "category": "solid_but_uncertain",
            "score": 7,
            "primary_mechanism": "REIPPP auctions",
            "secondary_mechanisms": ["Section 34 exemption (self-generation)"],
            "stability": "Moderate (procurement delays)",
            "predictability": "Moderate (REIPPP restarts but irregular)",
            "scalability": "Moderate (Eskom offtake constraints)",
            "recent_capacity_gw": 0.8,
            "status": "Successful REIPPP program but suffered multi-year procurement freeze, now restarting"
        },
        "Nigeria": {
            "category": "emerging_but_ineffective",
            "score": 2,
            "primary_mechanism": "Feed-in Tariff (approved but not implemented)",
            "secondary_mechanisms": ["NBET PPAs (limited)"],
            "stability": "Very Low",
            "predictability": "Very Low",
            "scalability": "Very Low",
            "recent_capacity_gw": 0.05,
            "status": "FiT approved but never effectively implemented, very limited deployment"
        },
        "Argentina": {
            "category": "under_threat",
            "score": 5,
            "primary_mechanism": "RenovAr auctions",
            "secondary_mechanisms": ["MATER private market", "Provincial schemes"],
            "stability": "Low (economic volatility)",
            "predictability": "Low (policy uncertainty)",
            "scalability": "Moderate",
            "recent_capacity_gw": 1.2,
            "status": "RenovAr program was successful but future uncertain due to fiscal constraints"
        },
        "Mexico": {
            "category": "forces_disadvantage",
            "score": 3,
            "primary_mechanism": "Auctions (suspended 2019)",
            "secondary_mechanisms": ["Legacy PPAs", "Self-supply permits (restricted)"],
            "stability": "Very Low (policy reversal)",
            "predictability": "Very Low",
            "scalability": "Low (policy barriers)",
            "recent_capacity_gw": 2.1,
            "status": "Successful auction program suspended in 2019, current policies favor state utilities over renewables"
        },
        "Indonesia": {
            "category": "emerging_but_ineffective",
            "score": 2,
            "primary_mechanism": "Feed-in Tariff (limited to 85% of cost)",
            "secondary_mechanisms": ["Direct selection"],
            "stability": "Low",
            "predictability": "Low",
            "scalability": "Low",
            "recent_capacity_gw": 0.15,
            "status": "FiT capped at unfavorable rates, very limited deployment despite high potential"
        },
        "Saudi Arabia": {
            "category": "strong_but_not_scalable",
            "score": 9,
            "primary_mechanism": "NREP auctions",
            "secondary_mechanisms": ["PIF equity participation"],
            "stability": "Very High (Vision 2030)",
            "predictability": "Very High",
            "scalability": "Moderate (nascent market building capacity)",
            "recent_capacity_gw": 0.6,
            "status": "Well-designed auction program with strong government backing, but market still building capacity"
        },
    }
    
    # Category to score mapping
    CATEGORY_SCORES = {
        "no_support": 1,
        "emerging_but_ineffective": 2,
        "forces_disadvantage": 3,
        "boom_bust": 4,
        "under_threat": 5,
        "federal_state_misalignment": 6,
        "solid_but_uncertain": 7,
        "broad_but_uneven": 8,
        "strong_but_not_scalable": 9,
        "highly_mature": 10
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Support Scheme Agent."""
        super().__init__(
            parameter_name="Support Scheme",
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
            
            support_config = params_config['parameters'].get('support_scheme', {})
            scoring = support_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
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
            {"score": 1, "description": "No Support"},
            {"score": 2, "description": "Emerging but Ineffective"},
            {"score": 3, "description": "Forces Into Disadvantage"},
            {"score": 4, "description": "Boom-Bust Support"},
            {"score": 5, "description": "Under Threat"},
            {"score": 6, "description": "Federal-State Misalignment"},
            {"score": 7, "description": "Solid but Uncertain"},
            {"score": 8, "description": "Broad but Uneven"},
            {"score": 9, "description": "Strong but Not Scalable"},
            {"score": 10, "description": "Highly Mature"}
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze support scheme for a country."""
        try:
            logger.info(f"Analyzing Support Scheme for {country} ({period})")
            
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
                f"Support Scheme analysis complete for {country}: "
                f"Score={score}, Category={data.get('category', 'unknown')}, "
                f"Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Support Scheme analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Support Scheme analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch support scheme data."""
        if self.mode == AgentMode.MOCK:
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate support")
                data = {
                    "category": "solid_but_uncertain",
                    "score": 7,
                    "primary_mechanism": "Mixed mechanisms",
                    "secondary_mechanisms": ["Various"],
                    "stability": "Moderate",
                    "predictability": "Moderate",
                    "scalability": "Moderate",
                    "recent_capacity_gw": 1.0,
                    "status": "Moderate support framework"
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
        """Calculate support scheme score.
        
        CATEGORICAL: Category determines score
        Better support = higher score
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using pre-calculated score {score} for {country}")
            return float(score)
        
        # Otherwise map from category
        category = data.get("category", "solid_but_uncertain")
        score = self.CATEGORY_SCORES.get(category, 7)
        
        logger.debug(f"Score {score} assigned for category {category}")
        
        return float(score)
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the support scheme score."""
        category = data.get("category", "solid_but_uncertain")
        primary = data.get("primary_mechanism", "mixed mechanisms")
        secondary = data.get("secondary_mechanisms", [])
        stability = data.get("stability", "moderate")
        predictability = data.get("predictability", "moderate")
        scalability = data.get("scalability", "moderate")
        recent_gw = data.get("recent_capacity_gw", 0)
        status = data.get("status", "moderate support framework")
        
        description = "moderate support"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"]
                break
        
        justification = (
            f"Support framework characterized as '{description}'. "
            f"Primary mechanism: {primary}. "
        )
        
        if secondary:
            secondary_str = ", ".join(secondary[:2]) if len(secondary) > 2 else ", ".join(secondary)
            justification += f"Secondary mechanisms: {secondary_str}. "
        
        justification += (
            f"Stability: {stability.lower()}, "
            f"predictability: {predictability.lower()}, "
            f"scalability: {scalability.lower()}. "
        )
        
        justification += (
            f"Recent deployment: {recent_gw:.1f} GW/year. "
            f"{status}. "
        )
        
        justification += (
            f"This support framework {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"enables renewable energy investment."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "IEA Policies and Measures Database",
            "IRENA Policy Database",
            f"{country} Energy ministry policy documents",
            "Auction calendars and results",
            "National renewable energy laws"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Support Scheme parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
        return [
            "IEA Policies and Measures Database",
            "IRENA Policy Database",
            "Auction calendars",
            "Feed-in Tariff schedules",
            "National policy documents"
        ]


def analyze_support_scheme(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze support scheme."""
    agent = SupportSchemeAgent(mode=mode)
    return agent.analyze(country, period)
