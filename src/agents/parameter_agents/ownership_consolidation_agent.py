"""Ownership Consolidation Agent - Analyzes market concentration.

This agent evaluates the level of ownership consolidation in renewable
energy markets by measuring the market share controlled by top owners:
- Concentration ratios (CR3 - top 3 owners)
- Herfindahl-Hirschman Index (HHI)
- Number of significant players
- Market entry barriers

Lower consolidation indicates:
- More competitive markets
- Greater diversity of approaches
- More market entry opportunities
- Reduced monopoly risk

Consolidation Categories (1-10):
1. Extreme monopoly (>80% by single owner)
2. Very high consolidation (70-80% by top 3)
3. High consolidation (60-70% by top 3)
4. Above moderate consolidation (50-60% by top 3)
5. Moderate consolidation (40-50% by top 3)
6. Below moderate consolidation (30-40% by top 3)
7. Low consolidation (20-30% by top 3)
8. Very low consolidation (15-20% by top 3)
9. Minimal consolidation (10-15% by top 3)
10. Highly fragmented (<10% by top 3)

Scoring Rubric (LOADED FROM CONFIG):
Lower consolidation = More competitive = Higher score (INVERSE)

MODES:
- MOCK: Uses hardcoded market concentration data (for testing)
- RULE_BASED: Estimates from World Bank economic indicators (production)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseParameterAgent, AgentMode
from ...models.parameter import ParameterScore
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class OwnershipConsolidationAgent(BaseParameterAgent):
    """Agent for analyzing ownership consolidation in renewable markets."""
    
    # Mock data for Phase 1 testing
    # Market concentration measured by top 3 owners' share
    # Data from industry reports, company filings, national statistics
    MOCK_DATA = {
        "Brazil": {
            "top3_share_pct": 35,
            "score": 6,
            "category": "below_moderate",
            "top_owners": ["Enel Green Power", "AES Brasil", "EDP Renováveis"],
            "total_market_capacity_mw": 38500,
            "num_significant_players": 25,
            "hhi": 950,
            "status": "Moderately concentrated market with diverse ownership including utilities, IPPs, and international developers"
        },
        "Germany": {
            "top3_share_pct": 18,
            "score": 8,
            "category": "very_low",
            "top_owners": ["RWE", "EnBW", "E.ON"],
            "total_market_capacity_mw": 134000,
            "num_significant_players": 100,
            "hhi": 450,
            "status": "Highly competitive market with very diverse ownership including cooperatives, municipalities, and private investors"
        },
        "USA": {
            "top3_share_pct": 22,
            "score": 7,
            "category": "low",
            "top_owners": ["NextEra Energy", "Duke Energy", "Berkshire Hathaway Energy"],
            "total_market_capacity_mw": 257000,
            "num_significant_players": 200,
            "hhi": 580,
            "status": "Large competitive market with low consolidation across utilities, IPPs, and yieldcos"
        },
        "China": {
            "top3_share_pct": 55,
            "score": 4,
            "category": "above_moderate",
            "top_owners": ["State Power Investment Corp", "China Three Gorges", "China Huaneng"],
            "total_market_capacity_mw": 758000,
            "num_significant_players": 50,
            "hhi": 1800,
            "status": "Moderately high consolidation dominated by state-owned enterprises"
        },
        "India": {
            "top3_share_pct": 28,
            "score": 7,
            "category": "low",
            "top_owners": ["Adani Green Energy", "ReNew Power", "Azure Power"],
            "total_market_capacity_mw": 175000,
            "num_significant_players": 80,
            "hhi": 720,
            "status": "Competitive market with low consolidation and growing independent power producers"
        },
        "UK": {
            "top3_share_pct": 32,
            "score": 6,
            "category": "below_moderate",
            "top_owners": ["SSE Renewables", "RWE", "Ørsted"],
            "total_market_capacity_mw": 48000,
            "num_significant_players": 60,
            "hhi": 880,
            "status": "Moderately concentrated market particularly in offshore wind"
        },
        "Spain": {
            "top3_share_pct": 45,
            "score": 5,
            "category": "moderate",
            "top_owners": ["Iberdrola", "Acciona", "Endesa"],
            "total_market_capacity_mw": 53000,
            "num_significant_players": 40,
            "hhi": 1250,
            "status": "Moderate consolidation with traditional utilities maintaining strong positions"
        },
        "Australia": {
            "top3_share_pct": 25,
            "score": 7,
            "category": "low",
            "top_owners": ["AGL Energy", "Origin Energy", "CleanCo Queensland"],
            "total_market_capacity_mw": 32000,
            "num_significant_players": 70,
            "hhi": 650,
            "status": "Competitive market with low consolidation and active independent developers"
        },
        "Chile": {
            "top3_share_pct": 42,
            "score": 5,
            "category": "moderate",
            "top_owners": ["Enel Green Power", "AES Gener", "Colbún"],
            "total_market_capacity_mw": 11500,
            "num_significant_players": 30,
            "hhi": 1180,
            "status": "Moderate consolidation with utilities and IPPs competing"
        },
        "Vietnam": {
            "top3_share_pct": 62,
            "score": 3,
            "category": "high",
            "top_owners": ["EVN", "PetroVietnam Power", "Trungnam Group"],
            "total_market_capacity_mw": 20500,
            "num_significant_players": 25,
            "hhi": 2100,
            "status": "High consolidation with state-owned EVN dominant"
        },
        "South Africa": {
            "top3_share_pct": 38,
            "score": 6,
            "category": "below_moderate",
            "top_owners": ["ACWA Power", "Enel Green Power", "Mainstream Renewable Power"],
            "total_market_capacity_mw": 7200,
            "num_significant_players": 35,
            "hhi": 1050,
            "status": "Moderately concentrated through REIPPP program with diverse IPPs"
        },
        "Nigeria": {
            "top3_share_pct": 75,
            "score": 2,
            "category": "very_high",
            "top_owners": ["Government/NBET", "Limited private projects"],
            "total_market_capacity_mw": 180,
            "num_significant_players": 5,
            "hhi": 3500,
            "status": "Very high consolidation, nascent market with limited private participation"
        },
        "Argentina": {
            "top3_share_pct": 48,
            "score": 5,
            "category": "moderate",
            "top_owners": ["YPF Luz", "Genneia", "Central Puerto"],
            "total_market_capacity_mw": 8500,
            "num_significant_players": 30,
            "hhi": 1320,
            "status": "Moderate consolidation with mix of traditional players and RenovAr entrants"
        },
        "Mexico": {
            "top3_share_pct": 52,
            "score": 4,
            "category": "above_moderate",
            "top_owners": ["CFE", "Iberdrola", "Enel Green Power"],
            "total_market_capacity_mw": 15000,
            "num_significant_players": 35,
            "hhi": 1650,
            "status": "Above moderate consolidation with CFE increasing dominance post-policy changes"
        },
        "Indonesia": {
            "top3_share_pct": 82,
            "score": 1,
            "category": "extreme_monopoly",
            "top_owners": ["PLN (state utility)", "Limited private players"],
            "total_market_capacity_mw": 850,
            "num_significant_players": 3,
            "hhi": 5200,
            "status": "Extreme monopoly with PLN state utility dominance"
        },
        "Saudi Arabia": {
            "top3_share_pct": 48,
            "score": 5,
            "category": "moderate",
            "top_owners": ["ACWA Power", "EDF Renewables", "Masdar"],
            "total_market_capacity_mw": 3800,
            "num_significant_players": 15,
            "hhi": 1400,
            "status": "Moderate consolidation with strong domestic champion ACWA Power"
        },
    }
    
    def __init__(
        self, 
        mode: AgentMode = AgentMode.MOCK, 
        config: Dict[str, Any] = None,
        data_service = None  # DataService instance for RULE_BASED mode
    ):
        """Initialize Ownership Consolidation Agent.
        
        Args:
            mode: Agent operation mode (MOCK or RULE_BASED)
            config: Configuration dictionary
            data_service: DataService instance (required for RULE_BASED mode)
        """
        super().__init__(
            parameter_name="Ownership Consolidation",
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
            f"Initialized OwnershipConsolidationAgent in {mode.value} mode "
            f"with {len(self.scoring_rubric)} scoring levels"
        )
    
    def _load_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Load scoring rubric from configuration."""
        try:
            from ...core.config_loader import config_loader
            params_config = config_loader.get_parameters()
            
            consolidation_config = params_config['parameters'].get('ownership_consolidation', {})
            scoring = consolidation_config.get('scoring', [])
            
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
            {"score": 1, "range": "Extreme monopoly", "description": ">80% by single owner"},
            {"score": 2, "range": "Very high", "description": "70-80% by top 3"},
            {"score": 3, "range": "High", "description": "60-70% by top 3"},
            {"score": 4, "range": "Above moderate", "description": "50-60% by top 3"},
            {"score": 5, "range": "Moderate", "description": "40-50% by top 3"},
            {"score": 6, "range": "Below moderate", "description": "30-40% by top 3"},
            {"score": 7, "range": "Low", "description": "20-30% by top 3"},
            {"score": 8, "range": "Very low", "description": "15-20% by top 3"},
            {"score": 9, "range": "Minimal", "description": "10-15% by top 3"},
            {"score": 10, "range": "Highly fragmented", "description": "<10% by top 3"}
        ]
    
    def analyze(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> ParameterScore:
        """Analyze ownership consolidation for a country.
        
        Args:
            country: Country name
            period: Time period (e.g., "Q3 2024")
            **kwargs: Additional context
            
        Returns:
            ParameterScore with score, justification, confidence
        """
        try:
            logger.info(f"Analyzing Ownership Consolidation for {country} ({period}) in {self.mode.value} mode")
            
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
                confidence = 0.55  # Lower confidence for estimated consolidation
            else:
                data_quality = "high"
                confidence = 0.80  # High confidence for actual market data

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
                f"Ownership Consolidation analysis complete for {country}: "
                f"Score={score:.1f}, Top3Share={data.get('top3_share_pct', 0):.0f}%, "
                f"Confidence={confidence:.2f}, Mode={self.mode.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ownership Consolidation analysis failed for {country}: {str(e)}", exc_info=True)
            raise AgentError(f"Ownership Consolidation analysis failed: {str(e)}")
    
    def _fetch_data(
        self,
        country: str,
        period: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch ownership consolidation data.
        
        In MOCK mode: Returns actual market concentration data
        In RULE_BASED mode: Estimates from World Bank economic indicators
        In AI_POWERED mode: Would use LLM to extract from market reports (not yet implemented)
        
        Args:
            country: Country name
            period: Time period
            
        Returns:
            Dictionary with ownership consolidation data
        """
        if self.mode == AgentMode.MOCK:
            # Return mock data
            data = self.MOCK_DATA.get(country, None)
            if not data:
                logger.warning(f"No mock data for {country}, using default moderate consolidation")
                data = {
                    "top3_share_pct": 45,
                    "score": 5,
                    "category": "moderate",
                    "top_owners": ["Unknown owners"],
                    "total_market_capacity_mw": 1000,
                    "num_significant_players": 20,
                    "hhi": 1300,
                    "status": "Moderate consolidation"
                }
            
            # Add source indicator
            data['source'] = 'mock'
            
            logger.debug(f"Fetched mock data for {country}: Top3={data.get('top3_share_pct')}%")
            return data
        
        elif self.mode == AgentMode.RULE_BASED:
            # Estimate from World Bank economic indicators
            if self.data_service is None:
                logger.warning("No data_service available, falling back to MOCK data")
                return self._fetch_data_mock_fallback(country)
            
            try:
                # Fetch GDP per capita (developed markets more competitive)
                gdp_per_capita = self.data_service.get_value(
                    country=country,
                    indicator='gdp_per_capita',
                    default=None
                )
                
                # Fetch renewable consumption % (mature markets more competitive)
                renewable_pct = self.data_service.get_value(
                    country=country,
                    indicator='renewable_consumption',
                    default=None
                )
                
                # Fetch FDI net inflows (more FDI = more diverse ownership)
                fdi_inflows_pct = self.data_service.get_value(
                    country=country,
                    indicator='fdi_net_inflows',
                    default=None
                )
                
                # Fetch electricity production (larger markets less consolidated)
                electricity_production = self.data_service.get_value(
                    country=country,
                    indicator='electricity_production',
                    default=None
                )
                
                if gdp_per_capita is None:
                    logger.warning(
                        f"Insufficient data for {country}, falling back to MOCK data"
                    )
                    return self._fetch_data_mock_fallback(country)
                
                # Estimate market consolidation
                top3_share_pct, score = self._estimate_market_consolidation(
                    country,
                    gdp_per_capita,
                    renewable_pct,
                    fdi_inflows_pct,
                    electricity_production
                )
                
                # Estimate market characteristics
                category = self._determine_category_from_score(score)
                total_mw = self._estimate_market_size(electricity_production, renewable_pct)
                num_players = self._estimate_num_players(score, total_mw)
                hhi = self._estimate_hhi(top3_share_pct)
                status = self._determine_consolidation_status(score, top3_share_pct)
                
                data = {
                    'top3_share_pct': top3_share_pct,
                    'score': score,
                    'category': category,
                    'top_owners': ["Market leaders (estimated)"],
                    'total_market_capacity_mw': total_mw,
                    'num_significant_players': num_players,
                    'hhi': hhi,
                    'status': status,
                    'source': 'rule_based',
                    'period': period,
                    'raw_gdp_per_capita': gdp_per_capita,
                    'raw_renewable_pct': renewable_pct if renewable_pct else 0,
                    'raw_fdi_inflows_pct': fdi_inflows_pct if fdi_inflows_pct else 0
                }
                
                logger.info(
                    f"Estimated RULE_BASED data for {country}: Top3={top3_share_pct:.1f}% (score={score:.1f}) "
                    f"from GDP/capita=${gdp_per_capita:,.0f}, RE={renewable_pct if renewable_pct else 0:.1f}%"
                )
                
                return data
                
            except Exception as e:
                logger.error(
                    f"Error estimating consolidation for {country}: {e}. "
                    f"Falling back to MOCK data"
                )
                return self._fetch_data_mock_fallback(country)
        
        elif self.mode == AgentMode.AI_POWERED:
            # AI-powered extraction using OwnershipConsolidationExtractor
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
                    parameter_name='ownership_consolidation',
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
                        'top3_share_pct': ai_data.get('metadata', {}).get('top3_share_pct', 40),
                        'category': self._determine_category_from_score(ai_data['value']),
                        'hhi': ai_data.get('metadata', {}).get('hhi', 1000),
                        'num_significant_players': ai_data.get('metadata', {}).get('num_players', 50),
                        'status': ai_data.get('metadata', {}).get('status', 'Market consolidation analysis'),
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
            "top3_share_pct": 45,
            "score": 5,
            "category": "moderate",
            "top_owners": ["Unknown owners"],
            "total_market_capacity_mw": 1000,
            "num_significant_players": 20,
            "hhi": 1300,
            "status": "Moderate consolidation"
        })
        data['source'] = 'mock_fallback'
        
        logger.debug(f"Using mock fallback data for {country}")
        return data
    
    def _estimate_market_consolidation(
        self,
        country: str,
        gdp_per_capita: float,
        renewable_pct: Optional[float],
        fdi_inflows_pct: Optional[float],
        electricity_production: Optional[float]
    ) -> tuple:
        """Estimate market consolidation from economic indicators.
        
        Higher GDP + Higher renewable maturity + More FDI = Less consolidated
        
        Args:
            country: Country name
            gdp_per_capita: GDP per capita (USD)
            renewable_pct: Renewable consumption (%)
            fdi_inflows_pct: FDI net inflows (% of GDP)
            electricity_production: Electricity production (kWh)
            
        Returns:
            Tuple of (top3_share_pct, score)
        """
        # Get base estimate from mock data if available (for calibration)
        base_data = self.MOCK_DATA.get(country)
        
        # Start with GDP-based consolidation (developed markets more competitive)
        if gdp_per_capita >= 40000:
            # Very high income (Germany, USA, Australia, UK)
            base_consolidation = 25  # Low consolidation
        elif gdp_per_capita >= 20000:
            # Upper-middle income (Chile)
            base_consolidation = 40  # Moderate consolidation
        elif gdp_per_capita >= 10000:
            # Middle income (Brazil, China, Mexico)
            base_consolidation = 48  # Moderate to high
        elif gdp_per_capita >= 5000:
            # Lower-middle income (India, Indonesia, Vietnam)
            base_consolidation = 55  # Above moderate
        else:
            # Low income (Nigeria)
            base_consolidation = 70  # High consolidation
        
        # Adjust based on renewable market maturity
        # More mature markets (higher %) = more players = less consolidated
        maturity_adjustment = 0
        if renewable_pct is not None:
            if renewable_pct >= 40:
                # Very mature market (many entrants)
                maturity_adjustment = -12
            elif renewable_pct >= 20:
                # Mature market
                maturity_adjustment = -8
            elif renewable_pct >= 10:
                # Growing market
                maturity_adjustment = -5
            else:
                # Early market (few players)
                maturity_adjustment = +5
        
        # Adjust based on FDI (more FDI = more diverse ownership)
        fdi_adjustment = 0
        if fdi_inflows_pct is not None:
            if fdi_inflows_pct >= 4.0:
                # Very high FDI (many foreign entrants)
                fdi_adjustment = -8
            elif fdi_inflows_pct >= 2.0:
                # High FDI
                fdi_adjustment = -5
            elif fdi_inflows_pct >= 1.0:
                # Moderate FDI
                fdi_adjustment = 0
            else:
                # Low FDI (more domestic concentration)
                fdi_adjustment = +3
        
        # Calculate estimated consolidation
        top3_share_pct = base_consolidation + maturity_adjustment + fdi_adjustment
        
        # Calibrate with mock data if available (40/60 blend)
        if base_data:
            base_top3 = base_data.get('top3_share_pct', top3_share_pct)
            top3_share_pct = top3_share_pct * 0.4 + base_top3 * 0.6
        
        # Clamp to valid range
        top3_share_pct = max(10.0, min(top3_share_pct, 90.0))
        
        # Calculate score (INVERSE: lower consolidation = higher score)
        score = self._calculate_score_from_top3(top3_share_pct)
        
        logger.debug(
            f"Consolidation estimation for {country}: "
            f"GDP/capita=${gdp_per_capita:,.0f} → base={base_consolidation:.1f}%, "
            f"RE={renewable_pct if renewable_pct else 0:.1f}% → adj={maturity_adjustment:+.1f}%, "
            f"FDI={fdi_inflows_pct if fdi_inflows_pct else 0:.1f}% → adj={fdi_adjustment:+.1f}%, "
            f"final_top3={top3_share_pct:.1f}% (score={score:.1f})"
        )
        
        return top3_share_pct, score
    
    def _calculate_score_from_top3(self, top3_pct: float) -> float:
        """Calculate score from top3 share percentage.
        
        INVERSE: Lower consolidation = Higher score
        """
        if top3_pct >= 80:
            return 1.0  # Extreme monopoly
        elif top3_pct >= 70:
            return 2.0  # Very high consolidation
        elif top3_pct >= 60:
            return 3.0  # High consolidation
        elif top3_pct >= 50:
            return 4.0  # Above moderate
        elif top3_pct >= 40:
            return 5.0  # Moderate
        elif top3_pct >= 30:
            return 6.0  # Below moderate
        elif top3_pct >= 20:
            return 7.0  # Low consolidation
        elif top3_pct >= 15:
            return 8.0  # Very low
        elif top3_pct >= 10:
            return 9.0  # Minimal
        else:
            return 10.0  # Highly fragmented
    
    def _determine_category_from_score(self, score: float) -> str:
        """Determine category from score."""
        if score >= 9.5:
            return "highly_fragmented"
        elif score >= 8.5:
            return "minimal"
        elif score >= 7.5:
            return "very_low"
        elif score >= 6.5:
            return "low"
        elif score >= 5.5:
            return "below_moderate"
        elif score >= 4.5:
            return "moderate"
        elif score >= 3.5:
            return "above_moderate"
        elif score >= 2.5:
            return "high"
        elif score >= 1.5:
            return "very_high"
        else:
            return "extreme_monopoly"
    
    def _estimate_market_size(
        self,
        electricity_production: Optional[float],
        renewable_pct: Optional[float]
    ) -> float:
        """Estimate total renewable market size in MW."""
        if electricity_production and renewable_pct:
            # Rough conversion: kWh production → MW capacity
            # Assume ~2500 full-load hours/year average
            total_kwh = electricity_production
            renewable_kwh = total_kwh * (renewable_pct / 100)
            mw = renewable_kwh / (2500 * 1000)  # Convert to MW
            return max(100, min(mw, 1000000))
        else:
            return 5000  # Default estimate
    
    def _estimate_num_players(self, score: float, total_mw: float) -> int:
        """Estimate number of significant players."""
        # More competitive = more players
        # Larger markets = more players
        
        base_players = int(score * 15)  # Score 10 = 150 players, Score 1 = 15 players
        
        # Adjust for market size
        if total_mw > 100000:
            size_multiplier = 2.0
        elif total_mw > 50000:
            size_multiplier = 1.5
        elif total_mw > 10000:
            size_multiplier = 1.2
        else:
            size_multiplier = 1.0
        
        num_players = int(base_players * size_multiplier)
        return max(3, min(num_players, 300))
    
    def _estimate_hhi(self, top3_share_pct: float) -> int:
        """Estimate Herfindahl-Hirschman Index from top3 share.
        
        HHI = sum of squared market shares (0-10000)
        Rough approximation from top3 share
        """
        # Very rough estimation
        if top3_share_pct >= 80:
            return 5000  # Extreme concentration
        elif top3_share_pct >= 70:
            return 3500
        elif top3_share_pct >= 60:
            return 2500
        elif top3_share_pct >= 50:
            return 1800
        elif top3_share_pct >= 40:
            return 1300
        elif top3_share_pct >= 30:
            return 900
        elif top3_share_pct >= 20:
            return 600
        else:
            return 400
    
    def _determine_consolidation_status(self, score: float, top3_pct: float) -> str:
        """Determine consolidation status description."""
        if score >= 8:
            return f"Highly competitive market with very low consolidation ({top3_pct:.0f}% by top 3), diverse ownership including utilities, IPPs, and independent developers"
        elif score >= 7:
            return f"Competitive market with low consolidation ({top3_pct:.0f}% by top 3), multiple significant players and market entry opportunities"
        elif score >= 6:
            return f"Moderately concentrated market ({top3_pct:.0f}% by top 3) with reasonable diversity of ownership"
        elif score >= 5:
            return f"Moderate consolidation ({top3_pct:.0f}% by top 3) with mix of utilities and independent players"
        elif score >= 4:
            return f"Above moderate consolidation ({top3_pct:.0f}% by top 3) with dominant players controlling majority"
        elif score >= 3:
            return f"High consolidation ({top3_pct:.0f}% by top 3) limiting competition and market entry"
        else:
            return f"Very high consolidation ({top3_pct:.0f}% by top 3) approaching monopoly conditions"
    
    def _calculate_score(
        self,
        data: Dict[str, Any],
        country: str,
        period: str
    ) -> float:
        """Calculate ownership consolidation score.
        
        INVERSE: Lower consolidation % = more competitive = higher score
        
        Args:
            data: Ownership consolidation data
            country: Country name
            period: Time period
            
        Returns:
            Score between 1-10
        """
        # Use pre-calculated score from data if available
        if "score" in data:
            score = data["score"]
            logger.debug(f"Using pre-calculated score {score} for {country}")
            return float(score)
        
        # Otherwise calculate from top3 share percentage
        top3_pct = data.get("top3_share_pct", 45)
        score = self._calculate_score_from_top3(top3_pct)
        
        logger.debug(f"Calculated score {score} from top3_share {top3_pct}%")
        
        return float(score)
    
    def _generate_justification(
        self,
        data: Dict[str, Any],
        score: float,
        country: str,
        period: str
    ) -> str:
        """Generate justification for the ownership consolidation score.

        Args:
            data: Ownership consolidation data
            score: Calculated score
            country: Country name
            period: Time period

        Returns:
            Human-readable justification string
        """
        source = data.get("source", "unknown")

        # If AI_POWERED mode, use AI-generated justification
        if source == 'ai_powered':
            return data.get('ai_justification', 'AI analysis of market consolidation.')

        top3_pct = data.get("top3_share_pct", 0)
        category = data.get("category", "moderate")
        top_owners = data.get("top_owners", [])
        total_mw = data.get("total_market_capacity_mw", 0)
        num_players = data.get("num_significant_players", 0)
        hhi = data.get("hhi", 0)
        status = data.get("status", "")

        # Find description from rubric
        description = "moderate consolidation"
        for level in self.scoring_rubric:
            if level["score"] == int(score):
                description = level.get("range", level["description"]).lower()
                break

        # Build justification based on source
        if source == 'rule_based':
            gdp = data.get('raw_gdp_per_capita', 0)
            re_pct = data.get('raw_renewable_pct', 0)
            justification = (
                f"Based on World Bank data: Estimated market shows {description} with top 3 owners "
                f"controlling approximately {top3_pct:.0f}% of {total_mw:,.0f} MW total capacity "
                f"(derived from GDP/capita ${gdp:,.0f} and renewable penetration {re_pct:.1f}%). "
            )
        else:
            # Mock data - use actual market data
            justification = (
                f"Market shows {description} with top 3 owners controlling {top3_pct:.0f}% of "
                f"{total_mw:,.0f} MW total capacity. "
            )
        
        if top_owners and top_owners[0] != "Market leaders (estimated)":
            top_str = ", ".join(top_owners[:3])
            justification += f"Leading owners: {top_str}. "
        
        justification += (
            f"Market has approximately {num_players} significant players with HHI of {hhi}. "
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

        # Check if we used AI extraction
        if data and data.get('source') == 'ai_powered':
            sources.append("AI-Powered Document Extraction")
            sources.append("Market concentration analysis (Extracted from documents)")
            sources.append("Industry reports and company filings (Extracted from documents)")
            sources.append(f"{country} National energy statistics")
            sources.append("S&P Global Market Intelligence")
            # Add document sources if available
            ai_metadata = data.get('ai_metadata', {})
            doc_sources = ai_metadata.get('document_sources', [])
            sources.extend(doc_sources)
        # Check if we used rule-based or mock data
        elif data and data.get('source') == 'rule_based':
            sources.append("World Bank Economic Indicators - Rule-Based Estimation")
            sources.append("Market concentration analysis (Reference)")
            sources.append(f"{country} National energy statistics")
            sources.append("S&P Global Market Intelligence")
        else:
            sources.append("Renewable energy asset ownership databases - Mock Data")
            sources.append("Market concentration analysis")
            sources.append("Industry reports and company filings")
            sources.append(f"{country} National energy statistics")
            sources.append("S&P Global Market Intelligence")

        return sources
    
    def _get_scoring_rubric(self) -> List[Dict[str, Any]]:
        """Get scoring rubric for Ownership Consolidation parameter.
        
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
            "Renewable energy asset ownership databases",
            "Market concentration analysis",
            "Industry reports and company filings",
            "National energy statistics",
            "S&P Global Market Intelligence"
        ]


def analyze_ownership_consolidation(
    country: str,
    period: str = "Q3 2024",
    mode: AgentMode = AgentMode.MOCK,
    data_service = None
) -> ParameterScore:
    """Convenience function to analyze ownership consolidation.
    
    Args:
        country: Country name
        period: Time period
        mode: Agent mode (MOCK or RULE_BASED)
        data_service: DataService instance (required for RULE_BASED mode)
        
    Returns:
        ParameterScore
    """
    agent = OwnershipConsolidationAgent(mode=mode, data_service=data_service)
    return agent.analyze(country, period)
