"""Base agent class for all parameter analysts."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..models.parameter import ParameterScore
from ..core.logger import get_logger
from ..core.exceptions import AgentError

logger = get_logger(__name__)


class AgentMode(str, Enum):
    """Agent operation mode."""
    MOCK = "mock"           # Use mock data (Phase 1)
    RULE_BASED = "rule"     # Use deterministic rules (Phase 2)
    AI_POWERED = "ai"       # Use LLM (Phase 2+)


class BaseParameterAgent(ABC):
    """Abstract base class for parameter analyst agents.
    
    All parameter agents must implement:
    - analyze() - Main analysis method
    - _fetch_data() - Data collection
    - _calculate_score() - Score calculation
    - _generate_justification() - Explanation generation
    """
    
    def __init__(
        self,
        parameter_name: str,
        mode: AgentMode = AgentMode.MOCK,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize parameter agent.
        
        Args:
            parameter_name: Name of the parameter (e.g., "Ambition")
            mode: Operation mode (mock/rule/ai)
            config: Optional configuration dictionary
        """
        self.parameter_name = parameter_name
        self.mode = mode
        self.config = config or {}
        
        logger.info(
            f"Initialized {self.__class__.__name__} "
            f"for parameter '{parameter_name}' in {mode} mode"
        )
    
    @abstractmethod
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze parameter for a country.
        
        This is the main entry point. Must be implemented by all agents.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, data sources
            
        Raises:
            AgentError: If analysis fails
        """
        pass
    
    @abstractmethod
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch required data for analysis.
        
        Args:
            country: Country name
            period: Time period
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing fetched data
            
        Raises:
            AgentError: If data fetching fails
        """
        pass
    
    @abstractmethod
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate parameter score based on data.
        
        Args:
            data: Fetched data
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
            
        Raises:
            AgentError: If calculation fails
        """
        pass
    
    @abstractmethod
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate human-readable justification for the score.
        
        Args:
            data: Fetched data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Justification string
        """
        pass
    
    def _validate_score(self, score: float) -> float:
        """Validate and clamp score to valid range.
        
        Args:
            score: Raw score value
            
        Returns:
            Validated score between 1-10
        """
        if score < 1:
            logger.warning(f"Score {score} below minimum, clamping to 1")
            return 1.0
        if score > 10:
            logger.warning(f"Score {score} above maximum, clamping to 10")
            return 10.0
        return round(score, 2)
    
    def _estimate_confidence(
        self,
        data: Dict[str, Any],
        data_quality: str = "medium"
    ) -> float:
        """Estimate confidence level in the score.
        
        Args:
            data: Data used for scoring
            data_quality: Data quality indicator (low/medium/high)
            
        Returns:
            Confidence level between 0-1
        """
        # Simple heuristic - can be overridden by subclasses
        confidence_map = {
            "low": 0.6,
            "medium": 0.8,
            "high": 0.95
        }
        
        base_confidence = confidence_map.get(data_quality, 0.8)
        
        # Reduce confidence if data is incomplete
        if not data or len(data) == 0:
            base_confidence *= 0.5
        
        return round(base_confidence, 2)
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for this parameter.
        
        Returns:
            List of scoring levels with ranges and descriptions
        """
        # Default rubric - should be overridden by subclasses
        # This will be loaded from config in production
        return [
            {"value": 1, "range": "Very Low", "description": "Minimal"},
            {"value": 5, "range": "Medium", "description": "Moderate"},
            {"value": 10, "range": "Very High", "description": "Excellent"}
        ]
    
    def get_data_sources(self) -> List[str]:
        """Get list of data sources used by this agent.
        
        Returns:
            List of data source names
        """
        # Default sources - should be overridden by subclasses
        return ["Government Reports", "International Organizations"]
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(parameter={self.parameter_name}, mode={self.mode})"
