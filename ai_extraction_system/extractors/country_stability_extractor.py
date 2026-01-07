"""Country Stability Extractor - AI-powered extraction for political and economic stability.

This extractor analyzes country risk factors affecting renewable energy investments.

Extracts:
    - Political stability indicators
    - Economic stability metrics
    - Policy continuity
    - Institutional quality
    - Corruption levels
    - Investment climate
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re

from ..base_extractor import BaseExtractor, ExtractedData
from ..prompts.prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class CountryStabilityExtractor(BaseExtractor):
    """Extractor for country stability and risk parameter.

    This extractor analyzes political, economic, and institutional stability
    factors that affect renewable energy investments.

    Example Usage:
        >>> extractor = CountryStabilityExtractor(
        ...     parameter_name="country_stability",
        ...     llm_service=llm_service
        ... )
        >>> result = extractor.extract(
        ...     country="Germany",
        ...     documents=[{
        ...         'content': stability_report_text,
        ...         'metadata': {'source': 'Country Risk Assessment'}
        ...     }]
        ... )
        >>> print(result.data.value)  # Stability score
    """

    def _get_extraction_prompt(
        self,
        country: str,
        document_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate extraction prompt for country stability parameter.

        Args:
            country: Country name
            document_content: Combined document text
            context: Optional additional context

        Returns:
            Formatted prompt string
        """
        template = PromptTemplates.COUNTRY_STABILITY_TEMPLATE

        prompt = PromptTemplates.format_template(
            template=template,
            parameter_name="country stability/political and economic risk",
            country=country,
            documents=document_content
        )

        return prompt

    def _parse_llm_response(
        self,
        llm_response: str,
        country: str
    ) -> Dict[str, Any]:
        """Parse LLM response for country stability data.

        Expected JSON format:
        {
            "value": <stability_score 1-10>,
            "confidence": 0.0-1.0,
            "justification": "...",
            "quotes": ["...", "..."],
            "metadata": {
                "political_stability": "low|moderate|high",
                "economic_stability": "low|moderate|high",
                "policy_continuity": "low|moderate|high",
                "corruption_level": "low|moderate|high",
                "institutional_quality": "weak|moderate|strong",
                ...
            }
        }

        Args:
            llm_response: Raw LLM output
            country: Country name for context

        Returns:
            Dictionary with parsed country stability data
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
                f"Parsed country stability for {country}: "
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
        """Validate extracted country stability data.

        Checks:
        - Score is within valid range (1-10)
        - Confidence is within bounds
        - Justification is provided

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

        return True, None

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON object from LLM response text."""
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
        """Normalize score value to 1-10 scale."""
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            value_clean = value.strip()
            if '/' in value_clean:
                parts = value_clean.split('/')
                if len(parts) == 2:
                    return float(parts[0])

            number_match = re.search(r'(\d+(?:\.\d+)?)', value_clean)
            if number_match:
                return float(number_match.group(1))

        logger.warning(f"Could not normalize score value: {value}")
        return 1.0

    def get_required_documents(self) -> List[str]:
        """Get list of recommended document types."""
        return [
            'country_risk_report',
            'political_stability_assessment',
            'economic_outlook',
            'governance_indicators',
            'investment_climate_report'
        ]

    def get_recommended_sources(self, country: str) -> List[Dict[str, str]]:
        """Get recommended data sources for country stability extraction."""
        sources = [
            {
                'name': 'World Bank Governance Indicators',
                'url': 'https://info.worldbank.org/governance/wgi/',
                'description': 'Political stability and governance'
            },
            {
                'name': 'Transparency International CPI',
                'url': 'https://www.transparency.org/cpi',
                'description': 'Corruption perceptions index'
            },
            {
                'name': 'IMF Economic Outlook',
                'url': 'https://www.imf.org/weo',
                'description': 'Economic stability forecasts'
            },
            {
                'name': 'Country Risk Ratings',
                'url': 'https://www.coface.com/Economic-Studies-and-Country-Risks',
                'description': 'Country risk assessments'
            }
        ]

        country_sources = self._get_country_specific_sources(country)
        sources.extend(country_sources)

        return sources

    def _get_country_specific_sources(self, country: str) -> List[Dict[str, str]]:
        """Get country-specific data sources."""
        return []


# Convenience function
def extract_country_stability(
    country: str,
    documents: List[Dict[str, Any]],
    llm_service: 'LLMService',
    cache: Optional['ExtractionCache'] = None
) -> Dict[str, Any]:
    """Extract country stability for a country."""
    extractor = CountryStabilityExtractor(
        parameter_name="country_stability",
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
