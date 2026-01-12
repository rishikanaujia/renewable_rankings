"""Research Agent - LLM-powered agent that conducts parameter-country research

Uses LLMService to generate comprehensive research documents based on
parameter-specific prompts.
"""

from typing import Dict, Any, Optional
import logging
import json
from datetime import datetime
from pathlib import Path

# Import from existing AI extraction system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_extraction_system.llm_service import LLMService, LLMConfig, LLMProvider
from .prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


class ResearchAgent:
    """LLM-powered research agent for parameter-country analysis."""

    def __init__(
        self,
        llm_config: Optional[Dict[str, Any]] = None,
        prompt_generator: Optional[PromptGenerator] = None
    ):
        """Initialize research agent.

        Args:
            llm_config: LLM configuration dictionary
            prompt_generator: PromptGenerator instance (creates if None)
        """
        # Initialize LLM service
        self.llm_service = self._initialize_llm(llm_config)

        # Initialize prompt generator
        if prompt_generator is None:
            self.prompt_generator = PromptGenerator()
        else:
            self.prompt_generator = prompt_generator

        logger.info("ResearchAgent initialized")

    def _initialize_llm(self, config: Optional[Dict[str, Any]]) -> LLMService:
        """Initialize LLM service from configuration.

        Args:
            config: LLM configuration dictionary

        Returns:
            Initialized LLMService
        """
        if config is None:
            # Load from default config
            from src.core.config_loader import config_loader
            full_config = config_loader.get_llm_config()
            config = full_config.get('llm', {})

        # Map provider string to enum
        provider_str = config.get('provider', 'openai')
        provider = LLMProvider(provider_str.lower())

        # Create LLMConfig
        llm_config = LLMConfig(
            provider=provider,
            model_name=config.get('model_name', 'gpt-4-turbo-preview'),
            temperature=config.get('temperature', 0.3),
            max_tokens=config.get('max_tokens', 8000),
            max_retries=config.get('max_retries', 3),
            retry_delay=config.get('retry_delay', 2.0)
        )

        return LLMService(llm_config)

    def conduct_research(
        self,
        parameter: str,
        country: str,
        period: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Conduct comprehensive research for a parameter-country combination.

        Args:
            parameter: Parameter name (e.g., "Ambition")
            country: Country name
            period: Time period (e.g., "Q3 2024")
            additional_context: Additional context or instructions

        Returns:
            Research document as dictionary

        Raises:
            ValueError: If parameter is invalid
            Exception: If research fails
        """
        start_time = datetime.now()

        logger.info(f"Starting research: {parameter} for {country} ({period})")

        try:
            # Generate research prompt
            prompt = self.prompt_generator.generate_prompt(
                parameter_name=parameter,
                country=country,
                period=period or datetime.now().strftime("Q%m %Y")
            )

            # Add additional context if provided
            if additional_context:
                prompt += f"\n\nADDITIONAL CONTEXT:\n{additional_context}\n"

            # Execute research via LLM
            logger.debug("Invoking LLM for research...")
            raw_response = self.llm_service.invoke(prompt)

            # Parse response
            research_data = self._parse_research_response(raw_response)

            # Add metadata
            research_data['_metadata'] = {
                'research_date': datetime.now().isoformat(),
                'execution_time_seconds': (datetime.now() - start_time).total_seconds(),
                'parameter': parameter,
                'country': country,
                'period': period,
                'llm_model': self.llm_service.model_name,
                'prompt_length': len(prompt),
                'response_length': len(raw_response)
            }

            # Store raw response for debugging
            research_data['_raw_response'] = raw_response

            logger.info(
                f"Research completed: {parameter}/{country} "
                f"({(datetime.now() - start_time).total_seconds():.1f}s)"
            )

            return research_data

        except Exception as e:
            logger.error(f"Research failed for {parameter}/{country}: {e}")
            raise

    def _parse_research_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured research document.

        Args:
            response: Raw LLM response

        Returns:
            Parsed research dictionary

        Raises:
            ValueError: If response cannot be parsed
        """
        # Try to extract JSON from response
        try:
            # Look for JSON block
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in response")

            # Parse JSON
            data = json.loads(json_str)

            # Validate required fields
            required_fields = ['parameter', 'country', 'overview']
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                logger.warning(f"Missing fields in research: {missing_fields}")
                # Add empty fields
                for field in missing_fields:
                    data[field] = ""

            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Return structured error with raw response
            return {
                'parameter': '',
                'country': '',
                'overview': '',
                'error': f"Failed to parse JSON: {str(e)}",
                'raw_content': response[:1000]  # First 1000 chars
            }
        except Exception as e:
            logger.error(f"Error parsing research response: {e}")
            raise

    def batch_research(
        self,
        parameter_country_pairs: list[tuple[str, str]],
        period: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Conduct research for multiple parameter-country combinations.

        Args:
            parameter_country_pairs: List of (parameter, country) tuples
            period: Time period for all research

        Returns:
            Dictionary mapping "parameter|country" to research data
        """
        results = {}

        for i, (parameter, country) in enumerate(parameter_country_pairs, 1):
            logger.info(f"Batch research {i}/{len(parameter_country_pairs)}: {parameter}/{country}")

            try:
                research = self.conduct_research(parameter, country, period)
                key = f"{parameter}|{country}"
                results[key] = research
            except Exception as e:
                logger.error(f"Failed batch research for {parameter}/{country}: {e}")
                results[f"{parameter}|{country}"] = {
                    'error': str(e),
                    'parameter': parameter,
                    'country': country
                }

        logger.info(
            f"Batch research complete: {len(results)}/{len(parameter_country_pairs)} successful"
        )

        return results

    def validate_research_quality(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality of research document.

        Args:
            research_data: Research document

        Returns:
            Validation report with scores and issues
        """
        issues = []
        scores = {
            'completeness': 0.0,
            'data_quality': 0.0,
            'source_quality': 0.0,
            'overall': 0.0
        }

        # Check completeness
        required_sections = [
            'overview', 'current_status', 'historical_trends',
            'policy_framework', 'key_metrics', 'sources'
        ]
        present_sections = sum(
            1 for section in required_sections
            if section in research_data and research_data[section]
        )
        scores['completeness'] = present_sections / len(required_sections)

        if scores['completeness'] < 0.7:
            issues.append(f"Missing sections: {7 - present_sections}/10")

        # Check data quality (key metrics)
        key_metrics = research_data.get('key_metrics', [])
        if isinstance(key_metrics, list) and len(key_metrics) >= 3:
            scores['data_quality'] = min(1.0, len(key_metrics) / 5)
        else:
            scores['data_quality'] = 0.3
            issues.append("Insufficient numerical data (< 3 metrics)")

        # Check sources
        sources = research_data.get('sources', [])
        if isinstance(sources, list) and len(sources) >= 3:
            scores['source_quality'] = min(1.0, len(sources) / 5)
        else:
            scores['source_quality'] = 0.3
            issues.append("Insufficient sources (< 3)")

        # Calculate overall score
        scores['overall'] = (
            scores['completeness'] * 0.4 +
            scores['data_quality'] * 0.3 +
            scores['source_quality'] * 0.3
        )

        return {
            'scores': scores,
            'issues': issues,
            'passed': scores['overall'] >= 0.6,
            'grade': self._get_grade(scores['overall'])
        }

    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade.

        Args:
            score: Score between 0 and 1

        Returns:
            Letter grade (A-F)
        """
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'

    def get_stats(self) -> Dict[str, Any]:
        """Get research agent statistics.

        Returns:
            Dictionary with usage statistics
        """
        llm_stats = self.llm_service.get_stats()

        return {
            'total_requests': llm_stats.total_requests,
            'successful_requests': llm_stats.successful_requests,
            'failed_requests': llm_stats.failed_requests,
            'total_tokens': llm_stats.total_prompt_tokens + llm_stats.total_completion_tokens,
            'prompt_tokens': llm_stats.total_prompt_tokens,
            'completion_tokens': llm_stats.total_completion_tokens,
            'total_cost_usd': llm_stats.total_cost_usd,
            'average_latency_ms': llm_stats.average_latency_ms
        }
