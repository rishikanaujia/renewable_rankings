"""Support Scheme Extractor - AI-powered extraction for renewable energy support policies.

This extractor analyzes policy support mechanisms for renewable energy.

Extracts:
    - Feed-in Tariffs (FiT) - rates, duration, technologies
    - Auction/tender mechanisms - frequency, volumes
    - Tax incentives - ITC, PTC, accelerated depreciation
    - Net metering policies
    - Renewable Energy Certificates
    - Policy stability and track record
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re

from ..base_extractor import BaseExtractor, ExtractedData
from ..prompts.prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class SupportSchemeExtractor(BaseExtractor):
    """Extractor for support scheme parameter.

    This extractor analyzes renewable energy policy support mechanisms
    including FiTs, auctions, tax incentives, and policy stability.

    Example Usage:
        >>> extractor = SupportSchemeExtractor(
        ...     parameter_name="support_scheme",
        ...     llm_service=llm_service
        ... )
        >>> result = extractor.extract(
        ...     country="Germany",
        ...     documents=[{
        ...         'content': policy_document_text,
        ...         'metadata': {'source': 'Ministry of Energy'}
        ...     }]
        ... )
        >>> print(result.data.value)  # Score 1-10
    """

    def _get_extraction_prompt(
        self,
        country: str,
        document_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate extraction prompt for support scheme parameter."""
        template = PromptTemplates.SUPPORT_SCHEME_TEMPLATE

        prompt = PromptTemplates.format_template(
            template=template,
            parameter_name="support scheme/policy support",
            country=country,
            documents=document_content
        )

        return prompt

    def _parse_llm_response(
        self,
        llm_response: str,
        country: str
    ) -> Dict[str, Any]:
        """Parse LLM response for support scheme data.

        Expected JSON format:
        {
            "value": <1-10 score>,
            "confidence": 0.0-1.0,
            "justification": "...",
            "quotes": ["...", "..."],
            "metadata": {
                "fit_availability": "yes|no|phased_out",
                "fit_rates": "€50-60/MWh",
                "auction_mechanism": "competitive|administrative",
                "tax_incentives": "ITC 30%, PTC available",
                "policy_stability": "high|medium|low",
                "support_duration": "15-20 years",
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

            score = self._normalize_score_value(parsed['value'])

            if 'metadata' not in parsed:
                parsed['metadata'] = {}

            parsed['metadata']['country'] = country
            parsed['normalized_value'] = score

            logger.info(
                f"Parsed support scheme for {country}: "
                f"score={score}/10, confidence={parsed['confidence']:.2f}"
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
        """Validate extracted support scheme data."""
        score = data.get('normalized_value', 0)
        if not 1 <= score <= 10:
            return False, f"Invalid score: {score} (must be 1-10)"

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

    def _normalize_score_value(self, value: Any) -> float:
        """Normalize score value to 1-10 scale."""
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Handle formats like "8", "8/10", "8.5"
            value_clean = value.strip().replace('/10', '').strip()
            number_match = re.search(r'(\d+(?:\.\d+)?)', value_clean)
            if number_match:
                return float(number_match.group(1))

        logger.warning(f"Could not normalize score value: {value}")
        return 5.0

    def get_required_documents(self) -> List[str]:
        """Get list of recommended document types."""
        return [
            'renewable_energy_law',
            'feed_in_tariff_decree',
            'auction_results',
            'tax_code_renewable_provisions',
            'policy_roadmap',
            'ministry_announcements'
        ]

    def get_recommended_sources(self, country: str) -> List[Dict[str, str]]:
        """Get recommended data sources for support scheme extraction."""
        sources = [
            {
                'name': 'IEA Policies Database',
                'url': 'https://www.iea.org/policies',
                'description': 'Comprehensive renewable energy policies'
            },
            {
                'name': 'REN21 Policy Database',
                'url': 'https://www.ren21.net/gsr-2023/',
                'description': 'Global status of renewable energy policies'
            },
            {
                'name': 'IRENA Policy Database',
                'url': 'https://www.irena.org/Energy-Transition/Policy',
                'description': 'Renewable energy policy frameworks'
            }
        ]

        return sources

    def _get_country_specific_sources(self, country: str) -> List[Dict[str, str]]:
        """Get country-specific data sources."""
        return []


# Convenience function
def extract_support_scheme(
    country: str,
    documents: List[Dict[str, Any]],
    llm_service: 'LLMService',
    cache: Optional['ExtractionCache'] = None
) -> Dict[str, Any]:
    """Extract support scheme for a country."""
    extractor = SupportSchemeExtractor(
        parameter_name="support_scheme",
        llm_service=llm_service,
        cache=cache
    )

    result = extractor.extract(country, documents)

    return {
        'success': result.success,
        'score': result.data.value if result.success else None,
        'confidence': result.data.confidence if result.success else 0.0,
        'justification': result.data.justification if result.success else None,
        'error': result.error
    }
