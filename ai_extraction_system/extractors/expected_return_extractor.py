"""Expected Return Extractor - AI-powered extraction for project return metrics.

This extractor analyzes expected returns (IRR) for renewable energy projects.

Extracts:
    - Typical project IRR ranges
    - Equity vs. debt returns
    - Technology-specific returns (solar, wind, hydro)
    - Auction clearing prices
    - PPA prices
    - Risk premiums
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re

from ..base_extractor import BaseExtractor, ExtractedData
from ..prompts.prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class ExpectedReturnExtractor(BaseExtractor):
    """Extractor for expected return/IRR parameter.

    This extractor analyzes typical project returns and IRR ranges
    to assess profitability of renewable energy investments.

    Example Usage:
        >>> extractor = ExpectedReturnExtractor(
        ...     parameter_name="expected_return",
        ...     llm_service=llm_service
        ... )
        >>> result = extractor.extract(
        ...     country="Germany",
        ...     documents=[{
        ...         'content': investment_report_text,
        ...         'metadata': {'source': 'Industry Report'}
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
        """Generate extraction prompt for expected return parameter."""
        template = PromptTemplates.EXPECTED_RETURN_TEMPLATE

        prompt = PromptTemplates.format_template(
            template=template,
            parameter_name="expected return/project IRR",
            country=country,
            documents=document_content
        )

        return prompt

    def _parse_llm_response(
        self,
        llm_response: str,
        country: str
    ) -> Dict[str, Any]:
        """Parse LLM response for expected return data.

        Expected JSON format:
        {
            "value": <1-10 score>,
            "confidence": 0.0-1.0,
            "justification": "...",
            "quotes": ["...", "..."],
            "metadata": {
                "typical_irr": 12.5,
                "irr_range_min": 10.0,
                "irr_range_max": 15.0,
                "equity_return": 14.0,
                "debt_cost": 4.5,
                "ppa_price": 50.0,
                "technology": "solar|wind|hydro",
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
                f"Parsed expected return for {country}: "
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
        """Validate extracted expected return data."""
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
            'investment_reports',
            'auction_results',
            'ppa_pricing',
            'financial_models',
            'market_analysis',
            'developer_presentations'
        ]

    def get_recommended_sources(self, country: str) -> List[Dict[str, str]]:
        """Get recommended data sources for expected return extraction."""
        sources = [
            {
                'name': 'IRENA Renewable Power Generation Costs',
                'url': 'https://www.irena.org/costs',
                'description': 'Global renewable energy cost data'
            },
            {
                'name': 'BloombergNEF Market Analysis',
                'url': 'https://about.bnef.com/',
                'description': 'Renewable energy market intelligence'
            },
            {
                'name': 'IEA PVPS Programme',
                'url': 'https://iea-pvps.org/',
                'description': 'Solar PV trends and analysis'
            },
            {
                'name': 'GWEC Global Wind Report',
                'url': 'https://gwec.net/global-wind-report/',
                'description': 'Wind energy market data'
            }
        ]

        return sources

    def _get_country_specific_sources(self, country: str) -> List[Dict[str, str]]:
        """Get country-specific data sources."""
        return []


# Convenience function
def extract_expected_return(
    country: str,
    documents: List[Dict[str, Any]],
    llm_service: 'LLMService',
    cache: Optional['ExtractionCache'] = None
) -> Dict[str, Any]:
    """Extract expected return for a country."""
    extractor = ExpectedReturnExtractor(
        parameter_name="expected_return",
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
