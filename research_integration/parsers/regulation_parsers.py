"""Parsers for Regulation subcategory parameters.

Regulation parameters:
1. Ambition - Renewable energy capacity targets
2. Country Stability - Political and economic risk
3. Track Record - Historical project performance
4. Support Scheme - Policy incentives and subsidies
5. Contract Terms - PPA terms and structures
"""
from typing import Dict, Any, List
from .base_parser import BaseParser
import logging

logger = logging.getLogger(__name__)


class AmbitionParser(BaseParser):
    """Parser for Ambition parameter - extracts renewable energy targets."""

    def __init__(self):
        super().__init__(parameter_name="Ambition")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract renewable energy capacity targets (GW).

        Returns:
            {
                'total_gw': float,
                'solar': float,
                'onshore_wind': float,
                'offshore_wind': float,
                'source': 'research',
                'confidence': float,
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        solar_gw = 0.0
        onshore_wind_gw = 0.0
        offshore_wind_gw = 0.0
        total_gw = 0.0

        for metric in metrics:
            if not isinstance(metric, dict):
                continue

            metric_name = metric.get('metric', '').lower()
            value = self._extract_numeric_value(metric)

            # Match metric to category
            if 'solar' in metric_name or 'pv' in metric_name:
                solar_gw += value
            elif 'onshore' in metric_name and 'wind' in metric_name:
                onshore_wind_gw += value
            elif 'offshore' in metric_name and 'wind' in metric_name:
                offshore_wind_gw += value
            elif 'total' in metric_name or 'combined' in metric_name:
                total_gw = value
            elif 'wind' in metric_name and 'solar' not in metric_name:
                # Generic wind - assume onshore
                onshore_wind_gw += value
            # Handle generic renewable energy targets
            elif any(kw in metric_name for kw in ['renewable', 'renewables', 'target', 'goal', 'capacity', 'ambition']):
                if total_gw == 0.0:
                    total_gw = value

        # Calculate total if not explicitly provided
        if total_gw == 0.0:
            total_gw = solar_gw + onshore_wind_gw + offshore_wind_gw

        return self._create_base_response(
            research_doc,
            additional_data={
                'total_gw': total_gw,
                'solar': solar_gw,
                'onshore_wind': onshore_wind_gw,
                'offshore_wind': offshore_wind_gw
            }
        )


class CountryStabilityParser(BaseParser):
    """Parser for Country Stability - extracts political/economic risk metrics."""

    def __init__(self):
        super().__init__(parameter_name="Country Stability")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract ECR (Euromoney Country Risk) rating and risk indicators.

        Returns:
            {
                'ecr_rating': float,  # 0-10 scale
                'risk_category': str,
                'political_risk': float,
                'economic_risk': float,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for ECR or risk ratings
        ecr_keywords = ['ecr', 'country risk', 'risk rating', 'risk score', 'stability score']
        ecr_metric = self._find_metric(metrics, ecr_keywords)

        if ecr_metric:
            ecr_rating = self._extract_numeric_value(ecr_metric, default=5.0)
        else:
            # Try to infer from other risk metrics
            political_metric = self._find_metric(metrics, ['political risk', 'political stability'])
            economic_metric = self._find_metric(metrics, ['economic risk', 'economic stability'])

            if political_metric or economic_metric:
                political_risk = self._extract_numeric_value(political_metric, 5.0) if political_metric else 5.0
                economic_risk = self._extract_numeric_value(economic_metric, 5.0) if economic_metric else 5.0
                ecr_rating = (political_risk + economic_risk) / 2
            else:
                # No specific metrics found, use default moderate risk
                ecr_rating = 5.0
                logger.warning(f"No ECR metrics found in research, using default {ecr_rating}")

        # Determine risk category
        risk_category = self._determine_risk_category(ecr_rating)

        return self._create_base_response(
            research_doc,
            additional_data={
                'ecr_rating': ecr_rating,
                'risk_category': risk_category
            }
        )

    def _determine_risk_category(self, ecr_rating: float) -> str:
        """Determine risk category from ECR rating."""
        if ecr_rating < 1.0:
            return "Extremely Stable"
        elif ecr_rating < 2.0:
            return "Very Stable"
        elif ecr_rating < 3.0:
            return "Stable"
        elif ecr_rating < 4.0:
            return "Moderately Stable"
        elif ecr_rating < 5.0:
            return "Fair Stability"
        elif ecr_rating < 6.0:
            return "Moderate Instability"
        elif ecr_rating < 7.0:
            return "Unstable"
        elif ecr_rating < 8.0:
            return "Very Unstable"
        elif ecr_rating < 9.0:
            return "Extremely Unstable"
        else:
            return "Failed/Fragile State"


class TrackRecordParser(BaseParser):
    """Parser for Track Record - extracts historical project performance."""

    def __init__(self):
        super().__init__(parameter_name="Track Record")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract project completion rates and historical performance.

        Returns:
            {
                'completion_rate': float,  # 0-100%
                'projects_completed': int,
                'total_capacity_mw': float,
                'avg_construction_time_months': float,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for completion rate
        completion_keywords = ['completion rate', 'success rate', 'project completion']
        completion_metric = self._find_metric(metrics, completion_keywords)
        completion_rate = self._extract_numeric_value(completion_metric, 75.0) if completion_metric else 75.0

        # Look for number of projects
        projects_keywords = ['projects completed', 'number of projects', 'project count']
        projects_metric = self._find_metric(metrics, projects_keywords)
        projects_completed = int(self._extract_numeric_value(projects_metric, 0)) if projects_metric else 0

        # Look for capacity
        capacity_keywords = ['total capacity', 'installed capacity', 'capacity mw']
        capacity_metric = self._find_metric(metrics, capacity_keywords)
        total_capacity_mw = self._extract_numeric_value(capacity_metric, 0) if capacity_metric else 0

        # Look for construction time
        time_keywords = ['construction time', 'build time', 'development time']
        time_metric = self._find_metric(metrics, time_keywords)
        avg_construction_time = self._extract_numeric_value(time_metric, 24.0) if time_metric else 24.0

        return self._create_base_response(
            research_doc,
            additional_data={
                'completion_rate': completion_rate,
                'projects_completed': projects_completed,
                'total_capacity_mw': total_capacity_mw,
                'avg_construction_time_months': avg_construction_time
            }
        )


class SupportSchemeParser(BaseParser):
    """Parser for Support Scheme - extracts policy incentives."""

    def __init__(self):
        super().__init__(parameter_name="Support Scheme")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract policy support mechanisms and incentives.

        Returns:
            {
                'scheme_type': str,  # FIT, FIP, CfD, tax credits, etc.
                'support_level': float,  # $/MWh or equivalent
                'duration_years': int,
                'has_support': bool,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Detect scheme type from overview or metrics
        overview = self._get_overview(research_doc).lower()

        scheme_type = "Unknown"
        if 'feed-in tariff' in overview or 'fit' in overview:
            scheme_type = "Feed-in Tariff (FIT)"
        elif 'feed-in premium' in overview or 'fip' in overview:
            scheme_type = "Feed-in Premium (FIP)"
        elif 'contract for difference' in overview or 'cfd' in overview:
            scheme_type = "Contract for Difference (CfD)"
        elif 'tax credit' in overview or 'itc' in overview or 'ptc' in overview:
            scheme_type = "Tax Credits"
        elif 'auction' in overview or 'tender' in overview:
            scheme_type = "Competitive Auction"

        # Look for support level
        support_keywords = ['support level', 'tariff', 'price', '$/mwh', 'subsidy']
        support_metric = self._find_metric(metrics, support_keywords)
        support_level = self._extract_numeric_value(support_metric, 0) if support_metric else 0

        # Look for duration
        duration_keywords = ['duration', 'contract length', 'years', 'term']
        duration_metric = self._find_metric(metrics, duration_keywords)
        duration_years = int(self._extract_numeric_value(duration_metric, 15)) if duration_metric else 15

        has_support = support_level > 0 or scheme_type != "Unknown"

        return self._create_base_response(
            research_doc,
            additional_data={
                'scheme_type': scheme_type,
                'support_level': support_level,
                'duration_years': duration_years,
                'has_support': has_support
            }
        )


class ContractTermsParser(BaseParser):
    """Parser for Contract Terms - extracts PPA terms."""

    def __init__(self):
        super().__init__(parameter_name="Contract Terms")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract PPA contract terms and conditions.

        Returns:
            {
                'avg_ppa_duration_years': int,
                'avg_ppa_price_mwh': float,
                'price_escalation_rate': float,  # % per year
                'offtaker_type': str,  # utility, corporate, government
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for PPA duration
        duration_keywords = ['ppa duration', 'contract term', 'ppa length', 'ppa term']
        duration_metric = self._find_metric(metrics, duration_keywords)
        avg_duration = int(self._extract_numeric_value(duration_metric, 20)) if duration_metric else 20

        # Look for PPA price
        price_keywords = ['ppa price', 'electricity price', 'power price', 'tariff']
        price_metric = self._find_metric(metrics, price_keywords)
        avg_price = self._extract_numeric_value(price_metric, 50.0) if price_metric else 50.0

        # Look for escalation rate
        escalation_keywords = ['escalation', 'price increase', 'annual increase']
        escalation_metric = self._find_metric(metrics, escalation_keywords)
        escalation_rate = self._extract_numeric_value(escalation_metric, 2.0) if escalation_metric else 2.0

        # Infer offtaker type from overview
        overview = self._get_overview(research_doc).lower()
        if 'utility' in overview:
            offtaker_type = "Utility"
        elif 'corporate' in overview:
            offtaker_type = "Corporate"
        elif 'government' in overview:
            offtaker_type = "Government"
        else:
            offtaker_type = "Mixed"

        return self._create_base_response(
            research_doc,
            additional_data={
                'avg_ppa_duration_years': avg_duration,
                'avg_ppa_price_mwh': avg_price,
                'price_escalation_rate': escalation_rate,
                'offtaker_type': offtaker_type
            }
        )
