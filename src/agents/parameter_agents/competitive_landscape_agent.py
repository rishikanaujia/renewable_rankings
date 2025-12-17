"""Competitive Landscape Agent - Analyzes market entry ease and competition.

This agent evaluates the competitive dynamics and ease of market entry
in renewable energy markets by assessing:
- Regulatory barriers to entry
- Licensing and permitting complexity
- Market openness to new players
- Competitive intensity
- Exit and entry patterns

Key evaluation criteria:
- Licensing requirements and timelines
- Capital requirements and access
- Grid connection processes
- Land acquisition complexity
- Environmental permitting
- Local content requirements

Market Openness Categories (1-10):
1. Extreme barriers (market closed)
2. Very high barriers
3. High barriers
4. Above moderate barriers
5. Moderate barriers
6. Below moderate barriers
7. Low barriers
8. Very low barriers
9. Minimal barriers
10. No barriers (fully open)

Scoring Rubric (LOADED FROM CONFIG):
Lower barriers = More competitive = Higher score
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class CompetitiveLandscapeAgent(BaseParameterAgent):
    """Agent for analyzing competitive landscape and market entry ease."""
    
    # Mock data for Phase 1 testing
    # Market entry ease assessment based on regulatory frameworks
    # Data from World Bank Doing Business, IEA, regulatory analysis
    MOCK_DATA = {
        "Brazil": {
            "score": 7,
            "category": "low_barriers",
            "licensing_complexity": "Moderate (auction-based, clear rules)",
            "permitting_timeline_months": 12,
            "grid_connection_ease": "Moderate (improving infrastructure)",
            "market_openness": "High (open to international and domestic players)",
            "competitive_intensity": "High (active auctions, many participants)",
            "entry_examples": "Strong IPP participation, international developers active",
            "status": "Open market with low barriers, active competition through auction system"
        },
        "Germany": {
            "score": 9,
            "category": "minimal_barriers",
            "licensing_complexity": "Low (streamlined EEG process)",
            "permitting_timeline_months": 6,
            "grid_connection_ease": "High (mature grid, clear rules)",
            "market_openness": "Very High (fully open market)",
            "competitive_intensity": "Very High (diverse players, cooperatives)",
            "entry_examples": "Thousands of small players, community projects",
            "status": "Highly competitive open market with minimal barriers and strong participation"
        },
        "USA": {
            "score": 8,
            "category": "very_low_barriers",
            "licensing_complexity": "Low to Moderate (state-dependent)",
            "permitting_timeline_months": 9,
            "grid_connection_ease": "Moderate to High (varies by region)",
            "market_openness": "Very High (competitive markets)",
            "competitive_intensity": "Very High (utilities, IPPs, yieldcos)",
            "entry_examples": "Robust IPP market, strong competition",
            "status": "Very competitive market with low barriers, though varies by state"
        },
        "China": {
            "score": 5,
            "category": "moderate_barriers",
            "licensing_complexity": "Moderate to High (government approvals)",
            "permitting_timeline_months": 18,
            "grid_connection_ease": "Moderate (state grid control)",
            "market_openness": "Moderate (preference for SOEs, JV requirements)",
            "competitive_intensity": "Moderate (large SOEs dominate)",
            "entry_examples": "Primarily state-owned enterprises, some private players",
            "status": "Moderate barriers with preference for state-owned enterprises"
        },
        "India": {
            "score": 7,
            "category": "low_barriers",
            "licensing_complexity": "Moderate (auction-based, improving)",
            "permitting_timeline_months": 15,
            "grid_connection_ease": "Moderate (grid constraints)",
            "market_openness": "High (open to domestic and international)",
            "competitive_intensity": "High (active IPP participation)",
            "entry_examples": "Strong IPP growth, international developers",
            "status": "Increasingly open market with improving ease of entry"
        },
        "UK": {
            "score": 8,
            "category": "very_low_barriers",
            "licensing_complexity": "Low (CfD auctions, clear process)",
            "permitting_timeline_months": 8,
            "grid_connection_ease": "High (mature system)",
            "market_openness": "Very High (competitive market)",
            "competitive_intensity": "Very High (especially offshore wind)",
            "entry_examples": "International developers, strong IPP market",
            "status": "Highly competitive market with low barriers and strong international participation"
        },
        "Spain": {
            "score": 6,
            "category": "below_moderate_barriers",
            "licensing_complexity": "Moderate (recovering from reforms)",
            "permitting_timeline_months": 14,
            "grid_connection_ease": "Moderate (grid queue issues)",
            "market_openness": "High (reopening to competition)",
            "competitive_intensity": "Moderate to High (recovering)",
            "entry_examples": "Renewed activity post-reform",
            "status": "Market reopening with improving entry conditions after past policy issues"
        },
        "Australia": {
            "score": 8,
            "category": "very_low_barriers",
            "licensing_complexity": "Low (state-level, generally streamlined)",
            "permitting_timeline_months": 7,
            "grid_connection_ease": "Moderate to High (NEM system)",
            "market_openness": "Very High (competitive market)",
            "competitive_intensity": "Very High (active IPP market)",
            "entry_examples": "Strong independent developer activity",
            "status": "Highly competitive market with low barriers and active entry"
        },
        "Chile": {
            "score": 7,
            "category": "low_barriers",
            "licensing_complexity": "Low to Moderate (auction system)",
            "permitting_timeline_months": 10,
            "grid_connection_ease": "Moderate (transmission challenges)",
            "market_openness": "High (open to competition)",
            "competitive_intensity": "High (competitive auctions)",
            "entry_examples": "Active international and domestic participation",
            "status": "Open competitive market with relatively low entry barriers"
        },
        "Vietnam": {
            "score": 4,
            "category": "above_moderate_barriers",
            "licensing_complexity": "High (complex approvals, EVN control)",
            "permitting_timeline_months": 24,
            "grid_connection_ease": "Low (EVN monopoly, curtailment)",
            "market_openness": "Moderate (opening but controlled)",
            "competitive_intensity": "Low to Moderate (limited by EVN)",
            "entry_examples": "Some IPP entry but significant challenges",
            "status": "Significant barriers with EVN control limiting competition"
        },
        "South Africa": {
            "score": 6,
            "category": "below_moderate_barriers",
            "licensing_complexity": "Moderate (REIPPP process established)",
            "permitting_timeline_months": 16,
            "grid_connection_ease": "Moderate (Eskom constraints)",
            "market_openness": "High (competitive bidding)",
            "competitive_intensity": "Moderate to High (REIPPP rounds)",
            "entry_examples": "Diverse IPP participation through REIPPP",
            "status": "Structured competitive market but Eskom challenges create barriers"
        },
        "Nigeria": {
            "score": 2,
            "category": "very_high_barriers",
            "licensing_complexity": "Very High (complex, uncertain process)",
            "permitting_timeline_months": 36,
            "grid_connection_ease": "Very Low (poor grid, NBET challenges)",
            "market_openness": "Low (limited framework)",
            "competitive_intensity": "Very Low (nascent market)",
            "entry_examples": "Very limited private sector entry",
            "status": "Severe barriers to entry with limited market opening"
        },
        "Argentina": {
            "score": 5,
            "category": "moderate_barriers",
            "licensing_complexity": "Moderate to High (policy uncertainty)",
            "permitting_timeline_months": 20,
            "grid_connection_ease": "Moderate (CAMMESA process)",
            "market_openness": "Moderate (RenovAr but policy risk)",
            "competitive_intensity": "Moderate (episodic activity)",
            "entry_examples": "RenovAr attracted players but policy risk",
            "status": "Moderate barriers with significant policy and currency risk"
        },
        "Mexico": {
            "score": 3,
            "category": "high_barriers",
            "licensing_complexity": "High (policy reversal, CFE preference)",
            "permitting_timeline_months": 30,
            "grid_connection_ease": "Low (CFE control, barriers)",
            "market_openness": "Low (market closing post-policy changes)",
            "competitive_intensity": "Low (CFE dominance increasing)",
            "entry_examples": "Entry severely restricted by policy changes",
            "status": "High barriers due to policy reversal favoring state utility"
        },
        "Indonesia": {
            "score": 2,
            "category": "very_high_barriers",
            "licensing_complexity": "Very High (PLN monopoly, complex process)",
            "permitting_timeline_months": 36,
            "grid_connection_ease": "Very Low (PLN control)",
            "market_openness": "Very Low (PLN dominance)",
            "competitive_intensity": "Very Low (limited private entry)",
            "entry_examples": "Minimal private sector participation",
            "status": "Severe barriers with PLN monopoly limiting market opening"
        },
        "Saudi Arabia": {
            "score": 6,
            "category": "below_moderate_barriers",
            "licensing_complexity": "Moderate (NREP process structured)",
            "permitting_timeline_months": 14,
            "grid_connection_ease": "Moderate to High (improving)",
            "market_openness": "Moderate to High (Vision 2030 opening)",
            "competitive_intensity": "Moderate (growing activity)",
            "entry_examples": "International developers participating in NREP",
            "status": "Market opening under Vision 2030 with moderate entry barriers"
        },
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Competitive Landscape Agent."""
        super().__init__(
            parameter_name="Competitive Landscape",
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
            
            competitive_config = params_config['parameters'].get('competitive_landscape', {})
            scoring = competitive_config.get('scoring', [])
            
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
            {"score": 1, "range": "Extreme barriers", "description": "Market effectively closed"},
            {"score": 2, "range": "Very high barriers", "description": "Severe entry restrictions"},
            {"score": 3, "range": "High barriers", "description": "Significant entry barriers"},
            {"score": 4, "range": "Above moderate barriers", "description": "Notable barriers"},
            {"score": 5, "range": "Moderate barriers", "description": "Balanced entry requirements"},
            {"score": 6, "range": "Below moderate barriers", "description": "Relatively open market"},
            {"score": 7, "range": "Low barriers", "description": "Open market, easy entry"},
            {"score": 8, "range": "Very low barriers", "description": "Minimal restrictions"},
            {"score": 9, "range": "Minimal barriers", "description": "Nearly open market"},
            {"score": 10, "range": "No barriers", "description": "Completely open market"}
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze competitive landscape for a country."""
        try:
            logger.info(f"Analyzing Competitive Landscape for {country} ({period})")
            
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
                f"Competitive Landscape analysis complete for {country}: "
                f"Score={score}, Category={data.get('category', 'unknown')}, "
                f"Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Competitive Landscape analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Competitive Landscape analysis failed: {str(e)}")
    
    def _fetch_data(self, country: str, period: str, **kwargs) -> Dict[str, Any]:
        """Fetch competitive landscape data."""
        if self.mode == AgentMode.MOCK:
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate barriers")
                data = {
                    "score": 5,
                    "category": "moderate_barriers",
                    "licensing_complexity": "Moderate",
                    "permitting_timeline_months": 18,
                    "grid_connection_ease": "Moderate",
                    "market_openness": "Moderate",
                    "competitive_intensity": "Moderate",
                    "entry_examples": "Some entry activity",
                    "status": "Moderate barriers to entry"
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
        """Calculate competitive landscape score.
        
        Lower barriers = More competitive = Higher score
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using pre-calculated score {score} for {country}")
            return float(score)
        
        # Otherwise could calculate from components
        # (This would require complex weighting of licensing, permitting, etc.)
        # For now, default to moderate
        score = 5
        
        logger.debug(f"Using default score {score} for {country}")
        
        return float(score)
    
    def _generate_justification(self, data: Dict[str, Any], score: float, country: str, period: str) -> str:
        """Generate justification for the competitive landscape score."""
        category = data.get("category", "moderate_barriers")
        licensing = data.get("licensing_complexity", "moderate")
        timeline = data.get("permitting_timeline_months", 18)
        grid = data.get("grid_connection_ease", "moderate")
        openness = data.get("market_openness", "moderate")
        intensity = data.get("competitive_intensity", "moderate")
        examples = data.get("entry_examples", "some activity")
        status = data.get("status", "")
        
        description = "moderate barriers"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level.get("range", level["description"]).lower()
                break
        
        justification = (
            f"Market shows {description}. "
            f"Licensing complexity: {licensing.lower()}, "
            f"permitting timeline ~{timeline} months, "
            f"grid connection: {grid.lower()}. "
        )
        
        justification += (
            f"Market openness: {openness.lower()}, "
            f"competitive intensity: {intensity.lower()}. "
        )
        
        justification += f"{examples}. {status}."
        
        return justification
    
    def _get_data_sources(self, country: str) -> List[str]:
        """Get data sources used for this analysis."""
        return [
            "Market entry analysis and regulatory frameworks",
            "World Bank Doing Business indicators",
            "Competitive intensity assessments",
            f"{country} licensing and permitting requirements",
            "Industry entry and exit data"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Competitive Landscape parameter."""
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter."""
        return [
            "Market entry analysis and regulatory frameworks",
            "Competitive intensity assessments",
            "Licensing and permitting requirements",
            "Industry entry and exit data",
            "World Bank Doing Business indicators"
        ]


def analyze_competitive_landscape(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze competitive landscape."""
    agent = CompetitiveLandscapeAgent(mode=mode)
    return agent.analyze(country, period)
