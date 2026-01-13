"""Research Integration Mixin for Parameter Agents.

This mixin provides agents with research system integration capabilities,
allowing them to fetch and parse research documents as a fallback data source.
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ResearchIntegrationMixin:
    """Mixin to add research system capabilities to parameter agents.

    Usage in agent:
        from research_integration.mixins import ResearchIntegrationMixin
        from research_integration.parsers import CountryStabilityParser

        class CountryStabilityAgent(BaseParameterAgent, ResearchIntegrationMixin):
            def __init__(self, ...):
                super().__init__(...)
                self.research_parser = CountryStabilityParser()

            def _fetch_data(self, country, period):
                # Try research as fallback
                research_data = self._fetch_data_from_research(country, period)
                if research_data:
                    return research_data
                # ... other fallbacks ...
    """

    @property
    def research_orchestrator(self):
        """Lazy-load research orchestrator.

        Returns:
            ResearchOrchestrator instance or None if unavailable
        """
        if not hasattr(self, '_research_orchestrator') or self._research_orchestrator is None:
            try:
                from research_system import ResearchOrchestrator
                self._research_orchestrator = ResearchOrchestrator()
                logger.info(f"Research system integrated with {self.__class__.__name__}")
            except Exception as e:
                logger.warning(f"Research system not available: {e}")
                self._research_orchestrator = None
        return self._research_orchestrator

    def _fetch_data_from_research(
        self,
        country: str,
        period: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Fetch and parse research data for this parameter.

        This method:
        1. Checks if research is enabled
        2. Fetches research document from research system
        3. Parses document using parameter-specific parser
        4. Returns parsed data ready for agent consumption

        Args:
            country: Country name
            period: Time period
            use_cache: Whether to use cached research

        Returns:
            Dictionary with parameter-specific data, or None if unavailable
        """
        # Check if research integration is enabled
        if not hasattr(self, '_research_enabled'):
            self._research_enabled = True

        if not self._research_enabled:
            logger.debug(f"{self.__class__.__name__}: Research integration disabled")
            return None

        # Check if research orchestrator is available
        if self.research_orchestrator is None:
            logger.debug(f"{self.__class__.__name__}: Research orchestrator not available")
            return None

        # Check if parser is configured
        if not hasattr(self, 'research_parser') or self.research_parser is None:
            logger.warning(
                f"{self.__class__.__name__}: No research_parser configured. "
                f"Set self.research_parser in __init__ to enable research integration."
            )
            return None

        try:
            logger.info(f"{self.__class__.__name__}: Fetching research data for {country}")

            # Get research document from research system
            research_doc = self.research_orchestrator.get_research(
                parameter=self.parameter_name,
                country=country,
                period=period,
                use_cache=use_cache
            )

            if not research_doc:
                logger.debug(f"No research available for {self.parameter_name} - {country}")
                return None

            # Parse research document using parameter-specific parser
            parsed_data = self.research_parser.parse(research_doc)

            if not parsed_data:
                logger.warning(f"Parser returned no data for {self.parameter_name} - {country}")
                return None

            logger.info(
                f"Successfully fetched and parsed research data for {country}: "
                f"confidence={parsed_data.get('confidence', 0):.2f}, "
                f"version={parsed_data.get('research_version', 'N/A')}"
            )

            return parsed_data

        except Exception as e:
            logger.error(
                f"Error fetching research data for {self.parameter_name} - {country}: {e}",
                exc_info=True
            )
            return None

    def disable_research_integration(self):
        """Disable research integration (for testing or fallback)."""
        self._research_enabled = False
        logger.info(f"{self.__class__.__name__}: Research integration disabled")

    def enable_research_integration(self):
        """Enable research integration."""
        self._research_enabled = True
        logger.info(f"{self.__class__.__name__}: Research integration enabled")

    def get_research_status(self) -> Dict[str, Any]:
        """Get current research integration status.

        Returns:
            Dictionary with status information
        """
        return {
            'enabled': getattr(self, '_research_enabled', True),
            'orchestrator_available': self.research_orchestrator is not None,
            'parser_configured': hasattr(self, 'research_parser') and self.research_parser is not None,
            'parser_class': self.research_parser.__class__.__name__ if hasattr(self, 'research_parser') else None,
            'parameter_name': self.parameter_name if hasattr(self, 'parameter_name') else None
        }
