"""Data models for comparative country analysis."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CountryComparison:
    """Comparison data for a single country."""
    country: str
    overall_score: float
    rank: int
    subcategory_scores: Dict[str, float]
    strengths_count: int
    weaknesses_count: int


@dataclass
class SubcategoryComparison:
    """Comparison across countries for a single subcategory."""
    name: str
    weight: float
    country_scores: Dict[str, float]  # country -> score
    best_country: str
    best_score: float
    worst_country: str
    worst_score: float
    average_score: float


@dataclass
class ComparativeAnalysis:
    """Complete comparative analysis result."""
    countries: List[str]
    period: str
    country_comparisons: List[CountryComparison]
    subcategory_comparisons: List[SubcategoryComparison]
    summary: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "countries": self.countries,
            "period": self.period,
            "country_comparisons": [
                {
                    "country": c.country,
                    "overall_score": c.overall_score,
                    "rank": c.rank,
                    "subcategory_scores": c.subcategory_scores,
                    "strengths_count": c.strengths_count,
                    "weaknesses_count": c.weaknesses_count
                }
                for c in self.country_comparisons
            ],
            "subcategory_comparisons": [
                {
                    "name": s.name,
                    "weight": s.weight,
                    "country_scores": s.country_scores,
                    "best_country": s.best_country,
                    "best_score": s.best_score,
                    "worst_country": s.worst_country,
                    "worst_score": s.worst_score,
                    "average_score": s.average_score
                }
                for s in self.subcategory_comparisons
            ],
            "summary": self.summary,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }
