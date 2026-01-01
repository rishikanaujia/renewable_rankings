"""Country Analysis Agent - Synthesizes all parameters into country profile.

This agent aggregates all 18 parameter analyses across 6 subcategories
to produce a comprehensive country investment profile with:
- Overall investment attractiveness score
- Detailed subcategory breakdown
- Identified strengths and weaknesses
- Overall assessment and justification

This is the first synthesis agent that sits above the parameter layer.

Architecture:
- Level III: CountryAnalysisAgent (this agent)
- Level II: 6 Subcategories (via agent_service)
- Level I: 18 Parameter Agents

ACTUAL STRUCTURE (from Implementation Guide):

LEVEL I - Critical Deal-Breakers (55-70%):
1. Regulation (5 parameters, 20-25% weight)
   - Ambition, Support Scheme, Track Record, Contract Terms, Country Stability
2. Profitability (4 parameters, 20-25% weight)
   - Revenue Stream Stability, Offtaker Status, Expected Return, Long-Term Interest Rates
3. Accommodation (2 parameters, 15-20% weight)
   - Status of Grid, Ownership Hurdles

LEVEL II - Opportunity Sizing (20-30%):
4. Market Size & Fundamentals (4 parameters, 10-15% weight)
   - Market Size, Resources, Energy Dependence, RE Penetration
5. Competition & Ease of Business (2 parameters, 10-15% weight)
   - Ownership Consolidation, Competitive Landscape

LEVEL III - Edge Cases (5-10%):
6. System/External Modifiers (1 composite parameter, 5-10% weight)
   - Handles: Cannibalization, Curtailment, Queue Dynamics, Supply Chain

Total: 18 parameter agents across 6 subcategories
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import AgentMode
from ...models.country_analysis import CountryAnalysis, SubcategoryScore, StrengthWeakness
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class CountryAnalysisAgent:
    """Agent for comprehensive country analysis and synthesis."""
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Country Analysis Agent.
        
        Args:
            mode: Agent operation mode (MOCK, RULE_BASED, AI_POWERED)
            config: Optional configuration dictionary
        """
        self.mode = mode
        self.config = config or {}
        
        # Load weights from config
        self.weights = self._load_weights()
        self.strength_threshold = self._load_threshold('strength_threshold', 7.5)
        self.weakness_threshold = self._load_threshold('weakness_threshold', 5.5)
        self.score_interpretations = self._load_score_interpretations()
        
        logger.info(f"Initialized CountryAnalysisAgent in {mode} mode")
        logger.debug(f"Subcategory weights: {self.weights}")
    
    def _load_weights(self) -> Dict[str, float]:
        """Load subcategory weights from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            analysis_config = params_config.get('analysis', {})
            weights = analysis_config.get('subcategory_weights', {})
            
            if weights:
                logger.info("Loaded subcategory weights from config")
                return weights
            else:
                logger.warning("No weights in config, using defaults")
                return self._get_default_weights()
                
        except Exception as e:
            logger.warning(f"Could not load weights from config: {e}. Using defaults.")
            return self._get_default_weights()
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Default subcategory weights matching Implementation Guide structure.
        
        Based on Brazil example calculation:
        - Level I (Critical): 55-70% total
        - Level II (Opportunity): 20-30% total
        - Level III (Modifiers): 5-10% total
        """
        return {
            # LEVEL I - Critical Deal-Breakers (60%)
            "regulation": 0.225,                    # 22.5% - Critical policy framework
            "profitability": 0.225,                 # 22.5% - Returns and economics
            "accommodation": 0.175,                 # 17.5% - Infrastructure
            # LEVEL II - Opportunity Sizing (27.5%)
            "market_size_fundamentals": 0.125,      # 12.5% - Market potential
            "competition_ease_business": 0.125,     # 12.5% - Competitive dynamics
            # LEVEL III - Edge Cases (7.5%)
            "system_modifiers": 0.075,              # 7.5% - Systemic factors
            # Total: 100%
        }
    
    def _load_threshold(self, key: str, default: float) -> float:
        """Load threshold from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            analysis_config = params_config.get('analysis', {})
            return analysis_config.get(key, default)
        except Exception:
            return default
    
    def _load_score_interpretations(self) -> List[Dict[str, Any]]:
        """Load score interpretation ranges from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            analysis_config = params_config.get('analysis', {})
            return analysis_config.get('score_interpretation', [])
        except Exception:
            return []
    
    def analyze(self, country: str, period: str, **kwargs) -> CountryAnalysis:
        """Perform comprehensive country analysis.
        
        Args:
            country: Country name
            period: Analysis period (e.g., "Q3 2024")
            **kwargs: Additional parameters
            
        Returns:
            CountryAnalysis with complete investment profile
        """
        try:
            logger.info(f"Analyzing country: {country} ({period})")
            
            # Get all subcategory scores
            subcategory_results = self._get_subcategory_scores(country, period)
            
            # Calculate overall score (weighted average of 6 subcategories)
            overall_score = self._calculate_overall_score(subcategory_results)
            
            # Identify strengths and weaknesses
            strengths = self._identify_strengths(subcategory_results)
            weaknesses = self._identify_weaknesses(subcategory_results)
            
            # Generate overall assessment
            assessment = self._generate_assessment(
                country, overall_score, subcategory_results, strengths, weaknesses
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(subcategory_results)
            
            result = CountryAnalysis(
                country=country,
                period=period,
                overall_score=overall_score,
                subcategory_scores=subcategory_results,
                strengths=strengths,
                weaknesses=weaknesses,
                overall_assessment=assessment,
                confidence=confidence,
                timestamp=datetime.now(),
                metadata={
                    "weights": self.weights,
                    "mode": str(self.mode),
                    "total_parameters": 18,
                    "subcategories": 6
                }
            )
            
            logger.info(
                f"Country analysis complete for {country}: "
                f"Overall={overall_score:.2f}, "
                f"Strengths={len(strengths)}, Weaknesses={len(weaknesses)}, "
                f"Confidence={confidence:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Country analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Country analysis failed: {str(e)}")
    
    def _get_subcategory_scores(self, country: str, period: str) -> List[SubcategoryScore]:
        """Get scores for all subcategories using agent_service.
        
        CORRECTED: Actual 6 subcategories from Implementation Guide.
        """
        from ..agent_service import agent_service
        
        # CORRECTED: Actual 6 subcategories matching Implementation Guide
        subcategories = [
            "regulation",                    # 5 parameters
            "profitability",                 # 4 parameters
            "accommodation",                 # 2 parameters
            "market_size_fundamentals",      # 4 parameters
            "competition_ease_business",     # 2 parameters
            "system_modifiers",              # 1 composite parameter
        ]
        
        results = []
        
        for subcategory in subcategories:
            try:
                result = agent_service.analyze_subcategory(subcategory, country, period)
                
                weight = self.weights.get(subcategory, 0.0)
                weighted_score = result.score * weight
                
                subcategory_score = SubcategoryScore(
                    name=subcategory.replace('_', ' ').title(),
                    score=result.score,
                    parameter_count=len(result.parameter_scores),
                    weight=weight,
                    weighted_score=weighted_score
                )
                
                results.append(subcategory_score)
                
                logger.debug(
                    f"{subcategory}: {result.score:.2f} "
                    f"(weight={weight:.2f}, weighted={weighted_score:.2f})"
                )
                
            except Exception as e:
                logger.error(f"Failed to get {subcategory} score: {e}")
                # Use default if subcategory fails
                results.append(SubcategoryScore(
                    name=subcategory.replace('_', ' ').title(),
                    score=5.0,  # Default moderate score
                    parameter_count=0,
                    weight=self.weights.get(subcategory, 0.0),
                    weighted_score=5.0 * self.weights.get(subcategory, 0.0)
                ))
        
        return results
    
    def _calculate_overall_score(self, subcategory_results: List[SubcategoryScore]) -> float:
        """Calculate weighted overall score from 6 subcategories.
        
        Formula: Overall = Σ(Subcategory Score × Weight)
        Example (Brazil): 6.47 = (8.0×0.225 + 6.0×0.225 + 5.5×0.175 + 8.0×0.125 + 7.3×0.125 + 6.0×0.075)
        """
        total_weighted_score = sum(s.weighted_score for s in subcategory_results)
        
        # Normalize to 10-point scale (should already be normalized if weights sum to 1.0)
        overall_score = total_weighted_score
        
        # Ensure score is within bounds
        overall_score = max(0.0, min(10.0, overall_score))
        
        logger.debug(f"Overall score calculated: {overall_score:.2f}")
        
        return round(overall_score, 2)
    
    def _identify_strengths(self, subcategory_results: List[SubcategoryScore]) -> List[StrengthWeakness]:
        """Identify top strengths (high scoring areas)."""
        strengths = []
        
        # Sort by score descending
        sorted_results = sorted(subcategory_results, key=lambda x: x.score, reverse=True)
        
        # Take top scoring areas above threshold
        for result in sorted_results:
            if result.score >= self.strength_threshold:
                reason = self._get_strength_reason(result.name, result.score)
                
                strength = StrengthWeakness(
                    area=result.name,
                    score=result.score,
                    reason=reason,
                    category="strength"
                )
                strengths.append(strength)
        
        logger.debug(f"Identified {len(strengths)} strengths")
        
        return strengths[:5]  # Return top 5
    
    def _identify_weaknesses(self, subcategory_results: List[SubcategoryScore]) -> List[StrengthWeakness]:
        """Identify key weaknesses (low scoring areas)."""
        weaknesses = []
        
        # Sort by score ascending
        sorted_results = sorted(subcategory_results, key=lambda x: x.score)
        
        # Take lowest scoring areas below threshold
        for result in sorted_results:
            if result.score < self.weakness_threshold:
                reason = self._get_weakness_reason(result.name, result.score)
                
                weakness = StrengthWeakness(
                    area=result.name,
                    score=result.score,
                    reason=reason,
                    category="weakness"
                )
                weaknesses.append(weakness)
        
        logger.debug(f"Identified {len(weaknesses)} weaknesses")
        
        return weaknesses[:5]  # Return top 5
    
    def _get_strength_reason(self, area: str, score: float) -> str:
        """Generate reason text for a strength."""
        reasons = {
            "Regulation": "Strong regulatory framework and policy support",
            "Profitability": "Attractive returns and favorable economics",
            "Accommodation": "Excellent infrastructure and market access",
            "Market Size Fundamentals": "Large market with excellent growth potential",
            "Competition Ease Business": "Favorable competitive dynamics and ease of entry",
            "System Modifiers": "Low systemic risks and stable environment"
        }
        
        return reasons.get(area, f"Strong performance in {area}")
    
    def _get_weakness_reason(self, area: str, score: float) -> str:
        """Generate reason text for a weakness."""
        reasons = {
            "Regulation": "Regulatory challenges and policy uncertainty",
            "Profitability": "Lower returns or challenging economics",
            "Accommodation": "Infrastructure constraints or access barriers",
            "Market Size Fundamentals": "Limited market scale or constrained growth",
            "Competition Ease Business": "Market barriers or competitive constraints",
            "System Modifiers": "Elevated systemic risks (cannibalization, curtailment, queue issues)"
        }
        
        return reasons.get(area, f"Challenges in {area}")
    
    def _generate_assessment(
        self,
        country: str,
        overall_score: float,
        subcategory_results: List[SubcategoryScore],
        strengths: List[StrengthWeakness],
        weaknesses: List[StrengthWeakness]
    ) -> str:
        """Generate overall investment assessment narrative."""
        
        # Get score interpretation
        interpretation = self._get_score_interpretation(overall_score)
        
        # Build assessment
        assessment = f"{country} scores {overall_score:.1f}/10, indicating a {interpretation['label'].lower()} investment destination. "
        
        # Add strength summary
        if strengths:
            strength_areas = [s.area for s in strengths[:3]]
            assessment += f"Key strengths include {', '.join(strength_areas).lower()}. "
        
        # Add weakness summary
        if weaknesses:
            weakness_areas = [w.area for w in weaknesses[:3]]
            assessment += f"Main challenges are in {', '.join(weakness_areas).lower()}. "
        
        # Add overall characterization
        assessment += interpretation['description'] + "."
        
        return assessment
    
    def _get_score_interpretation(self, score: float) -> Dict[str, str]:
        """Get interpretation for a score."""
        for interp in self.score_interpretations:
            range_min, range_max = interp['range']
            if range_min <= score < range_max:
                return interp
        
        # Default fallback
        if score >= 8.0:
            return {"label": "Excellent", "description": "Highly attractive market with strong fundamentals"}
        elif score >= 6.5:
            return {"label": "Good", "description": "Solid investment opportunity with manageable risks"}
        elif score >= 5.0:
            return {"label": "Moderate", "description": "Mixed profile with notable challenges"}
        elif score >= 3.5:
            return {"label": "Below Average", "description": "Significant barriers and risks present"}
        else:
            return {"label": "Poor", "description": "Substantial challenges limit attractiveness"}
    
    def _calculate_confidence(self, subcategory_results: List[SubcategoryScore]) -> float:
        """Calculate confidence in the analysis.
        
        Confidence based on:
        - Number of complete subcategories
        - Data quality from underlying parameters
        """
        # For now, use high confidence if all subcategories have data
        complete_count = sum(1 for s in subcategory_results if s.parameter_count > 0)
        total_count = len(subcategory_results)
        
        confidence = complete_count / total_count if total_count > 0 else 0.0
        
        # Assume moderate confidence for mock mode
        if self.mode == AgentMode.MOCK:
            confidence = max(0.85, confidence)
        
        return round(confidence, 2)


def analyze_country(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> CountryAnalysis:
    """Convenience function to analyze a country.
    
    Args:
        country: Country name
        period: Analysis period
        mode: Agent mode (MOCK, RULE_BASED, AI_POWERED)
        
    Returns:
        CountryAnalysis with complete investment profile
    """
    agent = CountryAnalysisAgent(mode=mode)
    return agent.analyze(country, period)
