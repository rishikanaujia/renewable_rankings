"""Data models for country analysis results."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SubcategoryScore:
    """Score for a single subcategory."""
    name: str
    score: float
    parameter_count: int
    weight: float
    weighted_score: float


@dataclass
class StrengthWeakness:
    """Identified strength or weakness."""
    area: str
    score: float
    reason: str
    category: str  # 'strength' or 'weakness'


@dataclass
class CountryAnalysis:
    """Complete analysis result for a country."""
    country: str
    period: str
    overall_score: float
    subcategory_scores: List[SubcategoryScore]
    strengths: List[StrengthWeakness]
    weaknesses: List[StrengthWeakness]
    overall_assessment: str
    confidence: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "country": self.country,
            "period": self.period,
            "overall_score": self.overall_score,
            "subcategory_scores": [
                {
                    "name": s.name,
                    "score": s.score,
                    "parameter_count": s.parameter_count,
                    "weight": s.weight,
                    "weighted_score": s.weighted_score
                }
                for s in self.subcategory_scores
            ],
            "strengths": [
                {
                    "area": s.area,
                    "score": s.score,
                    "reason": s.reason,
                    "category": s.category
                }
                for s in self.strengths
            ],
            "weaknesses": [
                {
                    "area": w.area,
                    "score": w.score,
                    "reason": w.reason,
                    "category": w.category
                }
                for w in self.weaknesses
            ],
            "overall_assessment": self.overall_assessment,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }
