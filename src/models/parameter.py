"""Parameter data model."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ParameterScore(BaseModel):
    """Individual parameter score."""
    parameter_name: str
    score: float = Field(ge=1, le=10, description="Score from 1-10")
    justification: str
    data_sources: List[str] = []
    confidence: float = Field(ge=0, le=1, default=0.8)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "parameter_name": "Ambition",
                "score": 7.0,
                "justification": "26.8 GW of renewable targets by 2030",
                "data_sources": ["Government NDC 2024"],
                "confidence": 0.95
            }
        }


class SubcategoryScore(BaseModel):
    """Aggregated subcategory score."""
    subcategory_name: str
    score: float = Field(ge=0, le=10, description="Weighted score 0-10")
    parameter_scores: List[ParameterScore]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "subcategory_name": "Regulation",
                "score": 8.0,
                "parameter_scores": []
            }
        }
