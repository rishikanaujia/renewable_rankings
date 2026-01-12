"""Extraction Adapter - Bridge between Research System and AI Extraction System

Allows AI extraction system to utilize cached research documents,
reducing LLM calls and costs.

Minimal integration that doesn't modify existing extraction code.
"""

from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ResearchExtractionAdapter:
    """Adapter that provides research documents to AI extraction system.

    This adapter sits between the research system and AI extraction system,
    allowing extractors to use cached research when available.
    """

    def __init__(self, research_orchestrator=None):
        """Initialize adapter.

        Args:
            research_orchestrator: ResearchOrchestrator instance (creates if None)
        """
        if research_orchestrator is None:
            # Lazy import to avoid circular dependencies
            from .research_orchestrator import ResearchOrchestrator
            self.orchestrator = ResearchOrchestrator()
        else:
            self.orchestrator = research_orchestrator

        logger.info("ResearchExtractionAdapter initialized")

    def get_research_context(
        self,
        parameter: str,
        country: str,
        period: Optional[str] = None,
        auto_generate: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get research document to use as context for extraction.

        Args:
            parameter: Parameter name
            country: Country name
            period: Time period
            auto_generate: If True, generate new research if not cached

        Returns:
            Research content dictionary, or None if not available
        """
        try:
            # Check if research exists
            if not self.orchestrator.research_store.exists(parameter, country):
                if not auto_generate:
                    logger.debug(f"No research found for {parameter}/{country}")
                    return None

                logger.info(f"Generating research for {parameter}/{country}")
                doc = self.orchestrator.get_research(
                    parameter=parameter,
                    country=country,
                    period=period,
                    use_cache=False
                )
            else:
                # Load cached research
                doc = self.orchestrator.get_research(
                    parameter=parameter,
                    country=country,
                    period=period,
                    use_cache=True
                )

            if doc:
                logger.debug(f"Using research v{doc.version} for {parameter}/{country}")
                return doc.content
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting research context: {e}")
            return None

    def extract_key_data(
        self,
        parameter: str,
        country: str,
        data_type: str = "key_metrics"
    ) -> Optional[Any]:
        """Extract specific data from research document.

        Args:
            parameter: Parameter name
            country: Country name
            data_type: Type of data to extract
                      ('key_metrics', 'overview', 'policy_framework', etc.)

        Returns:
            Extracted data, or None if not available
        """
        research = self.get_research_context(parameter, country)

        if research is None:
            return None

        return research.get(data_type)

    def enhance_extraction_prompt(
        self,
        base_prompt: str,
        parameter: str,
        country: str
    ) -> str:
        """Enhance an extraction prompt with research context.

        This can be used by extractors to add research context to their prompts.

        Args:
            base_prompt: Original extraction prompt
            parameter: Parameter name
            country: Country name

        Returns:
            Enhanced prompt with research context
        """
        research = self.get_research_context(parameter, country)

        if research is None:
            logger.debug(f"No research context available for {parameter}/{country}")
            return base_prompt

        # Build context section
        context = "\n\n--- BACKGROUND RESEARCH CONTEXT ---\n\n"

        # Add overview
        if 'overview' in research:
            context += f"Overview:\n{research['overview'][:500]}...\n\n"

        # Add key metrics
        if 'key_metrics' in research and research['key_metrics']:
            context += "Key Metrics:\n"
            metrics = research['key_metrics']
            if isinstance(metrics, list):
                for metric in metrics[:5]:
                    if isinstance(metric, dict):
                        context += f"• {metric.get('metric')}: {metric.get('value')} {metric.get('unit', '')}\n"
            context += "\n"

        # Add current status
        if 'current_status' in research:
            context += f"Current Status:\n{research['current_status'][:400]}...\n\n"

        context += "--- END CONTEXT ---\n\n"

        # Prepend to base prompt
        enhanced = context + base_prompt

        logger.debug(f"Enhanced prompt with research context (+{len(context)} chars)")

        return enhanced

    def get_cached_value(
        self,
        parameter: str,
        country: str,
        metric_name: str
    ) -> Optional[Dict[str, Any]]:
        """Try to get a specific metric value from cached research.

        This can be used for quick lookups without LLM calls.

        Args:
            parameter: Parameter name
            country: Country name
            metric_name: Name of metric to find

        Returns:
            Metric dictionary with value, unit, source, or None
        """
        metrics = self.extract_key_data(parameter, country, "key_metrics")

        if not metrics:
            return None

        # Search for matching metric
        metric_name_lower = metric_name.lower()

        for metric in metrics:
            if isinstance(metric, dict):
                if metric_name_lower in metric.get('metric', '').lower():
                    return metric

        return None

    def is_research_available(self, parameter: str, country: str) -> bool:
        """Check if research is available for parameter-country.

        Args:
            parameter: Parameter name
            country: Country name

        Returns:
            True if research exists and is cached
        """
        return self.orchestrator.research_store.exists(parameter, country)

    def get_research_age(self, parameter: str, country: str) -> Optional[float]:
        """Get age of research document in days.

        Args:
            parameter: Parameter name
            country: Country name

        Returns:
            Age in days, or None if research doesn't exist
        """
        if not self.is_research_available(parameter, country):
            return None

        try:
            from datetime import datetime

            version = self.orchestrator.research_store.version_manager.get_latest_version(
                parameter, country
            )
            metadata = self.orchestrator.research_store.version_manager.load_version_metadata(
                parameter, country, version
            )

            if metadata:
                created = datetime.fromisoformat(metadata.created_at)
                age = datetime.now() - created
                return age.total_seconds() / 86400  # Convert to days

        except Exception as e:
            logger.error(f"Error calculating research age: {e}")

        return None


# Convenience function for quick integration
def get_research_for_extraction(
    parameter: str,
    country: str,
    period: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Convenience function to get research context.

    Args:
        parameter: Parameter name
        country: Country name
        period: Time period

    Returns:
        Research content dictionary or None
    """
    adapter = ResearchExtractionAdapter()
    return adapter.get_research_context(parameter, country, period)
