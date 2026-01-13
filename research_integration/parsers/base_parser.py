"""Base parser class for extracting parameter-specific metrics from research documents.

All parameter parsers inherit from this base class to ensure consistent interface
and common utility methods.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Abstract base class for research document parsers.

    Each parameter-specific parser inherits from this class and implements
    the parse() method to extract relevant metrics for that parameter.
    """

    def __init__(self, parameter_name: str):
        """Initialize parser.

        Args:
            parameter_name: Name of the parameter this parser handles
        """
        self.parameter_name = parameter_name
        logger.debug(f"Initialized {self.__class__.__name__} for {parameter_name}")

    @abstractmethod
    def parse(self, research_doc) -> Dict[str, Any]:
        """Parse research document and extract parameter-specific metrics.

        Args:
            research_doc: ResearchDocument object from research system

        Returns:
            Dictionary with parameter-specific data structure

        Raises:
            ValueError: If research document is invalid or missing required data
        """
        pass

    def _get_metrics(self, research_doc) -> List[Dict[str, Any]]:
        """Extract key_metrics from research document.

        Args:
            research_doc: ResearchDocument object

        Returns:
            List of metric dictionaries
        """
        if not research_doc:
            return []

        return research_doc.content.get('key_metrics', [])

    def _get_overview(self, research_doc) -> str:
        """Extract overview from research document.

        Args:
            research_doc: ResearchDocument object

        Returns:
            Overview text
        """
        if not research_doc:
            return ""

        return research_doc.content.get('overview', '')

    def _get_confidence(self, research_doc) -> float:
        """Extract confidence score from research document.

        Args:
            research_doc: ResearchDocument object

        Returns:
            Confidence score (0.0-1.0)
        """
        if not research_doc:
            return 0.0

        return research_doc.content.get('confidence', 0.0)

    def _get_sources(self, research_doc) -> List[str]:
        """Extract source names from research document.

        Args:
            research_doc: ResearchDocument object

        Returns:
            List of source names
        """
        if not research_doc:
            return []

        sources = research_doc.content.get('sources', [])
        return [s.get('name', 'Unknown') for s in sources if isinstance(s, dict)]

    def _find_metric(
        self,
        metrics: List[Dict[str, Any]],
        keywords: List[str],
        case_insensitive: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Find first metric matching any of the keywords.

        Args:
            metrics: List of metric dictionaries
            keywords: Keywords to search for in metric names
            case_insensitive: Whether to ignore case in search

        Returns:
            First matching metric dictionary, or None if not found
        """
        for metric in metrics:
            if not isinstance(metric, dict):
                continue

            metric_name = metric.get('metric', '')
            if case_insensitive:
                metric_name = metric_name.lower()
                keywords = [kw.lower() for kw in keywords]

            if any(kw in metric_name for kw in keywords):
                return metric

        return None

    def _find_all_metrics(
        self,
        metrics: List[Dict[str, Any]],
        keywords: List[str],
        case_insensitive: bool = True
    ) -> List[Dict[str, Any]]:
        """Find all metrics matching any of the keywords.

        Args:
            metrics: List of metric dictionaries
            keywords: Keywords to search for in metric names
            case_insensitive: Whether to ignore case in search

        Returns:
            List of matching metric dictionaries
        """
        matches = []

        for metric in metrics:
            if not isinstance(metric, dict):
                continue

            metric_name = metric.get('metric', '')
            if case_insensitive:
                metric_name = metric_name.lower()
                search_keywords = [kw.lower() for kw in keywords]
            else:
                search_keywords = keywords

            if any(kw in metric_name for kw in search_keywords):
                matches.append(metric)

        return matches

    def _extract_numeric_value(
        self,
        metric: Dict[str, Any],
        default: float = 0.0
    ) -> float:
        """Extract numeric value from metric.

        Args:
            metric: Metric dictionary
            default: Default value if extraction fails

        Returns:
            Numeric value or default
        """
        if not metric:
            return default

        value_str = metric.get('value', str(default))

        try:
            # Try direct float conversion
            return float(value_str)
        except (ValueError, TypeError):
            # Try to extract number from string
            import re
            numbers = re.findall(r'-?\d+\.?\d*', str(value_str))
            if numbers:
                return float(numbers[0])
            return default

    def _validate_parsed_data(self, data: Dict[str, Any]) -> bool:
        """Validate that parsed data has required fields.

        Args:
            data: Parsed data dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['source']

        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False

        return True

    def _create_base_response(
        self,
        research_doc,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create base response dictionary with common fields.

        Args:
            research_doc: ResearchDocument object
            additional_data: Additional parameter-specific data

        Returns:
            Dictionary with base fields
        """
        response = {
            'source': 'research',
            'confidence': self._get_confidence(research_doc),
            'research_version': research_doc.version if research_doc else 'N/A',
            'research_sources': self._get_sources(research_doc)[:3],  # Top 3 sources
            'overview': self._get_overview(research_doc)[:200]  # First 200 chars
        }

        if additional_data:
            response.update(additional_data)

        return response
