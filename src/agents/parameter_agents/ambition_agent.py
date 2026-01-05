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

MODES:
- MOCK: Uses hardcoded test data (for testing)
- RULE_BASED: Fetches real target data from data service (production)
- AI_POWERED: Uses LLM to extract targets from policy documents (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class AmbitionAgent(BaseParameterAgent):
    """Agent for analyzing government renewable energy ambition."""
    
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
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Ambition Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Ambition",
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
        
        # Load scoring rubric from config
        self.scoring_rubric = self._load_scoring_rubric()
        
        logger.debug(
            f"Initialized AmbitionAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.
        
        Returns:
            List of scoring levels
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            # Get rubric for ambition parameter
            ambition_config = params_config['parameters'].get('ambition', {})
            scoring = ambition_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_gw": item.get('min_gw', 0),
                        "max_gw": item.get('max_gw', 10000),
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
            {"score": 1, "min_gw": 0, "max_gw": 3, "range": "< 3 GW", "description": "Minimal renewable targets"},
            {"score": 2, "min_gw": 3, "max_gw": 5, "range": "3-5 GW", "description": "Very low targets"},
            {"score": 3, "min_gw": 5, "max_gw": 10, "range": "5-10 GW", "description": "Low targets"},
            {"score": 4, "min_gw": 10, "max_gw": 15, "range": "10-15 GW", "description": "Below moderate targets"},
            {"score": 5, "min_gw": 15, "max_gw": 20, "range": "15-20 GW", "description": "Moderate targets"},
            {"score": 6, "min_gw": 20, "max_gw": 25, "range": "20-25 GW", "description": "Above moderate targets"},
            {"score": 7, "min_gw": 25, "max_gw": 30, "range": "25-30 GW", "description": "High targets"},
            {"score": 8, "min_gw": 30, "max_gw": 35, "range": "30-35 GW", "description": "Very high targets"},
            {"score": 9, "min_gw": 35, "max_gw": 40, "range": "35-40 GW", "description": "Extremely high targets"},
            {"score": 10, "min_gw": 40, "max_gw": 10000, "range": "≥ 40 GW", "description": "World-class targets"}
        ]
    
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
            logger.info(f"Analyzing Ambition for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # Different confidence levels based on data source
            if data.get('source') == 'ai_powered':
                # Use AI extraction confidence
                data_quality = "high"
                ai_confidence = data.get('ai_confidence', 0.8)
                confidence = ai_confidence  # Use AI's confidence directly
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "high"
                confidence = 0.9  # High confidence for rule-based data
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
                f"Ambition analysis complete for {country}: "
                f"Score={score:.1f}, Confidence={confidence:.2f}, Mode={self.mode.value}"
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
        In RULE_BASED mode: Fetches real target data from data service
        In AI_POWERED mode: Would use LLM to extract from documents (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with target data (total_gw, solar, onshore_wind, offshore_wind, source)
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default minimal target")
                data = {"total_gw": 2.0, "solar": 1.0, "onshore_wind": 1.0, "offshore_wind": 0.0}
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: {data.get('total_gw')} GW total")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Fetch rule-based data from data service
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Try to fetch renewable target data from data service
                # For now, we can use GDP growth as a proxy for ambition
                # In production, you'd have specific renewable target indicators
                
                # Option 1: If you have renewable target CSV files
                # renewable_target = self.data_service.get_value(country, 'renewable_target_gw', default=None)
                
                # Option 2: Use GDP growth as proxy (countries with higher growth might have higher targets)
                gdp_growth = self.data_service.get_value(
                    country=country,
                    indicator='gdp_growth',
                    default=None
                )
                
                if gdp_growth is None:
                    logger.warning(
                        f"No rule-based data found for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate renewable targets based on GDP growth
                # This is a simplified proxy - in production you'd use actual target data
                # Higher GDP growth → higher renewable ambition (rough correlation)
                total_gw = self._estimate_targets_from_gdp_growth(country, gdp_growth)
                
                data = {
                    'total_gw': total_gw,
                    'solar': total_gw * 0.5,  # Rough breakdown
                    'onshore_wind': total_gw * 0.4,
                    'offshore_wind': total_gw * 0.1,
                    'source': 'rule_based',
                    'period': period,
                    'proxy_used': 'gdp_growth',
                    'proxy_value': gdp_growth
                }
                
                logger.info(
                    f"Fetched RULE_BASED data for {country}: Total={total_gw:.1f} GW "
                    f"(estimated from GDP growth={gdp_growth:.1f}%)"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error fetching rule-based data for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # Use AI Extraction System to extract targets from documents
            try:
                from ai_extraction_system import AIExtractionAdapter

                logger.info(f"Using AI_POWERED mode for {country}")

                # Initialize AI extraction adapter
                adapter = AIExtractionAdapter(
                    llm_config=self.config.get('llm_config') if self.config else None,
                    cache_config=self.config.get('cache_config') if self.config else None
                )

                # Extract renewable targets using AI
                extraction_result = adapter.extract_parameter(
                    parameter_name='ambition',
                    country=country,
                    period=period,
                    documents=kwargs.get('documents'),
                    document_urls=kwargs.get('document_urls')
                )

                # Convert AI extraction result to agent data format
                # AI extraction returns percentage or absolute target
                # We need to convert to GW format for scoring
                if extraction_result and extraction_result.get('value'):
                    value = extraction_result['value']

                    # If value is percentage (e.g., 80%), convert to estimated GW
                    # For now, use a simplified conversion based on country context
                    if isinstance(value, (int, float)):
                        # Assume it's a percentage target (e.g., 80% renewable by 2030)
                        # Convert to GW estimate based on typical country capacity
                        # This is a simplification - ideally AI would extract GW directly
                        total_gw = self._convert_percentage_to_gw(country, value)
                    else:
                        # Try to parse as numeric
                        try:
                            total_gw = float(value)
                        except (ValueError, TypeError):
                            logger.warning(f"Could not parse AI value: {value}, falling back")
                            return self._fetch_data_mock_fallback(country)

                    data = {
                        'total_gw': total_gw,
                        'solar': total_gw * 0.5,  # Rough breakdown
                        'onshore_wind': total_gw * 0.4,
                        'offshore_wind': total_gw * 0.1,
                        'source': 'ai_powered',
                        'period': period,
                        'ai_confidence': extraction_result.get('confidence', 0.0),
                        'ai_justification': extraction_result.get('justification', ''),
                        'extraction_metadata': extraction_result.get('metadata', {})
                    }

                    logger.info(
                        f"AI extraction successful for {country}: {total_gw:.1f} GW "
                        f"(confidence: {extraction_result.get('confidence', 0.0):.2f})"
                    )

                    return data
                else:
                    logger.warning(f"AI extraction returned no value for {country}, falling back")
                    return self._fetch_data_mock_fallback(country)

            except ImportError as e:
                logger.error(f"AI extraction system not available: {e}")
                logger.info("Falling back to RULE_BASED mode")
                # Try RULE_BASED as fallback
                self.mode = AgentMode.RULE_BASED
                return self._fetch_data(country, period, **kwargs)

            except Exception as e:
                logger.error(f"AI extraction failed for {country}: {e}")
                logger.info("Falling back to RULE_BASED mode")
                # Try RULE_BASED as fallback
                self.mode = AgentMode.RULE_BASED
                return self._fetch_data(country, period, **kwargs)
        
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
            "total_gw": 2.0, 
            "solar": 1.0, 
            "onshore_wind": 1.0, 
            "offshore_wind": 0.0
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_targets_from_gdp_growth(self, country: str, gdp_growth: float) -> float:
        """Estimate renewable targets from GDP growth (temporary proxy).
        
        This is a simplified estimation. In production, you would:
        1. Have actual renewable target data in CSV files
        2. Or use multiple economic indicators
        3. Or use historical renewable capacity trends
        
        Args:
            country: Country name
            gdp_growth: GDP growth rate (%)
            
        Returns:
            Estimated total renewable target in GW
        """
        # Get base from mock data if available
        base_data = self.MOCK_DATA.get(country)
        if base_data:
            base_gw = base_data.get('total_gw', 20.0)
        else:
            base_gw = 20.0  # Default baseline
        
        # Adjust based on GDP growth
        # Positive growth → increase targets, negative growth → decrease targets
        # This is a rough heuristic - replace with actual data in production
        adjustment_factor = 1.0 + (gdp_growth / 10.0)  # ±10% growth changes targets by ±100%
        adjustment_factor = max(0.5, min(2.0, adjustment_factor))  # Cap at 0.5x to 2x
        
        estimated_gw = base_gw * adjustment_factor
        
        logger.debug(
            f"Estimated {country} targets: {estimated_gw:.1f} GW "
            f"(base={base_gw:.1f}, growth={gdp_growth:.1f}%, factor={adjustment_factor:.2f})"
        )
        
        return estimated_gw

    def _convert_percentage_to_gw(self, country: str, percentage: float) -> float:
        """Convert renewable percentage target to GW capacity estimate.

        This is a simplified conversion. In production, you would:
        1. Have actual GW targets extracted from documents
        2. Use country-specific conversion factors
        3. Consider total electricity capacity

        Args:
            country: Country name
            percentage: Renewable percentage target (e.g., 80 for 80%)

        Returns:
            Estimated capacity in GW
        """
        # Use mock data as baseline for conversion if available
        base_data = self.MOCK_DATA.get(country)
        if base_data:
            # Assume mock data represents 100% scenario
            # Scale down based on percentage
            reference_gw = base_data.get('total_gw', 50.0)
            # If percentage is close to 100%, use reference value
            # Otherwise scale proportionally
            estimated_gw = reference_gw * (percentage / 100.0)
        else:
            # Default conversion: assume typical country capacity
            # 80% renewable = ~40 GW for medium country
            # This is very rough - replace with actual data
            estimated_gw = (percentage / 80.0) * 40.0

        logger.debug(
            f"Converted {percentage}% target to {estimated_gw:.1f} GW for {country}"
        )

        return estimated_gw

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
        
        logger.debug(f"Calculating score for {country}: {total_gw:.1f} GW")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_gw = level.get("min_gw", 0)
            max_gw = level.get("max_gw", float('inf'))
            
            if min_gw <= total_gw < max_gw:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{total_gw:.1f} GW falls in range {min_gw}-{max_gw} GW"
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
        source = data.get("source", "unknown")
        
        # Find description from rubric
        description = "renewable targets"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"]
                break
        
        # Build justification based on source
        if source == 'ai_powered':
            # Use AI-generated justification if available
            ai_justification = data.get('ai_justification', '')
            if ai_justification:
                justification = (
                    f"Based on AI-powered document analysis: {ai_justification} "
                    f"Estimated capacity: {total_gw:.1f} GW targeted by 2030. "
                    f"{description.capitalize()}."
                )
            else:
                justification = (
                    f"Based on AI-powered document analysis: {total_gw:.1f} GW of renewable capacity "
                    f"targeted by 2030. {description.capitalize()}."
                )
        elif source == 'rule_based':
            proxy = data.get('proxy_used', '')
            if proxy:
                justification = (
                    f"Based on rule-based analysis: {total_gw:.1f} GW of renewable capacity "
                    f"targeted by 2030 "
                    f"(solar PV: {solar:.1f} GW, onshore wind: {onshore:.1f} GW, "
                    f"offshore wind: {offshore:.1f} GW). "
                    f"{description.capitalize()}."
                )
            else:
                justification = (
                    f"Based on rule-based data: {total_gw:.1f} GW of renewable capacity "
                    f"targeted by 2030. {description.capitalize()}."
                )
        else:
            justification = (
                f"{total_gw:.1f} GW of renewable capacity targeted by 2030 "
                f"(solar PV: {solar:.1f} GW, onshore wind: {onshore:.1f} GW, "
                f"offshore wind: {offshore:.1f} GW). "
                f"{description.capitalize()}."
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

        # Check data source type
        if data and data.get('source') == 'ai_powered':
            sources.append("AI-Powered Document Analysis")
            sources.append(f"{country} Policy Documents & NDC Submissions")
            # Add metadata about AI confidence if available
            ai_confidence = data.get('ai_confidence')
            if ai_confidence:
                sources.append(f"AI Confidence: {ai_confidence:.1%}")
        elif data and data.get('source') == 'rule_based':
            sources.append(f"{country} NDC 2024 - Rule-Based Data")
            sources.append("IRENA Renewable Capacity Statistics 2024")
            if data.get('proxy_used'):
                sources.append(f"World Bank {data['proxy_used']} (proxy indicator)")
        else:
            sources.append(f"{country} NDC 2024 - Mock Data")
            sources.append("IRENA Renewable Capacity Statistics 2024 (Estimated)")

        sources.append(f"{country} Ministry of Energy Official Targets")

        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Ambition parameter.
        
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
            "Government NDCs (Nationally Determined Contributions)",
            "Ministry of Energy publications",
            "IRENA country profiles",
            "IEA renewable energy policies database"
        ]


# Convenience function for direct usage
def analyze_ambition(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze ambition for a country.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = AmbitionAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
