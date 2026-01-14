"""Ambition Extractor - AI-powered extraction for renewable energy targets.

This is an example implementation showing how to create a parameter-specific
extractor using the base extraction framework.

Extracts:
    - Renewable energy targets (%, GW, TWh)
    - Target years (2030, 2050, etc.)
    - Policy framework and legal status
    - Sector-specific goals
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re

from ..base_extractor import BaseExtractor, ExtractedData
from ..prompts.prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class AmbitionExtractor(BaseExtractor):
    """Extractor for renewable energy ambition/targets parameter.
    
    This extractor analyzes policy documents, NDCs, and energy plans to
    extract renewable energy targets and ambitions.
    
    Example Usage:
        >>> extractor = AmbitionExtractor(
        ...     parameter_name="ambition",
        ...     llm_service=llm_service
        ... )
        >>> result = extractor.extract(
        ...     country="Germany",
        ...     documents=[{
        ...         'content': policy_doc_text,
        ...         'metadata': {'source': 'BMWi Energy Policy'}
        ...     }]
        ... )
        >>> print(result.data.value)  # Target percentage
    """
    
    def _get_extraction_prompt(
        self,
        country: str,
        document_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate extraction prompt for ambition parameter.
        
        Args:
            country: Country name
            document_content: Combined document text
            context: Optional additional context
            
        Returns:
            Formatted prompt string
        """
        template = PromptTemplates.AMBITION_TEMPLATE
        
        prompt = PromptTemplates.format_template(
            template=template,
            parameter_name="renewable energy targets/ambition",
            country=country,
            documents=document_content
        )
        
        return prompt
    
    def _parse_llm_response(
        self,
        llm_response: str,
        country: str
    ) -> Dict[str, Any]:
        """Parse LLM response for ambition data.
        
        Expected JSON format:
        {
            "value": <target percentage or description>,
            "confidence": 0.0-1.0,
            "justification": "...",
            "quotes": ["...", "..."],
            "metadata": {
                "target_year": "2030",
                "target_type": "electricity|total_energy",
                "legal_status": "binding|aspirational",
                ...
            }
        }
        
        Args:
            llm_response: Raw LLM output
            country: Country name for context
            
        Returns:
            Dictionary with parsed ambition data
        """
        try:
            # Extract JSON from response
            parsed = self._extract_json_from_response(llm_response)

            # Validate required fields
            required_fields = ['value', 'confidence', 'justification']
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            # Extract and normalize target value
            target_value = self._normalize_target_value(parsed['value'])
            
            # Ensure metadata exists
            if 'metadata' not in parsed:
                parsed['metadata'] = {}
            
            # Add country
            parsed['metadata']['country'] = country
            
            # Store normalized value
            parsed['normalized_value'] = target_value
            
            logger.info(
                f"Parsed ambition for {country}: "
                f"target={target_value}%, confidence={parsed['confidence']:.2f}"
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
        """Validate extracted ambition data.
        
        Checks:
        - Target value is reasonable (0-100%)
        - Confidence is within bounds
        - Target year is realistic
        - Justification is provided
        
        Args:
            data: Extracted data dictionary
            country: Country name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check target value
        target = data.get('normalized_value', 0)
        if not 0 <= target <= 150:  # Allow >100% for some contexts
            return False, f"Invalid target value: {target}% (must be 0-150)"
        
        # Check confidence
        confidence = data.get('confidence', 0)
        if not 0.0 <= confidence <= 1.0:
            return False, f"Invalid confidence: {confidence} (must be 0.0-1.0)"
        
        # Check justification
        justification = data.get('justification', '')
        if len(justification) < 20:
            return False, "Justification too short (minimum 20 characters)"
        
        # Check target year if provided
        metadata = data.get('metadata', {})
        target_year = metadata.get('target_year')
        if target_year:
            try:
                year = int(target_year)
                if year < 2020 or year > 2100:
                    return False, f"Unrealistic target year: {year}"
            except (ValueError, TypeError):
                logger.warning(f"Could not parse target year: {target_year}")
        
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
    
    def _normalize_target_value(self, value: Any) -> float:
        """Normalize target value to percentage.
        
        Handles various formats:
        - "80%" -> 80.0
        - "80" -> 80.0
        - 80 -> 80.0
        - "100 GW" -> extracted from context/description
        
        Args:
            value: Target value in various formats
            
        Returns:
            Normalized percentage value
        """
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove % sign and whitespace
            value_clean = value.strip().replace('%', '').strip()
            
            # Try to extract number
            number_match = re.search(r'(\d+(?:\.\d+)?)', value_clean)
            if number_match:
                return float(number_match.group(1))
        
        # If we can't parse it, log warning and return 0
        logger.warning(f"Could not normalize target value: {value}")
        return 0.0
    
    def get_required_documents(self) -> List[str]:
        """Get list of recommended document types.
        
        Returns:
            List of document type identifiers
        """
        return [
            'national_energy_plan',
            'ndc_submission',
            'renewable_energy_strategy',
            'climate_action_plan',
            'government_policy_documents'
        ]
    
    def get_recommended_sources(self, country: str) -> List[Dict[str, str]]:
        """Get recommended data sources for ambition extraction.
        
        Args:
            country: Country name
            
        Returns:
            List of source dictionaries with URLs
        """
        sources = [
            {
                'name': 'UNFCCC NDC Registry',
                'url': f'https://unfccc.int/NDCREG',
                'description': 'National Determined Contributions'
            },
            {
                'name': 'IEA Policies Database',
                'url': 'https://www.iea.org/policies',
                'description': 'Energy policies and measures'
            },
            {
                'name': 'IRENA Policy Database',
                'url': 'https://www.irena.org/policies',
                'description': 'Renewable energy policies'
            },
            {
                'name': 'REN21 Renewables Global Status Report',
                'url': 'https://www.ren21.net/gsr/',
                'description': 'Annual renewable energy status'
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
                    'name': 'BMWi Energy Transition',
                    'url': 'https://www.bmwi.de/Redaktion/EN/Dossier/renewable-energy.html',
                    'description': 'German Federal Ministry for Economic Affairs and Energy'
                }
            ],
            'USA': [
                {
                    'name': 'DOE Clean Energy',
                    'url': 'https://www.energy.gov/clean-energy',
                    'description': 'US Department of Energy'
                }
            ],
            'India': [
                {
                    'name': 'MNRE',
                    'url': 'https://mnre.gov.in/',
                    'description': 'Ministry of New and Renewable Energy'
                }
            ]
        }
        
        return country_sources_map.get(country, [])


# Convenience function
def extract_ambition(
    country: str,
    documents: List[Dict[str, Any]],
    llm_service: 'LLMService',
    cache: Optional['ExtractionCache'] = None
) -> Dict[str, Any]:
    """Extract ambition/targets for a country.
    
    Args:
        country: Country name
        documents: List of documents to analyze
        llm_service: LLM service instance
        cache: Optional cache instance
        
    Returns:
        Extraction result dictionary
    """
    extractor = AmbitionExtractor(
        parameter_name="ambition",
        llm_service=llm_service,
        cache=cache
    )
    
    result = extractor.extract(country, documents)
    
    return {
        'success': result.success,
        'target_percentage': result.data.value if result.success else None,
        'confidence': result.data.confidence if result.success else 0.0,
        'justification': result.data.justification if result.success else None,
        'error': result.error
    }
