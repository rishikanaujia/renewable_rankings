"""Energy Dependence Agent - Analyzes energy import dependency.

This agent evaluates energy security by measuring the percentage of primary energy
that must be imported. Lower import dependency indicates greater energy independence
and more favorable conditions for domestic renewable energy development.

Import Dependency Scale:
- < 10%: Energy independent (net exporter or minimal imports)
- 10-20%: Very low dependence
- 20-30%: Low dependence
- 30-40%: Moderate-low dependence
- 40-50%: Moderate dependence
- 50-60%: Moderate-high dependence
- 60-70%: High dependence
- 70-80%: Very high dependence
- 80-90%: Extreme dependence
- ≥ 90%: Nearly total dependence (energy security risk)

Scoring Rubric (LOADED FROM CONFIG):
Lower imports = Better energy security = Higher score (INVERSE relationship)
"""
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class EnergyDependenceAgent(BaseParameterAgent):
    """Agent for analyzing energy import dependency and energy security."""
    
    # Mock data for Phase 1 testing
    # Import dependency % = (Energy imports / Total primary energy consumption) × 100
    # Data sourced from IEA World Energy Balances 2023
    MOCK_DATA = {
        "Brazil": {
            "import_pct": 8.5,  # Net energy exporter (oil, biofuels)
            "production_mtoe": 305,
            "consumption_mtoe": 333,
            "status": "Near energy independent"
        },
        "Germany": {
            "import_pct": 63.5,  # High dependence on gas/oil imports
            "production_mtoe": 112,
            "consumption_mtoe": 307,
            "status": "High import dependence"
        },
        "USA": {
            "import_pct": 3.2,  # Energy independent since 2019 (shale revolution)
            "production_mtoe": 2425,
            "consumption_mtoe": 2501,
            "status": "Energy independent"
        },
        "China": {
            "import_pct": 22.5,  # Low-moderate dependence (domestic coal, growing imports)
            "production_mtoe": 2785,
            "consumption_mtoe": 3596,
            "status": "Low import dependence"
        },
        "India": {
            "import_pct": 38.2,  # Moderate-low dependence (domestic coal, oil imports)
            "production_mtoe": 651,
            "consumption_mtoe": 1053,
            "status": "Moderate-low dependence"
        },
        "UK": {
            "import_pct": 36.8,  # Moderate-low (North Sea declining)
            "production_mtoe": 101,
            "consumption_mtoe": 160,
            "status": "Moderate-low dependence"
        },
        "Spain": {
            "import_pct": 72.5,  # Very high dependence (limited domestic resources)
            "production_mtoe": 32,
            "consumption_mtoe": 116,
            "status": "Very high dependence"
        },
        "Australia": {
            "import_pct": -145.0,  # Huge net exporter (coal, LNG)
            "production_mtoe": 347,
            "consumption_mtoe": 142,
            "status": "Major energy exporter"
        },
        "Chile": {
            "import_pct": 68.5,  # High dependence (limited domestic fossil fuels)
            "production_mtoe": 11,
            "consumption_mtoe": 35,
            "status": "High import dependence"
        },
        "Vietnam": {
            "import_pct": 15.5,  # Very low dependence (domestic coal, growing imports)
            "production_mtoe": 72,
            "consumption_mtoe": 85,
            "status": "Very low dependence"
        },
        "South Africa": {
            "import_pct": -32.0,  # Net exporter (coal)
            "production_mtoe": 168,
            "consumption_mtoe": 127,
            "status": "Energy exporter"
        },
        "Nigeria": {
            "import_pct": -85.0,  # Major oil/gas exporter
            "production_mtoe": 246,
            "consumption_mtoe": 133,
            "status": "Major energy exporter"
        },
        "Argentina": {
            "import_pct": 12.5,  # Very low dependence (shale oil/gas, Vaca Muerta)
            "production_mtoe": 79,
            "consumption_mtoe": 90,
            "status": "Very low dependence"
        },
        "Mexico": {
            "import_pct": 25.8,  # Low dependence (oil production declining)
            "production_mtoe": 134,
            "consumption_mtoe": 181,
            "status": "Low dependence"
        },
        "Indonesia": {
            "import_pct": 18.5,  # Very low dependence (coal, becoming net importer)
            "production_mtoe": 456,
            "consumption_mtoe": 560,
            "status": "Very low dependence"
        },
    }
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Energy Dependence Agent."""
        super().__init__(
            parameter_name="Energy Dependence",
            mode=mode,
            config=config
        )
        
        # Load scoring rubric from config (NO HARDCODING!)
        self.scoring_rubric = self._load_scoring_rubric()
        
        logger.debug(f"Loaded scoring rubric with {len(self.scoring_rubric)} levels")
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration.
        
        Returns:
            List of scoring levels with import % thresholds
        """
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            # Get rubric for energy_dependence parameter
            dependence_config = params_config['parameters'].get('energy_dependence', {})
            scoring = dependence_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                # Convert config format to internal format
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_import_pct": item.get('min_import_pct', 0.0),
                        "max_import_pct": item.get('max_import_pct', 100.0),
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
            {"score": 10, "min_import_pct": 0.0, "max_import_pct": 10.0, "range": "< 10%", "description": "Energy independent (net exporter or minimal imports)"},
            {"score": 9, "min_import_pct": 10.0, "max_import_pct": 20.0, "range": "10-20%", "description": "Very low dependence"},
            {"score": 8, "min_import_pct": 20.0, "max_import_pct": 30.0, "range": "20-30%", "description": "Low dependence"},
            {"score": 7, "min_import_pct": 30.0, "max_import_pct": 40.0, "range": "30-40%", "description": "Moderate-low dependence"},
            {"score": 6, "min_import_pct": 40.0, "max_import_pct": 50.0, "range": "40-50%", "description": "Moderate dependence"},
            {"score": 5, "min_import_pct": 50.0, "max_import_pct": 60.0, "range": "50-60%", "description": "Moderate-high dependence"},
            {"score": 4, "min_import_pct": 60.0, "max_import_pct": 70.0, "range": "60-70%", "description": "High dependence"},
            {"score": 3, "min_import_pct": 70.0, "max_import_pct": 80.0, "range": "70-80%", "description": "Very high dependence"},
            {"score": 2, "min_import_pct": 80.0, "max_import_pct": 90.0, "range": "80-90%", "description": "Extreme dependence"},
            {"score": 1, "min_import_pct": 90.0, "max_import_pct": 100.0, "range": "≥ 90%", "description": "Nearly total dependence (energy security risk)"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze energy dependence for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Energy Dependence for {country} ({period})")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # IEA energy balance data is official and reliable
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
                f"Energy Dependence analysis complete for {country}: "
                f"Score={score}, Import%={data.get('import_pct', 0):.1f}, Confidence={confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Energy Dependence analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Energy Dependence analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch energy import dependency data.
        
        In MOCK mode: Returns mock import % data
        In RULE mode: Would query energy database
        In AI mode: Would use LLM to extract from IEA reports
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with import dependency data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate dependence")
                data = {
                    "import_pct": 45.0,
                    "production_mtoe": 100,
                    "consumption_mtoe": 182,
                    "status": "Moderate dependence"
                }
            
            logger.debug(f"Fetched mock data for {country}: {data}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # TODO Phase 2: Query from energy database
            # return self._query_energy_database(country, period)
            raise NotImplementedError("RULE_BASED mode not yet implemented")
        
        elif self.mode == AgentMode.AI_POWERED:
            # TODO Phase 2+: Use LLM to extract from IEA reports
            # return self._llm_extract_dependence(country, period)
            raise NotImplementedError("AI_POWERED mode not yet implemented")
        
        else:
            raise AgentError(f"Unknown agent mode: {self.mode}")
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate energy dependence score based on import %.
        
        INVERSE: Lower import % = better energy security = higher score
        
        Special handling for net exporters (negative import %):
        - Negative % treated as 0% (maximum score)
        
        Args:
            data: Import dependency data with import_pct
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        import_pct = data.get("import_pct", 0)
        
        # Handle net exporters (negative import %)
        if import_pct < 0:
            logger.debug(f"{country} is net energy exporter ({import_pct:.1f}%), assigning max score")
            return 10.0
        
        logger.debug(f"Calculating score for {country}: {import_pct:.1f}% import dependency")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_pct = level.get("min_import_pct", 0.0)
            max_pct = level.get("max_import_pct", 100.0)
            
            if min_pct <= import_pct < max_pct:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{import_pct:.1f}% falls in range {min_pct:.0f}-{max_pct:.0f}%"
                )
                return float(score)
        
        # Fallback (shouldn't reach here with proper rubric)
        logger.warning(f"No rubric match for {import_pct:.1f}%, defaulting to score 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the energy dependence score.
        
        Args:
            data: Import dependency data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        import_pct = data.get("import_pct", 0)
        production = data.get("production_mtoe", 0)
        consumption = data.get("consumption_mtoe", 0)
        status = data.get("status", "moderate dependence")
        
        # Find description from rubric
        description = "moderate energy dependence"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification with context
        if import_pct < 0:
            # Net exporter
            export_pct = abs(import_pct)
            justification = (
                f"Net energy exporter with production of {production:.0f} Mtoe exceeding "
                f"consumption of {consumption:.0f} Mtoe by {export_pct:.1f}%. "
                f"{status} provides strong foundation for renewable energy investment "
                f"and excellent energy security."
            )
        elif import_pct < 10:
            # Energy independent
            justification = (
                f"Import dependency of {import_pct:.1f}% indicates {description}. "
                f"Domestic production of {production:.0f} Mtoe meets {100-import_pct:.1f}% "
                f"of {consumption:.0f} Mtoe consumption, providing strong energy security "
                f"and favorable conditions for renewable development."
            )
        else:
            # Import dependent
            justification = (
                f"Import dependency of {import_pct:.1f}% indicates {description}. "
                f"Domestic production of {production:.0f} Mtoe covers {100-import_pct:.1f}% "
                f"of {consumption:.0f} Mtoe consumption. Renewable energy development can "
                f"improve energy security and reduce import reliance."
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
            "IEA World Energy Balances 2023",
            "BP Statistical Review of World Energy 2023",
            f"{country} National Energy Statistics"
        ]
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Energy Dependence parameter.
        
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
            "IEA World Energy Balances",
            "BP Statistical Review of World Energy",
            "National energy statistics agencies",
            "Energy Information Administration (EIA)",
            "Eurostat Energy Statistics"
        ]


# Convenience function for direct usage
def analyze_energy_dependence(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK
) -> ParameterScore:
    """Convenience function to analyze energy dependence.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode
        
    Returns:
        ParameterScore
    """
    agent = EnergyDependenceAgent(mode=mode)
    return agent.analyze(country, period)
