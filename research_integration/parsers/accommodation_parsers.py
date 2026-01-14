"""Parsers for Accommodation subcategory parameters.

Accommodation parameters:
1. Status of Grid - Grid infrastructure and interconnection
2. Ownership Hurdles - Land ownership and permitting complexity
"""
from typing import Dict, Any
from .base_parser import BaseParser
import logging

logger = logging.getLogger(__name__)


class StatusOfGridParser(BaseParser):
    """Parser for Status of Grid - extracts grid infrastructure metrics."""

    def __init__(self):
        super().__init__(parameter_name="Status of Grid")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract grid capacity and interconnection metrics.

        Returns:
            {
                'grid_capacity_score': float,  # 0-10
                'interconnection_cost_usd_kw': float,
                'grid_reliability_score': float,  # 0-10
                'avg_interconnection_time_months': int,
                'transmission_constraints': str,  # Low, Medium, High
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for grid capacity
        capacity_keywords = ['grid capacity', 'grid strength', 'grid infrastructure']
        capacity_metric = self._find_metric(metrics, capacity_keywords)
        grid_capacity = self._extract_numeric_value(capacity_metric, 6.0) if capacity_metric else 6.0

        # Look for interconnection cost
        cost_keywords = ['interconnection cost', 'connection cost', 'grid connection']
        cost_metric = self._find_metric(metrics, cost_keywords)
        interconnection_cost = self._extract_numeric_value(cost_metric, 50.0) if cost_metric else 50.0

        # Look for reliability
        reliability_keywords = ['reliability', 'grid reliability', 'uptime']
        reliability_metric = self._find_metric(metrics, reliability_keywords)
        reliability_score = self._extract_numeric_value(reliability_metric, 7.0) if reliability_metric else 7.0

        # Look for interconnection time
        time_keywords = ['interconnection time', 'connection time', 'lead time']
        time_metric = self._find_metric(metrics, time_keywords)
        interconnection_time = int(self._extract_numeric_value(time_metric, 12)) if time_metric else 12

        # Infer transmission constraints from overview
        overview = self._get_overview(research_doc).lower()
        if 'high constraint' in overview or 'congested' in overview:
            transmission_constraints = "High"
        elif 'moderate' in overview or 'some constraint' in overview:
            transmission_constraints = "Medium"
        else:
            transmission_constraints = "Low"

        return self._create_base_response(
            research_doc,
            additional_data={
                'grid_capacity_score': grid_capacity,
                'interconnection_cost_usd_kw': interconnection_cost,
                'grid_reliability_score': reliability_score,
                'avg_interconnection_time_months': interconnection_time,
                'transmission_constraints': transmission_constraints
            }
        )


class OwnershipHurdlesParser(BaseParser):
    """Parser for Ownership Hurdles - extracts land ownership complexity."""

    def __init__(self):
        super().__init__(parameter_name="Ownership Hurdles")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract land ownership and permitting complexity metrics.

        Returns:
            {
                'ownership_complexity_score': float,  # 0-10 (higher = more complex)
                'avg_permitting_time_months': int,
                'land_ownership_type': str,  # private, public, mixed
                'permit_approval_rate_percent': float,
                'environmental_review_required': bool,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for complexity score
        complexity_keywords = ['complexity', 'difficulty', 'hurdles', 'ownership complexity']
        complexity_metric = self._find_metric(metrics, complexity_keywords)
        complexity_score = self._extract_numeric_value(complexity_metric, 5.0) if complexity_metric else 5.0

        # Look for permitting time
        time_keywords = ['permitting time', 'permit duration', 'approval time']
        time_metric = self._find_metric(metrics, time_keywords)
        permitting_time = int(self._extract_numeric_value(time_metric, 18)) if time_metric else 18

        # Look for approval rate
        approval_keywords = ['approval rate', 'success rate', 'permit approval']
        approval_metric = self._find_metric(metrics, approval_keywords)
        approval_rate = self._extract_numeric_value(approval_metric, 70.0) if approval_metric else 70.0

        # Infer ownership type from overview
        overview = self._get_overview(research_doc).lower()
        if 'private land' in overview or 'private ownership' in overview:
            ownership_type = "Private"
        elif 'public land' in overview or 'government land' in overview:
            ownership_type = "Public"
        else:
            ownership_type = "Mixed"

        # Check for environmental review
        environmental_review = 'environmental' in overview or 'eia' in overview or 'impact assessment' in overview

        return self._create_base_response(
            research_doc,
            additional_data={
                'ownership_complexity_score': complexity_score,
                'avg_permitting_time_months': permitting_time,
                'land_ownership_type': ownership_type,
                'permit_approval_rate_percent': approval_rate,
                'environmental_review_required': environmental_review
            }
        )
