"""Competitive Landscape Extractor - AI-powered extraction for market entry ease.

This extractor analyzes regulatory barriers, market openness, and competitive
intensity in renewable energy markets.

Extracts:
    - Licensing complexity and requirements
    - Permitting timelines
    - Grid connection ease
    - Market openness score
    - Competitive intensity
    - Entry and exit patterns
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re

from ..base_extractor import BaseExtractor, ExtractedData
from ..prompts.prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class CompetitiveLandscapeExtractor(BaseExtractor):
    """Extractor for competitive landscape and market entry ease parameter.

    This extractor analyzes regulatory frameworks, licensing requirements,
    and market entry barriers to assess competitive dynamics.

    Example Usage:
        >>> extractor = CompetitiveLandscapeExtractor(
        ...     parameter_name="competitive_landscape",
        ...     llm_service=llm_service
        ... )
        >>> result = extractor.extract(
        ...     country="Germany",
        ...     documents=[{
        ...         'content': policy_doc_text,
        ...         'metadata': {'source': 'Regulatory Framework'}
        ...     }]
        ... )
        >>> print(result.data.value)  # Market openness score
    """

    def _get_extraction_prompt(
        self,
        country: str,
        document_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate extraction prompt for competitive landscape parameter.

        Args:
            country: Country name
            document_content: Combined document text
            context: Optional additional context

        Returns:
            Formatted prompt string
        """
        template = PromptTemplates.COMPETITIVE_LANDSCAPE_TEMPLATE

        prompt = PromptTemplates.format_template(
            template=template,
            parameter_name="competitive landscape/market entry ease",
            country=country,
            documents=document_content
        )

        return prompt

    def _parse_llm_response(
        self,
        llm_response: str,
        country: str
    ) -> Dict[str, Any]:
        """Parse LLM response for competitive landscape data.

        Expected JSON format:
        {
            "value": <market_openness_score 1-10>,
            "confidence": 0.0-1.0,
            "justification": "...",
            "quotes": ["...", "..."],
            "metadata": {
                "licensing_complexity": "low|moderate|high",
                "permitting_timeline_months": 6,
                "grid_connection_ease": "low|moderate|high",
                "competitive_intensity": "low|moderate|high|very_high",
                "entry_examples": "...",
                ...
            }
        }

        Args:
            llm_response: Raw LLM output
            country: Country name for context

        Returns:
            Dictionary with parsed competitive landscape data
        """
        try:
            # Extract JSON from response
            parsed = self._extract_json_from_response(llm_response)

            # Validate required fields
            required_fields = ['value', 'confidence', 'justification']
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")

            # Extract and normalize score value
            score = self._normalize_score_value(parsed['value'])

            # Ensure metadata exists
            if 'metadata' not in parsed:
                parsed['metadata'] = {}

            # Add country
            parsed['metadata']['country'] = country

            # Store normalized value
            parsed['normalized_value'] = score

            logger.info(
                f"Parsed competitive landscape for {country}: "
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
        """Validate extracted competitive landscape data.

        Checks:
        - Score is within valid range (1-10)
        - Confidence is within bounds
        - Justification is provided
        - Metadata fields are reasonable

        Args:
            data: Extracted data dictionary
            country: Country name

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check score value
        score = data.get('normalized_value', 0)
        if not 1 <= score <= 10:
            return False, f"Invalid score value: {score} (must be 1-10)"

        # Check confidence
        confidence = data.get('confidence', 0)
        if not 0.0 <= confidence <= 1.0:
            return False, f"Invalid confidence: {confidence} (must be 0.0-1.0)"

        # Check justification
        justification = data.get('justification', '')
        if len(justification) < 20:
            return False, "Justification too short (minimum 20 characters)"

        # Check permitting timeline if provided
        metadata = data.get('metadata', {})
        timeline = metadata.get('permitting_timeline_months')
        if timeline:
            try:
                months = int(timeline)
                if months < 0 or months > 120:  # Max 10 years seems reasonable
                    return False, f"Unrealistic permitting timeline: {months} months"
            except (ValueError, TypeError):
                logger.warning(f"Could not parse permitting timeline: {timeline}")

        return True, None

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON object from LLM response text.

        Handles responses that may include markdown code blocks or
        additional explanatory text.

        Args:
            response: LLM response text

        Returns:
            Parsed JSON dictionary
        """
        # Try to find JSON in markdown code block
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, response, re.DOTALL)

        if match:
            json_text = match.group(1)
        else:
            # Try to find any JSON object
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response, re.DOTALL)
            if match:
                json_text = match.group(0)
            else:
                json_text = response

        # Parse JSON
        return json.loads(json_text.strip())

    def _normalize_score_value(self, value: Any) -> float:
        """Normalize score value to 1-10 scale.

        Handles various formats:
        - 8 -> 8.0
        - "8" -> 8.0
        - "8/10" -> 8.0

        Args:
            value: Score value in various formats

        Returns:
            Normalized score value (1-10)
        """
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Remove whitespace
            value_clean = value.strip()

            # Handle "8/10" format
            if '/' in value_clean:
                parts = value_clean.split('/')
                if len(parts) == 2:
                    return float(parts[0])

            # Try to extract number
            number_match = re.search(r'(\d+(?:\.\d+)?)', value_clean)
            if number_match:
                return float(number_match.group(1))

        # If we can't parse it, log warning and return minimum
        logger.warning(f"Could not normalize score value: {value}")
        return 1.0

    def get_required_documents(self) -> List[str]:
        """Get list of recommended document types.

        Returns:
            List of document type identifiers
        """
        return [
            'regulatory_framework',
            'licensing_requirements',
            'permitting_guidelines',
            'grid_connection_rules',
            'market_entry_regulations',
            'investment_guidelines'
        ]

    def get_recommended_sources(self, country: str) -> List[Dict[str, str]]:
        """Get recommended data sources for competitive landscape extraction.

        Args:
            country: Country name

        Returns:
            List of source dictionaries with URLs
        """
        sources = [
            {
                'name': 'World Bank Doing Business',
                'url': 'https://www.doingbusiness.org/',
                'description': 'Business regulatory environment'
            },
            {
                'name': 'IEA Energy Policies',
                'url': 'https://www.iea.org/policies',
                'description': 'Energy market regulations'
            },
            {
                'name': 'IRENA Regulatory Database',
                'url': 'https://www.irena.org/regulations',
                'description': 'Renewable energy regulations'
            },
            {
                'name': 'OECD FDI Regulatory Index',
                'url': 'https://www.oecd.org/investment/fdiindex.htm',
                'description': 'Foreign investment restrictions'
            }
        ]

        # Add country-specific sources if known
        country_sources = self._get_country_specific_sources(country)
        sources.extend(country_sources)

        return sources

    def _get_country_specific_sources(self, country: str) -> List[Dict[str, str]]:
        """Get country-specific data sources.

        Args:
            country: Country name

        Returns:
            List of country-specific sources
        """
        # Example mapping - would be expanded in production
        country_sources_map = {
            'Germany': [
                {
                    'name': 'BNetzA Regulations',
                    'url': 'https://www.bundesnetzagentur.de/',
                    'description': 'Federal Network Agency regulations'
                }
            ],
            'USA': [
                {
                    'name': 'FERC Regulations',
                    'url': 'https://www.ferc.gov/',
                    'description': 'Federal Energy Regulatory Commission'
                }
            ],
            'Brazil': [
                {
                    'name': 'ANEEL Regulations',
                    'url': 'http://www.aneel.gov.br/',
                    'description': 'Brazilian Electricity Regulatory Agency'
                }
            ]
        }

        return country_sources_map.get(country, [])


# Convenience function
def extract_competitive_landscape(
    country: str,
    documents: List[Dict[str, Any]],
    llm_service: 'LLMService',
    cache: Optional['ExtractionCache'] = None
) -> Dict[str, Any]:
    """Extract competitive landscape for a country.

    Args:
        country: Country name
        documents: List of documents to analyze
        llm_service: LLM service instance
        cache: Optional cache instance

    Returns:
        Extraction result dictionary
    """
    extractor = CompetitiveLandscapeExtractor(
        parameter_name="competitive_landscape",
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
