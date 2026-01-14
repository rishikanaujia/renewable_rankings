"""Energy Dependence Extractor - AI-powered extraction for energy security indicators.

This extractor analyzes a country's energy import dependency and security.

Extracts:
    - Energy import dependency percentage
    - Fossil fuel reliance
    - Energy security indicators
    - Diversification metrics
    - Strategic energy policies
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re

from ..base_extractor import BaseExtractor, ExtractedData
from ..prompts.prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class EnergyDependenceExtractor(BaseExtractor):
    """Extractor for energy dependence and security parameter.

    This extractor analyzes energy import dependency and fossil fuel reliance
    to assess energy security motivations for renewable energy.

    Example Usage:
        >>> extractor = EnergyDependenceExtractor(
        ...     parameter_name="energy_dependence",
        ...     llm_service=llm_service
        ... )
        >>> result = extractor.extract(
        ...     country="Germany",
        ...     documents=[{
        ...         'content': energy_report_text,
        ...         'metadata': {'source': 'Energy Statistics'}
        ...     }]
        ... )
        >>> print(result.data.value)  # Import dependency percentage
    """

    def _get_extraction_prompt(
        self,
        country: str,
        document_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate extraction prompt for energy dependence parameter."""
        template = PromptTemplates.ENERGY_DEPENDENCE_TEMPLATE

        prompt = PromptTemplates.format_template(
            template=template,
            parameter_name="energy dependence/import dependency",
            country=country,
            documents=document_content
        )

        return prompt

    def _parse_llm_response(
        self,
        llm_response: str,
        country: str
    ) -> Dict[str, Any]:
        """Parse LLM response for energy dependence data.

        Expected JSON format:
        {
            "value": <import_dependency_percentage 0-100>,
            "confidence": 0.0-1.0,
            "justification": "...",
            "quotes": ["...", "..."],
            "metadata": {
                "fossil_fuel_share": 75.5,
                "primary_import_sources": ["Russia", "Norway"],
                "energy_security_risk": "low|moderate|high",
                "diversification_level": "low|moderate|high",
                ...
            }
        }
        """
        try:
            parsed = self._extract_json_from_response(llm_response)

            required_fields = ['value', 'confidence', 'justification']
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")

            dependency = self._normalize_percentage_value(parsed['value'])

            if 'metadata' not in parsed:
                parsed['metadata'] = {}

            parsed['metadata']['country'] = country
            parsed['normalized_value'] = dependency

            logger.info(
                f"Parsed energy dependence for {country}: "
                f"dependency={dependency}%, confidence={parsed['confidence']:.2f}"
            )

            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            raise ValueError(f"Invalid JSON in LLM response: {e}")

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            raise

    def _validate_extracted_data(
        self,
        data: Dict[str, Any],
        country: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate extracted energy dependence data."""
        dependency = data.get('normalized_value', 0)
        if not 0 <= dependency <= 100:
            return False, f"Invalid dependency percentage: {dependency}% (must be 0-100)"

        confidence = data.get('confidence', 0)
        if not 0.0 <= confidence <= 1.0:
            return False, f"Invalid confidence: {confidence} (must be 0.0-1.0)"

        justification = data.get('justification', '')
        if len(justification) < 20:
            return False, "Justification too short (minimum 20 characters)"

        return True, None

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON object from LLM response text."""
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, response, re.DOTALL)

        if match:
            json_text = match.group(1)
        else:
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response, re.DOTALL)
            if match:
                json_text = match.group(0)
            else:
                json_text = response

        return json.loads(json_text.strip())

    def _normalize_percentage_value(self, value: Any) -> float:
        """Normalize percentage value to 0-100 range."""
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            value_clean = value.strip().replace('%', '').strip()
            number_match = re.search(r'(\d+(?:\.\d+)?)', value_clean)
            if number_match:
                return float(number_match.group(1))

        logger.warning(f"Could not normalize percentage value: {value}")
        return 0.0

    def get_required_documents(self) -> List[str]:
        """Get list of recommended document types."""
        return [
            'energy_statistics',
            'energy_security_strategy',
            'import_export_data',
            'fossil_fuel_consumption',
            'energy_mix_report'
        ]

    def get_recommended_sources(self, country: str) -> List[Dict[str, str]]:
        """Get recommended data sources for energy dependence extraction."""
        sources = [
            {
                'name': 'IEA Energy Statistics',
                'url': 'https://www.iea.org/data-and-statistics',
                'description': 'Comprehensive energy data'
            },
            {
                'name': 'Eurostat Energy Data',
                'url': 'https://ec.europa.eu/eurostat/web/energy',
                'description': 'European energy statistics'
            },
            {
                'name': 'BP Statistical Review',
                'url': 'https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy.html',
                'description': 'Global energy statistics'
            },
            {
                'name': 'World Bank Energy Data',
                'url': 'https://data.worldbank.org/topic/energy',
                'description': 'Energy indicators by country'
            }
        ]

        return sources

    def _get_country_specific_sources(self, country: str) -> List[Dict[str, str]]:
        """Get country-specific data sources."""
        return []


# Convenience function
def extract_energy_dependence(
    country: str,
    documents: List[Dict[str, Any]],
    llm_service: 'LLMService',
    cache: Optional['ExtractionCache'] = None
) -> Dict[str, Any]:
    """Extract energy dependence for a country."""
    extractor = EnergyDependenceExtractor(
        parameter_name="energy_dependence",
        llm_service=llm_service,
        cache=cache
    )

    result = extractor.extract(country, documents)

    return {
        'success': result.success,
        'dependency_percentage': result.data.value if result.success else None,
        'confidence': result.data.confidence if result.success else 0.0,
        'justification': result.data.justification if result.success else None,
        'error': result.error
    }
