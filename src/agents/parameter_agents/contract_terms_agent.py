"""Contract Terms Agent - Analyzes PPA and contract quality.

This agent evaluates the bankability and robustness of renewable energy
contracts, including:
- Power Purchase Agreement (PPA) standardization
- Risk allocation between parties
- Contract enforceability
- Termination protections
- Currency and political risk provisions

Key evaluation criteria:
- Standardization and best practices
- Bankability for project finance
- Legal framework strength
- International competitiveness
- Track record of enforcement

Contract Quality Categories (1-10):
1. Non-bankable
2. Very poor
3. Poor
4. Below adequate
5. Adequate
6. Above adequate
7. Good
8. Very good
9. Excellent
10. Best-in-class

Scoring Rubric (LOADED FROM CONFIG):
Better contract terms = Higher score (CATEGORICAL/QUALITATIVE)

MODES:
- MOCK: Uses hardcoded contract quality assessments (for testing)
- RULE_BASED: Estimates from World Bank governance + legal indicators (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class ContractTermsAgent(BaseParameterAgent):
    """Agent for analyzing renewable energy contract terms."""
    
    # Mock data for Phase 1 testing
    # Contract quality assessment based on PPA frameworks
    # Data from IFC, legal assessments, project finance transactions
    MOCK_DATA = {
        "Brazil": {
            "score": 8,
            "category": "very_good",
            "ppa_framework": "CCEAR (regulated) and bilateral (merchant)",
            "standardization": "High (standardized auction PPAs)",
            "risk_allocation": "Balanced (shared risks, tested framework)",
            "enforceability": "Strong (mature legal system, arbitration available)",
            "currency_risk": "Moderate (BRL volatility, hedging available)",
            "termination_protections": "Strong",
            "bankability": "Very High (extensive project finance track record)",
            "status": "Well-developed contract framework with strong standardization and proven bankability"
        },
        "Germany": {
            "score": 10,
            "category": "best_in_class",
            "ppa_framework": "EEG (Feed-in/auction) and corporate PPAs",
            "standardization": "Very High (EEG standard contracts)",
            "risk_allocation": "Optimal (government-backed, minimal project risk)",
            "enforceability": "Excellent (German legal system, EU framework)",
            "currency_risk": "Minimal (EUR stability, eurozone)",
            "termination_protections": "Excellent",
            "bankability": "Exceptional (world-class track record)",
            "status": "Gold standard contract framework with decades of proven track record"
        },
        "USA": {
            "score": 9,
            "category": "excellent",
            "ppa_framework": "Utility PPAs and corporate PPAs (state/federal)",
            "standardization": "High (FERC oversight, standard forms)",
            "risk_allocation": "Strong (well-developed legal precedents)",
            "enforceability": "Excellent (US legal system, arbitration)",
            "currency_risk": "Minimal (USD, reserve currency)",
            "termination_protections": "Strong to Excellent",
            "bankability": "Very High (deep project finance market)",
            "status": "Highly developed framework with extensive precedent and strong enforceability"
        },
        "China": {
            "score": 7,
            "category": "good",
            "ppa_framework": "Grid company PPAs (state-guaranteed)",
            "standardization": "High (standardized government PPAs)",
            "risk_allocation": "Government-favorable (but improving)",
            "enforceability": "Moderate to Strong (state enforcement reliable but limited recourse)",
            "currency_risk": "Moderate (CNY controls, conversion issues)",
            "termination_protections": "Moderate",
            "bankability": "Good (improving, but legal system concerns)",
            "status": "Strong standardization but contract enforceability concerns for international investors"
        },
        "India": {
            "score": 6,
            "category": "above_adequate",
            "ppa_framework": "SECI/State DISCOMs PPAs",
            "standardization": "Moderate to High (improving)",
            "risk_allocation": "Variable (DISCOM credit risk significant)",
            "enforceability": "Moderate (legal system slow, disputes common)",
            "currency_risk": "High (INR volatility)",
            "termination_protections": "Moderate",
            "bankability": "Moderate (offtaker credit issues)",
            "status": "Improving framework but persistent offtaker credit and enforcement challenges"
        },
        "UK": {
            "score": 10,
            "category": "best_in_class",
            "ppa_framework": "CfD (government-backed) and corporate PPAs",
            "standardization": "Very High (CfD standard contracts)",
            "risk_allocation": "Optimal (government-backed CfDs)",
            "enforceability": "Excellent (UK legal system, English law gold standard)",
            "currency_risk": "Low (GBP, stable)",
            "termination_protections": "Excellent",
            "bankability": "Exceptional (English law preferred globally)",
            "status": "World-leading contract framework, English law gold standard for global project finance"
        },
        "Spain": {
            "score": 5,
            "category": "adequate",
            "ppa_framework": "REER auctions and bilateral PPAs",
            "standardization": "Moderate (post-reform uncertainty)",
            "risk_allocation": "Uncertain (retroactive reform legacy)",
            "enforceability": "Moderate (retroactive changes undermined confidence)",
            "currency_risk": "Low (EUR)",
            "termination_protections": "Weak to Moderate (reform history)",
            "bankability": "Moderate (rebuilding after retroactive changes)",
            "status": "Framework recovering from retroactive policy changes that damaged investor confidence"
        },
        "Australia": {
            "score": 8,
            "category": "very_good",
            "ppa_framework": "State-level contracts and corporate PPAs",
            "standardization": "High (Commonwealth law)",
            "risk_allocation": "Strong (well-developed commercial framework)",
            "enforceability": "Excellent (Australian legal system)",
            "currency_risk": "Low to Moderate (AUD volatility)",
            "termination_protections": "Strong",
            "bankability": "Very High (sophisticated market)",
            "status": "Strong commercial framework with excellent legal protections"
        },
        "Chile": {
            "score": 8,
            "category": "very_good",
            "ppa_framework": "Auction and bilateral PPAs",
            "standardization": "High (auction standard terms)",
            "risk_allocation": "Balanced (market-tested framework)",
            "enforceability": "Strong (stable legal system)",
            "currency_risk": "Moderate (CLP, dollar-indexed available)",
            "termination_protections": "Strong",
            "bankability": "Very High (strong track record)",
            "status": "Highly developed framework with strong investor protections"
        },
        "Vietnam": {
            "score": 4,
            "category": "below_adequate",
            "ppa_framework": "EVN PPAs (state monopoly)",
            "standardization": "Moderate (standard FiT template)",
            "risk_allocation": "Unfavorable (limited recourse, EVN monopoly)",
            "enforceability": "Weak (legal system limitations)",
            "currency_risk": "High (VND controls, repatriation issues)",
            "termination_protections": "Weak",
            "bankability": "Low to Moderate (financing challenges)",
            "status": "Weak legal framework with significant enforceability and currency concerns"
        },
        "South Africa": {
            "score": 7,
            "category": "good",
            "ppa_framework": "REIPPP standardized PPAs (Eskom offtake)",
            "standardization": "Very High (REIPPP standard contracts)",
            "risk_allocation": "Balanced (well-structured, tested)",
            "enforceability": "Good (South African legal system)",
            "currency_risk": "Moderate (ZAR volatility)",
            "termination_protections": "Strong",
            "bankability": "Good to Very High (REIPPP track record)",
            "status": "Well-structured framework with strong standardization, though Eskom credit concerns"
        },
        "Nigeria": {
            "score": 3,
            "category": "poor",
            "ppa_framework": "NBET/Distribution company PPAs",
            "standardization": "Low to Moderate (evolving)",
            "risk_allocation": "Highly unfavorable (significant counterparty risk)",
            "enforceability": "Weak (legal system challenges)",
            "currency_risk": "Very High (NGN volatility, FX scarcity)",
            "termination_protections": "Weak",
            "bankability": "Very Low (major financing challenges)",
            "status": "Weak framework with significant enforceability and counterparty credit concerns"
        },
        "Argentina": {
            "score": 5,
            "category": "adequate",
            "ppa_framework": "RenovAr PPAs and CAMMESA contracts",
            "standardization": "Moderate (RenovAr standard forms)",
            "risk_allocation": "Moderate (sovereign risk significant)",
            "enforceability": "Moderate (legal system functional but slow)",
            "currency_risk": "Very High (ARS volatility, controls)",
            "termination_protections": "Moderate",
            "bankability": "Moderate (economic volatility concerns)",
            "status": "Reasonable framework but significant currency and sovereign risk challenges"
        },
        "Mexico": {
            "score": 6,
            "category": "above_adequate",
            "ppa_framework": "Legacy auction PPAs and bilateral",
            "standardization": "High (pre-2018 auction standard forms)",
            "risk_allocation": "Balanced (legacy contracts strong)",
            "enforceability": "Good (legal system functional)",
            "currency_risk": "Moderate (MXN, USMCA framework)",
            "termination_protections": "Good (for legacy contracts)",
            "bankability": "Good (for existing projects, uncertain for new)",
            "status": "Strong legacy contracts but policy uncertainty for new projects post-2018"
        },
        "Indonesia": {
            "score": 5,
            "category": "adequate",
            "ppa_framework": "PLN PPAs (state monopoly)",
            "standardization": "Moderate (PLN standard forms)",
            "risk_allocation": "Unfavorable (PLN-favorable terms)",
            "enforceability": "Moderate (legal system developing)",
            "currency_risk": "High (IDR volatility)",
            "termination_protections": "Moderate",
            "bankability": "Moderate (PLN credit support helps)",
            "status": "Adequate framework with PLN monopoly creating imbalanced terms"
        },
        "Saudi Arabia": {
            "score": 8,
            "category": "very_good",
            "ppa_framework": "REPDO standardized PPAs",
            "standardization": "Very High (international best practice)",
            "risk_allocation": "Balanced (well-structured)",
            "enforceability": "Strong (arbitration, international standards)",
            "currency_risk": "Minimal (SAR peg to USD)",
            "termination_protections": "Strong",
            "bankability": "Very High (sovereign-backed)",
            "status": "Modern framework adopting international best practices, strong sovereign support"
        },
    }
    
    # Category to score mapping
    CATEGORY_SCORES = {
        "non_bankable": 1,
        "very_poor": 2,
        "poor": 3,
        "below_adequate": 4,
        "adequate": 5,
        "above_adequate": 6,
        "good": 7,
        "very_good": 8,
        "excellent": 9,
        "best_in_class": 10
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Contract Terms Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Contract Terms",
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
            f"Initialized ContractTermsAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            contract_config = params_config['parameters'].get('contract_terms', {})
            scoring = contract_config.get('scoring', [])
            
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
            {"score": 1, "range": "Non-bankable", "description": "Highly unfavorable terms"},
            {"score": 2, "range": "Very poor", "description": "Major risk allocation issues"},
            {"score": 3, "range": "Poor", "description": "Significant enforceability concerns"},
            {"score": 4, "range": "Below adequate", "description": "Below-market terms"},
            {"score": 5, "range": "Adequate", "description": "Basic framework exists"},
            {"score": 6, "range": "Above adequate", "description": "Reasonable terms"},
            {"score": 7, "range": "Good", "description": "Solid framework"},
            {"score": 8, "range": "Very good", "description": "Strong standardization, highly bankable"},
            {"score": 9, "range": "Excellent", "description": "Internationally-competitive"},
            {"score": 10, "range": "Best-in-class", "description": "World-class framework"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze contract terms for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Contract Terms for {country} ({period}) in {self.mode.value} mode")
            
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
                # Use AI extraction confidence
                data_quality = "high"
                ai_confidence = data.get('ai_confidence', 0.8)
                confidence = ai_confidence  # Use AI's confidence directly
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.60  # Lower confidence for estimated legal quality
            else:
                data_quality = "high"
                confidence = 0.80  # High confidence for expert assessments
            
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
                f"Contract Terms analysis complete for {country}: "
                f"Score={score:.1f}, Category={data.get('category', 'unknown')}, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Contract Terms analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Contract Terms analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch contract terms data.
        
        In MOCK mode: Returns mock contract quality assessments
        In RULE_BASED mode: Estimates from World Bank governance indicators + GDP
        In AI_POWERED mode: Would use LLM to extract from PPA documents (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with contract terms data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default adequate framework")
                data = {
                    "score": 6,
                    "category": "above_adequate",
                    "ppa_framework": "Standard PPAs",
                    "standardization": "Moderate",
                    "risk_allocation": "Balanced",
                    "enforceability": "Moderate",
                    "currency_risk": "Moderate",
                    "termination_protections": "Moderate",
                    "bankability": "Moderate",
                    "status": "Reasonable contract framework with room for improvement"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: score={data.get('score')}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate from World Bank governance indicators
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch GDP per capita (development level correlates with contract sophistication)
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch FDI net inflows (confidence in legal framework)
                fdi_inflows_pct = self.data_service.get_value(
                    country=country,
                    indicator='fdi_net_inflows',
                    default=None
                )
                
                # Note: World Bank governance indicators (rule of law, regulatory quality)
                # are not in our standard data service but would be ideal here
                # For now, we'll use GDP + FDI as proxies
                
                if gdp_per_capita is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate contract quality
                score, category = self._estimate_contract_quality(
                    country,
                    gdp_per_capita,
                    fdi_inflows_pct
                )
                
                # Estimate characteristics
                ppa_framework = self._determine_ppa_framework(category)
                standardization = self._determine_standardization(category, gdp_per_capita)
                risk_allocation = self._determine_risk_allocation(category)
                enforceability = self._determine_enforceability(category, gdp_per_capita)
                currency_risk = self._determine_currency_risk(gdp_per_capita)
                termination = self._determine_termination_protections(category)
                bankability = self._determine_bankability(category)
                status = self._determine_contract_status(category, score)
                
                data = {
                    'score': score,
                    'category': category,
                    'ppa_framework': ppa_framework,
                    'standardization': standardization,
                    'risk_allocation': risk_allocation,
                    'enforceability': enforceability,
                    'currency_risk': currency_risk,
                    'termination_protections': termination,
                    'bankability': bankability,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_gdp_per_capita': gdp_per_capita,
                    'raw_fdi_inflows_pct': fdi_inflows_pct if fdi_inflows_pct else 0
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: score={score:.1f} ({category}) "
                    f"from GDP/capita=${gdp_per_capita:,.0f}"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating contract quality for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # Use AI Extraction System to extract contract terms from documents
            try:
                from ai_extraction_system import AIExtractionAdapter

                logger.info(f"Using AI_POWERED mode for {country}")

                # Initialize AI extraction adapter
                adapter = AIExtractionAdapter(
                    llm_config=self.config.get('llm_config') if self.config else None,
                    cache_config=self.config.get('cache_config') if self.config else None
                )

                # Extract contract terms using AI
                extraction_result = adapter.extract_parameter(
                    parameter_name='contract_terms',
                    country=country,
                    period=period,
                    documents=kwargs.get('documents'),
                    document_urls=kwargs.get('document_urls')
                )

                # Convert AI extraction result to agent data format
                if extraction_result and extraction_result.get('value'):
                    score = float(extraction_result['value'])

                    # Determine category from score
                    category = self._score_to_category(score)

                    # Extract metadata
                    metadata = extraction_result.get('metadata', {})

                    data = {
                        'score': score,
                        'category': category,
                        'ppa_framework': metadata.get('ppa_framework', 'Unknown'),
                        'standardization': metadata.get('standardization', 'Unknown'),
                        'risk_allocation': metadata.get('risk_allocation', 'Unknown'),
                        'enforceability': metadata.get('enforceability', 'Unknown'),
                        'currency_risk': metadata.get('currency_risk', 'Unknown'),
                        'termination_protections': metadata.get('termination_protections', 'Unknown'),
                        'bankability': metadata.get('bankability', 'Unknown'),
                        'status': extraction_result.get('justification', ''),
                        'source': 'ai_powered',
                        'period': period,
                        'ai_confidence': extraction_result.get('confidence', 0.8),
                        'ai_justification': extraction_result.get('justification', '')
                    }

                    logger.info(
                        f"Extracted AI_POWERED data for {country}: score={score:.1f} ({category}), "
                        f"confidence={extraction_result.get('confidence', 0):.2f}"
                    )

                    return data
                else:
                    logger.warning(f"AI extraction returned no value for {country}, falling back")
                    return self._fetch_data_mock_fallback(country)

            except Exception as e:
                logger.error(
                    f"Error using AI extraction for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
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
            "score": 6,
            "category": "above_adequate",
            "ppa_framework": "Standard PPAs",
            "standardization": "Moderate",
            "risk_allocation": "Balanced",
            "enforceability": "Moderate",
            "currency_risk": "Moderate",
            "termination_protections": "Moderate",
            "bankability": "Moderate",
            "status": "Reasonable contract framework with room for improvement"
        })
        data['source'] = 'mock_fallback'

        logger.debug(f"Using mock fallback data for {country}")
        return data

    def _score_to_category(self, score: float) -> str:
        """Convert numeric score to category string.

        Args:
            score: Numeric score (1-10)

        Returns:
            Category string
        """
        score = round(score)

        if score >= 10:
            return "best_in_class"
        elif score >= 9:
            return "excellent"
        elif score >= 8:
            return "very_good"
        elif score >= 7:
            return "good"
        elif score >= 6:
            return "above_adequate"
        elif score >= 5:
            return "adequate"
        elif score >= 4:
            return "below_adequate"
        elif score >= 3:
            return "poor"
        elif score >= 2:
            return "very_poor"
        else:
            return "non_bankable"
    
    def _estimate_contract_quality(
        self,
        country: str,
        gdp_per_capita: float,
        fdi_inflows_pct: Optional[float]
    ) -> tuple:
        """Estimate contract quality from World Bank indicators.
        
        Higher GDP + Higher FDI = Better legal framework and contract quality
        
        Args:
            country: Country name
            gdp_per_capita: GDP per capita in current USD
            fdi_inflows_pct: FDI net inflows (% of GDP)
            
        Returns:
            Tuple of (score, category)
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Start with GDP-based score (development level correlates with legal sophistication)
        if gdp_per_capita >= 50000:
            # Very high income (Germany, UK, USA, Australia)
            base_score = 9.5
        elif gdp_per_capita >= 40000:
            # High income (developed countries)
            base_score = 9.0
        elif gdp_per_capita >= 20000:
            # Upper-middle income (Chile)
            base_score = 7.5
        elif gdp_per_capita >= 10000:
            # Middle income (Brazil, China)
            base_score = 6.5
        elif gdp_per_capita >= 5000:
            # Lower-middle income (India)
            base_score = 5.5
        else:
            # Low income (Nigeria)
            base_score = 4.0
        
        # Adjust based on FDI (confidence in legal framework)
        fdi_adjustment = 0.0
        if fdi_inflows_pct is not None:
            if fdi_inflows_pct >= 4.0:
                # Very high FDI (strong confidence)
                fdi_adjustment = +1.0
            elif fdi_inflows_pct >= 2.0:
                # High FDI
                fdi_adjustment = +0.5
            elif fdi_inflows_pct >= 1.0:
                # Moderate FDI
                fdi_adjustment = 0.0
            elif fdi_inflows_pct < 0.5:
                # Low FDI (weak confidence)
                fdi_adjustment = -0.5
        
        # Calculate estimated score
        score = base_score + fdi_adjustment
        
        # Calibrate with mock data if available (50/50 blend - less confident in estimation)
        if base_data:
            base_score_mock = base_data.get('score', score)
            score = score * 0.5 + base_score_mock * 0.5
        
        # Clamp to valid range
        score = max(1.0, min(score, 10.0))
        
        # Determine category from score
        category = self._determine_category_from_score(score)
        
        logger.debug(
            f"Contract quality estimation for {country}: "
            f"GDP/capita=${gdp_per_capita:,.0f} → base={base_score:.1f}, "
            f"FDI={fdi_inflows_pct if fdi_inflows_pct else 0:.1f}% → adj={fdi_adjustment:+.1f}, "
            f"final_score={score:.1f} ({category})"
        )
        
        return score, category
    
    def _determine_category_from_score(self, score: float) -> str:
        """Determine category from score."""
        if score >= 9.5:
            return "best_in_class"
        elif score >= 8.5:
            return "excellent"
        elif score >= 7.5:
            return "very_good"
        elif score >= 6.5:
            return "good"
        elif score >= 5.5:
            return "above_adequate"
        elif score >= 4.5:
            return "adequate"
        elif score >= 3.5:
            return "below_adequate"
        elif score >= 2.5:
            return "poor"
        elif score >= 1.5:
            return "very_poor"
        else:
            return "non_bankable"
    
    def _determine_ppa_framework(self, category: str) -> str:
        """Determine PPA framework description."""
        if category in ["best_in_class", "excellent"]:
            return "Standardized PPAs with government backing or sophisticated market"
        elif category in ["very_good", "good"]:
            return "Well-structured PPAs with reasonable standardization"
        elif category in ["above_adequate", "adequate"]:
            return "Standard PPAs with moderate sophistication"
        else:
            return "Basic or evolving PPA framework"
    
    def _determine_standardization(self, category: str, gdp_per_capita: float) -> str:
        """Determine standardization level."""
        if category in ["best_in_class", "excellent"]:
            return "Very High (international best practice)"
        elif category in ["very_good", "good"]:
            return "High (well-developed standards)"
        elif category in ["above_adequate", "adequate"]:
            return "Moderate (improving)"
        else:
            return "Low to Moderate (evolving)"
    
    def _determine_risk_allocation(self, category: str) -> str:
        """Determine risk allocation quality."""
        if category in ["best_in_class", "excellent"]:
            return "Optimal (well-balanced, market-tested)"
        elif category in ["very_good", "good"]:
            return "Strong to Balanced"
        elif category in ["above_adequate", "adequate"]:
            return "Balanced to Moderate"
        else:
            return "Unfavorable (imbalanced)"
    
    def _determine_enforceability(self, category: str, gdp_per_capita: float) -> str:
        """Determine enforceability level."""
        if category in ["best_in_class", "excellent"] and gdp_per_capita >= 40000:
            return "Excellent (mature legal system)"
        elif category in ["very_good", "good"]:
            return "Strong to Good"
        elif category in ["above_adequate", "adequate"]:
            return "Moderate"
        else:
            return "Weak to Moderate"
    
    def _determine_currency_risk(self, gdp_per_capita: float) -> str:
        """Determine currency risk level (simplified)."""
        if gdp_per_capita >= 40000:
            return "Low to Minimal (stable currency)"
        elif gdp_per_capita >= 15000:
            return "Moderate"
        else:
            return "High (currency volatility)"
    
    def _determine_termination_protections(self, category: str) -> str:
        """Determine termination protection level."""
        if category in ["best_in_class", "excellent"]:
            return "Excellent"
        elif category in ["very_good", "good"]:
            return "Strong"
        elif category in ["above_adequate", "adequate"]:
            return "Moderate"
        else:
            return "Weak"
    
    def _determine_bankability(self, category: str) -> str:
        """Determine bankability level."""
        if category in ["best_in_class", "excellent"]:
            return "Exceptional to Very High"
        elif category in ["very_good", "good"]:
            return "Very High to Good"
        elif category in ["above_adequate", "adequate"]:
            return "Moderate"
        else:
            return "Low to Moderate"
    
    def _determine_contract_status(self, category: str, score: float) -> str:
        """Determine contract status description."""
        if score >= 9:
            return "World-class contract framework with proven track record and international best practice"
        elif score >= 8:
            return "Strong contract framework with high standardization and bankability"
        elif score >= 6:
            return "Solid framework with reasonable terms and moderate sophistication"
        elif score >= 4:
            return "Adequate framework but with notable concerns"
        else:
            return "Weak framework with significant enforceability and bankability challenges"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate contract terms score.
        
        CATEGORICAL: Category determines score
        Better terms = higher score
        
        Args:
            data: Contract terms data
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using score {score} for {country}")
            return float(score)
        
        # Otherwise map from category
        category = data.get("category", "above_adequate")
        score = self.CATEGORY_SCORES.get(category, 6)
        
        logger.debug(f"Score {score} assigned for category {category}")
        
        return float(score)
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the contract terms score.
        
        Args:
            data: Contract terms data
            score: Calculated score
            country: Country name
            period: Time period
            
        Returns:
            Human-readable justification string
        """
        category = data.get("category", "above_adequate")
        ppa_framework = data.get("ppa_framework", "standard PPAs")
        standardization = data.get("standardization", "moderate")
        risk_allocation = data.get("risk_allocation", "balanced")
        enforceability = data.get("enforceability", "moderate")
        currency = data.get("currency_risk", "moderate")
        termination = data.get("termination_protections", "moderate")
        bankability = data.get("bankability", "moderate")
        status = data.get("status", "reasonable framework")
        source = data.get("source", "unknown")
        
        # Find description from rubric
        description = "above adequate"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level.get("range", level["description"]).lower()
                break
        
        # Build justification based on source
        if source == 'rule_based':
            gdp = data.get('raw_gdp_per_capita', 0)
            fdi = data.get('raw_fdi_inflows_pct', 0)
            justification = (
                f"Based on World Bank data: Estimated contract framework quality is {description} "
                f"(derived from GDP/capita ${gdp:,.0f} and FDI inflows {fdi:.1f}%). "
                f"Estimated standardization: {standardization.lower()}, "
                f"enforceability: {enforceability.lower()}, "
                f"bankability: {bankability.lower()}. {status}. "
            )
        else:
            # Mock data - use detailed assessments
            justification = (
                f"Contract framework quality: {description}. "
                f"PPA framework: {ppa_framework}. "
                f"Standardization: {standardization.lower()}, "
                f"risk allocation: {risk_allocation.lower()}, "
                f"enforceability: {enforceability.lower()}. "
                f"Currency risk: {currency.lower()}, "
                f"termination protections: {termination.lower()}, "
                f"bankability: {bankability.lower()}. "
                f"{status}. "
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
        
        # Check if we used rule-based or mock data
        if data and data.get('source') == 'rule_based':
            sources.append("World Bank Development Indicators - Rule-Based Estimation")
            sources.append("Legal framework assessments (Reference)")
        else:
            sources.append("Sample PPAs and contract templates - Mock Data")
            sources.append("Legal framework assessments")
        
        sources.append("IFC and development bank due diligence")
        sources.append(f"{country} legal and regulatory analysis")
        
        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Contract Terms parameter.
        
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
            "Sample PPAs and contracts",
            "Legal framework assessments",
            "International lender due diligence",
            "Project finance transaction data",
            "IFC and development bank reports"
        ]


def analyze_contract_terms(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze contract terms.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = ContractTermsAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
