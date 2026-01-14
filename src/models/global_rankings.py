"""Global Rankings data models.

This module defines the data structures for global rankings results,
including tier assignments, statistics, and transitions.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class Tier(str, Enum):
    """Performance tiers for countries."""
    A = "A"  # 8.0+
    B = "B"  # 6.5-7.99
    C = "C"  # 5.0-6.49
    D = "D"  # <5.0


@dataclass
class CountryRanking:
    """Individual country ranking with tier assignment."""
    
    rank: int
    country: str
    overall_score: float
    tier: Tier
    
    # Detailed breakdown
    subcategory_scores: Dict[str, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
    # Context
    period: str = "Q3 2024"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rank": self.rank,
            "country": self.country,
            "overall_score": round(self.overall_score, 2),
            "tier": self.tier.value,
            "subcategory_scores": {
                k: round(v, 2) for k, v in self.subcategory_scores.items()
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "period": self.period
        }


@dataclass
class TierStatistics:
    """Statistics for a performance tier."""
    
    tier: Tier
    count: int
    countries: List[str]
    avg_score: float
    min_score: float
    max_score: float
    score_range: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tier": self.tier.value,
            "count": self.count,
            "countries": self.countries,
            "avg_score": round(self.avg_score, 2),
            "min_score": round(self.min_score, 2),
            "max_score": round(self.max_score, 2),
            "score_range": round(self.score_range, 2)
        }


@dataclass
class TierTransition:
    """Country transition between tiers."""
    
    country: str
    from_tier: Optional[Tier]
    to_tier: Tier
    from_score: Optional[float]
    to_score: float
    score_change: Optional[float]
    
    @property
    def direction(self) -> str:
        """Get transition direction."""
        if self.from_tier is None:
            return "new"
        if self.from_tier.value < self.to_tier.value:
            return "downgrade"
        elif self.from_tier.value > self.to_tier.value:
            return "upgrade"
        return "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "country": self.country,
            "from_tier": self.from_tier.value if self.from_tier else None,
            "to_tier": self.to_tier.value,
            "from_score": round(self.from_score, 2) if self.from_score else None,
            "to_score": round(self.to_score, 2),
            "score_change": round(self.score_change, 2) if self.score_change else None,
            "direction": self.direction
        }


@dataclass
class GlobalRankings:
    """Complete global rankings with all countries."""
    
    rankings: List[CountryRanking]
    tier_statistics: Dict[Tier, TierStatistics]
    tier_transitions: List[TierTransition]
    
    period: str
    total_countries: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_tier_rankings(self, tier: Tier) -> List[CountryRanking]:
        """Get all rankings for a specific tier."""
        return [r for r in self.rankings if r.tier == tier]
    
    def get_country_rank(self, country: str) -> Optional[int]:
        """Get rank for a specific country."""
        for ranking in self.rankings:
            if ranking.country == country:
                return ranking.rank
        return None
    
    def get_top_n(self, n: int = 10) -> List[CountryRanking]:
        """Get top N countries."""
        return self.rankings[:n]
    
    def get_bottom_n(self, n: int = 10) -> List[CountryRanking]:
        """Get bottom N countries."""
        return self.rankings[-n:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rankings": [r.to_dict() for r in self.rankings],
            "tier_statistics": {
                tier.value: stats.to_dict() 
                for tier, stats in self.tier_statistics.items()
            },
            "tier_transitions": [t.to_dict() for t in self.tier_transitions],
            "period": self.period,
            "total_countries": self.total_countries,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"GlobalRankings(period={self.period}, "
            f"countries={self.total_countries}, "
            f"tiers={len(self.tier_statistics)})"
        )
