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

MODES:
- MOCK: Uses hardcoded foreign ownership assessments (for testing)
- RULE_BASED: Estimates from World Bank FDI indicators + economic freedom (production)
"""
from typing import Dict, Any, List, Optional
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
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Ownership Hurdles Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Ownership Hurdles",
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
            f"Initialized OwnershipHurdlesAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
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
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze ownership hurdles for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Ownership Hurdles for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)

            # Step 5: Estimate confidence
            if data.get('source') == 'ai_powered':
                # Use AI-provided confidence
                confidence = data.get('ai_confidence', 0.75)
                data_quality = "high"
                logger.debug(f"Using AI-provided confidence: {confidence:.2f}")
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.65  # Lower confidence for estimated data
            else:
                data_quality = "high"
                confidence = 0.85  # High confidence for known regulations

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
                f"Ownership Hurdles analysis complete for {country}: "
                f"Score={score:.1f}, ForeignOwnership={data.get('foreign_ownership_pct', 0)}%, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ownership Hurdles analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Ownership Hurdles analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch ownership hurdles data.
        
        In MOCK mode: Returns mock foreign ownership assessments
        In RULE_BASED mode: Estimates from World Bank FDI + economic freedom indicators
        In AI_POWERED mode: Would use LLM to extract from investment laws (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with ownership data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
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
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: foreign_ownership={data.get('foreign_ownership_pct')}%")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate from World Bank FDI indicators
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch FDI net inflows (% of GDP)
                fdi_inflows_pct = self.data_service.get_value(
                    country=country,
                    indicator='fdi_net_inflows',
                    default=None
                )
                
                # Fetch GDP per capita (development level)
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch trade openness
                trade_pct_gdp = self.data_service.get_value(
                    country=country,
                    indicator='trade',
                    default=None
                )
                
                if fdi_inflows_pct is None or gdp_per_capita is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate ownership openness
                foreign_ownership_pct, category = self._estimate_ownership_openness(
                    country,
                    fdi_inflows_pct,
                    gdp_per_capita,
                    trade_pct_gdp
                )
                
                # Estimate other characteristics
                approval = self._determine_approval_complexity(category, gdp_per_capita)
                local_content = self._determine_local_content_requirements(category)
                screening = self._determine_investment_screening(category, gdp_per_capita)
                status = self._determine_ownership_status(category, foreign_ownership_pct)
                
                data = {
                    'foreign_ownership_pct': foreign_ownership_pct,
                    'category': category,
                    'approval_complexity': approval,
                    'local_content_requirements': local_content,
                    'investment_screening': screening,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_fdi_inflows_pct': fdi_inflows_pct,
                    'raw_gdp_per_capita': gdp_per_capita
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: {foreign_ownership_pct}% "
                    f"({category}) from FDI={fdi_inflows_pct:.1f}% GDP, GDP/capita=${gdp_per_capita:,.0f}"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating ownership openness for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # AI-powered extraction using OwnershipHurdlesExtractor
            try:
                from ai_extraction_system import AIExtractionAdapter

                # Get documents from kwargs
                documents = kwargs.get('documents', [])
                if not documents:
                    logger.warning(f"No documents provided for AI extraction, falling back to MOCK mode")
                    return self._fetch_data_mock_fallback(country)

                # Use AI extraction adapter
                adapter = AIExtractionAdapter()
                result = adapter.extract_parameter(
                    parameter_name='ownership_hurdles',
                    country=country,
                    period=period,
                    documents=documents
                )

                if result['success']:
                    # Extract AI data
                    ai_data = result['data']

                    # Return in expected format
                    return {
                        'ai_score': ai_data['value'],
                        'ai_confidence': ai_data['confidence'],
                        'ai_justification': ai_data['justification'],
                        'ai_metadata': ai_data.get('metadata', {}),
                        'ai_quotes': ai_data.get('quotes', []),
                        'source': 'ai_powered',
                        'period': period,
                        'score': ai_data['value'],  # Use AI score directly
                        'foreign_ownership_pct': ai_data.get('metadata', {}).get('foreign_ownership_pct', 100),
                        'category': self._determine_category_from_pct(ai_data.get('metadata', {}).get('foreign_ownership_pct', 100)),
                        'approval_complexity': ai_data.get('metadata', {}).get('approval_complexity', 'Standard'),
                        'local_content_requirements': ai_data.get('metadata', {}).get('local_content_req', 'Minimal'),
                        'investment_screening': ai_data.get('metadata', {}).get('investment_screening', 'Limited'),
                        'status': ai_data.get('metadata', {}).get('status', 'Foreign ownership analysis'),
                    }
                else:
                    logger.error(f"AI extraction failed: {result['error']}, falling back to MOCK")
                    return self._fetch_data_mock_fallback(country)

            except Exception as e:
                logger.error(f"AI_POWERED mode error: {e}, falling back to MOCK mode")
                return self._fetch_data_mock_fallback(country)
        
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
            "foreign_ownership_pct": 70,
            "category": "below_moderate_barriers",
            "approval_complexity": "Moderate",
            "local_content_requirements": "Some",
            "investment_screening": "Moderate",
            "status": "Below moderate barriers"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_ownership_openness(
        self,
        country: str,
        fdi_inflows_pct: float,
        gdp_per_capita: float,
        trade_pct_gdp: Optional[float]
    ) -> tuple:
        """Estimate foreign ownership openness from World Bank indicators.
        
        Higher FDI inflows + higher development = More open to foreign investment
        
        Args:
            country: Country name
            fdi_inflows_pct: FDI net inflows (% of GDP)
            gdp_per_capita: GDP per capita in current USD
            trade_pct_gdp: Trade (% of GDP) - openness indicator
            
        Returns:
            Tuple of (foreign_ownership_pct, category)
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Start with FDI openness score
        # Higher FDI suggests fewer restrictions
        if fdi_inflows_pct >= 5.0:
            # Very high FDI (Chile, Vietnam)
            fdi_score = 90
        elif fdi_inflows_pct >= 3.0:
            # High FDI
            fdi_score = 80
        elif fdi_inflows_pct >= 2.0:
            # Moderate-high FDI
            fdi_score = 70
        elif fdi_inflows_pct >= 1.0:
            # Moderate FDI
            fdi_score = 60
        elif fdi_inflows_pct >= 0.5:
            # Low-moderate FDI
            fdi_score = 50
        else:
            # Low FDI (may indicate restrictions or instability)
            fdi_score = 40
        
        # Adjust based on development level
        # High-income countries tend to be more open (OECD, EU)
        if gdp_per_capita >= 40000:
            # High income (Germany, UK, USA, Australia)
            gdp_adjustment = +15
        elif gdp_per_capita >= 15000:
            # Upper middle income (Brazil, China)
            gdp_adjustment = +5
        elif gdp_per_capita >= 5000:
            # Lower middle income (India, Vietnam)
            gdp_adjustment = 0
        else:
            # Low income (Nigeria)
            gdp_adjustment = -10
        
        # Adjust based on trade openness (if available)
        trade_adjustment = 0
        if trade_pct_gdp is not None:
            if trade_pct_gdp >= 100:  # Very open (Singapore, Hong Kong)
                trade_adjustment = +5
            elif trade_pct_gdp >= 60:  # Open
                trade_adjustment = +3
            elif trade_pct_gdp < 30:  # Closed
                trade_adjustment = -5
        
        # Calculate estimated ownership percentage
        foreign_ownership_pct = fdi_score + gdp_adjustment + trade_adjustment
        
        # Calibrate with mock data if available (50/50 blend - less confident)
        if base_data:
            base_pct = base_data.get('foreign_ownership_pct', foreign_ownership_pct)
            foreign_ownership_pct = foreign_ownership_pct * 0.5 + base_pct * 0.5
        
        # Clamp to valid range
        foreign_ownership_pct = max(10, min(foreign_ownership_pct, 100))
        
        # Determine category from percentage
        category = self._determine_category_from_pct(foreign_ownership_pct)
        
        logger.debug(
            f"Ownership estimation for {country}: "
            f"FDI={fdi_inflows_pct:.1f}% → fdi_score={fdi_score}, "
            f"GDP/capita=${gdp_per_capita:,.0f} → adj={gdp_adjustment:+d}, "
            f"final_pct={foreign_ownership_pct:.0f}% ({category})"
        )
        
        return foreign_ownership_pct, category
    
    def _determine_category_from_pct(self, ownership_pct: float) -> str:
        """Determine category from foreign ownership percentage."""
        if ownership_pct >= 100:
            return "no_barriers"
        elif ownership_pct >= 95:
            return "minimal_barriers"
        elif ownership_pct >= 85:
            return "very_low_barriers"
        elif ownership_pct >= 75:
            return "low_barriers"
        elif ownership_pct >= 65:
            return "below_moderate_barriers"
        elif ownership_pct >= 50:
            return "moderate_barriers"
        elif ownership_pct >= 40:
            return "above_moderate_barriers"
        elif ownership_pct >= 25:
            return "high_barriers"
        elif ownership_pct >= 10:
            return "very_high_barriers"
        else:
            return "prohibitive"
    
    def _determine_approval_complexity(self, category: str, gdp_per_capita: float) -> str:
        """Determine approval process complexity."""
        if category in ["no_barriers", "minimal_barriers"]:
            return "Standard" if gdp_per_capita >= 40000 else "Moderate"
        elif category in ["very_low_barriers", "low_barriers"]:
            return "Moderate"
        elif category in ["below_moderate_barriers", "moderate_barriers"]:
            return "Moderate to High"
        else:
            return "High to Very High"
    
    def _determine_local_content_requirements(self, category: str) -> str:
        """Determine local content requirement level."""
        if category in ["no_barriers", "minimal_barriers"]:
            return "None to Minimal"
        elif category in ["very_low_barriers", "low_barriers"]:
            return "Limited"
        elif category in ["below_moderate_barriers", "moderate_barriers"]:
            return "Moderate"
        else:
            return "Significant to Extensive"
    
    def _determine_investment_screening(self, category: str, gdp_per_capita: float) -> str:
        """Determine investment screening level."""
        if category in ["no_barriers", "minimal_barriers"]:
            return "Limited" if gdp_per_capita >= 40000 else "Moderate"
        elif category in ["very_low_barriers", "low_barriers"]:
            return "Moderate"
        elif category in ["below_moderate_barriers", "moderate_barriers"]:
            return "Moderate to Extensive"
        else:
            return "Extensive"
    
    def _determine_ownership_status(self, category: str, ownership_pct: float) -> str:
        """Determine ownership status description."""
        if ownership_pct >= 100:
            return "Full foreign ownership allowed (no restrictions)"
        elif ownership_pct >= 95:
            return f"Minimal barriers ({ownership_pct:.0f}% foreign ownership allowed)"
        elif ownership_pct >= 75:
            return f"Low barriers ({ownership_pct:.0f}% foreign ownership)"
        elif ownership_pct >= 50:
            return f"Moderate barriers ({ownership_pct:.0f}% foreign ownership cap)"
        else:
            return f"Significant barriers ({ownership_pct:.0f}% foreign ownership limit)"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate ownership hurdles score.
        
        CATEGORICAL: Category determines score
        Lower barriers = better market access = higher score
        
        Args:
            data: Ownership data with category
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        category = data.get("category", "moderate_barriers")
        
        logger.debug(f"Calculating score for {country}: category={category}")
        
        # Get score from category mapping
        score = self.CATEGORY_SCORES.get(category, 5)
        
        logger.debug(f"Score {score} assigned for category {category}")
        
        return float(score)
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the ownership hurdles score.

        Args:
            data: Ownership data
            score: Calculated score
            country: Country name
            period: Time period

        Returns:
            Human-readable justification string
        """
        source = data.get("source", "unknown")

        # If AI_POWERED mode, use AI-generated justification
        if source == 'ai_powered':
            return data.get('ai_justification', 'AI analysis of foreign ownership restrictions.')

        foreign_pct = data.get("foreign_ownership_pct", 0)
        category = data.get("category", "moderate_barriers")
        approval = data.get("approval_complexity", "moderate")
        local_content = data.get("local_content_requirements", "some")
        screening = data.get("investment_screening", "moderate")
        status = data.get("status", "moderate barriers")

        # Find description from rubric
        description = "moderate barriers"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break

        # Build justification based on source
        if source == 'rule_based':
            fdi = data.get('raw_fdi_inflows_pct', 0)
            gdp = data.get('raw_gdp_per_capita', 0)
            justification = (
                f"Based on World Bank data: Estimated foreign ownership limit of {foreign_pct:.0f}% "
                f"(derived from FDI inflows {fdi:.1f}% of GDP and GDP/capita ${gdp:,.0f}) "
                f"indicates {description}. {status}. "
            )
        else:
            # Mock data - use detailed regulations
            justification = (
                f"Foreign ownership limit of {foreign_pct:.0f}% indicates {description}. "
                f"Approval process complexity is {approval.lower()} with {local_content.lower()} "
                f"local content requirements. Investment screening is {screening.lower()}. "
                f"{status}. "
            )
        
        justification += (
            f"This regulatory environment {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports international investment and market participation."
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

        # Check if we used AI extraction
        if data and data.get('source') == 'ai_powered':
            sources.append("AI-Powered Document Extraction")
            sources.append("OECD FDI Index (Extracted from documents)")
            sources.append("World Bank Doing Business reports (Extracted from documents)")
            sources.append(f"{country} National energy laws")
            sources.append("Investment treaties and bilateral agreements")
            # Add document sources if available
            ai_metadata = data.get('ai_metadata', {})
            doc_sources = ai_metadata.get('document_sources', [])
            sources.extend(doc_sources)
        # Check if we used rule-based or mock data
        elif data and data.get('source') == 'rule_based':
            sources.append("World Bank FDI Net Inflows - Rule-Based Estimation")
            sources.append("OECD FDI Index (Reference)")
            sources.append(f"{country} National energy laws")
            sources.append("Investment treaties and bilateral agreements")
        else:
            sources.append("OECD FDI Regulatory Restrictiveness Index - Mock Data")
            sources.append("World Bank Doing Business reports")
            sources.append(f"{country} National energy laws")
            sources.append("Investment treaties and bilateral agreements")

        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Ownership Hurdles parameter.
        
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
            "OECD FDI Regulatory Restrictiveness Index",
            "World Bank Doing Business reports",
            "National energy laws and regulations",
            "Investment treaties and bilateral agreements",
            "Regulatory guidance documents"
        ]


def analyze_ownership_hurdles(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze ownership hurdles.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = OwnershipHurdlesAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
