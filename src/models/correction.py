"""Expert correction data model."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CorrectionType(str, Enum):
    """Type of correction."""
    PARAMETER_SCORE = "parameter_score"
    DOMAIN_RULE = "domain_rule"
    DATA_SOURCE = "data_source"
    JUSTIFICATION = "justification"


class ExpertCorrection(BaseModel):
    """Expert feedback and correction."""
    correction_id: Optional[str] = None
    country_name: str
    parameter_name: str
    original_score: float
    corrected_score: float
    reasoning: str = Field(min_length=50, description="Expert reasoning (min 50 characters)")
    correction_type: CorrectionType = CorrectionType.PARAMETER_SCORE
    expert_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    applied: bool = False
    
    # Optional: Similar countries to apply correction to
    apply_to_countries: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_name": "Brazil",
                "parameter_name": "Contract Terms",
                "original_score": 8.0,
                "corrected_score": 9.0,
                "reasoning": "Curtailment improved from 3-4% to 2.1% in Q3 2024. Grid operator reports show significant transmission upgrades completed.",
                "correction_type": "parameter_score",
                "apply_to_countries": ["Colombia", "Chile"]
            }
        }


class DomainRule(BaseModel):
    """Domain-specific rule created from expert knowledge."""
    rule_id: Optional[str] = None
    rule_name: str
    description: str
    condition: str  # Logical condition (will be more structured in Phase 2)
    adjustment: str  # Score adjustment logic
    applies_to: List[str]  # Countries or regions
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_name": "GCC Sovereign Backing",
                "description": "GCC countries with sovereign wealth backing get bonus on Offtaker Status",
                "condition": "country IN ['UAE', 'Saudi Arabia', 'Qatar'] AND offtaker = 'government'",
                "adjustment": "offtaker_score += 1.5",
                "applies_to": ["UAE", "Saudi Arabia", "Qatar", "Kuwait", "Bahrain", "Oman"]
            }
        }
