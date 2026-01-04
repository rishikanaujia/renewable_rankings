"""Generic Configurable Extractor - Handles most parameters via configuration.

This extractor uses a configuration-driven approach to handle extraction for
most parameters without requiring separate extractor classes.

Design Philosophy:
    - Configuration over code
    - DRY (Don't Repeat Yourself)
    - Single source of truth for parameter definitions
    - Specialized extractors only when needed

Usage:
    >>> config = {
    ...     'parameter_name': 'support_scheme',
    ...     'output_type': 'score',
    ...     'score_range': (1, 10),
    ...     'validation_rules': {...}
    ... }
    >>> extractor = GenericExtractor(config, llm_service)
    >>> result = extractor.extract(country, documents)
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re

from ..base_extractor import BaseExtractor
from ..prompts.prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class GenericExtractor(BaseExtractor):
    """Generic configurable extractor for most parameters.
    
    This extractor is configured via a dictionary that specifies:
    - Parameter name and description
    - Expected output type (score, percentage, value)
    - Validation rules
    - Prompt template (or uses default)
    - Parsing logic
    
    This allows adding new parameters without creating new classes.
    """
    
    def __init__(
        self,
        parameter_config: Dict[str, Any],
        llm_service: 'LLMService',
        cache: Optional['ExtractionCache'] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize generic extractor with parameter configuration.
        
        Args:
            parameter_config: Parameter-specific configuration
            llm_service: LLM service instance
            cache: Optional cache
            config: Optional general configuration
        """
        self.parameter_config = parameter_config
        
        # Extract parameter name from config
        parameter_name = parameter_config['parameter_name']
        
        # Initialize base
        super().__init__(
            parameter_name=parameter_name,
            llm_service=llm_service,
            cache=cache,
            config=config
        )
        
        # Store parameter-specific attributes
        self.output_type = parameter_config.get('output_type', 'score')
        self.score_range = parameter_config.get('score_range', (1, 10))
        self.validation_rules = parameter_config.get('validation_rules', {})
        self.prompt_template_name = parameter_config.get('prompt_template')
        
        logger.info(
            f"Initialized GenericExtractor for {parameter_name} "
            f"(output_type: {self.output_type})"
        )
    
    def _get_extraction_prompt(
        self,
        country: str,
        document_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate extraction prompt from configuration.
        
        Args:
            country: Country name
            document_content: Combined document text
            context: Optional additional context
            
        Returns:
            Formatted prompt string
        """
        # Get template from configuration or use default
        if self.prompt_template_name:
            template = PromptTemplates.get_template(self.prompt_template_name)
        else:
            template = self._generate_default_template()
        
        # Format template
        prompt = PromptTemplates.format_template(
            template=template,
            parameter_name=self.parameter_name,
            country=country,
            documents=document_content,
            parameter_definition=self.parameter_config.get('definition', ''),
            scoring_rubric=self._format_scoring_rubric()
        )
        
        return prompt
    
    def _generate_default_template(self) -> str:
        """Generate default prompt template for this parameter.
        
        Returns:
            Default prompt template string
        """
        definition = self.parameter_config.get('definition', f'{self.parameter_name} assessment')
        key_factors = self.parameter_config.get('key_factors', [])
        
        template = f"""Extract {self.parameter_name} for {{country}} from the provided documents.

**PARAMETER DEFINITION**:
{definition}

**KEY FACTORS TO CONSIDER**:
{self._format_key_factors(key_factors)}

**DOCUMENTS**:
{{documents}}

**OUTPUT FORMAT** (respond with valid JSON only):
{{{{
    "value": <extracted value>,
    "confidence": <0.0-1.0>,
    "justification": "<step-by-step reasoning>",
    "quotes": ["<relevant quote 1>", "<relevant quote 2>"],
    "metadata": {{{{
        "data_year": "<year if mentioned>",
        "source_reliability": "<high|medium|low>"
    }}}}
}}}}

Think through this step-by-step before providing your final answer."""
        
        return template
    
    def _format_key_factors(self, factors: List[str]) -> str:
        """Format key factors as bullet list.
        
        Args:
            factors: List of key factors
            
        Returns:
            Formatted string
        """
        if not factors:
            return "- Analyze all relevant information in the documents"
        
        return '\n'.join([f"- {factor}" for factor in factors])
    
    def _format_scoring_rubric(self) -> str:
        """Format scoring rubric from configuration.
        
        Returns:
            Formatted rubric string
        """
        rubric = self.parameter_config.get('scoring_rubric', [])
        
        if not rubric:
            return f"Score on scale from {self.score_range[0]} to {self.score_range[1]}"
        
        lines = []
        for level in rubric:
            score = level.get('score', '')
            description = level.get('description', '')
            lines.append(f"- Score {score}: {description}")
        
        return '\n'.join(lines)
    
    def _parse_llm_response(
        self,
        llm_response: str,
        country: str
    ) -> Dict[str, Any]:
        """Parse LLM response based on output type.
        
        Args:
            llm_response: Raw LLM output
            country: Country name for context
            
        Returns:
            Dictionary with parsed data
        """
        try:
            # Extract JSON from response
            parsed = self._extract_json_from_response(llm_response)
            
            # Validate required fields
            required_fields = ['value', 'confidence', 'justification']
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            # Normalize value based on output type
            normalized_value = self._normalize_value(
                parsed['value'],
                self.output_type
            )
            
            # Ensure metadata exists
            if 'metadata' not in parsed:
                parsed['metadata'] = {}
            
            parsed['metadata']['country'] = country
            parsed['metadata']['output_type'] = self.output_type
            parsed['normalized_value'] = normalized_value
            
            logger.info(
                f"Parsed {self.parameter_name} for {country}: "
                f"value={normalized_value}, confidence={parsed['confidence']:.2f}"
            )
            
            return parsed
        
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            raise
    
    def _validate_extracted_data(
        self,
        data: Dict[str, Any],
        country: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate extracted data based on configuration.
        
        Args:
            data: Extracted data dictionary
            country: Country name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check normalized value
        value = data.get('normalized_value')
        if value is None:
            return False, "Missing normalized value"
        
        # Validate based on output type
        if self.output_type == 'score':
            min_val, max_val = self.score_range
            if not min_val <= value <= max_val:
                return False, f"Score {value} outside valid range [{min_val}, {max_val}]"
        
        elif self.output_type == 'percentage':
            if not 0 <= value <= 150:  # Allow >100% for some contexts
                return False, f"Percentage {value} outside valid range [0, 150]"
        
        # Check confidence
        confidence = data.get('confidence', 0)
        if not 0.0 <= confidence <= 1.0:
            return False, f"Invalid confidence: {confidence}"
        
        # Check justification length
        justification = data.get('justification', '')
        min_justification_length = self.validation_rules.get('min_justification_length', 20)
        if len(justification) < min_justification_length:
            return False, f"Justification too short (minimum {min_justification_length} characters)"
        
        # Apply custom validation rules
        custom_validators = self.validation_rules.get('custom_validators', [])
        for validator in custom_validators:
            is_valid, error = validator(data, country)
            if not is_valid:
                return False, error
        
        return True, None
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON object from LLM response.
        
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
    
    def _normalize_value(self, value: Any, output_type: str) -> float:
        """Normalize extracted value based on output type.
        
        Args:
            value: Raw extracted value
            output_type: Type of output expected
            
        Returns:
            Normalized numeric value
        """
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common suffixes and whitespace
            value_clean = value.strip()
            
            # Remove percentage sign
            if output_type == 'percentage':
                value_clean = value_clean.replace('%', '').strip()
            
            # Extract first number
            number_match = re.search(r'(\d+(?:\.\d+)?)', value_clean)
            if number_match:
                return float(number_match.group(1))
        
        logger.warning(f"Could not normalize value: {value}")
        return 0.0
    
    def get_required_documents(self) -> List[str]:
        """Get required document types from configuration.
        
        Returns:
            List of document type identifiers
        """
        return self.parameter_config.get('required_documents', [])
    
    def get_recommended_sources(self, country: str) -> List[Dict[str, str]]:
        """Get recommended sources from configuration.
        
        Args:
            country: Country name
            
        Returns:
            List of source dictionaries
        """
        return self.parameter_config.get('recommended_sources', [])


# ============================================================================
# PARAMETER CONFIGURATIONS
# ============================================================================

# Each parameter defines its extraction configuration
# This eliminates need for separate extractor classes for most parameters

PARAMETER_CONFIGS = {
    'support_scheme': {
        'parameter_name': 'support_scheme',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Quality and effectiveness of renewable energy support mechanisms including '
            'feed-in tariffs, auctions, tax incentives, net metering, and RECs'
        ),
        'key_factors': [
            'Feed-in Tariff (FiT) design and rates',
            'Auction/tender mechanisms and clearing prices',
            'Tax incentives (ITC, PTC, depreciation)',
            'Net metering policies',
            'Renewable Energy Certificates/Credits',
            'Policy stability and track record'
        ],
        'prompt_template': 'support_scheme',
        'required_documents': [
            'energy_policy_documents',
            'fit_tariff_schedules',
            'auction_results',
            'tax_code_provisions'
        ],
        'validation_rules': {
            'min_justification_length': 30
        }
    },
    
    'track_record': {
        'parameter_name': 'track_record',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Historical renewable energy deployment track record including installed '
            'capacity, growth rates, and project completion success'
        ),
        'key_factors': [
            'Total installed renewable capacity (GW)',
            'Historical growth rates (CAGR)',
            'Number of operational projects',
            'Project completion success rate',
            'Technology diversity (solar, wind, hydro)',
            'Time to market for new projects'
        ],
        'required_documents': [
            'irena_statistics',
            'national_energy_statistics',
            'project_databases'
        ],
        'validation_rules': {
            'min_justification_length': 25
        }
    },
    
    'contract_terms': {
        'parameter_name': 'contract_terms',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'PPA contract bankability including term length, escalation, termination '
            'rights, and risk allocation'
        ),
        'key_factors': [
            'Standard PPA term length',
            'Price escalation mechanisms',
            'Termination rights and penalties',
            'Force majeure provisions',
            'Payment security mechanisms',
            'Dispute resolution procedures'
        ],
        'required_documents': [
            'standard_ppa_templates',
            'regulatory_frameworks',
            'legal_requirements'
        ],
        'validation_rules': {
            'min_justification_length': 30
        }
    },
    
    'offtaker_status': {
        'parameter_name': 'offtaker_status',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Creditworthiness and reliability of power offtakers (utilities, '
            'corporates, government entities)'
        ),
        'key_factors': [
            'Utility financial health',
            'Payment track record',
            'Credit ratings',
            'Government backing',
            'Days sales outstanding (DSO)',
            'Historical payment delays'
        ],
        'required_documents': [
            'utility_financial_statements',
            'credit_ratings',
            'payment_statistics'
        ],
        'validation_rules': {
            'min_justification_length': 25
        }
    },
    
    'long_term_interest_rates': {
        'parameter_name': 'long_term_interest_rates',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Long-term interest rates and financing costs for renewable energy projects'
        ),
        'key_factors': [
            '10-year government bond yields',
            'Project finance lending rates',
            'Debt margin over risk-free rate',
            'Currency stability',
            'Inflation expectations',
            'Central bank policy'
        ],
        'required_documents': [
            'central_bank_data',
            'project_finance_data',
            'bond_market_data'
        ],
        'validation_rules': {
            'min_justification_length': 20
        }
    },
    
    'status_of_grid': {
        'parameter_name': 'status_of_grid',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Grid infrastructure quality, capacity, and reliability for renewable '
            'energy integration'
        ),
        'key_factors': [
            'Transmission and distribution losses (%)',
            'Grid capacity and robustness',
            'System stability (frequency, voltage)',
            'Interconnection capacity',
            'Smart grid deployment',
            'Grid extension plans'
        ],
        'required_documents': [
            'grid_operator_reports',
            'transmission_statistics',
            'infrastructure_plans'
        ],
        'validation_rules': {
            'min_justification_length': 25
        }
    },
    
    'ownership_hurdles': {
        'parameter_name': 'ownership_hurdles',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Foreign ownership restrictions and market access barriers for renewable '
            'energy projects'
        ),
        'key_factors': [
            'Foreign ownership limits (%)',
            'Licensing requirements',
            'Local content requirements',
            'Land acquisition restrictions',
            'Regulatory approval timeframes',
            'Joint venture requirements'
        ],
        'required_documents': [
            'fdi_regulations',
            'licensing_requirements',
            'investment_laws'
        ],
        'validation_rules': {
            'min_justification_length': 25
        }
    },
    
    'ownership_consolidation': {
        'parameter_name': 'ownership_consolidation',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Market concentration and competition level in renewable energy sector'
        ),
        'key_factors': [
            'Market share of top 3 players',
            'HHI index (if available)',
            'Number of active developers',
            'Barriers to entry',
            'Vertical integration levels',
            'Recent market entrants'
        ],
        'required_documents': [
            'market_analysis_reports',
            'developer_databases',
            'competition_assessments'
        ],
        'validation_rules': {
            'min_justification_length': 25
        }
    },
    
    'competitive_landscape': {
        'parameter_name': 'competitive_landscape',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Ease of market entry and competitive dynamics in renewable energy sector'
        ),
        'key_factors': [
            'Number of auction participants',
            'Diversity of developers (foreign/domestic)',
            'Technology competition levels',
            'Permit and licensing ease',
            'Land availability',
            'Recent auction participation trends'
        ],
        'prompt_template': 'competitive_landscape',
        'required_documents': [
            'auction_results',
            'market_reports',
            'regulatory_frameworks'
        ],
        'validation_rules': {
            'min_justification_length': 25
        }
    },
    
    'system_modifiers': {
        'parameter_name': 'system_modifiers',
        'output_type': 'score',
        'score_range': (1, 10),
        'definition': (
            'Composite assessment of external factors including cannibalization, '
            'curtailment, queue dynamics, and supply chain issues'
        ),
        'key_factors': [
            'Price cannibalization risk',
            'Curtailment rates and frequency',
            'Interconnection queue length',
            'Supply chain constraints',
            'Component availability',
            'Logistics and infrastructure'
        ],
        'required_documents': [
            'grid_operator_reports',
            'market_reports',
            'supply_chain_analysis'
        ],
        'validation_rules': {
            'min_justification_length': 30
        }
    }
}


# Factory function
def create_generic_extractor(
    parameter_name: str,
    llm_service: 'LLMService',
    cache: Optional['ExtractionCache'] = None,
    config: Optional[Dict[str, Any]] = None
) -> GenericExtractor:
    """Factory function to create generic extractor for a parameter.
    
    Args:
        parameter_name: Name of parameter
        llm_service: LLM service instance
        cache: Optional cache
        config: Optional configuration
        
    Returns:
        Configured GenericExtractor instance
        
    Raises:
        ValueError: If parameter not found in configs
    """
    if parameter_name not in PARAMETER_CONFIGS:
        raise ValueError(
            f"No configuration found for parameter: {parameter_name}. "
            f"Available: {list(PARAMETER_CONFIGS.keys())}"
        )
    
    parameter_config = PARAMETER_CONFIGS[parameter_name]
    
    return GenericExtractor(
        parameter_config=parameter_config,
        llm_service=llm_service,
        cache=cache,
        config=config
    )
