"""Global Rankings Agent - Produces global rankings with tier assignments.

This is the third and final synthesis agent (Level III) that:
- Analyzes ALL countries to produce complete global rankings
- Assigns performance tiers (A/B/C/D) based on overall scores
- Calculates tier statistics and identifies transitions
- Provides comprehensive global market overview

Architecture: GlobalRankingsAgent → CountryAnalysisAgent → AgentService (18 parameter agents)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from statistics import mean

from .country_analysis_agent import CountryAnalysisAgent
from ..base_agent import AgentMode
from ...models.global_rankings import (
    GlobalRankings,
    CountryRanking,
    TierStatistics,
    TierTransition,
    Tier
)
from ...core.logger import get_logger
from ...core.exceptions import AgentError

logger = get_logger(__name__)


class GlobalRankingsAgent:
    """Agent for generating global rankings with tier assignments."""
    
    def __init__(self, mode: AgentMode = AgentMode.MOCK, config: Dict[str, Any] = None):
        """Initialize Global Rankings Agent.
        
        Args:
            mode: Agent operation mode (MOCK, RULE_BASED, AI_POWERED)
            config: Optional configuration dictionary
        """
        self.mode = mode
        self.config = config or {}
        self.country_agent = CountryAnalysisAgent(mode=mode, config=config)
        
        # Load configuration with defaults
        global_config = self.config.get('global_rankings', {})
        
        # Tier thresholds
        tier_thresholds = global_config.get('tier_thresholds', {})
        self.tier_a_min = tier_thresholds.get('tier_a_min', 8.0)
        self.tier_b_min = tier_thresholds.get('tier_b_min', 6.5)
        self.tier_c_min = tier_thresholds.get('tier_c_min', 5.0)
        
        # Display settings
        display = global_config.get('ranking_display', {})
        self.countries_per_tier = display.get('countries_per_tier', 10)
        self.show_tier_stats = display.get('show_tier_statistics', True)
        self.include_transitions = display.get('include_tier_transitions', False)
        
        # Summary settings
        summary = global_config.get('summary', {})
        self.highlight_top_n = summary.get('highlight_top_performers', 5)
        self.highlight_bottom_n = summary.get('highlight_bottom_performers', 3)
        self.mention_movers = summary.get('mention_tier_movers', True)
        
        logger.info(f"Initialized GlobalRankingsAgent in {mode} mode")
        logger.info(f"Tier thresholds: A>={self.tier_a_min}, B>={self.tier_b_min}, C>={self.tier_c_min}")
    
    def generate_rankings(
        self,
        countries: List[str],
        period: str = "Q3 2024",
        previous_rankings: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> GlobalRankings:
        """Generate global rankings for all countries.
        
        Args:
            countries: List of country names to rank
            period: Time period for analysis
            previous_rankings: Optional previous period rankings for transition analysis
            **kwargs: Additional options
        
        Returns:
            GlobalRankings object with complete analysis
        
        Raises:
            AgentError: If validation fails or analysis errors occur
        """
        try:
            # Validation
            if not countries:
                raise AgentError("Must provide at least one country to rank")
            
            min_countries = self.config.get('global_rankings', {}).get('min_countries_for_ranking', 1)
            if len(countries) < min_countries:
                raise AgentError(
                    f"Global rankings require at least {min_countries} countries, got {len(countries)}"
                )
            
            logger.info(f"Generating global rankings for {len(countries)} countries")
            
            # Step 1: Analyze all countries
            country_analyses = {}
            for country in countries:
                logger.debug(f"Analyzing {country}...")
                analysis = self.country_agent.analyze(country=country, period=period)
                country_analyses[country] = analysis
            
            # Step 2: Create rankings with tier assignments
            rankings = self._create_rankings(country_analyses, period)
            
            # Step 3: Calculate tier statistics
            tier_stats = self._calculate_tier_statistics(rankings)
            
            # Step 4: Identify tier transitions
            transitions = self._identify_transitions(
                rankings, 
                previous_rankings
            ) if previous_rankings else []
            
            # Step 5: Generate summary
            summary = self._generate_summary(rankings, tier_stats, transitions)
            
            # Create final result
            result = GlobalRankings(
                rankings=rankings,
                tier_statistics=tier_stats,
                tier_transitions=transitions,
                period=period,
                total_countries=len(countries),
                summary=summary,
                metadata={
                    'mode': self.mode.value,
                    'tier_thresholds': {
                        'A': f'>= {self.tier_a_min}',
                        'B': f'{self.tier_b_min} - {self.tier_a_min - 0.01}',
                        'C': f'{self.tier_c_min} - {self.tier_b_min - 0.01}',
                        'D': f'< {self.tier_c_min}'
                    }
                }
            )
            
            logger.info(f"Generated global rankings: {len(rankings)} countries, {len(tier_stats)} tiers")
            return result
            
        except Exception as e:
            logger.error(f"Error generating global rankings: {str(e)}")
            raise AgentError(f"Failed to generate global rankings: {str(e)}")
    
    def _create_rankings(
        self,
        country_analyses: Dict[str, Any],
        period: str
    ) -> List[CountryRanking]:
        """Create ranked list with tier assignments.
        
        Args:
            country_analyses: Dictionary mapping countries to their analyses
            period: Time period
        
        Returns:
            Sorted list of CountryRanking objects
        """
        # Extract scores and create preliminary rankings
        country_scores = []
        for country, analysis in country_analyses.items():
            country_scores.append({
                'country': country,
                'score': analysis.overall_score,
                'analysis': analysis
            })
        
        # Sort by score (descending)
        country_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Assign ranks and tiers
        rankings = []
        for rank, item in enumerate(country_scores, start=1):
            tier = self._assign_tier(item['score'])
            analysis = item['analysis']
            
            # Convert subcategory scores to dict
            subcategory_score_dict = {
                sc.name: sc.score for sc in analysis.subcategory_scores
            }
            
            ranking = CountryRanking(
                rank=rank,
                country=item['country'],
                overall_score=item['score'],
                tier=tier,
                subcategory_scores=subcategory_score_dict,
                strengths=[sw.area for sw in analysis.strengths],
                weaknesses=[sw.area for sw in analysis.weaknesses],
                period=period
            )
            rankings.append(ranking)
        
        return rankings
    
    def _assign_tier(self, score: float) -> Tier:
        """Assign performance tier based on score.
        
        Args:
            score: Overall score
        
        Returns:
            Tier assignment
        """
        if score >= self.tier_a_min:
            return Tier.A
        elif score >= self.tier_b_min:
            return Tier.B
        elif score >= self.tier_c_min:
            return Tier.C
        else:
            return Tier.D
    
    def _calculate_tier_statistics(
        self,
        rankings: List[CountryRanking]
    ) -> Dict[Tier, TierStatistics]:
        """Calculate statistics for each tier.
        
        Args:
            rankings: List of country rankings
        
        Returns:
            Dictionary mapping tiers to their statistics
        """
        tier_stats = {}
        
        for tier in Tier:
            tier_rankings = [r for r in rankings if r.tier == tier]
            
            if tier_rankings:
                scores = [r.overall_score for r in tier_rankings]
                tier_stats[tier] = TierStatistics(
                    tier=tier,
                    count=len(tier_rankings),
                    countries=[r.country for r in tier_rankings],
                    avg_score=mean(scores),
                    min_score=min(scores),
                    max_score=max(scores),
                    score_range=max(scores) - min(scores)
                )
            else:
                # Empty tier
                tier_stats[tier] = TierStatistics(
                    tier=tier,
                    count=0,
                    countries=[],
                    avg_score=0.0,
                    min_score=0.0,
                    max_score=0.0,
                    score_range=0.0
                )
        
        return tier_stats
    
    def _identify_transitions(
        self,
        current_rankings: List[CountryRanking],
        previous_rankings: Dict[str, Dict[str, Any]]
    ) -> List[TierTransition]:
        """Identify countries that changed tiers.
        
        Args:
            current_rankings: Current period rankings
            previous_rankings: Previous period data {country: {tier, score, ...}}
        
        Returns:
            List of tier transitions
        """
        transitions = []
        
        for current in current_rankings:
            if current.country in previous_rankings:
                prev = previous_rankings[current.country]
                prev_tier_str = prev.get('tier')
                prev_score = prev.get('score')
                
                if prev_tier_str:
                    prev_tier = Tier(prev_tier_str)
                    
                    # Check if tier changed
                    if prev_tier != current.tier:
                        score_change = current.overall_score - prev_score if prev_score else None
                        
                        transition = TierTransition(
                            country=current.country,
                            from_tier=prev_tier,
                            to_tier=current.tier,
                            from_score=prev_score,
                            to_score=current.overall_score,
                            score_change=score_change
                        )
                        transitions.append(transition)
        
        return transitions
    
    def _generate_summary(
        self,
        rankings: List[CountryRanking],
        tier_stats: Dict[Tier, TierStatistics],
        transitions: List[TierTransition]
    ) -> str:
        """Generate executive summary of global rankings.
        
        Args:
            rankings: List of country rankings
            tier_stats: Tier statistics
            transitions: List of tier transitions
        
        Returns:
            Summary text
        """
        lines = []
        
        # Overall statistics
        lines.append(f"Global Rankings Summary - {rankings[0].period if rankings else 'N/A'}")
        lines.append(f"Total countries analyzed: {len(rankings)}")
        lines.append("")
        
        # Tier distribution
        lines.append("Tier Distribution:")
        for tier in [Tier.A, Tier.B, Tier.C, Tier.D]:
            stats = tier_stats[tier]
            if stats.count > 0:
                lines.append(
                    f"  {tier.value}-Tier: {stats.count} countries "
                    f"(avg: {stats.avg_score:.2f}, range: {stats.min_score:.2f}-{stats.max_score:.2f})"
                )
        lines.append("")
        
        # Top performers
        if self.highlight_top_n > 0 and rankings:
            top_n = min(self.highlight_top_n, len(rankings))
            lines.append(f"Top {top_n} Countries:")
            for i, ranking in enumerate(rankings[:top_n], 1):
                lines.append(
                    f"  #{i}: {ranking.country} ({ranking.overall_score:.2f}, {ranking.tier.value}-Tier)"
                )
            lines.append("")
        
        # Bottom performers (if configured)
        if self.highlight_bottom_n > 0 and len(rankings) > self.highlight_bottom_n:
            lines.append(f"Bottom {self.highlight_bottom_n} Countries:")
            for ranking in rankings[-self.highlight_bottom_n:]:
                lines.append(
                    f"  #{ranking.rank}: {ranking.country} ({ranking.overall_score:.2f}, {ranking.tier.value}-Tier)"
                )
            lines.append("")
        
        # Tier transitions
        if transitions and self.mention_movers:
            upgrades = [t for t in transitions if t.direction == "upgrade"]
            downgrades = [t for t in transitions if t.direction == "downgrade"]
            
            if upgrades:
                lines.append(f"Tier Upgrades ({len(upgrades)}):")
                for trans in upgrades:
                    lines.append(
                        f"  {trans.country}: {trans.from_tier.value} → {trans.to_tier.value} "
                        f"(+{trans.score_change:.2f})"
                    )
                lines.append("")
            
            if downgrades:
                lines.append(f"Tier Downgrades ({len(downgrades)}):")
                for trans in downgrades:
                    lines.append(
                        f"  {trans.country}: {trans.from_tier.value} → {trans.to_tier.value} "
                        f"({trans.score_change:.2f})"
                    )
                lines.append("")
        
        # Key insights
        lines.append("Key Insights:")
        
        # Tier concentration
        a_tier_pct = (tier_stats[Tier.A].count / len(rankings) * 100) if rankings else 0
        if a_tier_pct > 30:
            lines.append(f"  • Strong concentration in A-Tier ({a_tier_pct:.1f}% of countries)")
        elif a_tier_pct < 10:
            lines.append(f"  • Limited A-Tier representation ({a_tier_pct:.1f}% of countries)")
        
        # Score distribution
        if rankings:
            top_score = rankings[0].overall_score
            bottom_score = rankings[-1].overall_score
            score_spread = top_score - bottom_score
            
            if score_spread < 2.0:
                lines.append(f"  • Highly competitive field (spread: {score_spread:.2f} points)")
            elif score_spread > 4.0:
                lines.append(f"  • Wide performance gap (spread: {score_spread:.2f} points)")
        
        return "\n".join(lines)
