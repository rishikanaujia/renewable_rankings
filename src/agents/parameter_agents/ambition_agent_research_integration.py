"""Research System Integration for AmbitionAgent

This module provides research system integration methods that can be added
to the AmbitionAgent without modifying the core agent code heavily.

Usage:
    Add this import to ambition_agent.py:
    from .ambition_agent_research_integration import ResearchIntegrationMixin

    Then mix it into AmbitionAgent:
    class AmbitionAgent(BaseParameterAgent, MemoryMixin, ResearchIntegrationMixin):
"""

from typing import Dict, Any, Optional
from ...core.logger import get_logger

logger = get_logger(__name__)


class ResearchIntegrationMixin:
    """Mixin to add research system capabilities to parameter agents."""

    @property
    def research_orchestrator(self):
        """Lazy-load research orchestrator."""
        if not hasattr(self, '_research_orchestrator') or self._research_orchestrator is None:
            try:
                from research_system import ResearchOrchestrator
                self._research_orchestrator = ResearchOrchestrator()
                logger.info("Research system integrated with agent")
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
        """Fetch renewable target data from research system.

        This provides a rich data source between RULE_BASED and MOCK,
        using comprehensive LLM-generated research documents.

        Args:
            country: Country name
            period: Time period
            use_cache: Whether to use cached research

        Returns:
            Dictionary with target data, or None if research unavailable
        """
        # Initialize attributes if not present
        if not hasattr(self, '_research_enabled'):
            self._research_enabled = True

        if not self._research_enabled:
            return None

        if self.research_orchestrator is None:
            return None

        try:
            logger.info(f"Fetching research data for {country}")

            # Get research document
            research_doc = self.research_orchestrator.get_research(
                parameter=self.parameter_name,
                country=country,
                period=period,
                use_cache=use_cache
            )

            if not research_doc:
                logger.debug(f"No research available for {country}")
                return None

            # Extract key metrics from research
            content = research_doc.content
            key_metrics = content.get('key_metrics', [])

            if not key_metrics:
                logger.warning(f"Research for {country} has no key metrics")
                return None

            # Parse metrics to extract target values
            solar_gw = 0.0
            onshore_wind_gw = 0.0
            offshore_wind_gw = 0.0
            total_gw = 0.0

            for metric in key_metrics:
                if not isinstance(metric, dict):
                    continue

                metric_name = metric.get('metric', '').lower()
                value_str = metric.get('value', '0')

                # Parse value
                try:
                    value = float(value_str)
                except (ValueError, TypeError):
                    continue

                # Match metric to category
                if 'solar' in metric_name or 'pv' in metric_name:
                    solar_gw += value
                elif 'onshore' in metric_name and 'wind' in metric_name:
                    onshore_wind_gw += value
                elif 'offshore' in metric_name and 'wind' in metric_name:
                    offshore_wind_gw += value
                elif 'total' in metric_name or 'combined' in metric_name:
                    total_gw = value
                elif 'wind' in metric_name and 'solar' not in metric_name:
                    onshore_wind_gw += value
                # Handle generic renewable energy targets
                elif any(kw in metric_name for kw in ['renewable', 'renewables', 'target', 'goal', 'capacity', 'ambition']):
                    # Generic renewable target - assign to total if not already set
                    if total_gw == 0.0:
                        total_gw = value

            # Calculate total if not explicitly provided
            if total_gw == 0.0:
                total_gw = solar_gw + onshore_wind_gw + offshore_wind_gw

            # Validate we got meaningful data
            if total_gw < 0.1:
                logger.warning(f"Research for {country} yielded minimal targets: {total_gw} GW")
                return None

            # Build data dictionary
            data = {
                'total_gw': total_gw,
                'solar': solar_gw,
                'onshore_wind': onshore_wind_gw,
                'offshore_wind': offshore_wind_gw,
                'source': 'research',
                'period': period,
                'research_version': research_doc.version,
                'research_quality': content.get('_validation', {}).get('grade', 'N/A'),
                'research_overview': content.get('overview', '')[:200],
                'research_sources': [s.get('name', 'Unknown') for s in content.get('sources', [])[:3]],
                'research_confidence': content.get('confidence', 0.0),
                'research_metadata': {
                    'created_at': research_doc.created_at,
                    'completeness': content.get('completeness_score', 0.0)
                }
            }

            logger.info(
                f"Fetched RESEARCH data for {country}: Total={total_gw:.1f} GW "
                f"(solar={solar_gw:.1f}, onshore={onshore_wind_gw:.1f}, offshore={offshore_wind_gw:.1f}) "
                f"[version {research_doc.version}, quality: {data['research_quality']}]"
            )

            return data

        except Exception as e:
            logger.error(f"Error fetching research data for {country}: {e}", exc_info=True)
            return None

    def disable_research_integration(self):
        """Disable research integration (for testing or fallback)."""
        self._research_enabled = False
        logger.info("Research integration disabled")

    def enable_research_integration(self):
        """Enable research integration."""
        self._research_enabled = True
        logger.info("Research integration enabled")
