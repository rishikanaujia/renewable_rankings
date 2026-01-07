"""Support Scheme Agent - Analyzes quality and effectiveness of renewable energy support mechanisms.

This agent evaluates the renewable energy support scheme framework by analyzing:
- Feed-in tariffs (FiTs) design and generosity
- Auction/tender mechanisms and competitiveness
- Tax incentives and credits (ITC, PTC, accelerated depreciation)
- Net metering and distributed generation policies
- Renewable energy certificates/credits (RECs)
- Policy stability and predictability

Support schemes drive project economics through:
- Revenue certainty and risk reduction
- Improved project bankability
- Accelerated market development
- Technology cost reductions

Support Scheme Quality Categories (1-10):
- 10: Highly Mature (comprehensive, stable, proven)
- 9: Strong but Not Scalable (generous but limited scale)
- 8: Broad but Uneven (widespread but inconsistent)
- 7: Solid but Uncertain (good design but policy risk)
- 6: Developing (emerging framework)
- 5: Basic (limited mechanisms)
- 4: Boom-Bust (unstable, volatile)
- 3: Forces Disadvantage (distortions, barriers)
- 2: Emerging but Ineffective (weak implementation)
- 1: Minimal or Absent (no meaningful support)

Scoring Rubric (LOADED FROM CONFIG):
Higher support quality = Better framework = Higher score (DIRECT relationship)

MODES:
- MOCK: Uses hardcoded support scheme quality assessments (for testing)
- RULE_BASED: Estimates from World Bank renewable energy policy indicators (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class SupportSchemeAgent(BaseParameterAgent):
    """Agent for analyzing renewable energy support scheme quality and effectiveness."""
    
    # Mock data for Phase 1 testing
    # Support scheme quality scores (1-10) based on:
    # - FiT/auction design
    # - Tax incentives
    # - Net metering
    # - Policy stability
    # Data from IEA, IRENA, REN21, national energy ministries
    MOCK_DATA = {
        "Germany": {
            "support_score": 10,
            "category": "Highly Mature",
            "fit_quality": "Excellent (legacy)",
            "auction_design": "Excellent (competitive)",
            "tax_incentives": "Good",
            "net_metering": "Available",
            "recs": "Active market",
            "stability": "Very high",
            "key_schemes": ["EEG auctions", "FiT legacy", "Market premium"],
            "status": "World-leading Energiewende framework, highly mature and stable"
        },
        "China": {
            "support_score": 10,
            "category": "Highly Mature",
            "fit_quality": "Excellent",
            "auction_design": "Excellent",
            "tax_incentives": "Strong",
            "net_metering": "Emerging",
            "recs": "Green certificate system",
            "stability": "High (top-down)",
            "key_schemes": ["FiT for solar/wind", "Auctions", "Grid parity push"],
            "status": "Massive scale, comprehensive support, strong government backing"
        },
        "UK": {
            "support_score": 10,
            "category": "Highly Mature",
            "fit_quality": "Good (legacy)",
            "auction_design": "Excellent (CfD)",
            "tax_incentives": "Moderate",
            "net_metering": "Limited",
            "recs": "ROCs (being phased)",
            "stability": "High",
            "key_schemes": ["CfD auctions", "ROCs legacy", "Smart Export Guarantee"],
            "status": "Mature CfD auction system, excellent offshore wind support"
        },
        "USA": {
            "support_score": 8,
            "category": "Broad but Uneven",
            "fit_quality": "State-level only",
            "auction_design": "Varied by state",
            "tax_incentives": "Excellent (ITC/PTC)",
            "net_metering": "Widespread (state-level)",
            "recs": "Active REC markets",
            "stability": "Moderate (federal uncertainty)",
            "key_schemes": ["ITC 30%", "PTC", "State RPS", "Net metering"],
            "status": "Strong federal tax credits, but state-level variation creates unevenness"
        },
        "Brazil": {
            "support_score": 8,
            "category": "Broad but Uneven",
            "fit_quality": "None",
            "auction_design": "Good (proven track record)",
            "tax_incentives": "Moderate",
            "net_metering": "Excellent (distributed)",
            "recs": "None",
            "stability": "Moderate",
            "key_schemes": ["Energy auctions", "Net metering (micro/mini)", "PROINFA legacy"],
            "status": "Successful auction program, excellent net metering, but uneven application"
        },
        "India": {
            "support_score": 9,
            "category": "Strong but Not Scalable",
            "fit_quality": "State-level",
            "auction_design": "Excellent",
            "tax_incentives": "Strong",
            "net_metering": "State-level",
            "recs": "REC market exists",
            "stability": "Moderate (payment delays)",
            "key_schemes": ["Central auctions", "State FiTs", "RPO", "Accelerated depreciation"],
            "status": "Strong support mechanisms but constrained by grid and payment issues"
        },
        "Spain": {
            "support_score": 7,
            "category": "Solid but Uncertain",
            "fit_quality": "Eliminated (retroactive cuts)",
            "auction_design": "Good (restarted)",
            "tax_incentives": "Limited",
            "net_metering": "Recent (2019+)",
            "recs": "None",
            "stability": "Low (historical retroactivity)",
            "key_schemes": ["Auctions (post-2017)", "Net metering", "Pool market"],
            "status": "Recovering from retroactive cuts, auctions restarted but investor caution"
        },
        "Australia": {
            "support_score": 6,
            "category": "Developing",
            "fit_quality": "State-level only",
            "auction_design": "Limited",
            "tax_incentives": "Moderate",
            "net_metering": "Widespread",
            "recs": "LGCs active",
            "stability": "Low (policy volatility)",
            "key_schemes": ["RET/LGCs", "State schemes", "Net metering"],
            "status": "Fragmented state-level support, federal policy uncertainty"
        },
        "Chile": {
            "support_score": 6,
            "category": "Developing",
            "fit_quality": "None",
            "auction_design": "Good",
            "tax_incentives": "Limited",
            "net_metering": "Good (NetBilling)",
            "recs": "None",
            "stability": "Moderate",
            "key_schemes": ["Energy auctions", "NetBilling", "Quota obligation"],
            "status": "Market-driven with auctions, developing distributed generation support"
        },
        "Saudi Arabia": {
            "support_score": 9,
            "category": "Strong but Not Scalable",
            "fit_quality": "None",
            "auction_design": "Excellent (REPDO)",
            "tax_incentives": "N/A (no income tax)",
            "net_metering": "Emerging",
            "recs": "None",
            "stability": "High (Vision 2030)",
            "key_schemes": ["REPDO auctions", "Vision 2030 targets", "NREP"],
            "status": "Excellent auction design achieving world record-low prices, but limited to utility-scale"
        },
        "Vietnam": {
            "support_score": 4,
            "category": "Boom-Bust",
            "fit_quality": "Boom-bust cycles",
            "auction_design": "Emerging",
            "tax_incentives": "Moderate",
            "net_metering": "Limited",
            "recs": "None",
            "stability": "Very low (abrupt changes)",
            "key_schemes": ["FiT (solar boom 2019-20)", "Direct PPA", "Shifting policies"],
            "status": "Boom-bust cycles from sudden FiT changes, policy instability harms investment"
        },
        "South Africa": {
            "support_score": 5,
            "category": "Basic",
            "fit_quality": "None",
            "auction_design": "Good (REIPPPP)",
            "tax_incentives": "Limited",
            "net_metering": "Emerging (municipal)",
            "recs": "None",
            "stability": "Low (REIPPPP delays)",
            "key_schemes": ["REIPPPP auctions", "Net metering (select)", "Eskom constraints"],
            "status": "Good auction program (REIPPPP) but plagued by delays and grid constraints"
        },
        "Mexico": {
            "support_score": 3,
            "category": "Forces Disadvantage",
            "fit_quality": "Eliminated",
            "auction_design": "Suspended (2019+)",
            "tax_incentives": "Limited",
            "net_metering": "Rolled back",
            "recs": "Eliminated",
            "stability": "Very low (reversal)",
            "key_schemes": ["Legacy auctions (pre-2019)", "CFE dominant"],
            "status": "Policy reversal post-2018, auctions suspended, CFE favored over renewables"
        },
        "Nigeria": {
            "support_score": 2,
            "category": "Emerging but Ineffective",
            "fit_quality": "Announced but not operational",
            "auction_design": "None",
            "tax_incentives": "Minimal",
            "net_metering": "Not available",
            "recs": "None",
            "stability": "Very low",
            "key_schemes": ["FiT announced 2015", "REA programs", "Off-grid focus"],
            "status": "FiT announced but never implemented, weak enabling environment"
        },
        "Argentina": {
            "support_score": 5,
            "category": "Basic",
            "fit_quality": "Provincial level",
            "auction_design": "Good (RenovAr)",
            "tax_incentives": "Moderate",
            "net_metering": "Provincial level",
            "recs": "None",
            "stability": "Low (economic volatility)",
            "key_schemes": ["RenovAr auctions", "Provincial programs", "Net metering"],
            "status": "RenovAr auctions showed promise but economic instability limits effectiveness"
        },
        "Indonesia": {
            "support_score": 4,
            "category": "Boom-Bust",
            "fit_quality": "Complex, bureaucratic",
            "auction_design": "Limited",
            "tax_incentives": "Moderate",
            "net_metering": "Very limited",
            "recs": "None",
            "stability": "Low",
            "key_schemes": ["FiT (complex)", "Direct selection", "PLN PPAs"],
            "status": "Complex FiT system with administrative barriers, low policy predictability"
        },
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Support Scheme Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Support Scheme",
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
            f"Initialized SupportSchemeAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            support_config = params_config['parameters'].get('support_scheme', {})
            scoring = support_config.get('scoring', [])
            
            if scoring:
                logger.info("Loaded scoring rubric from config/parameters.yaml")
                rubric = []
                for item in scoring:
                    rubric.append({
                        "score": item['value'],
                        "min_support": item.get('min_support', 0.0),
                        "max_support": item.get('max_support', 10.1),
                        "category": item.get('category', ''),
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
            {"score": 1, "min_support": 0.0, "max_support": 1.5, "category": "Minimal/Absent", "description": "No meaningful support mechanisms"},
            {"score": 2, "min_support": 1.5, "max_support": 2.5, "category": "Emerging but Ineffective", "description": "Weak implementation"},
            {"score": 3, "min_support": 2.5, "max_support": 3.5, "category": "Forces Disadvantage", "description": "Distortions and barriers"},
            {"score": 4, "min_support": 3.5, "max_support": 4.5, "category": "Boom-Bust", "description": "Unstable and volatile"},
            {"score": 5, "min_support": 4.5, "max_support": 5.5, "category": "Basic", "description": "Limited mechanisms"},
            {"score": 6, "min_support": 5.5, "max_support": 6.5, "category": "Developing", "description": "Emerging framework"},
            {"score": 7, "min_support": 6.5, "max_support": 7.5, "category": "Solid but Uncertain", "description": "Good design but policy risk"},
            {"score": 8, "min_support": 7.5, "max_support": 8.5, "category": "Broad but Uneven", "description": "Widespread but inconsistent"},
            {"score": 9, "min_support": 8.5, "max_support": 9.5, "category": "Strong but Not Scalable", "description": "Generous but limited scale"},
            {"score": 10, "min_support": 9.5, "max_support": 10.1, "category": "Highly Mature", "description": "Comprehensive, stable, proven"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze support scheme quality for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Support Scheme for {country} ({period}) in {self.mode.value} mode")
            
            # Step 1: Fetch data
            data = self._fetch_data(country, period, **kwargs)
            
            # Step 2: Calculate score
            score = self._calculate_score(data, country, period)
            
            # Step 3: Validate score
            score = self._validate_score(score)
            
            # Step 4: Generate justification
            justification = self._generate_justification(data, score, country, period)
            
            # Step 5: Estimate confidence
            # AI-powered data uses AI's own confidence assessment
            if data.get('source') == 'ai_powered':
                data_quality = "high"
                ai_confidence = data.get('ai_confidence', 0.8)
                confidence = ai_confidence  # Use AI's confidence directly
            elif self.mode == AgentMode.RULE_BASED and data.get('source') == 'rule_based':
                data_quality = "medium"
                confidence = 0.70  # Moderate confidence for estimated data
            else:
                data_quality = "high"
                confidence = 0.85  # High confidence for assessed mock data

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
                f"Support Scheme analysis complete for {country}: "
                f"Score={score:.1f}, Category={data.get('category', 'Unknown')}, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Support Scheme analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Support Scheme analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch support scheme data.
        
        In MOCK mode: Returns mock support scheme assessments
        In RULE_BASED mode: Estimates from World Bank renewable energy indicators
        In AI_POWERED mode: Would use LLM to extract from policy documents (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with support scheme data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default basic support")
                data = {
                    "support_score": 5.0,
                    "category": "Basic",
                    "fit_quality": "Limited or none",
                    "auction_design": "Emerging",
                    "tax_incentives": "Limited",
                    "net_metering": "Limited or none",
                    "recs": "None",
                    "stability": "Moderate",
                    "key_schemes": ["Limited mechanisms"],
                    "status": "Basic support framework"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: support_score={data.get('support_score')}")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate support quality from World Bank data
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch renewable energy consumption (proxy for policy support)
                renewable_pct = self.data_service.get_value(
                    country=country,
                    indicator='renewable_consumption',
                    default=None
                )
                
                # Fetch renewable electricity output
                renewable_output = self.data_service.get_value(
                    country=country,
                    indicator='renewable_electricity_output',
                    default=None
                )
                
                # Fetch GDP per capita (development level correlates with support sophistication)
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch electricity production for context
                elec_production = self.data_service.get_value(
                    country=country,
                    indicator='electricity_production',
                    default=None
                )
                
                if renewable_pct is None or gdp_per_capita is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate support scheme quality
                support_score = self._estimate_support_quality(
                    country,
                    renewable_pct,
                    gdp_per_capita,
                    renewable_output,
                    elec_production
                )
                
                # Determine category and characteristics
                category = self._determine_support_category(support_score)
                status = self._determine_support_status(support_score, renewable_pct)
                
                data = {
                    'support_score': support_score,
                    'category': category,
                    'fit_quality': 'Estimated',
                    'auction_design': 'Estimated',
                    'tax_incentives': 'Estimated',
                    'net_metering': 'Estimated',
                    'recs': 'Unknown',
                    'stability': 'Estimated',
                    'key_schemes': ['Estimated from renewable adoption'],
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_renewable_pct': renewable_pct,
                    'raw_gdp_per_capita': gdp_per_capita
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: support_score={support_score:.1f} "
                    f"(renewable={renewable_pct:.1f}%, GDP/capita=${gdp_per_capita:,.0f})"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating support quality for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # Extract support scheme using AI extraction system
            try:
                from ai_extraction_system import AIExtractionAdapter

                adapter = AIExtractionAdapter(
                    llm_config=self.config.get('llm_config') if self.config else None,
                    cache_config=self.config.get('cache_config') if self.config else None
                )

                extraction_result = adapter.extract_parameter(
                    parameter_name='support_scheme',
                    country=country,
                    period=period,
                    documents=kwargs.get('documents'),
                    document_urls=kwargs.get('document_urls')
                )

                logger.info(f"Using AI_POWERED mode for {country}")

                if extraction_result and extraction_result.get('value') is not None:
                    score = float(extraction_result['value'])
                    metadata = extraction_result.get('metadata', {})
                    category = self._score_to_category(score)

                    data = {
                        'category': category,
                        'source': 'ai_powered',
                        'ai_confidence': extraction_result.get('confidence', 0.8),
                        'ai_justification': extraction_result.get('justification', ''),
                        'ai_score': score,
                        'fit_availability': metadata.get('fit_availability', 'Unknown'),
                        'auction_mechanism': metadata.get('auction_mechanism', 'Unknown'),
                        'policy_stability': metadata.get('policy_stability', 'Unknown'),
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
            "support_score": 5.0,
            "category": "Basic",
            "fit_quality": "Limited or none",
            "auction_design": "Emerging",
            "tax_incentives": "Limited",
            "net_metering": "Limited or none",
            "recs": "None",
            "stability": "Moderate",
            "key_schemes": ["Limited mechanisms"],
            "status": "Basic support framework"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_support_quality(
        self,
        country: str,
        renewable_pct: float,
        gdp_per_capita: float,
        renewable_output: Optional[float],
        elec_production: Optional[float]
    ) -> float:
        """Estimate support scheme quality from World Bank indicators.
        
        Higher renewable adoption + higher GDP = Better support frameworks
        
        Args:
            country: Country name
            renewable_pct: % renewable in energy consumption
            gdp_per_capita: GDP per capita in current USD
            renewable_output: Renewable electricity output (TWh)
            elec_production: Total electricity production (TWh)
            
        Returns:
            Estimated support quality score (1-10)
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Start with renewable penetration score
        if renewable_pct >= 60:
            # Very high renewable (Norway, Brazil, etc.)
            renewable_score = 8.5
        elif renewable_pct >= 40:
            # High renewable (implies strong support)
            renewable_score = 8.0
        elif renewable_pct >= 25:
            # Moderate-high renewable
            renewable_score = 7.0
        elif renewable_pct >= 15:
            # Moderate renewable
            renewable_score = 6.0
        elif renewable_pct >= 10:
            # Low-moderate renewable
            renewable_score = 5.0
        else:
            # Low renewable (weak support)
            renewable_score = 3.0
        
        # Adjust based on GDP per capita (wealthier = more sophisticated support)
        if gdp_per_capita >= 40000:
            # High income (Germany, UK, USA)
            gdp_adjustment = +1.5
        elif gdp_per_capita >= 15000:
            # Upper middle income (China, Brazil)
            gdp_adjustment = +0.5
        elif gdp_per_capita >= 5000:
            # Lower middle income (India)
            gdp_adjustment = 0.0
        else:
            # Low income (Nigeria)
            gdp_adjustment = -1.0
        
        # Calculate estimated score
        support_score = renewable_score + gdp_adjustment
        
        # Calibrate with mock data if available (60/40 blend - less confident in estimation)
        if base_data:
            base_score = base_data.get('support_score', support_score)
            support_score = support_score * 0.6 + base_score * 0.4
        
        # Clamp to valid range
        support_score = max(1.0, min(support_score, 10.0))
        
        logger.debug(
            f"Support quality estimation for {country}: "
            f"renewable={renewable_pct:.1f}% → renewable_score={renewable_score:.1f}, "
            f"GDP/capita=${gdp_per_capita:,.0f} → adj={gdp_adjustment:+.1f}, "
            f"final_score={support_score:.1f}"
        )
        
        return support_score
    
    def _determine_support_category(self, support_score: float) -> str:
        """Determine support category from score."""
        if support_score >= 9.5:
            return "Highly Mature"
        elif support_score >= 8.5:
            return "Strong but Not Scalable"
        elif support_score >= 7.5:
            return "Broad but Uneven"
        elif support_score >= 6.5:
            return "Solid but Uncertain"
        elif support_score >= 5.5:
            return "Developing"
        elif support_score >= 4.5:
            return "Basic"
        elif support_score >= 3.5:
            return "Boom-Bust"
        elif support_score >= 2.5:
            return "Forces Disadvantage"
        elif support_score >= 1.5:
            return "Emerging but Ineffective"
        else:
            return "Minimal or Absent"
    
    def _determine_support_status(self, support_score: float, renewable_pct: float) -> str:
        """Determine support status description."""
        if support_score >= 9:
            return f"Strong support framework with {renewable_pct:.1f}% renewable adoption"
        elif support_score >= 7:
            return f"Solid support mechanisms driving {renewable_pct:.1f}% renewable penetration"
        elif support_score >= 5:
            return f"Developing support framework with {renewable_pct:.1f}% renewable share"
        else:
            return f"Limited support mechanisms, {renewable_pct:.1f}% renewable adoption"

    def _score_to_category(self, score: float) -> str:
        """Convert numeric score (1-10) to category string.

        Used when AI provides score directly.

        Args:
            score: Score value 1-10

        Returns:
            Category description string
        """
        score = round(score)
        if score >= 10:
            return "comprehensive"
        elif score >= 9:
            return "very_strong"
        elif score >= 8:
            return "strong"
        elif score >= 7:
            return "good"
        elif score >= 6:
            return "moderate"
        elif score >= 5:
            return "developing"
        elif score >= 4:
            return "weak"
        else:
            return "minimal"

    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate support scheme score.

        DIRECT: Higher support quality = better framework = higher score

        Args:
            data: Support scheme data with support_score (or ai_score for AI mode)
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

        support_score = data.get("support_score", 5.0)
        
        logger.debug(f"Calculating score for {country}: {support_score:.1f} support quality")
        
        # Find matching rubric level
        for level in self.scoring_rubric:
            min_val = level.get("min_support", 0.0)
            max_val = level.get("max_support", 10.1)
            
            if min_val <= support_score < max_val:
                score = level["score"]
                logger.debug(
                    f"Score {score} assigned: "
                    f"{support_score:.1f} falls in range {min_val:.1f}-{max_val:.1f}"
                )
                return float(score)
        
        # Fallback
        logger.warning(f"No rubric match for {support_score:.1f}, defaulting to score 5")
        return 5.0
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the support scheme score.

        Args:
            data: Support scheme data
            score: Calculated score
            country: Country name
            period: Time period

        Returns:
            Human-readable justification string
        """
        # For AI-powered mode, use AI justification directly
        if data.get('source') == 'ai_powered':
            ai_justification = data.get('ai_justification', '')
            if ai_justification:
                return ai_justification
            # Fallback if AI didn't provide justification
            else:
                category = data.get('category', 'moderate')
                return (
                    f"AI-extracted support scheme score of {score}/10 indicates {category} policy framework. "
                    f"Renewable energy support mechanisms are {'well-established' if score >= 8 else 'developing' if score >= 6 else 'limited'}."
                )

        support_score = data.get("support_score", 5.0)
        category = data.get("category", "Unknown")
        fit_quality = data.get("fit_quality", "unknown")
        auction_design = data.get("auction_design", "unknown")
        tax_incentives = data.get("tax_incentives", "unknown")
        net_metering = data.get("net_metering", "unknown")
        stability = data.get("stability", "moderate")
        status = data.get("status", "unknown")
        source = data.get("source", "unknown")
        
        # Find description from rubric
        description = "basic support"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level["description"].lower()
                break
        
        # Build justification based on source
        if source == 'rule_based':
            renewable_pct = data.get('raw_renewable_pct', 0)
            gdp = data.get('raw_gdp_per_capita', 0)
            justification = (
                f"Based on World Bank data: Estimated support scheme quality of {support_score:.1f}/10 "
                f"(Category: {category}) derived from {renewable_pct:.1f}% renewable adoption "
                f"and GDP/capita ${gdp:,.0f}, indicating {description}. "
                f"{status}. "
            )
        else:
            # Mock data - use detailed assessments
            key_schemes = data.get('key_schemes', [])
            schemes_str = ', '.join(key_schemes[:3]) if key_schemes else "various mechanisms"
            
            justification = (
                f"Support scheme quality of {support_score:.1f}/10 (Category: {category}) indicates {description}. "
                f"Key mechanisms include: {schemes_str}. "
                f"FiT quality: {fit_quality}, Auction design: {auction_design}, "
                f"Tax incentives: {tax_incentives}, Net metering: {net_metering}. "
                f"Policy stability: {stability}. {status}. "
            )
        
        justification += (
            f"This support framework {'strongly' if score >= 8 else 'adequately' if score >= 6 else 'partially'} "
            f"enables renewable energy project development through revenue certainty and risk reduction."
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
            sources.append("World Bank Renewable Energy Indicators - Rule-Based Estimation")
            sources.append("IEA Renewable Energy Policies (Reference)")
        else:
            sources.append(f"{country} Energy Ministry - Mock Data")
            sources.append("IEA Renewable Energy Policies database")
        
        sources.append("IRENA Policy and Regulation database")
        sources.append("REN21 Renewables Global Status Report")
        
        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Support Scheme parameter.
        
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
            "IEA Renewable Energy Policies database",
            "IRENA Policy and Regulation database",
            "REN21 Renewables Global Status Report",
            "National energy ministry policy documents",
            "World Bank renewable energy indicators",
            "Country-specific FiT/auction schedules"
        ]


def analyze_support_scheme(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze support scheme quality.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = SupportSchemeAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
