"""Example: Adding Memory to CountryStabilityAgent

BEFORE (current code):
    class CountryStabilityAgent(BaseParameterAgent):
        def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
            super().__init__(parameter_name="Country Stability", mode=mode, config=config)

AFTER (with memory):
    from src.memory import MemoryMixin
    
    class CountryStabilityAgent(BaseParameterAgent, MemoryMixin):
        def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None, memory_manager=None):
            super().__init__(parameter_name="Country Stability", mode=mode, config=config)
            if memory_manager:
                MemoryMixin.init_memory(self, memory_manager, auto_record=True)
"""

from typing import Dict, Any, List
from datetime import datetime

from src.agents.base_agent import BaseParameterAgent, AgentMode
from src.models.parameter import ParameterScore
from src.core.logger import get_logger
from src.memory import MemoryMixin  # ADD THIS IMPORT

logger = get_logger(__name__)


class CountryStabilityAgentWithMemory(BaseParameterAgent, MemoryMixin):  # ADD MemoryMixin
    """Country Stability Agent with Memory Integration."""
    
    MOCK_DATA = {
        "Brazil": {"ecr_rating": 2.3, "risk_category": "Stable"},
        "Germany": {"ecr_rating": 0.8, "risk_category": "Extremely Stable"},
        "USA": {"ecr_rating": 1.2, "risk_category": "Very Stable"},
        "China": {"ecr_rating": 2.8, "risk_category": "Stable"},
        "India": {"ecr_rating": 3.2, "risk_category": "Moderately Stable"},
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        memory_manager=None  # ADD THIS PARAMETER
    ):
        """Initialize agent with optional memory."""
        # Initialize base agent first
        super().__init__(
            parameter_name="Country Stability",
            mode=mode,
            config=config
        )
        
        # Initialize memory if provided
        if memory_manager:
            MemoryMixin.init_memory(self, memory_manager, auto_record=True)
            logger.info("Memory integration enabled for CountryStabilityAgent")
        
        self.scoring_rubric = self._load_scoring_rubric()
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric."""
        return [
            {"score": 10, "min_ecr": 0.0, "max_ecr": 1.0, "description": "Extremely stable"},
            {"score": 9, "min_ecr": 1.0, "max_ecr": 2.0, "description": "Very stable"},
            {"score": 8, "min_ecr": 2.0, "max_ecr": 3.0, "description": "Stable"},
            {"score": 7, "min_ecr": 3.0, "max_ecr": 4.0, "description": "Moderately stable"},
            {"score": 6, "min_ecr": 4.0, "max_ecr": 5.0, "description": "Fair stability"},
        ]
    
    def analyze(self, country: str, period: str, **kwargs) -> ParameterScore:
        """Analyze country stability WITH MEMORY FEATURES."""
        try:
            start_time = datetime.now()
            
            # Fetch data
            data = self._fetch_data(country, period)
            
            # Calculate score
            score = self._calculate_score(data)
            
            # Generate justification
            justification = self._generate_justification(score, data)
            
            # CREATE RESULT
            result = ParameterScore(
                parameter_name=self.parameter_name,
                score=score,
                justification=justification,
                confidence=0.95,
                timestamp=datetime.now()
            )
            
            # === MEMORY INTEGRATION (AUTOMATIC IF ENABLED) ===
            # If memory is enabled and auto_record=True, the analysis is automatically recorded
            # You can also manually use memory features:
            
            if self.memory_enabled():
                # Get similar past cases
                similar = self.get_similar_cases(country, top_k=3)
                if similar:
                    logger.info(f"Found {len(similar)} similar past analyses")
                
                # Get score suggestion from memory
                suggestion = self.suggest_score_from_memory(country, score)
                if suggestion and suggestion['confidence'] >= 0.5:
                    logger.info(f"Memory suggests score: {suggestion['suggested_score']:.2f} "
                              f"(current: {score:.2f}, confidence: {suggestion['confidence']:.1%})")
                
                # Record analysis (if auto_record=False)
                if not self._memory_auto_record:
                    exec_time = (datetime.now() - start_time).total_seconds() * 1000
                    self.record_analysis(
                        country=country,
                        period=period,
                        input_data=data,
                        output_data=result.to_dict(),
                        execution_time_ms=exec_time
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _fetch_data(self, country: str, period: str) -> Dict[str, Any]:
        """Fetch country stability data."""
        if self.mode == AgentMode.MOCK:
            return self.MOCK_DATA.get(country, {"ecr_rating": 5.0, "risk_category": "Unknown"})
        # Add real data fetching logic here
        return {}
    
    def _calculate_score(self, data: Dict[str, Any]) -> float:
        """Calculate score from data."""
        ecr_rating = data.get("ecr_rating", 5.0)
        
        # Find matching score from rubric
        for level in self.scoring_rubric:
            if level["min_ecr"] <= ecr_rating < level["max_ecr"]:
                return float(level["score"])
        
        return 5.0  # Default
    
    def _generate_justification(self, score: float, data: Dict[str, Any]) -> str:
        """Generate justification."""
        ecr = data.get("ecr_rating", 0)
        category = data.get("risk_category", "Unknown")
        
        justification = f"ECR Rating: {ecr:.1f} ({category}). "
        justification += f"Score {score:.0f}/10 based on political and economic stability indicators."
        
        return justification


# === USAGE EXAMPLE ===
if __name__ == "__main__":
    import yaml
    from src.memory import MemoryManager
    
    # 1. Initialize memory manager (ONCE at application startup)
    with open('config/memory.yaml') as f:
        memory_config = yaml.safe_load(f)
    
    memory_manager = MemoryManager(memory_config['memory'])
    
    # 2. Create agent WITH memory
    agent = CountryStabilityAgentWithMemory(
        mode=AgentMode.MOCK,
        memory_manager=memory_manager  # Pass memory manager
    )
    
    # 3. Use agent normally - memory works automatically!
    result = agent.analyze("Germany", "Q1 2024")
    print(f"Score: {result.score}")
    print(f"Justification: {result.justification}")
    
    # 4. Analysis is automatically recorded in memory
    # 5. Next analysis can reference past cases
    result2 = agent.analyze("Germany", "Q2 2024")
    
    # Agent now has access to all memory features:
    # - agent.get_similar_cases(country)
    # - agent.suggest_score_from_memory(country, score)
    # - agent.record_expert_feedback(...)
    # - agent.get_patterns_for_context(country)
