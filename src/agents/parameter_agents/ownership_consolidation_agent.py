"""Ownership Consolidation Agent - Analyzes market concentration.

This agent evaluates the level of ownership consolidation in renewable
energy markets by measuring the market share controlled by top owners:
- Concentration ratios (CR3 - top 3 owners)
- Herfindahl-Hirschman Index (HHI)
- Number of significant players
- Market entry barriers

Lower consolidation indicates:
- More competitive markets
- Greater diversity of approaches
- More market entry opportunities
- Reduced monopoly risk

Consolidation Categories (1-10):
1. Extreme monopoly (>80% by single owner)
2. Very high consolidation (70-80% by top 3)
3. High consolidation (60-70% by top 3)
4. Above moderate consolidation (50-60% by top 3)
5. Moderate consolidation (40-50% by top 3)
6. Below moderate consolidation (30-40% by top 3)
7. Low consolidation (20-30% by top 3)
8. Very low consolidation (15-20% by top 3)
9. Minimal consolidation (10-15% by top 3)
10. Highly fragmented (<10% by top 3)

Scoring Rubric (LOADED FROM CONFIG):
Lower consolidation = More competitive = Higher score (INVERSE)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class OwnershipConsolidationAgent(BaseParameterAgent):
    """Agent for analyzing ownership consolidation in renewable markets."""
    
    # Mock data for Phase 1 testing
    # Market concentration measured by top 3 owners' share
    # Data from industry reports, company filings, national statistics
    MOCK_DATA = {
        "Brazil": {
            "top3_share_pct": 35,
            "score": 6,
            "category": "below_moderate",
            "top_owners": ["Enel Green Power", "AES Brasil", "EDP Renováveis"],
            "total_market_capacity_mw": 38500,
            "num_significant_players": 25,
            "hhi": 950,
            "status": "Moderately concentrated market with diverse ownership including utilities, IPPs, and international developers"
        },
        "Germany": {
            "top3_share_pct": 18,
            "score": 8,
            "category": "very_low",
            "top_owners": ["RWE", "EnBW", "E.ON"],
            "total_market_capacity_mw": 134000,
            "num_significant_players": 100,
            "hhi": 450,
            "status": "Highly competitive market with very diverse ownership including cooperatives, municipalities, and private investors"
        },
        "USA": {
            "top3_share_pct": 22,
            "score": 7,
            "category": "low",
            "top_owners": ["NextEra Energy", "Duke Energy", "Berkshire Hathaway Energy"],
            "total_market_capacity_mw": 257000,
            "num_significant_players": 200,
            "hhi": 580,
            "status": "Large competitive market with low consolidation across utilities, IPPs, and yieldcos"
        },
        "China": {
            "top3_share_pct": 55,
            "score": 4,
            "category": "above_moderate",
            "top_owners": ["State Power Investment Corp", "China Three Gorges", "China Huaneng"],
            "total_market_capacity_mw": 758000,
            "num_significant_players": 50,
            "hhi": 1800,
            "status": "Moderately high consolidation dominated by state-owned enterprises"
        },
        "India": {
            "top3_share_pct": 28,
            "score": 7,
            "category": "low",
            "top_owners": ["Adani Green Energy", "ReNew Power", "Azure Power"],
            "total_market_capacity_mw": 175000,
            "num_significant_players": 80,
            "hhi": 720,
            "status": "Competitive market with low consolidation and growing independent power producers"
        },
        "UK": {
            "top3_share_pct": 32,
            "score": 6,
            "category": "below_moderate",
            "top_owners": ["SSE Renewables", "RWE", "Ørsted"],
            "total_market_capacity_mw": 48000,
            "num_significant_players": 60,
            "hhi": 880,
            "status": "Moderately concentrated market particularly in offshore wind"
        },
        "Spain": {
            "top3_share_pct": 45,
            "score": 5,
            "category": "moderate",
            "top_owners": ["Iberdrola", "Acciona", "Endesa"],
            "total_market_capacity_mw": 53000,
            "num_significant_players": 40,
            "hhi": 1250,
            "status": "Moderate consolidation with traditional utilities maintaining strong positions"
        },
        "Australia": {
            "top3_share_pct": 25,
            "score": 7,
            "category": "low",
            "top_owners": ["AGL Energy", "Origin Energy", "CleanCo Queensland"],
            "total_market_capacity_mw": 32000,
            "num_significant_players": 70,
            "hhi": 650,
            "status": "Competitive market with low consolidation and active independent developers"
        },
        "Chile": {
            "top3_share_pct": 42,
            "score": 5,
            "category": "moderate",
            "top_owners": ["Enel Green Power", "AES Gener", "Colbún"],
            "total_market_capacity_mw": 11500,
            "num_significant_players": 30,
            "hhi": 1180,
            "status": "Moderate consolidation with utilities and IPPs competing"
        },
        "Vietnam": {
            "top3_share_pct": 62,
            "score": 3,
            "category": "high",
            "top_owners": ["EVN", "PetroVietnam Power", "Trungnam Group"],
            "total_market_capacity_mw": 20500,
            "num_significant_players": 25,
            "hhi": 2100,
            "status": "High consolidation with state-owned EVN dominant"
        },
        "South Africa": {
            "top3_share_pct": 38,
            "score": 6,
            "category": "below_moderate",
            "top_owners": ["ACWA Power", "Enel Green Power", "Mainstream Renewable Power"],
            "total_market_capacity_mw": 7200,
            "num_significant_players": 35,
            "hhi": 1050,
            "status": "Moderately concentrated through REIPPP program with diverse IPPs"
        },
        "Nigeria": {
            "top3_share_pct": 75,
            "score": 2,
            "category": "very_high",
            "top_owners": ["Government/NBET", "Limited private projects"],
            "total_market_capacity_mw": 180,
            "num_significant_players": 5,
            "hhi": 3500,
            "status": "Very high consolidation, nascent market with limited private participation"
        },
        "Argentina": {
            "top3_share_pct": 48,
            "score": 5,
            "category": "moderate",
            "top_owners": ["YPF Luz", "Genneia", "Central Puerto"],
            "total_market_capacity_mw": 8500,
            "num_significant_players": 30,
            "hhi": 1320,
            "status": "Moderate consolidation with mix of traditional players and RenovAr entrants"
        },
        "Mexico": {
            "top3_share_pct": 52,
            "score": 4,
            "category": "above_moderate",
            "top_owners": ["CFE", "Iberdrola", "Enel Green Power"],
            "total_market_capacity_mw": 15000,
            "num_significant_players": 35,
            "hhi": 1650,
            "status": "Above moderate consolidation with CFE increasing dominance post-policy changes"
        },
        "Indonesia": {
            "top3_share_pct": 82,
            "score": 1,
            "category": "extreme_monopoly",
            "top_owners": ["PLN (state utility)", "Limited private players"],
            "total_market_capacity_mw": 850,
            "num_significant_players": 8,
            "hhi": 4200,
            "status": "Extreme monopoly with PLN dominating, very limited private sector participation"
        },
        "Saudi Arabia": {
            "top3_share_pct": 58,
            "score": 4,
            "category": "above_moderate",
            "top_owners": ["ACWA Power", "SEC", "Masdar"],
            "total_market_capacity_mw": 2100,
            "num_significant_players": 12,
            "hhi": 1950,
            "status": "Above moderate consolidation in nascent market with government-backed developers"
        },
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Ownership Consolidation Agent."""
        super().__init__(
            parameter_name="Ownership Consolidation",
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
            
            ownership_config = params_config['parameters'].get('ownership_consolidation', {})
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
            {"score": 1, "range": "Extreme monopoly", "description": ">80% by single owner"},
            {"score": 2, "range": "Very high", "description": "70-80% by top 3"},
            {"score": 3, "range": "High", "description": "60-70% by top 3"},
            {"score": 4, "range": "Above moderate", "description": "50-60% by top 3"},
            {"score": 5, "range": "Moderate", "description": "40-50% by top 3"},
            {"score": 6, "range": "Below moderate", "description": "30-40% by top 3"},
            {"score": 7, "range": "Low", "description": "20-30% by top 3"},
            {"score": 8, "range": "Very low", "description": "15-20% by top 3"},
            {"score": 9, "range": "Minimal", "description": "10-15% by top 3"},
            {"score": 10, "range": "Highly fragmented", "description": "<10% by top 3"}
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze ownership consolidation for a country."""
        try:
            logger.info(f"Analyzing Ownership Consolidation for {country} ({period})")
            
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
                f"Ownership Consolidation analysis complete for {country}: "
                f"Score={score}, Top3Share={data.get('top3_share_pct', 0)}%, "
                f"Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ownership Consolidation analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Ownership Consolidation analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch ownership consolidation data."""
        if self.mode == AgentMode.MOCK:
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate consolidation")
                data = {
                    "top3_share_pct": 45,
                    "score": 5,
                    "category": "moderate",
                    "top_owners": ["Unknown owners"],
                    "total_market_capacity_mw": 1000,
                    "num_significant_players": 20,
                    "hhi": 1300,
                    "status": "Moderate consolidation"
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
        """Calculate ownership consolidation score.
        
        INVERSE: Lower consolidation % = more competitive = higher score
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using pre-calculated score {score} for {country}")
            return float(score)
        
        # Otherwise calculate from top3 share percentage
        top3_pct = data.get("top3_share_pct", 45)
        
        # Inverse mapping: lower consolidation = higher score
        if top3_pct >= 80:
            score = 1  # Extreme monopoly
        elif top3_pct >= 70:
            score = 2  # Very high consolidation
        elif top3_pct >= 60:
            score = 3  # High consolidation
        elif top3_pct >= 50:
            score = 4  # Above moderate
        elif top3_pct >= 40:
            score = 5  # Moderate
        elif top3_pct >= 30:
            score = 6  # Below moderate
        elif top3_pct >= 20:
            score = 7  # Low consolidation
        elif top3_pct >= 15:
            score = 8  # Very low
        elif top3_pct >= 10:
            score = 9  # Minimal
        else:
            score = 10  # Highly fragmented
        
        logger.debug(f"Calculated score {score} from top3_share {top3_pct}%")
        
        return float(score)
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the ownership consolidation score."""
        top3_pct = data.get("top3_share_pct", 0)
        category = data.get("category", "moderate")
        top_owners = data.get("top_owners", [])
        total_mw = data.get("total_market_capacity_mw", 0)
        num_players = data.get("num_significant_players", 0)
        hhi = data.get("hhi", 0)
        status = data.get("status", "")
        
        description = "moderate consolidation"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level.get("range", level["description"]).lower()
                break
        
        justification = (
            f"Market shows {description} with top 3 owners controlling {top3_pct}% of "
            f"{total_mw:,.0f} MW total capacity. "
        )
        
        if top_owners:
            top_str = ", ".join(top_owners[:3])
            justification += f"Leading owners: {top_str}. "
        
        justification += (
            f"Market has {num_players} significant players with HHI of {hhi}. "
            f"{status}."
        )
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "Renewable energy asset ownership databases",
            "Market concentration analysis",
            "Industry reports and company filings",
            f"{country} National energy statistics",
            "S&P Global Market Intelligence"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Ownership Consolidation parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
        return [
            "Renewable energy asset ownership databases",
            "Market concentration analysis",
            "Industry reports and company filings",
            "National energy statistics",
            "S&P Global Market Intelligence"
        ]


def analyze_ownership_consolidation(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze ownership consolidation."""
    agent = OwnershipConsolidationAgent(mode=mode)
    return agent.analyze(country, period)
