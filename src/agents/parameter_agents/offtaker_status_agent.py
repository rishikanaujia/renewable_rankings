"""Offtaker Status Agent - Analyzes PPA offtaker creditworthiness.

This agent evaluates the credit quality and reliability of Power Purchase Agreement
(PPA) offtakers. Higher creditworthiness reduces payment default risk, improves
project bankability, and lowers financing costs.

Credit Rating Scale:
- AAA/AA+: Superior (sovereign/AAA utilities) - Score 10
- AA/A+: Excellent (very strong capacity) - Score 9
- A/A-: Very good (strong capacity) - Score 8
- BBB+/BBB: Good (solid investment grade) - Score 7
- BBB-: Adequate (lower investment grade) - Score 6
- BB+/BB: Moderate (below investment grade) - Score 5
- BB-: Below moderate (speculative) - Score 4
- B+/B: Weak (significant risk) - Score 3
- B-/CCC+: Very weak (substantial risk) - Score 2
- CCC/D: Distressed (high default risk) - Score 1

Scoring Rubric (LOADED FROM CONFIG):
Higher credit rating = Lower default risk = Higher score (DIRECT relationship)

MODES:
- MOCK: Uses hardcoded credit ratings from S&P/Moody's/Fitch (for testing)
- RULE_BASED: Estimates from World Bank economic indicators (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class OfftakerStatusAgent(BaseParameterAgent):
    """Agent for analyzing offtaker credit status and reliability."""
    
    # Mock data for Phase 1 testing
    # Credit ratings for typical offtakers in each market
    # Data from S&P, Moody's, Fitch, sovereign ratings
    MOCK_DATA = {
        "Brazil": {
            "offtaker": "Eletrobras (state utility)",
            "credit_rating": "BBB",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "BB- (Brazil)",
            "status": "Good credit (solid investment grade utility)"
        },
        "Germany": {
            "offtaker": "German utilities (FiT backed)",
            "credit_rating": "AAA",
            "rating_agency": "S&P",
            "category": "superior",
            "sovereign_rating": "AAA (Germany)",
            "status": "Superior credit (sovereign-backed FiT)"
        },
        "USA": {
            "offtaker": "Investment grade utilities",
            "credit_rating": "A",
            "rating_agency": "S&P",
            "category": "very_good",
            "sovereign_rating": "AA+ (USA)",
            "status": "Very good credit (strong utilities)"
        },
        "China": {
            "offtaker": "State Grid Corporation",
            "credit_rating": "AA-",
            "rating_agency": "S&P",
            "category": "excellent",
            "sovereign_rating": "A+ (China)",
            "status": "Excellent credit (state-owned enterprise)"
        },
        "India": {
            "offtaker": "SECI/NTPC (government-backed)",
            "credit_rating": "BBB-",
            "rating_agency": "S&P",
            "category": "adequate",
            "sovereign_rating": "BBB- (India)",
            "status": "Adequate credit (government backing)"
        },
        "UK": {
            "offtaker": "CFD counterparty (LCCC)",
            "credit_rating": "AA",
            "rating_agency": "S&P",
            "category": "excellent",
            "sovereign_rating": "AA (UK)",
            "status": "Excellent credit (government CFD mechanism)"
        },
        "Spain": {
            "offtaker": "Corporate PPAs",
            "credit_rating": "BBB+",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "A- (Spain)",
            "status": "Good credit (investment grade corporates)"
        },
        "Australia": {
            "offtaker": "Corporate PPAs / retailers",
            "credit_rating": "BBB",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "AAA (Australia)",
            "status": "Good credit (corporate offtakers)"
        },
        "Chile": {
            "offtaker": "Mining companies / utilities",
            "credit_rating": "A-",
            "rating_agency": "S&P",
            "category": "very_good",
            "sovereign_rating": "A+ (Chile)",
            "status": "Very good credit (strong mining companies)"
        },
        "Vietnam": {
            "offtaker": "EVN (state utility)",
            "credit_rating": "BB",
            "rating_agency": "S&P",
            "category": "moderate",
            "sovereign_rating": "BB (Vietnam)",
            "status": "Moderate credit (state utility, below investment grade)"
        },
        "South Africa": {
            "offtaker": "Eskom (REIPPP)",
            "credit_rating": "BB-",
            "rating_agency": "S&P",
            "category": "below_moderate",
            "sovereign_rating": "BB- (South Africa)",
            "status": "Below moderate (Eskom financial challenges)"
        },
        "Nigeria": {
            "offtaker": "Local distribution companies",
            "credit_rating": "B",
            "rating_agency": "S&P",
            "category": "weak",
            "sovereign_rating": "B (Nigeria)",
            "status": "Weak credit (DISCO payment challenges)"
        },
        "Argentina": {
            "offtaker": "CAMMESA (RenovAr)",
            "credit_rating": "BB-",
            "rating_agency": "S&P",
            "category": "below_moderate",
            "sovereign_rating": "CCC+ (Argentina)",
            "status": "Below moderate (macro challenges despite RenovAr)"
        },
        "Mexico": {
            "offtaker": "CFE (state utility)",
            "credit_rating": "BBB",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "BBB (Mexico)",
            "status": "Good credit (CFE investment grade)"
        },
        "Indonesia": {
            "offtaker": "PLN (state utility)",
            "credit_rating": "BBB",
            "rating_agency": "S&P",
            "category": "good",
            "sovereign_rating": "BBB (Indonesia)",
            "status": "Good credit (state utility, sovereign level)"
        },
        "Saudi Arabia": {
            "offtaker": "ACWA/SEC (sovereign-backed)",
            "credit_rating": "AA",
            "rating_agency": "S&P",
            "category": "excellent",
            "sovereign_rating": "A- (Saudi Arabia)",
            "status": "Excellent credit (sovereign backing)"
        },
    }
    
    # Credit rating category mapping
    CATEGORY_SCORES = {
        "superior": 10,        # AAA/AA+
        "excellent": 9,        # AA/A+
        "very_good": 8,        # A/A-
        "good": 7,             # BBB+/BBB
        "adequate": 6,         # BBB-
        "moderate": 5,         # BB+/BB
        "below_moderate": 4,   # BB-
        "weak": 3,             # B+/B
        "very_weak": 2,        # B-/CCC+
        "distressed": 1        # CCC/D
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Offtaker Status Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Offtaker Status",
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
            f"Initialized OfftakerStatusAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            offtaker_config = params_config['parameters'].get('offtaker_status', {})
            scoring = offtaker_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "category": item.get('category', ''),
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
        """Fallback scoring rubric if config is not available."""
        return [
            {"score": 1, "category": "distressed", "range": "D/CCC", "description": "Distressed offtaker (high default risk)"},
            {"score": 2, "category": "very_weak", "range": "CCC+/B-", "description": "Very weak credit (substantial credit risk)"},
            {"score": 3, "category": "weak", "range": "B/B+", "description": "Weak credit (significant risk)"},
            {"score": 4, "category": "below_moderate", "range": "BB-", "description": "Below investment grade (speculative)"},
            {"score": 5, "category": "moderate", "range": "BB/BB+", "description": "Moderate credit (below investment grade)"},
            {"score": 6, "category": "adequate", "range": "BBB-", "description": "Adequate credit (lower investment grade)"},
            {"score": 7, "category": "good", "range": "BBB/BBB+", "description": "Good credit (solid investment grade)"},
            {"score": 8, "category": "very_good", "range": "A-/A", "description": "Very good credit (strong capacity)"},
            {"score": 9, "category": "excellent", "range": "A+/AA", "description": "Excellent credit (very strong capacity)"},
            {"score": 10, "category": "superior", "range": "AA+/AAA", "description": "Superior credit (sovereign/AAA utilities)"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze offtaker status for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Offtaker Status for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # For AI-powered mode, use AI confidence directly
            if data.get('source') == 'ai_powered':
                data_quality = "high"
                ai_confidence = data.get('ai_confidence', 0.8)
                confidence = ai_confidence  # Use AI's confidence directly
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.60  # Lower confidence for estimated credit
            else:
                data_quality = "high"
                confidence = 0.85  # High confidence for actual ratings

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
                f"Offtaker Status analysis complete for {country}: "
                f"Score={score:.1f}, Rating={data.get('credit_rating', 'N/A')}, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Offtaker Status analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Offtaker Status analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch offtaker status data.
        
        In MOCK mode: Returns actual credit ratings from agencies
        In RULE_BASED mode: Estimates from World Bank economic indicators
        In AI_POWERED mode: Would use LLM to extract from financial statements (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with offtaker status data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default adequate credit")
                data = {
                    "offtaker": "Utility",
                    "credit_rating": "BBB-",
                    "rating_agency": "S&P",
                    "category": "adequate",
                    "sovereign_rating": "BBB-",
                    "status": "Adequate credit"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: Rating={data.get('credit_rating')}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate from World Bank economic indicators
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch GDP per capita (proxy for economic strength)
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch FDI net inflows (investor confidence)
                fdi_inflows_pct = self.data_service.get_value(
                    country=country,
                    indicator='fdi_net_inflows',
                    default=None
                )
                
                # Fetch GDP growth (economic momentum)
                gdp_growth = self.data_service.get_value(
                    country=country,
                    indicator='gdp_growth',
                    default=None
                )
                
                if gdp_per_capita is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate credit quality
                score, category = self._estimate_credit_quality(
                    country,
                    gdp_per_capita,
                    fdi_inflows_pct,
                    gdp_growth
                )
                
                # Estimate characteristics
                credit_rating = self._determine_credit_rating(category, score)
                offtaker = self._determine_offtaker_type(gdp_per_capita)
                sovereign_rating = self._estimate_sovereign_rating(gdp_per_capita, category)
                status = self._determine_credit_status(category, score)
                
                data = {
                    'offtaker': offtaker,
                    'credit_rating': credit_rating,
                    'rating_agency': 'Estimated',
                    'category': category,
                    'sovereign_rating': sovereign_rating,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_gdp_per_capita': gdp_per_capita,
                    'raw_fdi_inflows_pct': fdi_inflows_pct if fdi_inflows_pct else 0,
                    'raw_gdp_growth': gdp_growth if gdp_growth else 0
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: score={score:.1f} ({category}, {credit_rating}) "
                    f"from GDP/capita=${gdp_per_capita:,.0f}"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating credit quality for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # Extract offtaker status using AI extraction system
            try:
                from ai_extraction_system import AIExtractionAdapter

                adapter = AIExtractionAdapter(
                    llm_config=self.config.get('llm_config') if self.config else None,
                    cache_config=self.config.get('cache_config') if self.config else None
                )

                extraction_result = adapter.extract_parameter(
                    parameter_name='offtaker_status',
                    country=country,
                    period=period,
                    documents=kwargs.get('documents'),
                    document_urls=kwargs.get('document_urls')
                )

                logger.info(f"Using AI_POWERED mode for {country}")

                if extraction_result and extraction_result.get('value') is not None:
                    score = float(extraction_result['value'])
                    metadata = extraction_result.get('metadata', {})

                    data = {
                        'source': 'ai_powered',
                        'ai_confidence': extraction_result.get('confidence', 0.8),
                        'ai_justification': extraction_result.get('justification', ''),
                        'ai_score': score,
                        'creditworthiness': metadata.get('creditworthiness', 'Unknown'),
                        'payment_history': 'Extracted from AI',
                        'period': period
                    }

                    logger.info(f"AI extraction successful for {country}: score={score}/10, confidence={data['ai_confidence']:.2f}")
                    return data
                else:
                    logger.warning(f"AI extraction returned no value for {country}, falling back to MOCK")
                    return self._fetch_data_mock_fallback(country)

            except Exception as e:
                logger.error(f"Error using AI extraction for {country}: {e}. Falling back to MOCK data")
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
            "offtaker": "Utility",
            "credit_rating": "BBB-",
            "rating_agency": "S&P",
            "category": "adequate",
            "sovereign_rating": "BBB-",
            "status": "Adequate credit"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_credit_quality(
        self,
        country: str,
        gdp_per_capita: float,
        fdi_inflows_pct: Optional[float],
        gdp_growth: Optional[float]
    ) -> tuple:
        """Estimate credit quality from World Bank indicators.
        
        State-backed offtakers typically track sovereign credit quality
        Higher GDP + Stable economy = Better credit
        
        Args:
            country: Country name
            gdp_per_capita: GDP per capita (USD)
            fdi_inflows_pct: FDI net inflows (% of GDP)
            gdp_growth: GDP growth (annual %)
            
        Returns:
            Tuple of (score, category)
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Start with GDP-based score (economic strength correlates with credit)
        if gdp_per_capita >= 50000:
            # Very high income (Germany, USA, Australia, UK)
            base_score = 9.5
        elif gdp_per_capita >= 40000:
            # High income
            base_score = 9.0
        elif gdp_per_capita >= 20000:
            # Upper-middle income (Chile)
            base_score = 7.5
        elif gdp_per_capita >= 10000:
            # Middle income (Brazil, China, Mexico)
            base_score = 6.5
        elif gdp_per_capita >= 5000:
            # Lower-middle income (India, Indonesia)
            base_score = 6.0
        else:
            # Low income (Nigeria, Vietnam)
            base_score = 4.0
        
        # Adjust based on FDI confidence
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
        
        # Adjust based on GDP growth (economic momentum)
        growth_adjustment = 0.0
        if gdp_growth is not None:
            if gdp_growth >= 5.0:
                # Strong growth
                growth_adjustment = +0.5
            elif gdp_growth >= 3.0:
                # Moderate growth
                growth_adjustment = +0.3
            elif gdp_growth < 1.0:
                # Weak growth
                growth_adjustment = -0.5
        
        # Calculate estimated score
        score = base_score + fdi_adjustment + growth_adjustment
        
        # Calibrate with mock data if available (50/50 blend - less confident)
        if base_data:
            base_score_mock = self.CATEGORY_SCORES.get(base_data.get('category', 'adequate'), score)
            score = score * 0.5 + base_score_mock * 0.5
        
        # Clamp to valid range
        score = max(1.0, min(score, 10.0))
        
        # Determine category from score
        category = self._determine_category_from_score(score)
        
        logger.debug(
            f"Credit quality estimation for {country}: "
            f"GDP/capita=${gdp_per_capita:,.0f} → base={base_score:.1f}, "
            f"FDI={fdi_inflows_pct if fdi_inflows_pct else 0:.1f}% → adj={fdi_adjustment:+.1f}, "
            f"growth={gdp_growth if gdp_growth else 0:.1f}% → adj={growth_adjustment:+.1f}, "
            f"final_score={score:.1f} ({category})"
        )
        
        return score, category
    
    def _determine_category_from_score(self, score: float) -> str:
        """Determine category from score."""
        if score >= 9.5:
            return "superior"
        elif score >= 8.5:
            return "excellent"
        elif score >= 7.5:
            return "very_good"
        elif score >= 6.5:
            return "good"
        elif score >= 5.5:
            return "adequate"
        elif score >= 4.5:
            return "moderate"
        elif score >= 3.5:
            return "below_moderate"
        elif score >= 2.5:
            return "weak"
        elif score >= 1.5:
            return "very_weak"
        else:
            return "distressed"
    
    def _determine_credit_rating(self, category: str, score: float) -> str:
        """Determine credit rating from category."""
        rating_map = {
            "superior": "AAA",
            "excellent": "AA",
            "very_good": "A",
            "good": "BBB",
            "adequate": "BBB-",
            "moderate": "BB",
            "below_moderate": "BB-",
            "weak": "B",
            "very_weak": "B-",
            "distressed": "CCC"
        }
        return rating_map.get(category, "BBB-")
    
    def _determine_offtaker_type(self, gdp_per_capita: float) -> str:
        """Determine typical offtaker type."""
        if gdp_per_capita >= 40000:
            return "Investment grade utilities / Government-backed"
        elif gdp_per_capita >= 15000:
            return "State utilities / Corporate PPAs"
        else:
            return "State utility (government-backed)"
    
    def _estimate_sovereign_rating(self, gdp_per_capita: float, category: str) -> str:
        """Estimate sovereign rating."""
        if gdp_per_capita >= 50000:
            return f"AAA (estimated)"
        elif gdp_per_capita >= 40000:
            return f"AA+ (estimated)"
        elif gdp_per_capita >= 20000:
            return f"A (estimated)"
        elif gdp_per_capita >= 10000:
            return f"BBB (estimated)"
        elif gdp_per_capita >= 5000:
            return f"BBB- (estimated)"
        else:
            return f"BB or below (estimated)"
    
    def _determine_credit_status(self, category: str, score: float) -> str:
        """Determine credit status description."""
        if score >= 9:
            return "Superior credit quality with government backing or AAA utility"
        elif score >= 8:
            return "Excellent credit with very strong payment capacity"
        elif score >= 7:
            return "Good credit quality (solid investment grade)"
        elif score >= 6:
            return "Adequate credit (lower investment grade, government backing helps)"
        elif score >= 5:
            return "Moderate credit (below investment grade, manageable risk)"
        elif score >= 4:
            return "Below investment grade with notable credit concerns"
        else:
            return "Weak credit with significant payment default risk"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate offtaker status score based on credit category.

        DIRECT: Higher credit rating = lower default risk = higher score

        Args:
            data: Offtaker status data
            country: Country name
            period: Time period

        Returns:
            Score between 1-10
        """
        # For AI-powered mode, use the score directly
        if data.get('source') == 'ai_powered' and 'ai_score' in data:
            score = float(data['ai_score'])
            logger.debug(f"Using AI-provided score for {country}: {score}/10")
            return score

        category = data.get("category", "adequate")

        # Get score from category mapping
        score = self.CATEGORY_SCORES.get(category, 6)

        logger.debug(
            f"Calculating score for {country}: "
            f"Category={category}, Rating={data.get('credit_rating')}, Score={score}"
        )

        return float(score)
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the offtaker status score.

        Args:
            data: Offtaker status data
            score: Calculated score
            country: Country name
            period: Time period

        Returns:
            Human-readable justification string
        """
        source = data.get("source", "unknown")

        # For AI-powered mode, use AI justification directly
        if source == 'ai_powered':
            ai_justification = data.get('ai_justification', '')
            if ai_justification:
                return ai_justification
            # Fallback if no AI justification provided
            return f"AI-extracted offtaker status score of {score:.1f}/10 for {country} based on utility creditworthiness and payment history analysis."

        offtaker = data.get("offtaker", "utility")
        credit_rating = data.get("credit_rating", "N/A")
        rating_agency = data.get("rating_agency", "S&P")
        sovereign_rating = data.get("sovereign_rating", "")
        status = data.get("status", "moderate credit")

        # Find description from rubric
        description = "moderate credit"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break

        # Build justification based on source
        if source == 'rule_based':
            gdp = data.get('raw_gdp_per_capita', 0)
            fdi = data.get('raw_fdi_inflows_pct', 0)
            justification = (
                f"Based on World Bank data: Estimated offtaker {offtaker} carries "
                f"estimated {rating_agency} credit rating of {credit_rating}, indicating {description} "
                f"(derived from GDP/capita ${gdp:,.0f} and FDI inflows {fdi:.1f}%). "
                f"{status.capitalize()}. "
            )
        else:
            # Mock data - use actual ratings
            justification = (
                f"Offtaker {offtaker} carries {rating_agency} credit rating of {credit_rating}, "
                f"indicating {description}. {status.capitalize()}. "
            )

        if sovereign_rating:
            justification += f"Sovereign rating of {sovereign_rating} provides context for offtaker creditworthiness. "

        justification += (
            f"This credit profile {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"supports project financing and {'significantly reduces' if score >= 8 else 'moderately reduces' if score >= 6 else 'addresses'} "
            f"payment default risk. "
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
            sources.append("AI-Powered Document Extraction (Offtaker Status)")
            sources.append("Utility Financial Reports and Credit Assessments")
        elif data and data.get('source') == 'rule_based':
            sources.append("World Bank Economic Indicators - Rule-Based Estimation")
            sources.append("Credit rating agencies (Reference)")
        else:
            sources.append("S&P Global Ratings - Mock Data")
            sources.append("Moody's Ratings")
            sources.append("Fitch Ratings")

        sources.append(f"{country} Offtaker financial statements")
        sources.append("Sovereign credit ratings")

        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Offtaker Status parameter.
        
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
            "S&P Global Ratings",
            "Moody's Ratings",
            "Fitch Ratings",
            "Offtaker financial statements",
            "Sovereign credit ratings",
            "Project finance documentation"
        ]


def analyze_offtaker_status(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze offtaker status.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = OfftakerStatusAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
