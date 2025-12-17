"""Ownership Hurdles Agent - Analyzes foreign ownership restrictions.

This agent evaluates regulatory and practical barriers to foreign ownership
and market participation in renewable energy projects. Key factors include:
- Foreign ownership limits
- Regulatory approval complexity
- Local content requirements
- Investment screening processes

Lower barriers enable:
- Greater international capital access
- Increased competition
- Technology transfer
- Market efficiency

Ownership Restriction Categories:
1. Prohibitive (foreign ownership banned/<10%)
2. Very high (10-25% foreign ownership)
3. High (25-40% foreign ownership)
4. Above moderate (40-50% foreign ownership)
5. Moderate (50-65% foreign ownership)
6. Below moderate (65-75% foreign ownership)
7. Low (75-85% foreign ownership)
8. Very low (85-95% foreign ownership)
9. Minimal (95-99% foreign ownership)
10. None (100% foreign ownership allowed)

Scoring Rubric (LOADED FROM CONFIG):
Lower restrictions = Better market access = Higher score (DIRECT/CATEGORICAL)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class OwnershipHurdlesAgent(BaseParameterAgent):
    """Agent for analyzing ownership hurdles and market access barriers."""
    
    # Mock data for Phase 1 testing
    # Foreign ownership restrictions in renewable energy sector
    # Data from OECD FDI Index, World Bank, national regulations
    MOCK_DATA = {
        "Brazil": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Standard",
            "local_content_requirements": "Minimal (expired)",
            "investment_screening": "Limited",
            "status": "Full foreign ownership allowed (liberalized market)"
        },
        "Germany": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Standard",
            "local_content_requirements": "None",
            "investment_screening": "EU nationals exempt",
            "status": "Full foreign ownership allowed (EU single market)"
        },
        "USA": {
            "foreign_ownership_pct": 95,
            "category": "minimal_barriers",
            "approval_complexity": "Moderate (CFIUS review)",
            "local_content_requirements": "Some for incentives",
            "investment_screening": "CFIUS for sensitive cases",
            "status": "Nearly unrestricted (CFIUS security review for certain cases)"
        },
        "China": {
            "foreign_ownership_pct": 49,
            "category": "moderate_barriers",
            "approval_complexity": "High (multiple approvals)",
            "local_content_requirements": "Significant",
            "investment_screening": "Extensive (NDRC, MOFCOM)",
            "status": "Moderate barriers (49% foreign ownership cap in many cases)"
        },
        "India": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Moderate (automatic route)",
            "local_content_requirements": "Phase-out (2020)",
            "investment_screening": "Limited",
            "status": "Full foreign ownership allowed (automatic route for renewables)"
        },
        "UK": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Standard",
            "local_content_requirements": "None",
            "investment_screening": "NSI Act for sensitive assets",
            "status": "Full foreign ownership allowed (open market)"
        },
        "Spain": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Standard",
            "local_content_requirements": "None",
            "investment_screening": "EU nationals exempt",
            "status": "Full foreign ownership allowed (EU single market)"
        },
        "Australia": {
            "foreign_ownership_pct": 90,
            "category": "minimal_barriers",
            "approval_complexity": "Moderate (FIRB review)",
            "local_content_requirements": "None",
            "investment_screening": "FIRB for >$300M",
            "status": "Minimal barriers (FIRB review for large investments)"
        },
        "Chile": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Low",
            "local_content_requirements": "None",
            "investment_screening": "Minimal",
            "status": "Full foreign ownership allowed (very open market)"
        },
        "Vietnam": {
            "foreign_ownership_pct": 49,
            "category": "moderate_barriers",
            "approval_complexity": "High",
            "local_content_requirements": "Moderate",
            "investment_screening": "Extensive",
            "status": "Moderate barriers (49% foreign ownership limit)"
        },
        "South Africa": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Moderate (local participation encouraged)",
            "local_content_requirements": "Significant (REIPPP)",
            "investment_screening": "Limited",
            "status": "Full foreign ownership allowed (but local content required)"
        },
        "Nigeria": {
            "foreign_ownership_pct": 60,
            "category": "below_moderate_barriers",
            "approval_complexity": "Very High",
            "local_content_requirements": "Extensive",
            "investment_screening": "Extensive",
            "status": "Below moderate barriers (60% foreign ownership, complex approvals)"
        },
        "Argentina": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Moderate",
            "local_content_requirements": "Some (RenovAr)",
            "investment_screening": "Limited",
            "status": "Full foreign ownership allowed"
        },
        "Mexico": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Moderate",
            "local_content_requirements": "Some",
            "investment_screening": "Limited",
            "status": "Full foreign ownership allowed (USMCA framework)"
        },
        "Indonesia": {
            "foreign_ownership_pct": 95,
            "category": "minimal_barriers",
            "approval_complexity": "Moderate to High",
            "local_content_requirements": "Significant (TKDN)",
            "investment_screening": "Moderate",
            "status": "Minimal barriers (95% foreign ownership in renewables)"
        },
        "Saudi Arabia": {
            "foreign_ownership_pct": 100,
            "category": "no_barriers",
            "approval_complexity": "Moderate",
            "local_content_requirements": "Significant (Vision 2030 targets)",
            "investment_screening": "Moderate (strategic sectors)",
            "status": "Full foreign ownership allowed (Vision 2030 opening)"
        },
    }
    
    # Category scoring mapping
    CATEGORY_SCORES = {
        "prohibitive": 1,
        "very_high_barriers": 2,
        "high_barriers": 3,
        "above_moderate_barriers": 4,
        "moderate_barriers": 5,
        "below_moderate_barriers": 6,
        "low_barriers": 7,
        "very_low_barriers": 8,
        "minimal_barriers": 9,
        "no_barriers": 10
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Ownership Hurdles Agent."""
        super().__init__(
            parameter_name="Ownership Hurdles",
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
            
            ownership_config = params_config['parameters'].get('ownership_hurdles', {})
            scoring = ownership_config.get('scoring', [])
            
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
            {"score": 1, "range": "Prohibitive", "description": "Foreign ownership banned or <10%"},
            {"score": 2, "range": "Very high", "description": "10-25% foreign ownership"},
            {"score": 3, "range": "High", "description": "25-40% foreign ownership"},
            {"score": 4, "range": "Above moderate", "description": "40-50% foreign ownership"},
            {"score": 5, "range": "Moderate", "description": "50-65% foreign ownership"},
            {"score": 6, "range": "Below moderate", "description": "65-75% foreign ownership"},
            {"score": 7, "range": "Low", "description": "75-85% foreign ownership"},
            {"score": 8, "range": "Very low", "description": "85-95% foreign ownership"},
            {"score": 9, "range": "Minimal", "description": "95-99% foreign ownership"},
            {"score": 10, "range": "None", "description": "100% foreign ownership allowed"}
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze ownership hurdles for a country."""
        try:
            logger.info(f"Analyzing Ownership Hurdles for {country} ({period})")
            
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
                f"Ownership Hurdles analysis complete for {country}: "
                f"Score={score}, ForeignOwnership={data.get('foreign_ownership_pct', 0)}%, "
                f"Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ownership Hurdles analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Ownership Hurdles analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch ownership hurdles data."""
        if self.mode == AgentMode.MOCK:
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate barriers")
                data = {
                    "foreign_ownership_pct": 70,
                    "category": "below_moderate_barriers",
                    "approval_complexity": "Moderate",
                    "local_content_requirements": "Some",
                    "investment_screening": "Moderate",
                    "status": "Below moderate barriers"
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
        """Calculate ownership hurdles score.
        
        CATEGORICAL: Category determines score
        Lower barriers = better market access = higher score
        """
        category = data.get("category", "moderate_barriers")
        
        logger.debug(f"Calculating score for {country}: category={category}")
        
        # Get score from category mapping
        score = self.CATEGORY_SCORES.get(category, 5)
        
        logger.debug(f"Score {score} assigned for category {category}")
        
        return float(score)
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the ownership hurdles score."""
        foreign_pct = data.get("foreign_ownership_pct", 0)
        category = data.get("category", "moderate_barriers")
        approval = data.get("approval_complexity", "moderate")
        local_content = data.get("local_content_requirements", "some")
        screening = data.get("investment_screening", "moderate")
        status = data.get("status", "moderate barriers")
        
        description = "moderate barriers"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        justification = (
            f"Foreign ownership limit of {foreign_pct}% indicates {description}. "
            f"Approval process complexity is {approval.lower()} with {local_content.lower()} "
            f"local content requirements. "
        )
        
        justification += (
            f"Investment screening is {screening.lower()}. "
            f"{status.capitalize()}. "
        )
        
        justification += (
            f"This regulatory environment {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports international investment and market participation."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "OECD FDI Regulatory Restrictiveness Index",
            "World Bank Doing Business reports",
            f"{country} National energy laws",
            "Investment treaties and bilateral agreements",
            "Regulatory guidance documents"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Ownership Hurdles parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
        return [
            "OECD FDI Regulatory Restrictiveness Index",
            "World Bank Doing Business reports",
            "National energy laws and regulations",
            "Investment treaties and bilateral agreements",
            "Regulatory guidance documents"
        ]


def analyze_ownership_hurdles(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze ownership hurdles."""
    agent = OwnershipHurdlesAgent(mode=mode)
    return agent.analyze(country, period)
