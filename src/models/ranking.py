"""Ranking data models."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

from .parameter import SubcategoryScore


class RankingPeriod(str, Enum):
    """Time period for rankings."""
    Q1_2024 = "Q1 2024"
    Q2_2024 = "Q2 2024"
    Q3_2024 = "Q3 2024"
    Q4_2024 = "Q4 2024"


class CountryRanking(BaseModel):
    """Complete ranking for a single country."""
    country_name: str
    country_code: str  # ISO 3-letter code
    period: str
    overall_score: float = Field(ge=0, le=10, description="Overall ranking score")
    rank: Optional[int] = None
    subcategory_scores: List[SubcategoryScore]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Optional metadata
    key_strengths: List[str] = []
    key_weaknesses: List[str] = []
    flagged_issues: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_name": "Brazil",
                "country_code": "BRA",
                "period": "Q3 2024",
                "overall_score": 6.47,
                "rank": 15,
                "subcategory_scores": [],
                "key_strengths": ["Strong track record", "High ambition"],
                "key_weaknesses": ["High interest rates", "Grid constraints"]
            }
        }
    
    def get_subcategory_score(self, subcategory_name: str) -> Optional[float]:
        """Get score for a specific subcategory."""
        for sc in self.subcategory_scores:
            if sc.subcategory_name == subcategory_name:
                return sc.score
        return None


class GlobalRankings(BaseModel):
    """Rankings for all countries in a period."""
    period: str
    rankings: List[CountryRanking]
    generated_at: datetime = Field(default_factory=datetime.now)
    total_countries: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        self.total_countries = len(self.rankings)
        # Sort by overall score descending
        self.rankings.sort(key=lambda x: x.overall_score, reverse=True)
        # Assign ranks
        for i, ranking in enumerate(self.rankings, 1):
            ranking.rank = i
    
    def get_country(self, country_name: str) -> Optional[CountryRanking]:
        """Get ranking for a specific country."""
        for ranking in self.rankings:
            if ranking.country_name.lower() == country_name.lower():
                return ranking
        return None
    
    def get_top_n(self, n: int = 10) -> List[CountryRanking]:
        """Get top N countries."""
        return self.rankings[:n]
