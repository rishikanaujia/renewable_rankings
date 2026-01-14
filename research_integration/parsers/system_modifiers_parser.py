"""Parser for System Modifiers parameter.

System Modifiers is a composite parameter that applies adjustments
to the overall score based on various cross-cutting factors.
"""
from typing import Dict, Any
from .base_parser import BaseParser
import logging

logger = logging.getLogger(__name__)


class SystemModifiersParser(BaseParser):
    """Parser for System Modifiers - extracts composite adjustment factors."""

    def __init__(self):
        super().__init__(parameter_name="System Modifiers")

    def parse(self, research_doc) -> Dict[str, Any]:
        """Extract system-wide modifiers and adjustment factors.

        Returns:
            {
                'currency_risk_modifier': float,  # -1.0 to +1.0
                'political_stability_modifier': float,
                'regulatory_risk_modifier': float,
                'technology_risk_modifier': float,
                'overall_adjustment': float,  # Composite adjustment
                'modifier_notes': str,
                'source': 'research',
                ...
            }
        """
        metrics = self._get_metrics(research_doc)

        # Look for currency risk
        currency_keywords = ['currency', 'exchange rate', 'fx risk', 'currency risk']
        currency_metric = self._find_metric(metrics, currency_keywords)
        currency_modifier = self._extract_numeric_value(currency_metric, 0.0) if currency_metric else 0.0

        # Look for political stability
        political_keywords = ['political', 'political risk', 'governance']
        political_metric = self._find_metric(metrics, political_keywords)
        political_modifier = self._extract_numeric_value(political_metric, 0.0) if political_metric else 0.0

        # Look for regulatory risk
        regulatory_keywords = ['regulatory', 'regulation risk', 'policy risk']
        regulatory_metric = self._find_metric(metrics, regulatory_keywords)
        regulatory_modifier = self._extract_numeric_value(regulatory_metric, 0.0) if regulatory_metric else 0.0

        # Look for technology risk
        technology_keywords = ['technology', 'tech risk', 'technical risk']
        technology_metric = self._find_metric(metrics, technology_keywords)
        technology_modifier = self._extract_numeric_value(technology_metric, 0.0) if technology_metric else 0.0

        # Calculate overall adjustment (average of modifiers)
        modifiers = [currency_modifier, political_modifier, regulatory_modifier, technology_modifier]
        overall_adjustment = sum(modifiers) / len(modifiers)

        # Generate notes from overview
        overview = self._get_overview(research_doc)
        modifier_notes = overview[:300] if overview else "No specific modifiers identified"

        return self._create_base_response(
            research_doc,
            additional_data={
                'currency_risk_modifier': currency_modifier,
                'political_stability_modifier': political_modifier,
                'regulatory_risk_modifier': regulatory_modifier,
                'technology_risk_modifier': technology_modifier,
                'overall_adjustment': overall_adjustment,
                'modifier_notes': modifier_notes
            }
        )
