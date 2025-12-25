"""Country Stability Agent - Analyzes political and economic risk.

This agent evaluates country stability based on Euromoney Country Risk (ECR) ratings.
Lower ECR ratings indicate higher stability and lower investment risk.

ECR Rating Scale:
- 0-1: Extremely stable (minimal risk)
- 1-2: Very stable (very low risk)
- 2-3: Stable (low risk)
- 3-4: Moderately stable (moderate risk)
- 4-5: Fair stability (elevated risk)
- 5-6: Moderate instability (significant risk)
- 6-7: Unstable (high risk)
- 7-8: Very unstable (very high risk)
- 8-9: Extremely unstable (severe risk)
- 9+: Failed/fragile state (extreme risk)

Scoring Rubric (LOADED FROM CONFIG):
Score 10: ECR < 1.0    - Extremely stable
Score 9:  ECR 1.0-2.0  - Very stable
Score 8:  ECR 2.0-3.0  - Stable
Score 7:  ECR 3.0-4.0  - Moderately stable
Score 6:  ECR 4.0-5.0  - Fair stability
Score 5:  ECR 5.0-6.0  - Moderate instability
Score 4:  ECR 6.0-7.0  - Unstable
Score 3:  ECR 7.0-8.0  - Very unstable
Score 2:  ECR 8.0-9.0  - Extremely unstable
Score 1:  ECR ≥ 9.0    - Failed/fragile state

MODES:
- MOCK: Uses hardcoded test data (for testing)
- RULE_BASED: Fetches real ECR data from data service (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class CountryStabilityAgent(BaseParameterAgent):
    """Agent for analyzing country stability based on political/economic risk."""
    
    # Mock data for Phase 1 testing (ECR ratings as of 2024)
    # Lower ECR = more stable = higher score
    MOCK_DATA = {
        "Brazil": {"ecr_rating": 2.3, "risk_category": "Stable"},
        "Germany": {"ecr_rating": 0.8, "risk_category": "Extremely Stable"},
        "USA": {"ecr_rating": 1.2, "risk_category": "Very Stable"},
        "China": {"ecr_rating": 2.8, "risk_category": "Stable"},
        "India": {"ecr_rating": 3.2, "risk_category": "Moderately Stable"},
        "United Kingdom": {"ecr_rating": 1.5, "risk_category": "Very Stable"},
        "Spain": {"ecr_rating": 1.8, "risk_category": "Very Stable"},
        "Australia": {"ecr_rating": 0.9, "risk_category": "Extremely Stable"},
        "Chile": {"ecr_rating": 2.1, "risk_category": "Stable"},
        "Vietnam": {"ecr_rating": 3.8, "risk_category": "Moderately Stable"},
        "South Africa": {"ecr_rating": 4.5, "risk_category": "Fair Stability"},
        "Nigeria": {"ecr_rating": 6.2, "risk_category": "Unstable"},
        "Argentina": {"ecr_rating": 5.8, "risk_category": "Moderate Instability"},
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Country Stability Agent.
        
        Args:
            mode: Agent operation mode (MOCK or REAL)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Country Stability",
            mode=mode,
            config=config
        )
        
        # Store data service for RULE_BASED mode
        self.data_service = data_service
        
        # Validate data service if in RULE_BASED mode
        if self.mode == AgentMode.RULE_BASED and self.data_service is None:
            logger.warning(
                "RULE_BASED mode enabled but no data_service provided. "
                "Agent will fall back to MOCK data."
            )
        
        # Load scoring rubric from config (NO HARDCODING!)
        self.scoring_rubric = self._load_scoring_rubric()
        
        logger.debug(
            f"Initialized CountryStabilityAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.
        
        Returns:
            List of scoring levels with ECR thresholds
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            # Get rubric for country_stability parameter
            stability_config = params_config['parameters'].get('country_stability', {})
            scoring = stability_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_ecr": item.get('min_ecr', 0.0),
                        "max_ecr": item.get('max_ecr', 100.0),
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
        """Fallback scoring rubric if config is not available.
        
        This ensures agent works even without full config.
        
        Returns:
            Default scoring rubric
        """
        return [
            {"score": 10, "min_ecr": 0.0, "max_ecr": 1.0, "range": "< 1.0", "description": "Extremely stable (minimal risk)"},
            {"score": 9, "min_ecr": 1.0, "max_ecr": 2.0, "range": "1.0-2.0", "description": "Very stable (very low risk)"},
            {"score": 8, "min_ecr": 2.0, "max_ecr": 3.0, "range": "2.0-3.0", "description": "Stable (low risk)"},
            {"score": 7, "min_ecr": 3.0, "max_ecr": 4.0, "range": "3.0-4.0", "description": "Moderately stable (moderate risk)"},
            {"score": 6, "min_ecr": 4.0, "max_ecr": 5.0, "range": "4.0-5.0", "description": "Fair stability (elevated risk)"},
            {"score": 5, "min_ecr": 5.0, "max_ecr": 6.0, "range": "5.0-6.0", "description": "Moderate instability (significant risk)"},
            {"score": 4, "min_ecr": 6.0, "max_ecr": 7.0, "range": "6.0-7.0", "description": "Unstable (high risk)"},
            {"score": 3, "min_ecr": 7.0, "max_ecr": 8.0, "range": "7.0-8.0", "description": "Very unstable (very high risk)"},
            {"score": 2, "min_ecr": 8.0, "max_ecr": 9.0, "range": "8.0-9.0", "description": "Extremely unstable (severe risk)"},
            {"score": 1, "min_ecr": 9.0, "max_ecr": 100.0, "range": "≥ 9.0", "description": "Failed/fragile state (extreme risk)"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze country stability for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Country Stability for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # Rule-based data has higher confidence than mock data
            if self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "high"
                confidence = 0.9  # High confidence for real ECR data
            else:
                data_quality = "medium"
                confidence = 0.7  # Lower confidence for mock data
            
            confidence = self._estimate_confidence(data, data_quality)
            
            # Step 6: Identify data sources
            data_sources = self._get_data_sources(country, data)
            
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
                f"Country Stability analysis complete for {country}: "
                f"Score={score:.1f}, Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Country Stability analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Country Stability analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch country risk data.
        
        In MOCK mode: Returns mock ECR ratings
        In RULE_BASED mode: Fetches real ECR data from data service
        In RULE mode: Would query database (not yet implemented)
        In AI mode: Would use LLM to extract from documents (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with ECR rating, risk category, and source
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate risk")
                data = {"ecr_rating": 5.0, "risk_category": "Moderate Instability"}
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: ECR={data.get('ecr_rating')}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Fetch rule-based data from data service
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Try to fetch ECR rating from data service
                # Indicator name: 'ecr' (from our CSV files or future data sources)
                ecr_rating = self.data_service.get_value(
                    country=country,
                    indicator='ecr',
                    default=None
                )
                
                if ecr_rating is None:
                    logger.warning(
                        f"No real ECR data found for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Determine risk category based on ECR rating
                risk_category = self._determine_risk_category(ecr_rating)
                
                data = {
                    'ecr_rating': float(ecr_rating),
                    'risk_category': risk_category,
                    'source': 'rule_based',
                    'period': period
                }
                
                logger.info(
                    f"Fetched REAL data for {country}: ECR={ecr_rating:.1f}, "
                    f"Category={risk_category}"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error fetching rule-based data for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.RULE_BASED:
            # TODO Phase 2: Query from database
            # return self._query_risk_database(country, period)
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from documents
            # return self._llm_extract_risk(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _fetch_data_mock_fallback(self, country: str) -> Dict[str, Any]:
        """Fallback to mock data when rule-based data is unavailable.
        
        Args:
            country: Country name
            
        Returns:
            Mock data dictionary
        """
        data = self.MOCK_DATA.get(country, {
            "ecr_rating": 5.0, 
            "risk_category": "Moderate Instability"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _determine_risk_category(self, ecr_rating: float) -> str:
        """Determine risk category from ECR rating.
        
        Args:
            ecr_rating: ECR rating value
            
        Returns:
            Risk category string
        """
        # Map ECR rating to risk category using scoring rubric
        for level in self.scoring_rubric:
            min_ecr = level.get('min_ecr', 0.0)
            max_ecr = level.get('max_ecr', 100.0)
            
            if min_ecr <= ecr_rating < max_ecr:
                # Extract category from description
                description = level.get('description', '')
                # Get first part before parenthesis
                category = description.split('(')[0].strip()
                return category.title()
        
        # Fallback
        return "Unknown Risk"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate stability score based on ECR rating.
        
        Lower ECR = higher stability = higher score (inverse relationship)
        
        Args:
            data: Risk data with ecr_rating
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        ecr_rating = data.get("ecr_rating", 5.0)
        
        logger.debug(f"Calculating score for {country}: ECR {ecr_rating}")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_ecr = level.get("min_ecr", 0.0)
            max_ecr = level.get("max_ecr", 100.0)
            
            if min_ecr <= ecr_rating < max_ecr:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"ECR {ecr_rating} falls in range {min_ecr}-{max_ecr}"
                )
                return float(score)
        
        # Fallback (shouldn't reach here with proper rubric)
        logger.warning(f"No rubric match for ECR {ecr_rating}, defaulting to score 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the stability score.
        
        Args:
            data: Risk data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        ecr_rating = data.get("ecr_rating", 0.0)
        risk_category = data.get("risk_category", "Unknown")
        source = data.get("source", "unknown")
        
        # Find description from rubric
        description = "moderate risk profile"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"]
                break
        
        # Build justification
        if source == 'real':
            justification = (
                f"Based on real ECR data: rating of {ecr_rating:.1f} indicates "
                f"{risk_category.lower()}. {description.capitalize()}. "
                f"Political and economic environment supports renewable energy investments."
            )
        else:
            justification = (
                f"ECR rating of {ecr_rating:.1f} indicates {risk_category.lower()}. "
                f"{description.capitalize()}. "
                f"Political and economic environment supports renewable energy investments."
            )
        
        return justification
    
    def _get_data_sources(self, country: str, data: Dict[str, Any] = None) -> List[str]:
        """Get data sources used for this analysis.
        
        Args:
            country: Country name
            data: Data dictionary with source info
            
        Returns:
            List of data source identifiers
        """
        sources = []
        
        # Check if we used real or mock data
        if data and data.get('source') == 'rule_based':
            sources.append("Euromoney Country Risk (ECR) - Real Data")
            sources.append(f"{country} Political Risk Assessment")
        else:
            sources.append("Euromoney Country Risk (ECR) - Mock Data")
            sources.append(f"{country} Political Risk Assessment (Estimated)")
        
        sources.append("World Bank Governance Indicators 2024")
        
        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Country Stability parameter.
        
        Returns:
            Complete scoring rubric
        """
        return self.scoring_rubric
    
    def get_data_sources(self) -> List[str]:
        """Get general data sources for this parameter.
        
        Returns:
            List of typical data sources
        """
        return [
            "Euromoney Country Risk (ECR)",
            "World Bank Governance Indicators",
            "Political Risk Services (PRS) Group",
            "Economist Intelligence Unit (EIU)",
            "International Country Risk Guide (ICRG)"
        ]


# Convenience function for direct usage
def analyze_country_stability(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze country stability.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or REAL)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = CountryStabilityAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
