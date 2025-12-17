"""Ambition Agent - Analyzes government renewable energy targets.

This agent evaluates a country's renewable energy ambition based on
targeted installed capacity (solar PV + onshore wind + offshore wind)
by 2030 in GW.

Scoring Rubric:
1:  < 3 GW    - Minimal renewable targets
2:  3-4.99 GW - Very low targets
3:  5-9.99 GW - Low targets
4:  10-14.99 GW - Below moderate
5:  15-19.99 GW - Moderate targets
6:  20-24.99 GW - Above moderate
7:  25-29.99 GW - High targets
8:  30-34.99 GW - Very high targets
9:  35-39.99 GW - Extremely high targets
10: ≥40 GW    - World-class targets
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class AmbitionAgent(BaseParameterAgent):
    """Agent for analyzing government renewable energy ambition."""
    
    # Scoring rubric (GW thresholds)
    SCORING_RUBRIC = [
        {"score": 1, "min_gw": 0, "max_gw": 3, "description": "Minimal renewable targets"},
        {"score": 2, "min_gw": 3, "max_gw": 5, "description": "Very low targets"},
        {"score": 3, "min_gw": 5, "max_gw": 10, "description": "Low targets"},
        {"score": 4, "min_gw": 10, "max_gw": 15, "description": "Below moderate targets"},
        {"score": 5, "min_gw": 15, "max_gw": 20, "description": "Moderate targets"},
        {"score": 6, "min_gw": 20, "max_gw": 25, "description": "Above moderate targets"},
        {"score": 7, "min_gw": 25, "max_gw": 30, "description": "High targets"},
        {"score": 8, "min_gw": 30, "max_gw": 35, "description": "Very high targets"},
        {"score": 9, "min_gw": 35, "max_gw": 40, "description": "Extremely high targets"},
        {"score": 10, "min_gw": 40, "max_gw": float('inf'), "description": "World-class targets"}
    ]
    
    # Mock data for Phase 1 testing (will be replaced with real data fetching)
    MOCK_DATA = {
        "Brazil": {"total_gw": 26.8, "solar": 15.0, "onshore_wind": 10.8, "offshore_wind": 1.0},
        "Germany": {"total_gw": 115.0, "solar": 58.0, "onshore_wind": 40.0, "offshore_wind": 17.0},
        "USA": {"total_gw": 350.0, "solar": 200.0, "onshore_wind": 130.0, "offshore_wind": 20.0},
        "China": {"total_gw": 600.0, "solar": 350.0, "onshore_wind": 220.0, "offshore_wind": 30.0},
        "India": {"total_gw": 175.0, "solar": 100.0, "onshore_wind": 70.0, "offshore_wind": 5.0},
        "United Kingdom": {"total_gw": 50.0, "solar": 20.0, "onshore_wind": 15.0, "offshore_wind": 15.0},
        "Spain": {"total_gw": 62.0, "solar": 35.0, "onshore_wind": 25.0, "offshore_wind": 2.0},
        "Australia": {"total_gw": 82.0, "solar": 50.0, "onshore_wind": 30.0, "offshore_wind": 2.0},
        "Chile": {"total_gw": 18.5, "solar": 12.0, "onshore_wind": 6.0, "offshore_wind": 0.5},
        "Vietnam": {"total_gw": 28.0, "solar": 18.0, "onshore_wind": 9.0, "offshore_wind": 1.0},
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Ambition Agent."""
        super().__init__(
            parameter_name="Ambition",
            mode=mode,
            config=config
        )
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze ambition for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Ambition for {country} ({period})")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            data_quality = "high" if data else "low"
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
                f"Ambition analysis complete for {country}: "
                f"Score={score}, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ambition analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Ambition analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch renewable energy target data.
        
        In MOCK mode: Returns mock data
        In RULE mode: Would query database
        In AI mode: Would use LLM to extract from documents
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with target data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default minimal target")
                data = {"total_gw": 2.0, "solar": 1.0, "onshore_wind": 1.0, "offshore_wind": 0.0}
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # TODO Phase 2: Query from database
            # return self._query_targets_database(country, period)
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from documents
            # return self._llm_extract_targets(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate ambition score based on total GW target.
        
        Args:
            data: Target data with total_gw
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        total_gw = data.get("total_gw", 0)
        
        logger.debug(f"Calculating score for {country}: {total_gw} GW")
        
        # Find matching rubric level
        for level in self.SCORING_RUBRIC:
            if level["min_gw"] <= total_gw < level["max_gw"]:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{total_gw} GW falls in range {level['min_gw']}-{level['max_gw']} GW"
                )
                return float(score)
        
        # Fallback (shouldn't reach here with proper rubric)
        logger.warning(f"No rubric match for {total_gw} GW, defaulting to score 1")
        return 1.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the ambition score.
        
        Args:
            data: Target data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        total_gw = data.get("total_gw", 0)
        solar = data.get("solar", 0)
        onshore = data.get("onshore_wind", 0)
        offshore = data.get("offshore_wind", 0)
        
        # Find description from rubric
        description = "renewable targets"
        for level in self.SCORING_RUBRIC:
            if level["score"] == int(score):
                description = level["description"]
                break
        
        # Build justification
        justification = (
            f"{total_gw} GW of renewable capacity targeted by 2030 "
            f"(solar PV: {solar} GW, onshore wind: {onshore} GW, offshore wind: {offshore} GW). "
            f"{description.capitalize()}."
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
            f"{country} NDC 2024",
            "IRENA Renewable Capacity Statistics 2024",
            f"{country} Ministry of Energy Official Targets"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Ambition parameter.
        
        Returns:
            Complete scoring rubric
        """
        return self.SCORING_RUBRIC
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter.
        
        Returns:
            List of typical data sources
        """
        return [
            "Government NDCs (Nationally Determined Contributions)",
            "Ministry of Energy publications",
            "IRENA country profiles",
            "IEA renewable energy policies database"
        ]


# Convenience function for direct usage
def analyze_ambition(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze ambition for a country.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode
        
    Returns:
        ParameterScore
    """
    agent = AmbitionAgent(mode=mode)
    return agent.analyze(country, period)
