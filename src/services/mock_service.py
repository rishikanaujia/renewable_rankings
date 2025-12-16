"""Mock service with sample data for Phase 1 UI development."""
from typing import List, Optional, Dict
from datetime import datetime

from ..models.ranking import CountryRanking, GlobalRankings, RankingPeriod
from ..models.parameter import ParameterScore, SubcategoryScore
from ..models.correction import ExpertCorrection
from ..core.logger import get_logger

logger = get_logger(__name__)


class MockRankingService:
    """Mock service that returns sample data for UI testing."""
    
    def __init__(self):
        """Initialize with sample rankings."""
        self.rankings = self._generate_sample_rankings()
        logger.info("MockRankingService initialized with sample data")
    
    def _generate_sample_rankings(self) -> GlobalRankings:
        """Generate sample country rankings."""
        # Sample countries with realistic scores
        sample_data = [
            {
                "country_name": "Brazil",
                "country_code": "BRA",
                "overall_score": 6.47,
                "subcategories": {
                    "Regulation": 8.0,
                    "Profitability": 6.0,
                    "Accommodation": 5.5,
                    "Market Size & Fundamentals": 8.0,
                    "Competition & Ease": 7.3,
                    "System Modifiers": 6.0
                },
                "strengths": ["Strong track record (9/10)", "High ambition (7/10)", "Good market size"],
                "weaknesses": ["High interest rates (11.62%)", "Grid constraints", "Curtailment risk"]
            },
            {
                "country_name": "Germany",
                "country_code": "DEU",
                "overall_score": 8.75,
                "subcategories": {
                    "Regulation": 9.5,
                    "Profitability": 8.0,
                    "Accommodation": 9.0,
                    "Market Size & Fundamentals": 8.5,
                    "Competition & Ease": 9.0,
                    "System Modifiers": 7.5
                },
                "strengths": ["World-class regulation", "Mature market", "Strong grid"],
                "weaknesses": ["High market saturation", "Some curtailment issues"]
            },
            {
                "country_name": "United States",
                "country_code": "USA",
                "overall_score": 8.42,
                "subcategories": {
                    "Regulation": 7.5,
                    "Profitability": 8.5,
                    "Accommodation": 7.8,
                    "Market Size & Fundamentals": 9.5,
                    "Competition & Ease": 8.8,
                    "System Modifiers": 7.2
                },
                "strengths": ["Massive market size", "High profitability", "Open competition"],
                "weaknesses": ["Federal-state policy conflicts", "Regional grid issues"]
            },
            {
                "country_name": "China",
                "country_code": "CHN",
                "overall_score": 8.31,
                "subcategories": {
                    "Regulation": 8.5,
                    "Profitability": 7.0,
                    "Accommodation": 8.0,
                    "Market Size & Fundamentals": 10.0,
                    "Competition & Ease": 6.5,
                    "System Modifiers": 7.5
                },
                "strengths": ["Enormous market scale", "Strong government support", "Rapid deployment"],
                "weaknesses": ["Market access challenges", "Curtailment issues"]
            },
            {
                "country_name": "India",
                "country_code": "IND",
                "overall_score": 7.25,
                "subcategories": {
                    "Regulation": 7.5,
                    "Profitability": 6.5,
                    "Accommodation": 6.0,
                    "Market Size & Fundamentals": 9.0,
                    "Competition & Ease": 7.5,
                    "System Modifiers": 6.5
                },
                "strengths": ["Large market", "Ambitious targets", "Improving policy"],
                "weaknesses": ["Grid infrastructure gaps", "Offtaker credit risks"]
            },
            {
                "country_name": "United Kingdom",
                "country_code": "GBR",
                "overall_score": 8.65,
                "subcategories": {
                    "Regulation": 9.0,
                    "Profitability": 8.5,
                    "Accommodation": 8.8,
                    "Market Size & Fundamentals": 7.5,
                    "Competition & Ease": 9.2,
                    "System Modifiers": 8.0
                },
                "strengths": ["Strong offshore wind", "Excellent regulation", "Good grid"],
                "weaknesses": ["Smaller market size", "High costs"]
            },
            {
                "country_name": "Spain",
                "country_code": "ESP",
                "overall_score": 8.10,
                "subcategories": {
                    "Regulation": 8.5,
                    "Profitability": 7.5,
                    "Accommodation": 8.0,
                    "Market Size & Fundamentals": 7.8,
                    "Competition & Ease": 8.5,
                    "System Modifiers": 7.5
                },
                "strengths": ["Excellent solar resource", "Strong regulation", "Good track record"],
                "weaknesses": ["Some policy uncertainty", "Curtailment periods"]
            },
            {
                "country_name": "Australia",
                "country_code": "AUS",
                "overall_score": 7.85,
                "subcategories": {
                    "Regulation": 7.8,
                    "Profitability": 8.0,
                    "Accommodation": 6.5,
                    "Market Size & Fundamentals": 8.5,
                    "Competition & Ease": 8.2,
                    "System Modifiers": 7.0
                },
                "strengths": ["Excellent resources", "High returns", "Open market"],
                "weaknesses": ["Grid connection challenges", "Regional fragmentation"]
            },
            {
                "country_name": "Chile",
                "country_code": "CHL",
                "overall_score": 6.95,
                "subcategories": {
                    "Regulation": 7.5,
                    "Profitability": 7.0,
                    "Accommodation": 6.0,
                    "Market Size & Fundamentals": 6.5,
                    "Competition & Ease": 7.5,
                    "System Modifiers": 6.5
                },
                "strengths": ["World-class solar resource", "Open market", "Good track record"],
                "weaknesses": ["Smaller market", "Grid constraints", "Curtailment"]
            },
            {
                "country_name": "Vietnam",
                "country_code": "VNM",
                "overall_score": 6.80,
                "subcategories": {
                    "Regulation": 7.0,
                    "Profitability": 6.5,
                    "Accommodation": 5.5,
                    "Market Size & Fundamentals": 7.5,
                    "Competition & Ease": 7.0,
                    "System Modifiers": 6.0
                },
                "strengths": ["Rapid growth", "Strong ambition", "Good resource"],
                "weaknesses": ["Policy uncertainty", "Grid bottlenecks", "PPA risks"]
            }
        ]
        
        rankings = []
        for data in sample_data:
            # Create subcategory scores
            subcategory_scores = []
            for name, score in data["subcategories"].items():
                subcategory_scores.append(
                    SubcategoryScore(
                        subcategory_name=name,
                        score=score,
                        parameter_scores=[]  # Simplified for mock
                    )
                )
            
            ranking = CountryRanking(
                country_name=data["country_name"],
                country_code=data["country_code"],
                period="Q3 2024",
                overall_score=data["overall_score"],
                subcategory_scores=subcategory_scores,
                key_strengths=data["strengths"],
                key_weaknesses=data["weaknesses"]
            )
            rankings.append(ranking)
        
        return GlobalRankings(period="Q3 2024", rankings=rankings)
    
    def get_rankings(self, period: str = "Q3 2024") -> GlobalRankings:
        """Get global rankings for a period."""
        logger.info(f"Fetching rankings for period: {period}")
        return self.rankings
    
    def get_country_ranking(self, country_name: str, period: str = "Q3 2024") -> Optional[CountryRanking]:
        """Get ranking for a specific country."""
        logger.info(f"Fetching ranking for country: {country_name}")
        return self.rankings.get_country(country_name)
    
    def apply_correction(self, correction: ExpertCorrection) -> CountryRanking:
        """Apply expert correction (mock implementation)."""
        logger.info(f"Applying correction: {correction.parameter_name} for {correction.country_name}")
        
        # In mock, we just return the existing ranking
        # Real implementation would recalculate scores
        country = self.rankings.get_country(correction.country_name)
        if country:
            logger.info(f"Correction applied. New score would be calculated in real implementation.")
            return country
        else:
            raise ValueError(f"Country not found: {correction.country_name}")
    
    def search_countries(self, query: str) -> List[str]:
        """Search for countries matching query."""
        query_lower = query.lower()
        matches = [
            r.country_name for r in self.rankings.rankings
            if query_lower in r.country_name.lower()
        ]
        logger.info(f"Found {len(matches)} countries matching '{query}'")
        return matches


# Global mock service instance
mock_service = MockRankingService()
